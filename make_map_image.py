import numpy as np
weather_map = np.genfromtxt('2018.csv', delimiter=',')

from PIL import Image, ImageDraw

def main():
	px = 25
	size = 50

	img = Image.new('RGB', (size * px, size * px), color = (255, 255, 255))
	draw = ImageDraw.Draw(img)

	for x in range(size):
		for y in range(size):
			value = int((weather_map[x][y] + 5) / 10 * 255)
			draw.rectangle([y * px, x * px, (y + 1) * px, (x + 1) * px], fill = (value, value, value), outline = None, width = 1)

	img.save('spiral.jpg')


if __name__ == "__main__":
	main()