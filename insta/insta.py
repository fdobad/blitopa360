# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Insta
                                 A QGIS plugin
 Import and preview Insta 360 files to a QGIS layer
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-04-09
        git sha              : $Format:%H$
        copyright            : (C) 2023 by fdo bad
        email                : fbadilla@ing.uchile.cl
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
import os.path
from pathlib import Path
from subprocess import Popen, PIPE
from shlex import split as shlex_split
from pandas import Timestamp, DataFrame

from qgis.core import Qgis, QgsFeature, QgsMessageLog, QgsVectorLayer, QgsGeometry, QgsPointXY, QgsProject
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Import the code for the dialog
from .insta_dialog import InstaDialog
# Initialize Qt resources from file resources.py
from .resources import *


class Insta:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Insta_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Insta 360 importer')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Insta', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/insta/icon16.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Insta360 importer'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Insta 360 importer'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = InstaDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            apath = self.dlg.mQgsFileWidget.filePath()
            QgsMessageLog.logMessage( apath, MSGCAT , Qgis.Info)
            doit = InstaDoIt(apath, self.plugin_dir)
            if not doit.check():
                QgsMessageLog.logMessage( 'No .insp file found', MSGCAT , Qgis.Critical)
                return
            #self.iface.addVectorLayer( doit.doit())
            QgsProject.instance().addMapLayer(doit.doit())




# TODO
# InstaDoIt to qgsTask
# shlex smarter
# exiftool disable warnings
# preguntarle al ivan cuanto cuesta leerlo rapido

MSGCAT = 'tioblitoPa'

import numpy as np
class InstaDoIt:
    def __init__(self, img_dir, plugin_dir):
        self.exif_dir = Path( plugin_dir) / 'exiftool'
        self.img_dir = Path(img_dir)
        self.img_cmd = "./exiftool -ee3 -p '${DateTimeOriginal} ${gpslatitude#} ${gpslongitude#} ${gpsaltitude#}' "
        self.image_file_list = sorted( self.img_dir.glob('*.insp'))
        self.vl = QgsVectorLayer("Point?crs=epsg:4326&field=filename:string&field=elevation:float&field=date:datetime",MSGCAT, "memory")
        QgsMessageLog.logMessage( f'{len(self.image_file_list)} .insp files found', MSGCAT , Qgis.Info)

    def check(self):
        if self.image_file_list:
            return True
        return False

    def doit(self):
        #df = DataFrame( columns=('datetime','filename','lat','lon','ele'))
        feats = []
        for i,afile in enumerate(self.image_file_list):
            #QgsMessageLog.logMessage( f'{i}', MSGCAT , Qgis.Info)
            cmd = self.img_cmd + f"'{afile}'"
            #print('cmd',cmd)
            #QgsMessageLog.logMessage( f'{i} {cmd}', MSGCAT , Qgis.Info)
            process = Popen( shlex_split(cmd), stdout=PIPE, stderr=PIPE, cwd=self.exif_dir)
            stdout, stderr = process.communicate()
            #print('stdout',stdout)#.decode().replace('\n',''))
            #print('stdout',stdout.decode().split())#.decode().replace('\n',''))
            #QgsMessageLog.logMessage( f'{i} {cmd} {stdout} {stderr}', MSGCAT , Qgis.Info)
            date,time,lat,lon,ele = stdout.decode().split()
            if lat=='0' and lon=='0':
                continue
            dt = Timestamp(date.replace(':','-')+' '+time).isoformat(timespec='seconds')
            #df.loc[i] = [dt, afile.stem, np.float32(lat), np.float32(lon), np.float32(ele)]

            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(np.float32(lon), np.float32(lat))))
            #f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(np.float32(lat), np.float32(lon))))
            f.setId(i)
            f.setAttributes([afile.stem, np.float32(ele), dt]) #QDateTime(QDate(2020, 5, 4), QTime(12, 13, 14)), QDate(2020, 5, 2), QTime(12, 13, 1)])
            feats += [f]
            #if i>50:
            #    break

        #QgsMessageLog.logMessage( f'{df}', MSGCAT , Qgis.Info)
        self.vl.dataProvider().addFeatures(feats)
        return self.vl
