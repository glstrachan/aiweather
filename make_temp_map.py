# Input will be a station id (marker), a date and a time

# First we locate all stations whos decimal degrees coordinates are within +- 150km
# Then for all of these stations we check which of them will have data for our desired date and time

# Next we iterate through the remaining list of stations, and add to a list an object
# The object will have
	# An id
	# A decimal x and y coordinate
	# A temperature (Based on the date and time)

# Next for each of the 2500 (50 * 50) cells, we use interpolation to determine their temperature
# For every cell we find the five closest station objects
# Based on their relative distances we assign each of them a weight
# The weighted average of their temperatures will be assigned to the cell at the given coordinate

# Once the map has been completed we save it as a csv numpy array


# For time
import datetime

# For inventory and data retrieval
import csv
import sys
import os

# For calculations
import math

# For arrays
import numpy as np


threshold = 70


def main(station_id, year, month, date):
	# Get the stations coordinates
	stations = csv.reader(open('Stations/Inventory Headerless.csv', "r"), delimiter=",")
	lat, lon = 1000, 1000

	# Searches for a station with the specified id
	for row in stations:
		if station_id == int(row[3]):
			if row[4] == '' or row[5] == '':
				return 1
			lat = float(row[4])
			lon = float(row[5])
			break

	if lat == 1000:
		#print("No such station " + str(station_id) + ", for year " + str(year))
		return 1

	# Calculate the distance of one latitude degree at latitude
	lat_dist = (111132.954 - 559.822 * math.cos(math.radians(lat) * 2) + 1.175 * math.cos(math.radians(lat) * 4)) / 1000

	# Calculate the distance of one longitude degree at latitude
	lon_dist = ((math.pi / 180) * 6378137 * math.cos(math.atan((6356752.3142 / 6378137) * math.tan(math.radians(lat))))) / 1000


	# Calculate maximum and minimum decimal coordinates for +- 150km
	min_lat = lat - (150 * (1 / lat_dist))
	max_lat = lat + (150 * (1 / lat_dist))
	min_lon = lon - (150 * (1 / lon_dist))
	max_lon = lon + (150 * (1 / lon_dist))


	# Gets all viable stations in a list
	station_list = get_stations(min_lat, max_lat, min_lon, max_lon, year)

	if len(station_list) < threshold:
		#print("Not enough stations for station: " + str(station_id) + " for year: " + str(year)) 
		#print("stations: " + str(len(station_list)))
		return 1

	# For every hour make map
	for hour in range(24):
		make_hour_map(station_id, min_lat, max_lat, min_lon, max_lon, station_list, year, month, date, hour)


# Gets all of the stations that are within the defined range and have data for the specified years
def get_stations(min_lat, max_lat, min_lon, max_lon, year):
	station_list = []

	stations = csv.reader(open('Stations/Inventory Headerless.csv', "r"), delimiter=",")

	for row in stations:
		try:
			if row[4] == '' or row[5] == '':
				return 1 
			lat = float(row[4])
			lon = float(row[5])
		except IndexError:
			pass

		if lat >= min_lat and lat <= max_lat and lon >= min_lon and lon <= max_lon:
			if int(row[11]) <= year and year <= int(row[12]):
				new_station = Location(lat, lon, int(row[3]))
				station_list.append(new_station)


	return station_list


# Stores decimal coordinates pertaining to a station location
class Location:
	def __init__(self, lat, lon, name):
		self.lat = lat
		self.lon = lon
		self.name = name


# Stores decimal coordinates 
class Station:
	def __init__(self, lat, lon, temp):
		self.lat = lat
		self.lon = lon
		self.temp = temp

	def __lt__(self, other):
		return self.temp < other.temp



# Makes a map for a marker station and an hour
def make_hour_map(station_id, min_lat, max_lat, min_lon, max_lon, station_list, year, month, date, hour):

	num_hour = hour

	if hour < 10:
		hour = '0' + str(hour) + ':00'
	else:
		hour = str(hour) + ':00'


	# Get all of the station temperatures defined by station_list
	station_temps = []

	for location in station_list:
		station_data = csv.reader(open('Hourly Data/' + str(location.name) + '/hourly/' + str(year) + '.csv', "r"), delimiter=",")

		temp = 0
		row_on = 0

		for row in station_data:
			if row_on == 0:
				row_on = row_on + 1
				continue

			try:
				found_month = int(row[6])
				found_date = int(row[7])
				found_hour = row[8]
				found_temp = float(row[9])

				if found_month == month and found_date == date and found_hour == hour:
					new_station = Station(location.lat, location.lon, found_temp)
					station_temps.append(new_station)
					break
			except IndexError:
				pass #Invalid Row Quantity
			except ValueError:
				pass #Invalid Temperature


	if len(station_temps) < threshold:
		#print("Not enough stations for station year:" + str(year)) 
		return 1
	

	x_step = (max_lat - min_lat) / 50
	y_step = (max_lon - min_lon) / 50


	# Holds the standardized weather cell data
	weather_cells = np.arange(2500, dtype=np.float64).reshape(50, 50)

	for x in range(50):
		for y in range(50):

			# Position in center of cell
			new_lat = min_lat + (x_step * x) + (x_step / 2)
			new_lon = min_lon + (y_step * y) + (y_step / 2)

			close_temps = []
			lengths = []

			for i in range(len(station_temps)):

				temp = station_temps[i]
				new_length = pythagoras(new_lat, new_lon, temp.lat, temp.lon)
				
				if len(close_temps) < 5:
					close_temps.append(temp)
					lengths.append(new_length)

				else:
					highest = -1
					index = -1

					for i in range(len(lengths)):
						if new_length < lengths[i]:
							if lengths[i] < highest:
								index = i
								highest = lengths[i]

					if index >= 0:
						close_temps.pop(index)
						lengths.pop(index)

						close_temps.append(temp)
						lengths.append(new_length)

			# Determine max length, max length gets weight of 0
			highest = 0

			for i in range(len(lengths)):
				if lengths[i] > highest:
					highest = lengths[i]


			sum = 0

			# Assign lengths inverted values (highest - length)
			for i in range(len(lengths)):
				lengths[i] = highest - lengths[i]
				sum = sum + lengths[i]

			avg_temp = 0
			for i in range(len(lengths)):
				avg_temp = avg_temp + lengths[i] * close_temps[i].temp

			avg_temp = avg_temp / sum

			weather_cells[x][y] = avg_temp

	# Save numpy array as csv file

	if not os.path.isdir(os.getcwd() + '/Temperature Maps/' + str(year) + '/' + str(station_id)):
		os.makedirs(os.getcwd() + '/Temperature Maps/' + str(year) + '/' + str(station_id))
	np.savetxt('Temperature Maps/' + str(year) + '/' + str(station_id) + '/' + str(month) + '_' + str(date) + '_' + str(num_hour) + '.csv', weather_cells, delimiter=',')
				


# Returns the distance between any two point
def pythagoras(x, y, a, b):
	return math.sqrt((x - a) * (x - a) + (y - b) * (y - b))


