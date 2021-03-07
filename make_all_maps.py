import make_temp_map
import csv
import time

def main():
	years = [2018]
	days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

	stations = []
	station_data = csv.reader(open('Stations/Inventory Headerless.csv', "r"), delimiter=",")
	for row in station_data:
		try:
			if row[3] != '':
				stations.append(int(row[3]))
		except IndexError:
			pass

	start = time.perf_counter_ns()

	month = 1


	for year in years:
		for day in range(days[month]):
			for i in range(len(stations)):			
				station = stations[i]
				print("Now Performing " + str(year) + " " + str(month) + " " + str(day + 1) + " Station: " + str(station), end = "\n\n")

				duration = time.perf_counter_ns() - start
				complete = (i / len(stations) * ((day + 1) / days[month]) * 100)

				try:
					make_temp_map.main(station, year, month, day + 1)
				except:
					pass

				print("{:.5f}".format(complete) + "% Complete", end = '')
				print(" DURATION: " + str(duration / (1000000000 * 60)) + " minutes")	

	print("\a")


if __name__ == "__main__":
	main()