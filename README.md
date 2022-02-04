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

* python 3.6.8
* scipy 1.3.1
* numpy 1.17.2
* nibabel 2.5.1
* cv2 4.1.1
* pandas 0.25.1

# Citation
If you found this script useful and would like to cite it please cite one or both of these papers

[Balaban G, Halliday BP, Bai W, Porter B, Malvuccio C, Lamata P, Rinaldi CA, Plank G, Rueckert D, Prasad SK, Bishop MJ. Scar shape analysis and simulated electrical instabilities in a non-ischemic dilated cardiomyopathy patient cohort. PLOS computational biology. 2019 Oct;15(10):e1007421-.](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007421)


[Balaban G, Halliday BP, Porter B, Bai W, Nygåard S, Owen R, Hatipoglu S, Ferreira ND, Izgi C, Tayal U, Corden B. Late-gadolinium enhancement interface area and electrophysiological simulations predict arrhythmic events in patients with nonischemic dilated cardiomyopathy. Clinical Electrophysiology. 2021 Feb 1;7(2):238-49.](https://www.jacc.org/doi/abs/10.1016/j.jacep.2020.08.036)

# Lisence 
[CC-BY 4.0](https://creativecommons.org/licenses/) or later version.