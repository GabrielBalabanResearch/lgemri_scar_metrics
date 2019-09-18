from transmurality import *
from matplotlib import pyplot as plt
from visualiser.segmented_mri import get_interface
from scipy import ndimage

import os
import pandas as pd
import nibabel as nib
import numpy as np
import cv2 as cv
import argparse

def get_scar_interface_length(seg_arr, marker, imres):
	interface_im = get_interface(seg_arr, marker, thickness = 1)
	interface_contours, foo = cv.findContours(interface_im.copy(),
										     cv.RETR_LIST,
										     cv.CHAIN_APPROX_NONE)
	is_closed = [(cont[0] == cont[-1]).all() for cont in interface_contours]
	return sum([cv.arcLength(cont, closed) for cont, closed in zip(interface_contours, is_closed)])*imres


class CircleStats():
	@staticmethod
	def mean(thetas):
		return np.arctan2(np.sin(thetas).sum(), np.cos(thetas).sum())
	
	@staticmethod
	def var(thetas):
		var_theta = 1 - (np.sqrt((np.cos(thetas).sum())**2 + (np.sin(thetas).sum())**2))/len(thetas)
		return var_theta

def get_radial_extent(theta_arr, scar_arr, marker):
	thetas = theta_arr[scar_arr == marker]
	return CircleStats.var(thetas)

###########################################
#Functions which loop over all images and calculate feature vectors
###########################################

def get_scar_components(seg_image):
	labeled, num_components = ndimage.label(seg_image.get_data() == MARK_SCAR)
	return num_components

def get_scar_entropy(raw_image, seg_image):
	entropy_vals = raw_image.get_data()[seg_image.get_data() == MARK_SCAR]
	if len(np.unique(entropy_vals)) == 1:
		return 0
	
	pdf = np.histogram(np.array(entropy_vals), 
					   density = True,
					   bins = np.unique(entropy_vals).max() - np.unique(entropy_vals).min())[0]
	pdf = pdf[pdf >0]
	return np.sum(-np.log(pdf)*pdf)

def get_scar_area(seg_image):
	pixel_area = seg_image.header.get_zooms()[0]*seg_image.header.get_zooms()[1]
	return (seg_image.get_data() == MARK_SCAR).sum()*pixel_area

def main(args):
	raw_image = nib.load(args.raw_image)
	seg_image = nib.load(args.segmentation)
	
	scar_area = get_scar_area(seg_image)
	scar_entropy = get_scar_entropy(raw_image, seg_image)
	scar_components = get_scar_components(seg_image)
	scar_transmurality = get_scar_transmurality(seg_image)
	scar_radiality = 0.1#get_scar_radiality(seg_image)
	scar_interface_length = 0.3 #get_scar_interface_length(seg_image)
	
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
	parser.add_argument("-raw_image", default = "example_data/rawimage.nii")	
	parser.add_argument("-segmentation", default = "example_data/segmentation.nii")	
	parser.add_argument("-output", default = "image_metrics.csv")	
	args = parser.parse_args()
	main(args)
