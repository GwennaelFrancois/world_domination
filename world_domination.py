# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WorldDomination
                                 A QGIS plugin
 Strategy game
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-05-16
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Gwennaël François
        email                : gwennaelfrancois@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
# Initialize Qt resources from file resources.py
from .resources import *
from .game import Game

# Import the code for the DockWidget
from .world_domination_dockwidget import WorldDominationDockWidget
from .toolbox import rollDice
import os.path

MAX_PLAYERS = 5

class WorldDomination:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'WorldDomination_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&World Domination')
        self.toolbar = self.iface.addToolBar(u'WorldDomination')
        self.toolbar.setObjectName(u'WorldDomination')

        self.pluginIsActive = False
        self.dockwidget = None


    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        return QCoreApplication.translate('WorldDomination', message)


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
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/world_domination/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'World Domination'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&World Domination'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            if self.dockwidget == None:
                self.dockwidget = WorldDominationDockWidget()

            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            self.runGame()
        
    
    # GAME --------------------------------------------------------------------------
    def debugLabel(self, message: str):
        """Function to set text the debug label (to remove)

        :param message: Text message
        :type message: str
        """
        self.dockwidget.debugLabel.setText(message)

    def runGame(self):
        self.game = self.loadOrCreateGame()
        if self.game is None: return
        self.debugLabel(str(self.game))
        self.restoreGameUi(self.game)
        self.game.drawTurns()
        self.debugLabel(str(self.game.turns))

    def loadOrCreateGame(self) -> Game:
        """Ask user if he wants to play a new game or load a previously saved one
        return Game object (if None : cancel)
        """
        createNewGame = True
        game = None
        if createNewGame:
            nbPlayers = self.askNbPlayers()
            game = Game(nbPlayers)
        else:
            # @todo load new game
            pass
        return game

    def askNbPlayers(self):
        """Ask the user how many players are playing (between 3 and 5 included) (default is 3 players)
        """
        # @todo
        return 3

    def restoreGameUi(self, game: Game):
        """Restore UI from given game object

        :param game: Game object
        :type game: Game
        """
        for player in self.game.players.keys():
            self.dockwidget.setPlayerData(self.game.players[player], player)
        
        for playerToHide in range(MAX_PLAYERS - self.game.nbPlayers):
            self.dockwidget.hidePlayer(MAX_PLAYERS-playerToHide)
