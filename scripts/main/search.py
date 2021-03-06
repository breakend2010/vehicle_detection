import time
import numpy as np
np.random.seed(1337)  # for reproducibility
from keras.preprocessing import image as imageproc
import pandas as pd
import sys
try:
    import cPickle as pickle
except:
    import pickle
from keras.models import model_from_json
from keras.optimizers import SGD
from PIL import Image
import json

#path_to_project = "/home/konoplich/workspace/projects/BloodTranscriptome/scripts/data/vehicle_detection/" #ubuntu
path_to_project = "C:/workspace/ml/graduate_work/vehicle_detection/" #windows"

path_to_model = path_to_project + "/models/dnn200_128"

path_to_photo = path_to_project + "scripts/main/photo.jpg"#sys.argv[1]

path2 = path_to_project + "scripts/main/99.jpg"#sys.argv[1]

def load_neural_network(file_from):
	file1 = open(file_from, 'rb')
	(nn_arch, nn_weights_path) = pickle.load(file1)
	file1.close()
	nn = model_from_json(nn_arch)
	nn.set_weights(nn_weights_path)
	return nn

def get_image(x):
	image = imageproc.array_to_img(x)
	return image

def get_array(image):
	x = imageproc.img_to_array(image)
	return x

def load_image(path):
	image = imageproc.load_img(path, grayscale=True)
	return image

def save_photos(imgs, path):
	cnt = 0
	for x in imgs:
		cnt += 1
		image = get_image(x)
		image.save(path + str(cnt) + '.jpg')	

def resize_imagearrays(imgs, size):
	img_res = []
	for x in imgs:
		image = get_image(x)
		image.thumbnail(size, Image.ANTIALIAS)
		x = imageproc.img_to_array(image)
		img_res.append(x)
	img_res = np.array(img_res)
	return img_res

def filtration(imgs, coord, min_dist):
	x = coord[0]
	num = 0
	images = []
	images.append(imgs[0])
	for i in range(1, len(imgs)):
		if abs(coord[i][0] - x[0]) + abs(coord[i][1] - x[1]) > min_dist:
			x = coord[i]
			num = i
			images.append(imgs[num])
	imgs = np.array(images)
	return imgs

def geometric_center(img, x, y):
	m10 = 0
	m01 = 0
	m00 = 0
	for i in range(0, img.shape[1]):
		for j in range(0, img.shape[2]):
			m10 += (i ** 1) * (j ** 0) * img[0][i][j]
			m01 += (i ** 0) * (j ** 1) * img[0][i][j]
			m00 += (i ** 0) * (j ** 0) * img[0][i][j]
	xx = int(m10 / m00)
	yy = int(m01 / m00)
	return (x + xx, y + yy)

def get_windows(image, size = [48, 48], step = 1, factor = 1.4, min_din = 1.5):
	x = 0
	y = 0
	imgs = []
	imgsmax = []
	imgsmin = []
	coord = []
	i = 0
	img_array = get_array(image)
	while x + size[0] <= image.size[1]:
		y = 0
		while y + size[1] <= image.size[0]:
			l = x + size[0]
			r = y + size[1]
			lmin = x + int(size[0] / factor)
			rmin = y + int(size[1] / factor)
			lmax = x + int(size[0] * factor)
			rmax = y + int(size[1] * factor)
			imgs.append(img_array[0:1, x:l, y:r])
			imgsmin.append(img_array[0:1, x:lmin, y:rmin])
			if lmax < image.size[1] and rmax < image.size[0]:
				imgsmax.append(img_array[0:1, x:lmax, y:rmax])
			coord.append(((x + l) / 2, (y + r) / 2 , i * 3))
			coord.append(((x + lmin) / 2, (y + rmin) / 2 , i * 3 + 1))
			if lmax < image.size[1] and rmax < image.size[0]:
				coord.append(((x + lmax) / 2, (y + rmax) / 2 , i * 3 + 2))
			i += 1
			(xx, yy) = geometric_center(img_array[0:1, x:l, y:r], x, y)
			l = xx + size[0]
			r = yy + size[1]
			lmin = xx + int(size[0] / factor)
			rmin = yy + int(size[1] / factor)
			lmax = xx + int(size[0] * factor)
			rmax = yy + int(size[1] * factor)
			if l < image.size[1] and r < image.size[0]:
				imgs.append(img_array[0:1, xx:l, yy:r])
				coord.append(((xx + l) / 2, (yy + r) / 2 , i * 3))
			if lmin < image.size[1] and rmin < image.size[0]:
				imgsmin.append(img_array[0:1, xx:lmin, yy:rmin])
				coord.append(((xx + lmin) / 2, (yy + rmin) / 2 , i * 3 + 1))
			if lmax < image.size[1] and rmax < image.size[0]:
				imgsmax.append(img_array[0:1, xx:lmax, yy:rmax])
				coord.append(((xx + lmax) / 2, (yy + rmax) / 2 , i * 3 + 2))
			i += 1
			y += step
		x += step
	imgs = resize_imagearrays(imgs, (48, 48))
	imgsmax = resize_imagearrays(imgsmax, (48, 48))
	imgsmin = resize_imagearrays(imgsmin, (48, 48))
	imgs = np.concatenate((imgs, imgsmax, imgsmin), axis = 0)
	print(imgs.shape)
	imgs = filtration(imgs, coord, min_din) 
	print(imgs.shape)
	return imgs

def test(model, img_array):
	arr1 = img_array[0:1, 0:48, 0:48]
	img1 = imageproc.img_to_array(imageproc.load_img(path2, grayscale=True))
	ar2 = []
	arr4 = np.zeros([1, 48, 48])
	ar2.append(arr1)
	ar2.append(img1)
	ar2.append(arr4)

	ar3 = np.array(ar2)
	print(ar3.shape)
	att = model.predict(ar3)
	for x in att:
		print("%.4f" % x)
	

image = load_image(path_to_photo)
img_array = get_array(image)


model = load_neural_network(path_to_model)

sgd = SGD(lr=0.001, decay=0, momentum=0, nesterov=True)
model.compile(loss='binary_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])

test(model, img_array)

start_time = time.time()
imgs = get_windows(image, size = [100, 100], step = 80, min_din = 50)

imgs1 = imgs

arr  = model.predict(imgs1)

mx = 0.97

cnt = 0
for x in arr:
	cnt += 1
	if mx <= x:
		get_image(imgs1[cnt - 1]).save("res/" +str(cnt) + ".jpg")

print("--- %s seconds ---" % (time.time() - start_time))


		                                 