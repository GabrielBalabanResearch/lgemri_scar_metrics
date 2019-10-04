from transmurality import *
from scipy import ndimage

import os
import pandas as pd
import nibabel as nib
import numpy as np
import cv2 as cv
import argparse

def get_scar_interface_length(seg_image, markers):
	seg_array = seg_image.get_data()[:,:,0]
	pixel_area = seg_image.header.get_zooms()[0]*seg_image.header.get_zooms()[1]
	interface_contours, foo = cv.findContours((seg_array == markers.scar).astype("uint8").copy(),
										  		cv.RETR_LIST,
										  		cv.CHAIN_APPROX_NONE)
	is_closed = [(cont[0] == cont[-1]).all() for cont in interface_contours]
	return sum([cv.arcLength(cont, closed) for cont, closed in zip(interface_contours, is_closed)])*pixel_area

def get_scar_radiality(seg_image, markers):
	seg_array = seg_image.get_data()[:,:,0]

	x,y = np.where(np.logical_or(seg_array == markers.scar, seg_array == markers.myo))
	
	#calculate centre of blood pool
	pc = np.array([np.mean(x), np.mean(y)])

	thetas = np.arctan2(x - pc[0], y - pc[1])
	theta_im = np.zeros(seg_array.shape)
	theta_im[x,y] = thetas
	thetas = theta_im[seg_array == markers.scar]
	
	#Circular angular variance formula
	var_theta = 1 - (np.sqrt((np.cos(thetas).sum())**2 + (np.sin(thetas).sum())**2))/len(thetas)
	return var_theta

def get_scar_components(seg_image, markers):
	labeled, num_components = ndimage.label(seg_image.get_data() == markers.scar)
	return num_components

def get_scar_entropy(raw_image, seg_image, markers):
	entropy_vals = raw_image.get_data()[seg_image.get_data() == markers.scar]
	if len(np.unique(entropy_vals)) == 1:
		return 0
	
	pdf = np.histogram(np.array(entropy_vals), 
					   density = True,
					   bins = np.unique(entropy_vals).max() - np.unique(entropy_vals).min())[0]
	pdf = pdf[pdf >0]
	return np.sum(-np.log(pdf)*pdf)

def get_scar_area(seg_image, markers):
	pixel_area = seg_image.header.get_zooms()[0]*seg_image.header.get_zooms()[1]
	return (seg_image.get_data() == markers.scar).sum()*pixel_area

def main(args):
	raw_image = nib.load(args.raw_image)
	seg_image = nib.load(args.segmentation)

	#Image markers in segmentation
	markers = lambda:None
	markers.scar = args.mark_scar
	markers.myo = args.mark_myocardium

	scar_area = get_scar_area(seg_image, markers)
	scar_entropy = get_scar_entropy(raw_image, seg_image, markers)
	scar_components = get_scar_components(seg_image, markers)
	scar_transmurality = get_scar_transmurality(seg_image, markers)
	scar_radiality = get_scar_radiality(seg_image, markers)
	scar_interface_length = get_scar_interface_length(seg_image, markers)
	
	features_df = pd.DataFrame([[scar_area,
								 scar_entropy,
								 scar_components,
								 scar_transmurality,
								 scar_radiality,
								 scar_interface_length]],
								 columns = ["area", 
				   							"entropy",
				   							"components",
				   							"transmurality",
				   							"scar_radiality",
				   							"interface_length"])

	features_df.to_csv(args.output,
						index = False)

	print "Exported scar metrics to ", args.output

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-raw_image", default = "example_data/rawimage.nii", help = "Raw pixel data in nifti format.")	
	parser.add_argument("-segmentation", default = "example_data/segmentation.nii", help = "Segmentation pixel data in nifti format.")	
	parser.add_argument("-output", default = "image_metrics.csv", help = "Location of desired output file in .csv format.")
	parser.add_argument("-mark_myocardium", default = 1, type = int, help = "The marker of the myocardium in the segmentation.")
	parser.add_argument("-mark_scar", default = 3, type = int,help = "The marker of the scar in the segmentation.")
	args = parser.parse_args()
	main(args)
