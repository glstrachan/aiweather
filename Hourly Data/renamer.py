import os

rootdir = '/root/aiweather/Hourly Data'


for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		if(len(file) < 10):
			print(file[0:4])
			#os.rename(r'' + subdir + '/' + file + '',r'' + subdir + '/' + file[33:37] + '_' + file[(len(file) - 15):(len(file) - 13)] + '.csv')
			os.rename(r'' + subdir + '/' + file + '',r'' + subdir + '/' + file[0:4] + '_01.csv')
