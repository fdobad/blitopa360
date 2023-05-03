# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Insta
                                 A QGIS plugin
 Import and preview Insta 360 files to a QGIS layer
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-04-09
        copyright            : (C) 2023 by fdo bad
        email                : fbadilla@ing.uchile.cl
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Insta class from file Insta.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .insta import Insta
    return Insta(iface)
