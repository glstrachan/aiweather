import os

rootdir = 'C:/Users/xray1/OneDrive/Desktop/Weather/Hourly Data'


for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		if(len(file) > 10):
			os.rename(r'' + subdir + '/' + file + '',r'' + subdir + '/' + file[33:37] + '.csv')

