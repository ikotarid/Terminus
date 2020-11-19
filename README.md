# Terminus
Terminus was developed on Open Source QGIS software. It is a fast and easy to use plugin that allows users to implement image segmentation on Remote Sensing data.
Image segmentation is the initial and integral procedure to produce the fundamental elements of OBIA. It is about the partitioning of an image into spatially adjoining and homogenous regions (segments) that form the foundation for further analysis. Terminus includes four popular image segmentation algorithms: felzenszwalb, quickshift, slic and watershed. Each algorithm produces two outputs, a vector file and a raster file. The plugin offers user the option to compute various statistics over each segment. If this is the case, these zonal statistics are included in the fields of the output vector file and a multiband raster file is created. This raster file contains the statistics of the pixels within each segment as the output bands, thus it can be displayed as a false color composite of choice.

![alt text](https://github.com/ikotarid/Terminus/blob/main/aux/doc.png)

## Install requirements
You will need to install (if not already installed):

***Scikit-image*** open-source image processing library for Python programming language.

To install this Python library, open OSGEO4W Shell.
Then, copy-paste and execute the following two lines as shown in the image.

- [x] py3_env

- [x] pip install scikit-image

![alt text](https://github.com/ikotarid/Terminus/blob/main/aux/osgeo4w.jpg)

Since image segmentation is a computationally expensive procedure, it is best to first work with a small subset of the study area to test the parameters' values you will use.
Once the optimal parameters' values are determined, segmentation can be run on the full scene. After a successful image segmentation, either the vector file or the raster file can be used in an object-based classification approach.
