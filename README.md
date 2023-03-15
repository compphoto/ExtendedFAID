# Dataset Preparation
Our dataset contains flash/no-flash pairs from [Flash and Ambient Illuminations Dataset
](http://yaksoy.github.io/faid/), [Dataset of Multi-Illumination Images in the Wild
](https://projects.csail.mit.edu/illumination/) and [DeepFlash](http://graphics.unibas.it/www/flash_no_flash/index.md.html).
## Flash and Ambient Illuminations Dataset
Download all the illuminations from the main dataset in the link and extract them into a single folder called 'Illuminations'. 

Download and extract the exif files.

Use the [IluminationsToXYZ](./IluminationsToXYZ.m/) script to map the illuminations to XYZ color space with the color matrix available in exif data of the PNG files. 

Use the [FAID](./FAID.py/) script to convert the illuminations to linear RGB and white balance them. 

## Multi-Illumination Dataset

Download the multi illumination dataset through the link. 
 

Use the [MID](./MID.py/) script to convert the illuminations to linear RGB, white balance them and put the different ambient illuminations for each scene in different sub-folders.

## DeepFlash Portrait Dataset

Please contact the authors to get access to the preprocessed dataset. The preprocessing has an affine aligement between flash and no-flash photos. 

We utilize flash photographs in 'inputs_origin' and no-flash photographs in 'target' folders.

Each portrait is rotated from 10 different angles, we only select one of the angles for each photoghraph.

We segment and generate the alpha mattings for the flash and no-flash pairs. Download the alpha mats [here](https://vault.sfu.ca/index.php/s/wdRHtP6qqXQ5gOn). 

We select photographs from the FAID that are suitable to use as background images. Download them [here](https://vault.sfu.ca/index.php/s/U8Hm9Q83A45ZQ0g).

Utilize the [DPD](./DPD.py/) script to blend the portraits with background images, white balance them and save the linear RGB images in sub-folders based on the number of different backgrounds chosen for each portrait.  


