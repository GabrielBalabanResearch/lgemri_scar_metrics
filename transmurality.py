from scipy.ndimage.morphology import binary_fill_holes
from matplotlib import pyplot as plt

import numpy as np
import collections

NUM_RAYS = 360

def get_scar_transmurality(seg_nii, markers):
	mark_outsidemyo = max(markers.myo, markers.scar) + 1

	segdata = seg_nii.get_data()[:,:,0]
	myo_im = np.logical_or(segdata == markers.scar, segdata == markers.myo)
	outside_myo = np.logical_not(binary_fill_holes(myo_im))
	
	ray_im = np.array(myo_im, dtype =int)
	ray_im[outside_myo] = mark_outsidemyo
	
	centre_coords = np.mean(np.array(np.where(myo_im >0)),
 							axis = 1)

	thetas = np.linspace(0, 2*np.pi, NUM_RAYS + 1)[:-1]
	rays = [trace_ray(ray_im, centre_coords[0], centre_coords[1], theta, mark_outsidemyo) for theta in thetas]
	
	scar_im = segdata == markers.scar

	ray_counts = [collections.Counter(scar_im[ray[:,0], ray[:,1]]) for ray in rays]
	trans_along_rays = [(r[True])/float((r[True] + r[False])) for r in ray_counts]

	mean_trans = np.mean(trans_along_rays[trans_along_rays > 0])
	return mean_trans
	
def trace_ray(image, X, Y, theta, mark_outsidemyo):
	"""
	Traces a ray through a SAX image, returning the list of pixels which intersect the ray
	Only the ray going through the myocardium is returned. 
	In the image 0 = blood pool
				 1 = myocardium
				 mark_outsidemyo = outside of the myocardium

	Algorithm is based on Amanatides and Woo (1987)
	"""

	px, py = (int(X), int(Y))
	dx, dy = np.cos(theta), np.sin(theta)

	stepX, stepY = np.array(np.sign([dx, dy]), dtype = int)

	if stepX == 1:
		get_nextX = lambda x : np.floor(x + 1)
	else:
		get_nextX = lambda x : np.ceil(x - 1)

	if stepY == 1:
		get_nextY = lambda y : np.floor(y + 1)
	else:
		get_nextY = lambda y : np.ceil(y - 1)
	
	t = 0

	pixels = []
	while True:
		#Ray is outside epicardium so stop
		if image[px, py] == mark_outsidemyo:
			break

		#We are not in the myocardium so record
		if image[px, py]  == 1:
			pixels.append([px, py])

		tMaxX = np.abs((get_nextX(X) - X)/dx) if dx != 0 else np.inf
		tMaxY = np.abs((get_nextY(Y) - Y)/dy) if dy != 0 else np.inf
		
		if tMaxX < tMaxY:
		 	t = tMaxX

		elif tMaxY <= tMaxX:
		 	t = tMaxY		
		
		#Round to prevent funny numerical errors
		X, Y = (np.around(X + t*dx, 12), np.around(Y + t*dy, 12))
		
		px, py = (int(X), int(Y))

	return np.array(pixels)
	
def plot_with_rays(image, graylevels, myo_im, scar_im, rays):
	"""output an MRI with the rays visualized in yellow"""

	pngout = PNGOutput(graylevels, (0.2, 0.5))

	threshim = np.copy(myo_im)
	threshim[threshim == 2] = 0
	threshim[scar_im > 0] = 3

	regionim = pngout.make_regionim(threshim)

	color_ray = [1,1,0,1]

	for ray in rays:
	    regionim[ray[:,0], ray[:,1]] = color_ray

	plt.imshow(regionim)
	#plt.show()
	plt.savefig("rayimage.png")
	exit()
	#from IPython import embed; embed()

def test_trace_ray():
	image = np.zeros((100,100))
	
	inner_box = np.zeros(image.shape, dtype = bool)
	inner_box[40:60, 40:60] = 1

	outer_box = np.zeros(image.shape, dtype = bool)
	outer_box[20:80, 20:80] = 1

	image[np.logical_and(outer_box, np.logical_not(inner_box))] = 1
	image[np.logical_not(outer_box)] = 2

	ray = trace_ray(image, 50.0, 50.0, -np.pi/4)
	print ray[-1]
	image[ray[:, 0], ray[:,1]] = 3

	plt.imshow(image)
	plt.show()

if __name__ == "__main__":
	test_trace_ray()