# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Terminus
                                 A QGIS plugin
 This plugin performs Image Segmentation
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-10-13
        copyright            : (C) 2020 by Ioannis Kotaridis
        email                : ikotarid@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Ioannis Kotaridis'
__date__ = '2020-10-13'
__copyright__ = '(C) 2020 by Ioannis Kotaridis'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import inspect
import gdal
import processing
from qgis.PyQt.QtGui import QIcon
from skimage import io
from skimage.segmentation import felzenszwalb
from collections import OrderedDict
from qgis.analysis import QgsZonalStatistics
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (Qgis,
                       QgsVectorLayer,
                       QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterString,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterEnum
                                              )


class Imagesegmentationfelzenszwalb(QgsProcessingAlgorithm):
    """All Processing algorithms should extend the QgsProcessingAlgorithm
    class."""

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    IN_RASTER = 'IN_RASTER'
    SCALE = 'SCALE'
    SIGMA ='SIGMA'
    MIN_SIZE='MIN_SIZE'
    OUT_VECTOR = 'OUT_VECTOR'
    RASTER = 'RASTER'
    CHECKBOX = 'CHECKBOX'
    COLUMN_PREFIX = 'COLUMN_PREFIX'
    STATISTICS = 'STATISTICS'
    #-------------------------------------------------------------------------

    def initAlgorithm(self, config):
        #Here we define the inputs and output of the algorithm

        #Inputs
        self.addParameter(QgsProcessingParameterRasterLayer(
                            self.IN_RASTER,
                            self.tr('Input raster')))

        self.addParameter(QgsProcessingParameterNumber(
                        self.SCALE,
                        self.tr("scale"),
                        QgsProcessingParameterNumber.Double,
                        100, False, 1e-10)) #1= default, True=optional, 0=min, 1=max
        self.addParameter(QgsProcessingParameterNumber(
                        self.SIGMA,
                        self.tr("sigma"),
                        QgsProcessingParameterNumber.Double,
                        0.5, False, 0))
        self.addParameter(QgsProcessingParameterNumber(
                                self.MIN_SIZE,
                                self.tr("min_size"),
                                QgsProcessingParameterNumber.Integer,
                                20, False, 1e-10))
        #Zonal Statistics inputs
        self.addParameter(QgsProcessingParameterBoolean(self.CHECKBOX,
            self.tr("Calculate Zonal Statistics of segments"),
            defaultValue=False))

        self.STATS = OrderedDict([(self.tr('Count'), QgsZonalStatistics.Count),
                                  (self.tr('Sum'), QgsZonalStatistics.Sum),
                                  (self.tr('Mean'), QgsZonalStatistics.Mean),
                                  (self.tr('Median'), QgsZonalStatistics.Median),
                                  (self.tr('Std. dev.'), QgsZonalStatistics.StDev),
                                  (self.tr('Min'), QgsZonalStatistics.Min),
                                  (self.tr('Max'), QgsZonalStatistics.Max),
                                  (self.tr('Range'), QgsZonalStatistics.Range),
                                  (self.tr('Minority'), QgsZonalStatistics.Minority),
                                  (self.tr('Majority (mode)'), QgsZonalStatistics.Majority),
                                  (self.tr('Variety'), QgsZonalStatistics.Variety),
                                  (self.tr('Variance'), QgsZonalStatistics.Variance),
                                  (self.tr('All'), QgsZonalStatistics.All)])
        keys = list(self.STATS.keys())
        self.addParameter(QgsProcessingParameterEnum(self.STATISTICS,
                                                     self.tr('Specify statistics'),
                                                     keys,
                                                     allowMultiple=True, defaultValue=[2,4,11]))
        self.addParameter(QgsProcessingParameterString(self.COLUMN_PREFIX,
                                                       self.tr('Output column prefix'), '_'))

        # Outputs
        self.addParameter(QgsProcessingParameterRasterDestination(
                self.RASTER,
                self.tr('Output raster')))

        self.addParameter(QgsProcessingParameterVectorDestination(
                self.OUT_VECTOR,
                self.tr('Output layer')))
    #-------------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback): #THIS IS A METHOD
        """Here is where the processing itself takes place."""

        in_raster = self.parameterAsRasterLayer(parameters, self.IN_RASTER, context)
        scale = self.parameterAsDouble(parameters, self.SCALE, context)
        sigma = self.parameterAsDouble(parameters, self.SIGMA, context)
        min_size = self.parameterAsInt(parameters, self.MIN_SIZE, context)
        checkboxcalculation = self.parameterAsBool(parameters, self.CHECKBOX, context)
        self.columnPrefix = self.parameterAsString(parameters, self.COLUMN_PREFIX, context)
        stats = self.parameterAsEnums(parameters, self.STATISTICS, context)
        out_vector = self.parameterAsOutputLayer(parameters, self.OUT_VECTOR,context)
        out_raster = self.parameterAsOutputLayer(parameters, self.RASTER, context)

        input_raster_src = in_raster.source()
        img = io.imread(input_raster_src)

        feedback.setProgress(20)
        log = feedback.setProgressText
        log("Segmenting imagery...")

        # Segmentation
        segments=felzenszwalb(img, scale=scale, sigma=sigma, min_size=min_size)

        feedback.setProgress(50)

        # Create a new raster data source
        ds = gdal.Open(input_raster_src, gdal.GA_ReadOnly)
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        driverTiff = gdal.GetDriverByName('GTiff')
        outDs = driverTiff.Create(out_raster, cols, rows, 1, gdal.GDT_Float32)

        # Write metadata
        outDs.SetGeoTransform(ds.GetGeoTransform())
        outDs.SetProjection(ds.GetProjectionRef())

        # Write raster data sets
        outBand = outDs.GetRasterBand(1)
        outBand.WriteArray(segments)

        # Close raster file
        outDs = None

        feedback.setProgress(80)
        log("Converting raster to vector...")

        # Raster to Vector
        processing.run('gdal:polygonize', {'INPUT':out_raster,'BAND':1,'FIELD':'DN',
        'EIGHT_CONNECTEDNESS':False,'EXTRA':'','OUTPUT': out_vector})

        # Convert to QgsVectorLayer
        vector_QGIS = QgsVectorLayer(out_vector)

        feedback.setProgress(100)

        # Compute Vector Statistics
        if checkboxcalculation:
            log = feedback.setProgressText
            log(self.tr("Calculating Zonal Statistics ..."))

            keys = list(self.STATS.keys())
            self.selectedStats = 0
            for i in stats:
                self.selectedStats |= self.STATS[keys[i]]
            self.raster_band_count = in_raster.bandCount()

            for band in range(self.raster_band_count):
                if feedback.isCanceled():
                    break
                columnPrefix = '{}band{}_'.format(self.columnPrefix, band+1)
                zonal_stats = QgsZonalStatistics(vector_QGIS,
                                    in_raster,
                                    columnPrefix,
                                    band + 1,
                                    QgsZonalStatistics.Statistics(self.selectedStats))
                zonal_stats.calculateStatistics(feedback)

        return {self.OUT_VECTOR: out_vector,self.RASTER: out_raster}
    #-------------------------------------------------------------------------

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'segmentationfelzenszwalb'
    #-------------------------------------------------------------------------
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Felzenszwalb algorithm')
    #-------------------------------------------------------------------------
    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Image Segmentation') #self.groupId() default value
    #-------------------------------------------------------------------------
    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'imagesegmentation'
    #-------------------------------------------------------------------------
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    #-------------------------------------------------------------------------
    #add custom icon
    def icon(self):
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'icons\F.png')))
        return icon
    #-------------------------------------------------------------------------
    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Computes Felsenszwalb’s efficient graph based image segmentation. The parameter scale sets an observation level. Higher scale means less and larger segments. sigma is the diameter of a Gaussian kernel, used for smoothing the image prior to segmentation. The number of produced segments as well as their size can only be controlled indirectly through scale."+"\n"
                        +"scale (float): Free parameter. Higher means larger clusters."+"\n"
                        +"sigma (float): Width (standard deviation) of Gaussian kernel used in preprocessing."+"\n"
                        +"min_size (int): Minimum component size. Enforced using postprocessing.")
    #-------------------------------------------------------------------------
    def createInstance(self):
        return Imagesegmentationfelzenszwalb()
