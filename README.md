# What this script does
This repository provides a script that creates a list of metrics quantifying a scar pattern
seen in a cardiac short axis late gadolinium enhanced MRI image. The metrics provided are

* area - The total area of the scar.
* entropy - The Shannon entropy of the scar pixels.
* components - The number of 4 connected components of the scar.
* transmurality - The mean transmurality of all scar components, calculated by a ray tracing method.
                  This value is between 0-1, with 1 being a completely transmural pattern.
* radiality - The angular extent of the LGE pattern, with values between 0 and 1. A score of 1 indicates
              that scars are present in a full 360 degree pattern with respect to the centre of the blood pool,
              wheras 0 indicates no angular extent of scar.
* interface length - The total length of the border between the scar and healthy myocardium.

The physical units of the area, and interface length scores are determined by the pixel sizes specified in the image.

# How to use it
You will need pairs of short axis medical images in nifti format.


![Example images](/example_data/example_images.png)

One image in each pair should contain
the raw pixel values, while the other should contain a segmentation of the myocardium and the 
scar with seperate markers. The myocardium should be a complete ring with a blood pool in the middle. All background areas (not myocardium or scar) should be marked 0.

The script can then be run with the command

`python calculate metrics.py -raw image im1.nii -segmentation im2.nii -output metrics.csv -mark_myocardium mark1 -mark_scar mark2`

where *im1* and *im2* are the raw pixel and segmentation data in nifti format, *metrics.csv* is the output file, and *mark1* and *mark2* are the markers of the myocardium and the scar in the segmentation image. 

Running the script without any parameters will analyze the data in the "example_data" folder.

# Known compatible dependencies

* python 2.7.12
* scipy 1.1.0
* numpy 1.15.2
* nibabel 2.1.0
* cv2 2.4.9.1
* pandas 0.24.1

# Lisence 
CC-BY 4.0 or later version (https://creativecommons.org/licenses/)