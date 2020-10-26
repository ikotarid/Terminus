# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Terminus
                                 A QGIS plugin
 This plugin performs Image Segemntation
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Ioannis Kotaridis'
__date__ = '2020-10-13'
__copyright__ = '(C) 2020 by Ioannis Kotaridis'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Terminus class from file Terminus.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .terminus_processing import TerminusPlugin
    return TerminusPlugin(iface)
