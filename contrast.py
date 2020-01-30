import numpy as np
import matplotlib.pyplot as plt
import imageio as imio
import glob

def save_img(img, fname):
	img = (img-np.min(img))/(np.max(img)-np.min(img))
	img = (img*255.).astype(np.uint8)
	imio.imwrite(fname, img)

IMAGE_LOC = 'input_images'
file_list = glob.glob(IMAGE_LOC+'/*.png')

for f in file_list:
	fname = f.split('/')[-1].split('.')[0]
	img = imio.imread(f).astype(np.float32)/255.

	print("Image dimensions for ", fname, img.shape)

	if len(img.shape) < 3: # if the image is in greyscale
		img = np.tile(img[..., np.newaxis], (1, 1, 3))

	r = img[..., 0]
	g = img[..., 1]
	b = img[..., 2]

	w = 0.33*np.ones_like(img) # weights for normalizing

	pix = img.shape[0]*img.shape[1]

	mu = np.mean(img, (0, 1))
	std = np.std(img, (0, 1))

	out = np.sum(img*w, 2)
	mu = np.mean(out)
	var = np.mean((out-mu)**2)

	grad_r = (2.*(pix-1)/pix)*(out - mu)*r
	grad_g = (2.*(pix-1)/pix)*(out - mu)*g
	grad_b = (2.*(pix-1)/pix)*(out - mu)*b

	al = 100.*np.exp(-1.*(var+mu))

	out = np.sum(img*w, 2)
	init = np.tile(out[..., np.newaxis], (1, 1, 3))
	save_img(out, './results/'+fname+'_initial.png')

	standard = 0.30*r+0.59*g+0.11*b
	standard = np.tile(standard[..., np.newaxis], (1, 1, 3))
	save_img(standard, './results/'+fname+'_opencv.png')

	epochs = 500

	be = 0.99

	for i in range(epochs):
		out = np.sum(img*w, 2)
		mu = np.mean(out)
		var = np.mean((out-mu)**2)

		al = 1000.*np.exp(-1.*(var+mu))

		if i % 100 == 0:
			print("Epoch {0:5d} | Mean {1:0.6f} | Variance {2:0.6f} | Learning rate {3:0.6f} | Mean weights {4:0.5f}".format(i, mu, var, al, np.mean(w)))

		grad_r = (2.*(pix-1)/(pix*pix))*(out - mu)*r+r
		grad_g = (2.*(pix-1)/(pix*pix))*(out - mu)*g+g
		grad_b = (2.*(pix-1)/(pix*pix))*(out - mu)*b+b
		
		w[..., 0] += al*grad_r
		w[..., 1] += al*grad_g
		w[..., 2] += al*grad_b

		w = (w-np.min(w))/(np.max(w)-np.min(w))
		w += np.random.uniform(0.0001, 1, w.shape)*0.001
		w = (w-np.min(w))/(np.max(w)-np.min(w))

	out = np.sum(img*w, 2)
	save_img(out, './results/'+fname+'_final.png')

	out = (out - np.min(out))/(np.max(out) - np.min(out))
	final_result = np.concatenate((img, standard, init, np.tile(out[..., np.newaxis], (1, 1, 3))), 1)
	final_result = (final_result*255.).astype(np.uint8)
	imio.imwrite('results/'+fname+'.png', final_result)