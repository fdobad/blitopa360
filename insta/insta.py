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
from logging import warning
from pathlib import Path
from shlex import split as shlex_split
from sys import platform

import numpy as np
from pandas import read_csv
from qgis import processing
from qgis.core import (Qgis, QgsCoordinateReferenceSystem, QgsMessageLog,
                       QgsProject, QgsVectorLayer)
from qgis.PyQt.QtCore import QCoreApplication, QProcess, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .insta_dialog import InstaDialog
from .resources import *

MSGCAT = 'blitoPa'

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
        self.dlg = None
        self.qproc = None

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
        if self.first_start:
            self.first_start = False
            self.dlg = InstaDialog()
            QgsProject.instance().homePathChanged.connect( self.slot_homePathChanged)
            self.dlg.checkBox_stdout.stateChanged.connect( self.slot_checkBox_stdout_StateChanged)
            self.dlg.checkBox_stderr.stateChanged.connect( self.slot_checkBox_stderr_StateChanged)
            self.dlg.pushButton_terminate.pressed.connect( self.pushButton_terminate_pressed)
            QgsMessageLog.logMessage( 'Dialog created', MSGCAT, Qgis.Info)
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            apath = Path(self.dlg.mQgsFileWidget.filePath())
            QgsMessageLog.logMessage(f'Reading media from {apath}', MSGCAT, Qgis.Info)
            #TODO check if exif csv exists, compare length to files
            if not self.qproc:
                self.qproc = QProcessQsgMsgLog( apath=apath, plugin_dir=Path(self.plugin_dir))
                self.slot_checkBox_stdout_StateChanged(self.dlg.checkBox_stdout.isChecked())
                self.slot_checkBox_stderr_StateChanged(self.dlg.checkBox_stderr.isChecked())
                self.qproc.start(*qproc_cmd(apath))
            elif self.qproc.fin:
                self.qproc.start(*qproc_cmd(apath))
            else:
                QgsMessageLog.logMessage('Process already running!', MSGCAT, Qgis.Info)
        else: 
            QgsMessageLog.logMessage( 'Dialog closed, no action', MSGCAT, Qgis.Info)

    def slot_homePathChanged(self, *args, **kwargs):
        self.dlg.mQgsFileWidget.setFilePath(QgsProject.instance().absolutePath())
        QgsMessageLog.logMessage('Project homePath changed, changing folder chooser too...', MSGCAT, Qgis.Info)

    def slot_checkBox_stderr_StateChanged(self, state, *args, **kwargs):
        if self.qproc:
            if state==0:
                self.qproc.toggle_stderr(False)
            elif state==2:
                self.qproc.toggle_stderr(True)

    def pushButton_terminate_pressed(self):
        if self.qproc:
            self.qproc.terminate()

    def slot_checkBox_stdout_StateChanged(self, state, *args, **kwargs):
        if self.qproc:
            if self.qproc.display_stdout != state:
                self.qproc.display_stdout = state

def qproc_cmd(apath):
    # filepath -> ImageDescription
    pre ='./exiftool'
    post=' -s -ee3 -p $filepath,${CreateDate;DateFmt("%s")},${gpslatitude#},${gpslongitude#},${gpsaltitude#} -ext insp '
    if platform=='linux':
        plt=''
    elif  platform=='Windows':
        plt='(-1).exe'
    cmd = pre+plt+post+str(apath)
    QgsMessageLog.logMessage(f'cmd {cmd}', MSGCAT, Qgis.Info)
    return cmd, apath

def proc_exiftool_output(apath):
    """ load exiftool_output.csv
        flag and interpolate missing geoloc data
        write import_me.csv
    """
    try:
        #apath=Path.cwd()
        df = read_csv( apath/'exiftool_output.csv', names=['filename','datetime','lat','lon','ele'], sep=',')
        QgsMessageLog.logMessage( f'{len(df)} records found', MSGCAT, Qgis.Info)
        df['tag']=((df['lat']!=0)|(df['lon']!=0)).astype(np.int64)
        for col in ['lat','lon','ele']:
            df[col] = df[col].apply( lambda x: np.nan if x==0 else x)
        QgsMessageLog.logMessage( f"{df['tag'].sum()} correctly geo tagged", MSGCAT, Qgis.Info)
        df.sort_values('datetime', inplace=True)
        df.index = df.datetime
        #df[['lat','lon','ele']] = df[['lat','lon','ele']].interpolate(method='polynomial', order=5, limit_direction='both')
        df[['lat','lon','ele']] = df[['lat','lon','ele']].interpolate()
        df.to_csv( apath/'import_me.csv',sep=',')
    except Exception as e:
        QgsMessageLog.logMessage( f"Problem procesing exiftool output: {e}", MSGCAT, Qgis.Critical)

def layer_from_file(apath, plugin_dir):
    """ processing toolbox create points from csv
        load style
        add to layer
    """
    #try:
    name = apath.stem
    output = processing.run('qgis:createpointslayerfromtable',{ 'INPUT' : str(apath/'import_me.csv'), 'MFIELD' : None, 'OUTPUT' : str(apath/(name+'.gpkg')), 'TARGET_CRS' : QgsCoordinateReferenceSystem('EPSG:4326'), 'XFIELD' : 'lon', 'YFIELD' : 'lat', 'ZFIELD' : 'ele', 'MFIELD' : 'datetime' })['OUTPUT']
    
    QgsMessageLog.logMessage( f"Createpointslayerfromtable created {output}", MSGCAT, Qgis.Info)
    vectorLayer = QgsVectorLayer( str(apath/(name+'.gpkg'))+'|layername='+name, name)
    vectorLayer.loadNamedStyle( str(plugin_dir/'points_layerStyle.qml'))
    QgsProject.instance().addMapLayer(vectorLayer)
    #except Exception as e:
    #    QgsMessageLog.logMessage( f"Problem procesing exiftool output: {e}", MSGCAT, Qgis.Critical)

# TODO
# InstaDoIt to qgsTask
# shlex smarter
# exiftool disable warnings
# preguntarle al ivan cuanto cuesta leerlo rapido

#atEnd()
ExitStatus = {0:'CrashExit',
              1:'NormalExit'}
#state()
ProcessState = {0:'NotRunning',
                1:'Running',
                2:'Starting'}
#error()
ProcessError = {0:'Crashed',
                1:'FailedToStart',
                2:'ReadError',
                3:'Timedout',
                4:'UnknownError',
                5:'WriteError'}

class QProcessQsgMsgLog(QProcess):
    def __init__(self, parent=None, apath=None, plugin_dir=None):
        super().__init__(parent)
        self.finished.connect(self.on_finished)
        self.setInputChannelMode(QProcess.ForwardedInputChannel)
        self.setProcessChannelMode( QProcess.SeparateChannels)
        self.readyReadStandardOutput.connect(self.on_ready_read_standard_output)
        self.readyReadStandardError.connect(self.on_ready_read_standard_error)
        #self.proc.stateChanged.connect(self.externalProcess_handle_state)
        #self.proc.finished.connect(self.externalProcess_finished)  # Clean up once complete.
        self.setWorkingDirectory( str(plugin_dir/'exiftool'))
        self.apath = apath
        self.plugin_dir = plugin_dir
        self.display_stdout = True
        self.fin = False

    def toggle_stderr(self, enable):
        if enable:
            self.readyReadStandardError.connect(self.on_ready_read_standard_error)
        else:
            self.readyReadStandardError.disconnect()

    def start(self, command, apath):
        super().start(command)
        self.apath = apath
        self.stdout_file = open( self.apath/'exiftool_output.csv', "wb")
        QgsMessageLog.logMessage(f"QProcess started, state: {ProcessState[self.state()]}", MSGCAT, Qgis.Info)

    def terminate(self):
        process_code = self.state()
        if process_code != QProcess.ProcessState.NotRunning:
            QgsMessageLog.logMessage(f"QProcess terminating, state: {ProcessState[process_code]}", MSGCAT, Qgis.Warning)
            self.terminate()
        else:
            QgsMessageLog.logMessage(f"QProcess can't terminate, state: {ProcessState[process_code]}", MSGCAT, Qgis.Warning)

    def on_finished(self):
        self.stdout_file.close()
        exit_code = self.exitCode()
        if exit_code==QProcess.ExitStatus.NormalExit:
            QgsMessageLog.logMessage("QProcess finished with NormalExit status", MSGCAT, Qgis.Info)
            QgsMessageLog.logMessage('Extracted metadata to exiftool_output.csv', MSGCAT , Qgis.Info)
            #TODO check if import csv exists, compare nans length to files
            proc_exiftool_output(self.apath)
            QgsMessageLog.logMessage('Processed metadata to import_me.csv', MSGCAT, Qgis.Info)
            layer_from_file( self.apath, self.plugin_dir)
            QgsMessageLog.logMessage('Loaded layer', MSGCAT, Qgis.Info)
            QgsMessageLog.logMessage('All Done', MSGCAT, Qgis.Success)
        elif exit_code==QProcess.ExitStatus.CrashExit:
            QgsMessageLog.logMessage(f"QProcess ProcessError {ProcessError[self.error()]}", MSGCAT, Qgis.Critical)
        else:
            QgsMessageLog.logMessage("QProcess finished with unknown ExitStatus!!", MSGCAT, Qgis.Critical)
        self.fin = True

    def on_ready_read_standard_output(self):
        output = self.readAllStandardOutput()
        self.stdout_file.write(output)
        if self.display_stdout:
            output = bytes(output).decode("utf8")
            QgsMessageLog.logMessage(output, MSGCAT, Qgis.Info)

    def on_ready_read_standard_error(self):
        output = self.readAllStandardError()
        output = bytes(output).decode("utf8")
        QgsMessageLog.logMessage(output, MSGCAT, Qgis.Info)
