from os import unlink
from os.path import isfile, normpath
from enigma import checkInternetAccess, eConsoleAppContainer, eDVBDB, eTimer, gRGB
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap, HelpableNumberActionMap
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigText
from skin import parseColor
from Components.GUIComponent import GUIComponent
from Components.Sources.List import List
from Components.Harddisk import harddiskmanager
from Components import Opkg
from Components.Label import Label
from Components.Language import language
from Components.PluginComponent import plugins
from Components.PluginList import PluginList, PluginCategoryComponent, PluginDownloadComponent
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.ParentalControlSetup import ProtectedScreen
from Screens.Screen import Screen, ScreenSummary
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_GUISKIN, isPluginInstalled
from Tools.LoadPixmap import LoadPixmap
from Tools.NumericalTextInput import NumericalTextInput

config.misc.pluginbrowser = ConfigSubsection()
config.misc.pluginbrowser.bootlogos = ConfigYesNo(default=True)
config.misc.pluginbrowser.display = ConfigYesNo(default=True)
config.misc.pluginbrowser.drivers = ConfigYesNo(default=True)
config.misc.pluginbrowser.extensions = ConfigYesNo(default=True)
config.misc.pluginbrowser.kernel = ConfigYesNo(default=False)
config.misc.pluginbrowser.m2k = ConfigYesNo(default=True)
config.misc.pluginbrowser.picons = ConfigYesNo(default=True)
config.misc.pluginbrowser.languages_po = ConfigYesNo(default=False)
config.misc.pluginbrowser.security = ConfigYesNo(default=True)
config.misc.pluginbrowser.settings = ConfigYesNo(default=True)
config.misc.pluginbrowser.skin = ConfigYesNo(default=True)
config.misc.pluginbrowser.softcams = ConfigYesNo(default=True)
config.misc.pluginbrowser.systemplugins = ConfigYesNo(default=True)
config.misc.pluginbrowser.weblinks = ConfigYesNo(default=True)
config.misc.pluginbrowser.plugin_order = ConfigText(default="")

INTERNET_TIMEOUT = 2


def languageChanged():
	plugins.clearPluginList()
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))


class PluginBrowser(Screen, NumericalTextInput, ProtectedScreen):
	skin = """
	<screen name="PluginBrowser" title="Plugin Browser" position="center,center" size="1000,535" resolution="1280,720">
		<widget source="pluginList" render="Listbox" position="0,0" size="e,450" conditional="pluginList" listOrientation="vertical" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{
				"template":
					[
					MultiContentEntryPixmapAlphaBlend(pos=(10, 5), size=(100, 40), png=3, flags=BT_SCALE),
					MultiContentEntryText(pos=(125, 3), size=(865, 24), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_TOP, text=1),
					MultiContentEntryText(pos=(145, 30), size=(845, 19), font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_BOTTOM, text=2)
					],
				"fonts": [parseFont("Regular;20"), parseFont("Regular;15")],
				"itemHeight": 50
				}
			</convert>
		</widget>
		<widget source="pluginGrid" render="Listbox" position="0,0" size="e,448" conditional="pluginGrid" listOrientation="grid" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{
				"template":
					[
					MultiContentEntryText(pos=(0, 0), size=(195, 110), font=0),
					MultiContentEntryText(pos=(4, 4), size=(187, 102), font=0, backcolor=0x00404040),
					MultiContentEntryPixmapAlphaBlend(pos=(45, 14), size=(100, 40), png=3, flags=BT_SCALE),
					MultiContentEntryText(pos=(5, 58), size=(185, 45), font=0, flags=RT_VALIGN_CENTER | RT_HALIGN_CENTER | RT_WRAP, text=1)
					],
				"fonts": [parseFont("Regular;18")],
				"itemWidth": 195,
				"itemHeight": 112
				}
			</convert>
		</widget>
		<widget name="quickselect" position="0,0" size="e,450" font="Regular;100" foregroundColor="#00fff000" horizontalAlignment="center" transparent="1" verticalAlignment="center" zPosition="+1" />
		<widget name="description" position="0,e-75" size="e,25" font="Regular;20" verticalAlignment="center" />
		<widget source="key_red" render="Label" position="0,e-40" size="180,40" backgroundColor="key_red" font="Regular;20" foregroundColor="key_text" horizontalAlignment="center" verticalAlignment="center">
			<convert type="ConditionalShowHide" />
		</widget>
		<widget source="key_green" render="Label" position="190,e-40" size="180,40" backgroundColor="key_green" font="Regular;20" foregroundColor="key_text" horizontalAlignment="center" verticalAlignment="center">
			<convert type="ConditionalShowHide" />
		</widget>
		<widget source="key_blue" render="Label" position="570,e-40" size="180,40" backgroundColor="key_blue" conditional="key_blue" font="Regular;20" foregroundColor="key_text" horizontalAlignment="center" verticalAlignment="center">
			<convert type="ConditionalShowHide" />
		</widget>
		<widget source="key_menu" render="Label" position="e-190,e-40" size="90,40" backgroundColor="key_back" conditional="key_menu" font="Regular;20" foregroundColor="key_text" horizontalAlignment="center" verticalAlignment="center">
			<convert type="ConditionalShowHide" />
		</widget>
		<widget source="key_help" render="Label" position="e-90,e-40" size="90,40" backgroundColor="key_back" conditional="key_help" font="Regular;20" foregroundColor="key_text" horizontalAlignment="center" verticalAlignment="center">
			<convert type="ConditionalShowHide" />
		</widget>
	</screen>"""
	moveBackgroundColor = gRGB(0x00DC143C)
	moveFontColor = None

	def __init__(self, session):
		self.layout = "pluginGrid" if config.usage.pluginListLayout.value == "gridmode" else "pluginList"
		Screen.__init__(self, session, enableHelp=True, mandatoryWidgets=[self.layout])
		NumericalTextInput.__init__(self, handleTimeout=False, mode="SearchUpper")
		self.skinName = ["PluginBrowserGrid" if config.usage.pluginListLayout.value == "gridmode" else "PluginBrowserList", "PluginBrowser"]
		self.setTitle(_("Plugin Browser"))
		ProtectedScreen.__init__(self)
		self.firsttime = True
		self["key_menu"] = StaticText(_("MENU"))
		self["key_red"] = StaticText(_("Remove plugins"))
		self["key_green"] = StaticText(_("Download plugins"))
		self["key_blue"] = StaticText("")
		self[self.layout] = List([])
		self[self.layout].onSelectionChanged.append(self.selectionChanged)
		self.currentList = self[self.layout]
		self["quickselect"] = Label()
		self["quickselect"].hide()
		self["description"] = Label()
		self["actions"] = HelpableActionMap(self, ["OkCancelActions", "MenuActions"], {
			"ok": (self.keySelect, _("Start the highlighted plugin")),
			"cancel": (self.keyCancel, _("Close the Plugin Browser screen")),
			"menu": (self.keyMenu, _("Open the Plugin Browser settings screen"))
		}, prio=0, description=_("Plugin Browser Actions"))
		self["pluginRemoveActions"] = HelpableActionMap(self, ["ColorActions"], {
			"red": (self.keyRed, _("Remove plugins")),
			"green": (self.keyGreen, _("Download plugins")),
			"blue": (self.keyBlue, _("Start edit mode"))
		}, prio=0, description=_("Plugin Browser Select Actions"))
		self["pluginDownloadActions"] = HelpableActionMap(self, ["ColorActions"], {
			"green": (self.keyGreen, _("Download plugins"))
		}, prio=0, description=_("Plugin Browser Select Actions"))
		self["pluginEditActions"] = HelpableActionMap(self, ["ColorActions"], {
			"red": (self.keyRed, _("Reset sort order")),
			"green": (self.keyGreen, _("Toggle move mode")),
			"blue": (self.keyBlue, _("Stop edit mode"))
		}, prio=0, description=_("Plugin Browser Edit Actions"))
		if config.usage.pluginListLayout.value == "listmode":
			self["navigationActions"] = HelpableActionMap(self, ["NavigationActions"], {
				"top": (self.keyTop, _("Move to first line / screen")),
				"left": (self.keyPageUp, _("Move up a screen")),
				"right": (self.keyPageDown, _("Move down a screen")),
				"up": (self.keyUp, _("Move up a line")),
				"down": (self.keyDown, _("Move down a line")),
				"bottom": (self.keyBottom, _("Move to last line / screen"))
			}, prio=0, description=_("Plugin Browser Navigation Actions"))
		else:
			self["navigationActions"] = HelpableActionMap(self, ["NavigationActions"], {
				"top": (self.keyTop, _("Move to the first item on the first screen")),
				"pageUp": (self.keyPageUp, _("Move up a screen")),
				"up": (self.keyUp, _("Move up a line")),
				"first": (self.keyFirst, _("Move to the first item on the current line")),
				"left": (self.keyLeft, _("Move to the previous item in list")),
				"right": (self.keyRight, _("Move to the next item in the list")),
				"last": (self.keyLast, _("Move to the last item on the current line")),
				"down": (self.keyDown, _("Move down a line")),
				"pageDown": (self.keyPageDown, _("Move down a screen")),
				"bottom": (self.keyBottom, _("Move to the last item on the last screen"))
			}, prio=0, description=_("Plugin Browser Navigation Actions"))
		smsMsg = _("SMS style QuickSelect entry selection")
		self["quickSelectActions"] = HelpableNumberActionMap(self, "NumberActions", {  # Action used by QuickSelect.
			"1": (self.keyNumberGlobal, smsMsg),
			"2": (self.keyNumberGlobal, smsMsg),
			"3": (self.keyNumberGlobal, smsMsg),
			"4": (self.keyNumberGlobal, smsMsg),
			"5": (self.keyNumberGlobal, smsMsg),
			"6": (self.keyNumberGlobal, smsMsg),
			"7": (self.keyNumberGlobal, smsMsg),
			"8": (self.keyNumberGlobal, smsMsg),
			"9": (self.keyNumberGlobal, smsMsg),
			"0": (self.keyNumberGlobal, smsMsg)
		}, prio=0, description=_("Quick Select Actions"))
		self.pluginIcon = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "icons/plugin.png"))
		self.quickSelectTimer = eTimer()  # Initialize QuickSelect timer.
		self.quickSelectTimer.callback.append(self.quickSelectTimeout)
		self.quickSelectTimerType = 0
		self.quickSelect = ""
		self.quickSelectPos = -1
		self.onChangedEntry = []
		self.pluginList = []
		self.firstTime = True
		self.sortMode = False
		self.selectedPlugin = None
		self.onLayoutFinish.append(self.layoutFinished)
		self.onFirstExecBegin.append(self.checkWarnings)
		self.onShown.append(self.updatePluginList)

	def isProtected(self):
		return config.ParentalControl.setuppinactive.value and not config.ParentalControl.config_sections.main_menu.value and config.ParentalControl.config_sections.plugin_browser.value

	def createGUIScreen(self, parent, desktop, updateonly=False):
		for item in self.renderer:
			if isinstance(item, GUIComponent) and item.__class__.__name__ == "Listbox":  # Is the listbox name "pluginGrid" available so this test can be more specific?
				for attribute, value in item.skinAttributes[:]:
					if attribute == "moveBackgroundColor":
						PluginBrowser.moveBackgroundColor = parseColor(value)
						item.skinAttributes.remove((attribute, value))
					elif attribute == "moveFontColor":
						PluginBrowser.moveFontColor = parseColor(value)
						item.skinAttributes.remove((attribute, value))
		Screen.createGUIScreen(self, parent, desktop, updateonly)

	def layoutFinished(self):
		self[self.layout].enableAutoNavigation(False)  # Override list box self navigation.

	def updatePluginList(self):
		pluginList = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)[:]
		emptySortOrder = config.usage.plugin_sort_weight.value or False
		self.pluginList = []
		for weight, plugin in enumerate(pluginList, start=1):
			plugin.listWeight = config.usage.plugin_sort_weight.getConfigValue(plugin.name.lower(), "sort") or weight * 10
			if self.sortMode or not config.usage.plugin_sort_weight.getConfigValue(plugin.name.lower(), "hidden"):
				self.pluginList.append((plugin, plugin.name, plugin.description, plugin.icon or self.pluginIcon))
		self.pluginList.sort(key=lambda x: x[0].listWeight)
		if self.sortMode:
			self["key_red"].setText(_("Reset Order"))
			self["key_green"].setText(_("Deactivate movement") if self.selectedPlugin else _("Activate movement"))
			self["key_blue"].setText(_("Edit Mode Off"))
			self["pluginRemoveActions"].setEnabled(False)
			self["pluginDownloadActions"].setEnabled(False)
			self["pluginEditActions"].setEnabled(True)
		else:
			self["key_red"].setText(_("Remove plugins"))
			self["key_blue"].setText(_("Edit Mode On"))
			self["pluginRemoveActions"].setEnabled(True)
			internetAccess = checkInternetAccess("ip-api.com", INTERNET_TIMEOUT)
			if internetAccess == 0:  # 0=Site reachable, 1=DNS error, 2=Other network error, 3=No link, 4=No active adapter.
				self["key_green"].setText(_("Download plugins"))
				self["pluginDownloadActions"].setEnabled(True)
			else:
				self["key_green"].setText("")
				self["pluginDownloadActions"].setEnabled(False)
			self["pluginEditActions"].setEnabled(False)
		self[self.layout].updateList(self.pluginList)

	def keyCancel(self):
		if self.sortMode:
			self.toggleSortMode()
		self.close()

	def toggleSortMode(self):
		if self.sortMode:
			self.sortMode = False
			for index, plugin in enumerate(self.pluginList):
				config.usage.plugin_sort_weight.changeConfigValue(plugin[0].name.lower(), "sort", (index + 1) * 10)
				if self.selectedPlugin and plugin[0] == self.selectedPlugin:
					self.pluginList.pop(index)
					self.pluginList.insert(index, (plugin[0], plugin[0].name, plugin[0].description, plugin[0].icon or self.pluginIcon))
					self.selectedPlugin = None
			config.usage.plugin_sort_weight.save()
			self.currentList.master.master.instance.clearBackgroundColorSelected()
			if self.moveFontColor:
				self.currentList.master.master.instance.clearForegroundColorSelected()
		else:
			self.sortMode = True
		self.updatePluginList()

	def keySelect(self):
		if self.pluginList:
			currentPlugin = self.pluginList[self.currentList.getSelectedIndex()][0]
			if self.sortMode:
				select = (self.selectedPlugin is None or self.selectedPlugin != currentPlugin)
				if not select:
					self.selectedPlugin = None
				for index, plugin in enumerate(self.pluginList):
					if currentPlugin == plugin[0]:
						self.pluginList.pop(index)
						self.pluginList.insert(index, (plugin[0], plugin[0].name, plugin[0].description, plugin[0].icon or self.pluginIcon))
						self.selectedPlugin = currentPlugin if select else None
						break
				if self.selectedPlugin:
					self["key_green"].setText(_("Deactivate movement"))
					self.currentList.master.master.instance.setBackgroundColorSelected(self.moveBackgroundColor)
					if self.moveFontColor:
						self.currentList.master.master.instance.setForegroundColorSelected(self.moveFontColor)
				else:
					self["key_green"].setText(_("Activate movement"))
					self.currentList.master.master.instance.clearBackgroundColorSelected()
					if self.moveFontColor:
						self.currentList.master.master.instance.clearForegroundColorSelected()
				self.currentList.updateList(self.pluginList)
			else:
				currentPlugin.__call__(session=self.session)

	def keyMenu(self):
		from Screens.Setup import Setup
		self.session.open(Setup, "PluginBrowser")

	def keyRed(self):
		if self.sortMode:
			config.usage.plugin_sort_weight.value = {}
			config.usage.plugin_sort_weight.save()
			self.updatePluginList()
		else:
			self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.REMOVE, True)

	def keyGreen(self):
		if self.sortMode:
			if self.sortMode:
				self.keySelect()
		else:
			self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.DOWNLOAD, self.firsttime)
			self.firstTime = False

	def keyBlue(self):
		self.toggleSortMode()
		self.selectionChanged()

	def keyTop(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goTop()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyPageUp(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goPageUp()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyUp(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goLineUp()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyFirst(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goFirst()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyLeft(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goLeft()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyRight(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goRight()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyLast(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goLast()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyDown(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goLineDown()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyPageDown(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goPageDown()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def keyBottom(self):
		self.currentIndex = self.currentList.getSelectedIndex()
		self.currentList.goBottom()
		if self.sortMode and self.selectedPlugin:
			self.moveAction()

	def moveAction(self):
		entry = self.pluginList.pop(self.currentIndex)
		newpos = self.currentList.getSelectedIndex()
		self.pluginList.insert(newpos, entry)
		self.currentList.updateList(self.pluginList)

	def keyNumberGlobal(self, digit):
		self.quickSelectTimer.stop()
		if self.lastKey != digit:  # Is this a different digit?
			self.nextKey()  # Reset lastKey again so NumericalTextInput triggers its key change.
			self.selectByStart()
			self.quickSelectPos += 1
		char = self.getKey(digit)  # Get char and append to text.
		self.quickSelect = "%s%s" % (self.quickSelect[:self.quickSelectPos], str(char))
		self["quickselect"].setText(self.quickSelect)
		self["quickselect"].show()
		self.quickSelectTimerType = 0
		self.quickSelectTimer.start(1000, True)  # Allow 1 second to select the desired character for the QuickSelect text.

	def quickSelectTimeout(self, force=False):
		if not force and self.quickSelectTimerType == 0:
			self.selectByStart()
			self.quickSelectTimerType = 1
			self.quickSelectTimer.start(1500, True)  # Allow 1.5 seconds before reseting the QuickSelect text.
		else:  # Timeout QuickSelect
			self.quickSelectTimer.stop()
			self.quickSelect = ""
			self.quickSelectPos = -1
		self.lastKey = -1  # Finalize current character.

	def selectByStart(self):  # Try to select what was typed so far.
		if self.pluginList and self.quickSelect:
			self["quickselect"].hide()
			self["quickselect"].setText("")
			pattern = self.quickSelect.lower()
			for index, item in enumerate(self.pluginList):
				package = item[0]
				if package.name.lower().startswith(pattern):  # Select first file starting with case insensitive QuickSelect text.
					self.currentList.setCurrentIndex(index)
					break

	def openSetup(self):
		from Screens.Setup import Setup
		self.session.open(Setup, "PluginBrowser")

	def isProtected(self):
		return config.ParentalControl.setuppinactive.value and (not config.ParentalControl.config_sections.main_menu.value or hasattr(self.session, 'infobar') and self.session.infobar is None) and config.ParentalControl.config_sections.plugin_browser.value

	def createSummary(self):
		return PluginBrowserSummary

	def selectionChanged(self):
		if self.pluginList:
			item = self.pluginList[self.currentList.getSelectedIndex()]
			if item:
				package = item[0]
				name = package.name
				description = package.description
				self["description"].setText(description)
			else:
				name = "-"
				description = ""
				if self.sortMode:
					self["key_yellow"].setText("")
			for callback in self.onChangedEntry:
				callback(name, description)

	def checkWarnings(self):
		if len(plugins.warnings):
			text = _("Some plugins are not available:\n")
			for (pluginname, error) in plugins.warnings:
				text += "%s (%s)\n" % (pluginname, error)
			plugins.resetWarnings()
			self.session.open(MessageBox, text=text, type=MessageBox.TYPE_WARNING)

	def delete(self):
		config.misc.pluginbrowser.languages_po.value = False
		self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.REMOVE, True)

	def download(self):
		config.misc.pluginbrowser.languages_po.value = True
		self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.DOWNLOAD, self.firsttime)
		self.firsttime = False

	def PluginDownloadBrowserClosed(self):
		self.updatePluginList()
		self.checkWarnings()

	def openExtensionmanager(self):
		if isPluginInstalled("SoftwareManager"):
			try:
				from Plugins.SystemPlugins.SoftwareManager.plugin import PluginManager
			except ImportError as e:
				self.session.open(MessageBox, _("The software management extension is not installed!\nPlease install it."), type=MessageBox.TYPE_INFO, timeout=10)
			else:
				self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginManager)


class PluginBrowserSummary(ScreenSummary):
	def __init__(self, session, parent):
		ScreenSummary.__init__(self, session, parent=parent)
		self["entry"] = StaticText("")
		self["desc"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)

	def selectionChanged(self, name, desc):
		self["entry"].text = name
		self["desc"].text = desc


class PluginDownloadBrowser(Screen):
	DOWNLOAD = 0
	REMOVE = 1
	UPDATE = 2
	PLUGIN_PREFIX = 'enigma2-plugin-'
	PLUGIN_PREFIX2 = []
	lastDownloadDate = None

	def __init__(self, session, type=0, needupdate=True, skin_name=None):
		Screen.__init__(self, session)
		self.type = type
		self.needupdate = needupdate
		self.skinName = ["PluginDownloadBrowser"]
		if isinstance(skin_name, str):
			self.skinName.insert(0, skin_name)

		if self.type == self.REMOVE:
			config.pluginbrowser.languages_po.value = False
			config.pluginbrowser.languages_po.save()

		self.createPluginFilter()
		self.LanguageList = language.getLanguageListSelection()
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)

		self.list = []
		self["list"] = PluginList(self.list)
		self.pluginlist = []
		self.expanded = []
		self.installedplugins = []
		self.plugins_changed = False
		self.reload_settings = False
		self.check_settings = False
		self.check_bootlogo = False
		self.install_settings_name = ''
		self.remove_settings_name = ''
		self.onChangedEntry = []
		self.setTitle(self.type == self.DOWNLOAD and _("Install plugins") or _("Remove plugins"))
		self["list"].onSelectionChanged.append(self.selectionChanged)

		if self.type == self.DOWNLOAD:
			self["text"] = Label(_("Downloading plugin information. Please wait..."))
		elif self.type == self.REMOVE:
			self["text"] = Label(_("Getting plugin information. Please wait..."))

		self.run = 0
		self.remainingdata = ""
		self["actions"] = ActionMap(["WizardActions"],
		{
			"ok": self.go,
			"back": self.requestClose,
		})
		if isfile('/usr/bin/opkg'):
			self.ipkg = '/usr/bin/opkg'
			self.ipkg_install = self.ipkg + ' install'
			self.ipkg_remove = self.ipkg + ' remove --autoremove'
		else:
			self.ipkg = 'ipkg'
			self.ipkg_install = 'ipkg install -force-defaults'
			self.ipkg_remove = self.ipkg + ' remove'

	def createSummary(self):
		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["list"].getCurrent()
		try:
			if isinstance(item[0], str):  # category
				name = item[0]
				desc = ""
			else:
				p = item[0]
				name = item[1][0:8][7]
				desc = p.description
		except:
			name = ""
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def createPluginFilter(self):
		# Create Plugin Filter
		self.PLUGIN_PREFIX2 = []
		if config.misc.pluginbrowser.bootlogos.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'bootlogos')
		if config.misc.pluginbrowser.drivers.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'drivers')
		if config.misc.pluginbrowser.extensions.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'extensions')
		if config.misc.pluginbrowser.m2k.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'm2k')
		if config.misc.pluginbrowser.picons.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'picons')
		if config.misc.pluginbrowser.security.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'security')
		if config.misc.pluginbrowser.settings.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'settings')
		if config.misc.pluginbrowser.skin.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'skin')
		if config.misc.pluginbrowser.display.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'display')
		if config.misc.pluginbrowser.softcams.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'softcams')
		if config.misc.pluginbrowser.systemplugins.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'systemplugins')
		if config.misc.pluginbrowser.weblinks.value:
			self.PLUGIN_PREFIX2.append(self.PLUGIN_PREFIX + 'weblinks')
		if config.misc.pluginbrowser.kernel.value:
			self.PLUGIN_PREFIX2.append('kernel-module-')
		if config.pluginbrowser.languages_po.value:
			self.PLUGIN_PREFIX2.append('enigma2-locale-')

	def go(self):
		sel = self["list"].l.getCurrentSelection()

		if sel is None:
			return

		sel = sel[0]
		if isinstance(sel, str):  # category
			if sel in self.expanded:
				self.expanded.remove(sel)
			else:
				self.expanded.append(sel)
			self.updateList()
		else:
			if self.type == self.DOWNLOAD:
				self.session.openWithCallback(self.runInstall, MessageBox, _("You want to install the plugin \"%s\"?") % sel.name)
			elif self.type == self.REMOVE:
				self.session.openWithCallback(self.runInstall, MessageBox, _("You want to remove the plugin \"%s\"?") % sel.name)

	def requestClose(self):
		if self.plugins_changed:
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		if self.reload_settings:
			self["text"].setText(_("Reloading bouquets and services..."))
			eDVBDB.getInstance().reloadBouquets()
			eDVBDB.getInstance().reloadServicelist()
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.container.appClosed.remove(self.runFinished)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()

	def resetPostInstall(self):
		try:
			del self.postInstallCall
		except:
			pass

	def installDestinationCallback(self, result):
		if result is not None:
			dest = result[1]
			if dest.startswith('/'):
				# Custom install path, add it to the list too
				dest = normpath(dest)
				extra = '--add-dest %s:%s -d %s' % (dest, dest, dest)
				Opkg.opkgAddDestination(dest)
			else:
				extra = '-d ' + dest
			self.doInstall(self.installFinished, self["list"].l.getCurrentSelection()[0].name + ' ' + extra)
		else:
			self.resetPostInstall()

	def runInstall(self, val):
		if val:
			if self.type == self.DOWNLOAD:
				if self["list"].l.getCurrentSelection()[0].name.startswith("picons-"):
					supported_filesystems = frozenset(('ext4', 'ext3', 'ext2', 'reiser', 'reiser4', 'jffs2', 'ubifs', 'rootfs'))
					candidates = []
					import Components.Harddisk
					mounts = Components.Harddisk.getProcMounts()
					for partition in harddiskmanager.getMountedPartitions(False, mounts):
						if partition.filesystem(mounts) in supported_filesystems:
							candidates.append((partition.description, partition.mountpoint))
					if candidates:
						from Components.Renderer import Picon
						self.postInstallCall = Picon.initPiconPaths
						self.session.openWithCallback(self.installDestinationCallback, ChoiceBox, title=_("Install picons on"), list=candidates)
					return
				elif self["list"].l.getCurrentSelection()[0].name.startswith("display-picon"):
					supported_filesystems = frozenset(('ext4', 'ext3', 'ext2', 'reiser', 'reiser4', 'jffs2', 'ubifs', 'rootfs'))
					candidates = []
					import Components.Harddisk
					mounts = Components.Harddisk.getProcMounts()
					for partition in harddiskmanager.getMountedPartitions(False, mounts):
						if partition.filesystem(mounts) in supported_filesystems:
							candidates.append((partition.description, partition.mountpoint))
					if candidates:
						from Components.Renderer import LcdPicon
						self.postInstallCall = LcdPicon.initLcdPiconPaths
						self.session.openWithCallback(self.installDestinationCallback, ChoiceBox, title=_("Install lcd picons on"), list=candidates)
					return
				self.install_settings_name = self["list"].l.getCurrentSelection()[0].name
				self.install_bootlogo_name = self["list"].l.getCurrentSelection()[0].name
				if self["list"].l.getCurrentSelection()[0].name.startswith('settings-'):
					self.check_settings = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'settings-*')
				elif self["list"].l.getCurrentSelection()[0].name.startswith('bootlogos-'):
					self.check_bootlogo = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'bootlogos-*')
				else:
					self.runSettingsInstall()
			elif self.type == self.REMOVE:
				self.doRemove(self.installFinished, self["list"].l.getCurrentSelection()[0].name + " --force-remove --force-depends")

	def doRemove(self, callback, pkgname):
		if pkgname.startswith('kernel-module-') or pkgname.startswith('enigma2-locale-'):
			self.session.openWithCallback(callback, Console, cmdlist=[self.ipkg_remove + Opkg.opkgExtraDestinations() + " " + pkgname, "sync"], skin="Console_Pig")
		else:
			self.session.openWithCallback(callback, Console, cmdlist=[self.ipkg_remove + Opkg.opkgExtraDestinations() + " " + self.PLUGIN_PREFIX + pkgname, "sync"], skin="Console_Pig")

	def doInstall(self, callback, pkgname):
		if pkgname.startswith('kernel-module-') or pkgname.startswith('enigma2-locale-'):
			self.session.openWithCallback(callback, Console, cmdlist=[self.ipkg_install + " " + pkgname, "sync"], skin="Console_Pig")
		else:
			self.session.openWithCallback(callback, Console, cmdlist=[self.ipkg_install + " " + self.PLUGIN_PREFIX + pkgname, "sync"], skin="Console_Pig")

	def runSettingsRemove(self, val):
		if val:
			self.doRemove(self.runSettingsInstall, self.remove_settings_name)

	def runBootlogoRemove(self, val):
		if val:
			self.doRemove(self.runSettingsInstall, self.remove_bootlogo_name + " --force-remove --force-depends")

	def runSettingsInstall(self):
		self.doInstall(self.installFinished, self.install_settings_name)

	def startIpkgListInstalled(self, pkgname=None):
		self.container.execute(self.ipkg + Opkg.opkgExtraDestinations() + " list_installed" + (" '%s'" % pkgname if pkgname else ""))

	def startIpkgListAvailable(self):
		self.container.execute(self.ipkg + Opkg.opkgExtraDestinations() + " list")

	def startRun(self):
		listsize = self["list"].instance.size()
		self["list"].instance.hide()
		self.listWidth = listsize.width()
		self.listHeight = listsize.height()
		if self.type == self.DOWNLOAD:
			self.type = self.UPDATE
			self.container.execute(self.ipkg + " update")
		elif self.type == self.REMOVE:
			self.run = 1
			self.startIpkgListInstalled()

	def installFinished(self):
		if hasattr(self, 'postInstallCall'):
			try:
				self.postInstallCall()
			except Exception as ex:
				print("[PluginBrowser] postInstallCall failed:", ex)
			self.resetPostInstall()
		try:
			unlink('/tmp/opkg.conf')
		except:
			pass
		for plugin in self.pluginlist:
			if plugin[3] == self["list"].l.getCurrentSelection()[0].name or plugin[0] == self["list"].l.getCurrentSelection()[0].name:
				self.pluginlist.remove(plugin)
				break
		self.plugins_changed = True
		if self["list"].l.getCurrentSelection()[0].name.startswith("settings-"):
			self.reload_settings = True
		self.expanded = []
		self.updateList()
		self["list"].moveToIndex(0)

	def runFinished(self, retval):
		if self.check_settings:
			self.check_settings = False
			self.runSettingsInstall()
			return
		if self.check_bootlogo:
			self.check_bootlogo = False
			self.runSettingsInstall()
			return
		self.remainingdata = ""
		if self.run == 0:
			self.run = 1
			if self.type == self.UPDATE:
				self.type = self.DOWNLOAD
				self.startIpkgListInstalled()
		elif self.run == 1 and self.type == self.DOWNLOAD:
			self.run = 2
			self.startIpkgListAvailable()
		else:
			if len(self.pluginlist) > 0:
				self.updateList()
				self["list"].instance.show()
				self["text"].setText(_("List of available plugins."))
			else:
				if self.type == self.DOWNLOAD:
					self["text"].setText(_("No plugins found, check server."))

	def dataAvail(self, str):
		str = str.decode()
		str = self.remainingdata + str
		if self.type == self.DOWNLOAD and any([x for x in ('wget returned 1', 'wget returned 255', '404 Not Found') if x in str]):
			self.run = 3
			return
		# prepend any remaining data from the previous call
		str = self.remainingdata + str
		# split in lines
		lines = str.split('\n')
		# 'str' should end with '\n', so when splitting, the last line should be empty. If this is not the case, we received an incomplete line
		if len(lines[-1]):
			# remember this data for next time
			self.remainingdata = lines[-1]
			lines = lines[0:-1]
		else:
			self.remainingdata = ""

		if self.check_settings:
			self.check_settings = False
			self.remove_settings_name = str.split(' - ')[0].replace(self.PLUGIN_PREFIX, '')
			self.session.openWithCallback(self.runSettingsRemove, MessageBox, _('You already have a channel list installed,\nwould you like to remove\n"%s"?') % self.remove_settings_name)
			return

		if self.check_bootlogo:
			self.check_bootlogo = False
			self.remove_bootlogo_name = str.split(' - ')[0].replace(self.PLUGIN_PREFIX, '')
			self.session.openWithCallback(self.runBootlogoRemove, MessageBox, _('You already have a bootlogo installed,\nwould you like to remove\n"%s"?') % self.remove_bootlogo_name)
			return

		for x in lines:
			plugin = x.split(" - ", 2)
			# 'opkg list_installed' only returns name + version, no description field
			if len(plugin) >= 1:
				if not plugin[0].endswith('-dev') and not plugin[0].endswith('-staticdev') and not plugin[0].endswith('-dbg') and not plugin[0].endswith('-doc') and not plugin[0].endswith('-common') and not plugin[0].endswith('-meta') and plugin[0] not in self.installedplugins and ((not config.pluginbrowser.languages_po.value and not plugin[0].endswith('-po')) or config.pluginbrowser.languages_po.value) and ((not config.pluginbrowser.src.value and not plugin[0].endswith('-src')) or config.pluginbrowser.src.value):
					# Plugin filter
					for s in self.PLUGIN_PREFIX2:
						if plugin[0].startswith(s):
							if self.run == 1 and self.type == self.DOWNLOAD:
								self.installedplugins.append(plugin[0])
							else:
								if len(plugin) == 2:
									# 'opkg list_installed' does not return descriptions, append empty description
									if plugin[0].startswith('enigma2-locale-'):
										lang = plugin[0].split('-')
										if len(lang) > 3:
											plugin.append(lang[2] + '-' + lang[3])
										else:
											plugin.append(lang[2])
									else:
										plugin.append('')
								plugin.append(plugin[0][15:])
								self.pluginlist.append(plugin)
		self.pluginlist.sort()

	def updateList(self):
		updatedlist = []
		expandableIcon = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "icons/expandable-plugins.png"))
		expandedIcon = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "icons/expanded-plugins.png"))
		verticallineIcon = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "icons/verticalline-plugins.png"))

		self.plugins = {}

		if self.type == self.UPDATE:
			self.list = updatedlist
			self["list"].l.setList(updatedlist)
			return

		for x in self.pluginlist:
			split = x[3].split('-', 1)
			if x[0][0:14] == 'kernel-module-':
				split[0] = "kernel modules"
			elif x[0][0:15] == 'enigma2-locale-':
				split[0] = _("languages")

			if split[0] not in self.plugins:
				self.plugins[split[0]] = []

			if split[0] == "kernel modules":
				self.plugins[split[0]].append((PluginDescriptor(name=x[0], description=x[2], icon=verticallineIcon), x[0][14:], x[1]))
			elif split[0] == _("languages"):
				for t in self.LanguageList:
					if len(x[2]) > 2:
						tmpT = t[0].lower()
						tmpT = tmpT.replace('_', '-')
						if tmpT == x[2]:
							countryIcon = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "countries/" + t[0] + ".png"))
							if countryIcon is None:
								countryIcon = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "countries/missing.png"))
							self.plugins[split[0]].append((PluginDescriptor(name=x[0], description=x[2], icon=countryIcon), t[1], x[1]))
							break
					else:
						if t[0][:2] == x[2] and t[0][3:] != 'GB':
							countryIcon = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "countries/" + t[0] + ".png"))
							if countryIcon is None:
								countryIcon = LoadPixmap(resolveFilename(SCOPE_GUISKIN, "countries/missing.png"))
							self.plugins[split[0]].append((PluginDescriptor(name=x[0], description=x[2], icon=countryIcon), t[1], x[1]))
							break
			else:
				if len(split) < 2:
					continue
				self.plugins[split[0]].append((PluginDescriptor(name=x[3], description=x[2], icon=verticallineIcon), split[1], x[1]))

		temp = list(self.plugins.keys())
		if config.usage.sort_pluginlist.value:
			temp.sort()
		for x in temp:
			if x in self.expanded:
				updatedlist.append(PluginCategoryComponent(x, expandedIcon, self.listWidth))
				updatedlist.extend([PluginDownloadComponent(plugin[0], plugin[1], plugin[2], self.listWidth) for plugin in self.plugins[x]])
			else:
				updatedlist.append(PluginCategoryComponent(x, expandableIcon, self.listWidth))
		self.list = updatedlist
		self["list"].l.setList(updatedlist)


language.addCallback(languageChanged)
