from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigInteger
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText


config.plugins.minitv = ConfigSubsection()
config.plugins.minitv.enable = ConfigSelection(default="disable", choices=[("enable", "enable"), ("disable", "disable")])

class MiniTVSetup(ConfigListScreen, Screen):
	skin = """
		<screen position="center,center" size="400,270" title="MiniTV Setup" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="30,10" size="140,40" alphaTest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="230,10" size="140,40" alphaTest="on" />
			<widget source="key_red" render="Label" position="30,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
			<widget source="key_green" render="Label" position="230,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />
			<widget name="config" zPosition="2" position="5,70" size="380,180" scrollbarMode="showOnDemand" transparent="1" />
		</screen>
		"""

	def __init__(self,session):
		Screen.__init__(self,session)
		self.session = session
		self["shortcuts"] = ActionMap(["ShortcutActions", "SetupActions"],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
		}, -2)
		self.list = []
		ConfigListScreen.__init__(self, self.list,session = self.session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["current"] = StaticText(_(" "))
		self.createSetup()

	def createSetup(self):
		self.minitvModeEntry = (_("MiniTV Mode"), config.plugins.minitv.enable)
		self.list = []
		self.list.append(self.minitvModeEntry)
		self["config"].list = self.list
		self["config"].l.setList(self.list)	

class MiniTV:
	def __init__(self):
		config.plugins.minitv.enable.addNotifier(self.miniTVChanged, initial_call=True)
		config.misc.standbyCounter.addNotifier(self.standbyCounterChanged, initial_call=False)

	def miniTVChanged(self, configElement):
		self.setMiniTV(configElement.value)

	def setMiniTV(self, value):
		cur_value = open("/proc/stb/lcd/live_enable").read().strip()
		if cur_value != value:
			open("/proc/stb/lcd/live_enable", "w").write(value)

	def standbyCounterChanged(self, configElement):
		from Screens.Standby import inStandby
		if self.leaveStandby not in inStandby.onClose:
			inStandby.onClose.append(self.leaveStandby)

		self.setMiniTV("disable")

	def leaveStandby(self):
		self.setMiniTV(config.plugins.minitv.enable.value)

minitv_instance = MiniTV()

def autoStart(reason, **kwargs):
	if reason == 1:
		minitv_instance.setMiniTV("standby")

def main(session, **kwargs):
	session.open(MiniTVSetup)

def Plugins(**kwargs):
	list = []
	list.append(
		PluginDescriptor(
		where = [PluginDescriptor.WHERE_AUTOSTART],
		fnc = autoStart))

	list.append(
		PluginDescriptor(
		name=_("MiniTV Setup"),
		description="MiniTV Setup",
		where = [PluginDescriptor.WHERE_PLUGINMENU],
		fnc = main))

	return list
