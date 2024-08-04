# -*- coding: utf-8 -*-
from os import W_OK, access
from os.path import exists

from enigma import eAVControl, getDesktop

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.AVSwitch import iAVSwitch
from Components.config import ConfigNumber, ConfigSelection, ConfigSelectionInteger, ConfigSlider, ConfigSubsection, ConfigText, ConfigYesNo, NoSave, config, configfile
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.Label import Label
from Components.SystemInfo import BoxInfo
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Setup import Setup, SetupSummary
from Tools.Directories import fileReadLine, fileWriteLine

MODULE_NAME = __name__.split(".")[-1]


def InitOSDCalibration():
	def setPositionParameter(parameter, value):
		if BoxInfo.getItem("CanChangeOsdPosition"):
			fileWriteLine(f"/proc/stb/fb/dst_{parameter}", f"{value:08x}\n", source=MODULE_NAME)
			fileName = "/proc/stb/fb/dst_apply"
			if exists(fileName):
				fileWriteLine(fileName, "1", source=MODULE_NAME)
		elif BoxInfo.getItem("CanChangeOsdPositionAML"):
			value = f"{config.osd.dst_left.value} {config.osd.dst_top.value} {config.osd.dst_width.value} {config.osd.dst_height.value}"
			fileWriteLine("/sys/class/graphics/fb0/window_axis", value, source=MODULE_NAME)
			fileWriteLine("/sys/class/graphics/fb0/free_scale", "0x10001", source=MODULE_NAME)

	def setLeft(configElement):
		setPositionParameter("left", configElement.value)

	def setTop(configElement):
		setPositionParameter("top", configElement.value)

	def setWidth(configElement):
		setPositionParameter("width", configElement.value)

	def setHeight(configElement):
		setPositionParameter("height", configElement.value)

	print(f"[OSDCalibration] Setting OSD position: {config.osd.dst_left.value} {config.osd.dst_width.value} {config.osd.dst_top.value} {config.osd.dst_height.value}")

	def setAlpha(configElement):
		value = configElement.value
		print(f"[OSDCalibration] Setting OSD alpha to {value}.")
		config.av.osd_alpha.setValue(value)
		eAVControl.getInstance().setOSDAlpha(value)

	def set3DMode(configElement):
		value = configElement.value
		print(f"[OSDCalibration] Setting 3D mode to {value}.")
		if BoxInfo.getItem("CanUse3DModeChoices"):
			choices = fileReadLine("/proc/stb/fb/3dmode_choices", "", source=MODULE_NAME).split()
			if value not in choices:
				match value:
					case "sidebyside":
						value = "sbs"
					case "topandbottom":
						value = "tab"
					case "auto":
						value = "off"
			fileWriteLine("/proc/stb/fb/3dmode", value, source=MODULE_NAME)

	def set3DZnorm(configElement):
		value = configElement.value
		print(f"[OSDCalibration] Setting 3D depth to {value}.")
		fileWriteLine("/proc/stb/fb/znorm", str(value), source=MODULE_NAME)

	BoxInfo.setItem("CanChangeOsdPosition", access("/proc/stb/fb/dst_left", W_OK))
	BoxInfo.setItem("CanChangeOsdPositionAML", access("/sys/class/graphics/fb0/free_scale", W_OK))  # Is this the same as BoxInfo.getItem("AmlogicFamily")?
	BoxInfo.setItem("CanChangeOsdAlpha", eAVControl.getInstance().hasOSDAlpha())
	BoxInfo.setItem("OSDCalibration", BoxInfo.getItem("CanChangeOsdPosition") or BoxInfo.getItem("CanChangeOsdPositionAML") or BoxInfo.getItem("CanChangeOsdAlpha"))
	BoxInfo.setItem("OSD3DCalibration", access("/proc/stb/fb/3dmode", W_OK))
	print(f"[OSDCalibration] Setting OSD position to (X={config.osd.dst_left.value}, Y={config.osd.dst_top.value}) and size to (W={config.osd.dst_width.value}, H={config.osd.dst_height.value}).")
	config.osd.dst_left.addNotifier(setLeft)
	config.osd.dst_top.addNotifier(setTop)
	config.osd.dst_width.addNotifier(setWidth)
	config.osd.dst_height.addNotifier(setHeight)
	if BoxInfo.getItem("CanChangeOsdAlpha"):
		config.osd.alpha.addNotifier(setAlpha)
	if BoxInfo.getItem("OSD3DCalibration"):
		config.osd.threeDmode.addNotifier(set3DMode)
		config.osd.threeDznorm.addNotifier(set3DZnorm)


class OSDCalibration(ConfigListScreen, Screen):
	if (getDesktop(0).size().width() == 1920):
		skin = """
			<screen name="OSDCalibration" position="fill" backgroundColor="#1A0F0F0F" flags="wfNoBorder" title="OSD Calibration Settings">

				<widget name="text" position="300,165" zPosition="+4" size="1320,180" font="Regular;32" halign="center" valign="center" foregroundColor="#00FFFF00" transparent="1" />
				<widget name="config" position="225,375" zPosition="1" size="1470,315" itemHeight="45" font="Regular;30" transparent="1" />
				<widget source="status" render="Label" position="300,713" zPosition="1" size="1320,120" font="Regular;32" halign="center" valign="center" foregroundColor="#00FFFF00" transparent="1" />

				<eLabel backgroundColor="red" position="0,0" size="1920,1" zPosition="0" />
				<eLabel backgroundColor="red" position="0,1079" size="1920,1" zPosition="0" />
				<eLabel backgroundColor="red" position="0,0" size="1,1080" zPosition="0" />
				<eLabel backgroundColor="red" position="1919,0" size="1,1080" zPosition="0" />
				<eLabel backgroundColor="green" position="38,38" size="1845,1" zPosition="0" />
				<eLabel backgroundColor="green" position="38,1041" size="1845,1" zPosition="0" />
				<eLabel backgroundColor="green" position="38,38" size="1,1005" zPosition="0" />
				<eLabel backgroundColor="green" position="1881,38" size="1,1005" zPosition="0" />
				<eLabel backgroundColor="yellow" position="75,75" size="1770,1" zPosition="0" />
				<eLabel backgroundColor="yellow" position="75,1004" size="1770,1" zPosition="0" />
				<eLabel backgroundColor="yellow" position="75,75" size="1,930" zPosition="0" />
				<eLabel backgroundColor="yellow" position="1844,75" size="1,930" zPosition="0" />
				<eLabel backgroundColor="blue" position="113,113" size="1695,1" zPosition="0" />
				<eLabel backgroundColor="blue" position="113,966" size="1695,1" zPosition="0" />
				<eLabel backgroundColor="blue" position="113,113" size="1,855" zPosition="0" />
				<eLabel backgroundColor="blue" position="1806,113" size="1,855" zPosition="0" />

				<eLabel backgroundColor="red" position="284,941" size="210,5" zPosition="0" />
				<eLabel backgroundColor="green" position="665,941" size="210,5" zPosition="0" />
				<eLabel backgroundColor="yellow" position="1046,941" size="210,5" zPosition="0" />
				<eLabel backgroundColor="blue" position="1427,941" size="210,5" zPosition="0" />
				<widget source="key_red" render="Label" position="284,908" zPosition="1" size="210,33" font="Regular;27" halign="center" valign="center" transparent="1" />
				<widget source="key_green" render="Label" position="665,908" zPosition="1" size="210,33" font="Regular;27" halign="center" valign="center" transparent="1" />
				<widget source="key_yellow" render="Label" position="1046,908" zPosition="1" size="210,33" font="Regular;27" halign="center" valign="center" transparent="1" />
				<widget source="key_blue" render="Label" position="1427,908" zPosition="1" size="210,33" font="Regular;27" halign="center" valign="center" transparent="1" />

			</screen>"""
	elif (getDesktop(0).size().width() == 1280):
		skin = """
			<screen name="OSDCalibration" position="fill" backgroundColor="#1A0F0F0F" flags="wfNoBorder" title="OSD Calibration Settings">

				<widget name="text" position="200,110" zPosition="+4" size="880,120" font="Regular;21" halign="center" valign="center" foregroundColor="#00FFFF00" transparent="1" />
				<widget name="config" position="150,250" zPosition="1" size="980,210" itemHeight="30" font="Regular;20" transparent="1" />
				<widget source="status" render="Label" position="200,475" zPosition="1" size="880,80" font="Regular;21" halign="center" valign="center" foregroundColor="#00FFFF00" transparent="1" />

				<eLabel backgroundColor="red" position="0,0" size="1280,1" zPosition="0" />
				<eLabel backgroundColor="red" position="0,719" size="1280,1" zPosition="0" />
				<eLabel backgroundColor="red" position="0,0" size="1,720" zPosition="0" />
				<eLabel backgroundColor="red" position="1279,0" size="1,720" zPosition="0" />
				<eLabel backgroundColor="green" position="25,25" size="1230,1" zPosition="0" />
				<eLabel backgroundColor="green" position="25,694" size="1230,1" zPosition="0" />
				<eLabel backgroundColor="green" position="25,25" size="1,670" zPosition="0" />
				<eLabel backgroundColor="green" position="1254,25" size="1,670" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,50" size="1180,1" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,669" size="1180,1" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,50" size="1,620" zPosition="0" />
				<eLabel backgroundColor="yellow" position="1229,50" size="1,620" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,75" size="1130,1" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,644" size="1130,1" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,75" size="1,570" zPosition="0" />
				<eLabel backgroundColor="blue" position="1204,75" size="1,570" zPosition="0" />

				<eLabel backgroundColor="red" position="189,627" size="140,3" zPosition="0" />
				<eLabel backgroundColor="green" position="443,627" size="140,3" zPosition="0" />
				<eLabel backgroundColor="yellow" position="697,627" size="140,3" zPosition="0" />
				<eLabel backgroundColor="blue" position="951,627" size="140,3" zPosition="0" />
				<widget source="key_red" render="Label" position="189,605" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_green" render="Label" position="443,605" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_yellow" render="Label" position="697,605" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_blue" render="Label" position="951,605" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />

			</screen>"""

	elif (getDesktop(0).size().width() == 1024):
		skin = """
			<screen name="OSDCalibration" position="fill" backgroundColor="#1A0F0F0F" flags="wfNoBorder" title="OSD Calibration Settings">

				<widget name="text" position="200,180" zPosition="+4" size="624,100" font="Regular;21" halign="center" valign="center" foregroundColor="#00FFFF00" transparent="1" />
				<widget name="config" position="100,180" zPosition="1" size="824,50" font="Regular;24" halign="center" valign="center" transparent="1" />
				<widget source="status" render="Label" position="200,450" zPosition="1" size="624,80" font="Regular;21" halign="center" valign="center" foregroundColor="#00FFFF00" transparent="1" />

				<eLabel backgroundColor="red" position="0,0" size="1024,1" zPosition="0" />
				<eLabel backgroundColor="red" position="0,575" size="1024,1" zPosition="0" />
				<eLabel backgroundColor="red" position="0,0" size="1,576" zPosition="0" />
				<eLabel backgroundColor="red" position="1023,0" size="1,576" zPosition="0" />
				<eLabel backgroundColor="green" position="25,25" size="974,1" zPosition="0" />
				<eLabel backgroundColor="green" position="25,551" size="974,1" zPosition="0" />
				<eLabel backgroundColor="green" position="25,25" size="1,526" zPosition="0" />
				<eLabel backgroundColor="green" position="999,25" size="1,526" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,50" size="924,1" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,526" size="924,1" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,50" size="1,476" zPosition="0" />
				<eLabel backgroundColor="yellow" position="974,50" size="1,476" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,75" size="874,1" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,501" size="874,1" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,75" size="1,426" zPosition="0" />
				<eLabel backgroundColor="blue" position="949,75" size="1,426" zPosition="0" />

				<eLabel backgroundColor="red" position="138,477" size="140,3" zPosition="0" />
				<eLabel backgroundColor="green" position="341,477" size="140,3" zPosition="0" />
				<eLabel backgroundColor="yellow" position="544,477" size="140,3" zPosition="0" />
				<eLabel backgroundColor="blue" position="747,477" size="140,3" zPosition="0" />
				<widget source="key_red" render="Label" position="138,455" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_green" render="Label" position="341,455" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_yellow" render="Label" position="544,455" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_blue" render="Label" position="747,455" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
			</screen>"""

	else:
		skin = """
			<screen name="OSDCalibration" position="fill" backgroundColor="#1A0F0F0F" flags="wfNoBorder" title="OSD Calibration Settings">

				<widget name="text" position="75,80" zPosition="+4" size="570,100" font="Regular;21" halign="center" valign="center" foregroundColor="#00FFFF00" transparent="1" />
				<widget name="config" position="75,180" zPosition="1" size="570,50" font="Regular;21" halign="center" valign="center" transparent="1" />
				<widget source="status" render="Label" position="75,450" zPosition="1" size="570,80" font="Regular;21" halign="center" valign="center" foregroundColor="#00FFFF00" transparent="1" />

				<eLabel backgroundColor="red" position="0,0" size="720,1" zPosition="0" />
				<eLabel backgroundColor="red" position="0,575" size="720,1" zPosition="0" />
				<eLabel backgroundColor="red" position="0,0" size="1,576" zPosition="0" />
				<eLabel backgroundColor="red" position="719,0" size="1,576" zPosition="0" />
				<eLabel backgroundColor="green" position="25,25" size="670,1" zPosition="0" />
				<eLabel backgroundColor="green" position="25,551" size="670,1" zPosition="0" />
				<eLabel backgroundColor="green" position="25,25" size="1,526" zPosition="0" />
				<eLabel backgroundColor="green" position="694,25" size="1,526" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,50" size="620,1" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,526" size="620,1" zPosition="0" />
				<eLabel backgroundColor="yellow" position="50,50" size="1,476" zPosition="0" />
				<eLabel backgroundColor="yellow" position="670,50" size="1,476" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,75" size="570,1" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,501" size="570,1" zPosition="0" />
				<eLabel backgroundColor="blue" position="75,75" size="1,426" zPosition="0" />
				<eLabel backgroundColor="blue" position="645,75" size="1,426" zPosition="0" />

				<eLabel backgroundColor="red" position="80,477" size="140,3" zPosition="0" />
				<eLabel backgroundColor="green" position="220,477" size="140,3" zPosition="0" />
				<eLabel backgroundColor="yellow" position="360,477" size="140,3" zPosition="0" />
				<eLabel backgroundColor="blue" position="500,477" size="140,3" zPosition="0" />
				<widget source="key_red" render="Label" position="80,455" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_green" render="Label" position="220,455" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_yellow" render="Label" position="360,455" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />
				<widget source="key_blue" render="Label" position="500,455" zPosition="1" size="140,22" font="Regular;18" halign="center" valign="center" transparent="1" />

			</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["OSDCalibration"]  # Don't use the standard Setup screen.
		self.setup_title = _("Position Setup")
		# self.Console = Console()
		self["status"] = StaticText()
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Defaults"))
		self["key_blue"] = StaticText()

		self["title"] = StaticText(_("OSD Adjustment"))
		text = []
		text.append(_("Before changing these settings try to disable any overscan settings on th TV / display screen. To calibrate the On-Screen-Display (OSD) adjust the position and size values until the red box is *just* visible and touches the edges of the screen."))
		text.append(_("When the red box is correctly visible press the GREEN button to save the settings and exit."))
		self["text"] = Label("\n".join(text))

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"save": self.keySave,
				"left": self.keyLeft,
				"right": self.keyRight,
				"yellow": self.keyDefault,
			}, -2)

		self.onChangedEntry = []
		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
		if BoxInfo.getItem("CanChangeOsdAlpha") or BoxInfo.getItem("CanChangeOsdPlaneAlpha"):
			self.list.append((_("User interface visibility"), config.osd.alpha, _("This option lets you adjust the transparency of the user interface")))
			self.list.append((_("Teletext base visibility"), config.osd.alpha_teletext, _("Base transparency for teletext, more options available within teletext screen.")))
			self.list.append((_("Web browser base visibility"), config.osd.alpha_webbrowser, _("Base transparency for OpenOpera web browser")))
		if BoxInfo.getItem("CanChangeOsdPosition"):
			self.list.append((_("Move Left/Right"), config.osd.dst_left, _("Use the Left/Right buttons on your remote to move the user interface left/right")))
			self.list.append((_("Width"), config.osd.dst_width, _("Use the Left/Right buttons on your remote to adjust the size of the user interface. Left button decreases the size, Right increases the size.")))
			self.list.append((_("Move Up/Down"), config.osd.dst_top, _("Use the Left/Right buttons on your remote to move the user interface up/down")))
			self.list.append((_("Height"), config.osd.dst_height, _("Use the Left/Right buttons on your remote to adjust the size of the user interface. Left button decreases the size, Right increases the size.")))
		if BoxInfo.getItem("CanChangeOsdPositionAML"):
			self.list.append((_("Left"), config.osd.dst_left, _("Use the Left/Right buttons on your remote to move the user interface left")))
			self.list.append((_("Right"), config.osd.dst_width, _("Use the Left/Right buttons on your remote to move the user interface right")))
			self.list.append((_("Top"), config.osd.dst_top, _("Use the Left/Right buttons on your remote to move the user interface top")))
			self.list.append((_("Bottom"), config.osd.dst_height, _("Use the Left/Right buttons on your remote to move the user interface bottom")))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

		self.onLayoutFinish.append(self.layoutFinished)
		if self.selectionChanged not in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def selectionChanged(self):
		self["status"].setText(self["config"].getCurrent()[2])

	def layoutFinished(self):
		self.setTitle(_(self.setup_title))
#		self.Console.ePopen("/usr/bin/showiframe /usr/share/enigma2/hd-testcard.mvi")

	def createSummary(self):
		return SetupSummary

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		if BoxInfo.getItem("CanChangeOsdPosition"):
			self.setPreviewPosition()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		if BoxInfo.getItem("CanChangeOsdPosition"):
			self.setPreviewPosition()

	def keyDefault(self):
		config.osd.alpha.setValue(255)
		config.osd.alpha_teletext.setValue(255)
		config.osd.alpha_webbrowser.setValue(255)

		if BoxInfo.getItem("CanChangeOsdPosition"):
			config.osd.dst_width.setValue(720)
			config.osd.dst_height.setValue(576)
			config.osd.dst_left.setValue(0)
			config.osd.dst_top.setValue(0)
		elif BoxInfo.getItem("CanChangeOsdPositionAML"):
			from Plugins.SystemPlugins.Videomode.VideoHardware import video_hw
			limits = [int(x) for x in video_hw.getWindowsAxis().split()]
			config.osd.dst_left.setValue(limits[0])
			config.osd.dst_top.setValue(limits[1])
			config.osd.dst_width.setValue(limits[2])
			config.osd.dst_height.setValue(limits[3])
		self["config"].l.setList(self.list)

	def setPreviewPosition(self):
		size_w = getDesktop(0).size().width()
		size_h = getDesktop(0).size().height()
		dsk_w = int(float(size_w)) / float(720)
		dsk_h = int(float(size_h)) / float(576)
		dst_left = int(config.osd.dst_left.value)
		dst_width = int(config.osd.dst_width.value)
		dst_top = int(config.osd.dst_top.value)
		dst_height = int(config.osd.dst_height.value)
		while dst_width + (dst_left / float(dsk_w)) >= 720.5 or dst_width + dst_left > 720:
			dst_width = int(dst_width) - 1
		while dst_height + (dst_top / float(dsk_h)) >= 576.5 or dst_height + dst_top > 576:
			dst_height = int(dst_height) - 1

		config.osd.dst_left.setValue(dst_left)
		config.osd.dst_width.setValue(dst_width)
		config.osd.dst_top.setValue(dst_top)
		config.osd.dst_height.setValue(dst_height)
		print(f"[OSDCalibration] Setting OSD position: {config.osd.dst_left.value} {config.osd.dst_width.value} {config.osd.dst_top.value} {config.osd.dst_height.value}")

	def saveAll(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	# keySave and keyCancel are just provided in case you need them.
	# you have to call them by yourself.
	def keySave(self):
		self.saveAll()
		self.close()

	def cancelConfirm(self, result):
		if not result:
			return

		for x in self["config"].list:
			x[1].cancel()
		self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), default=False)
		else:
			self.close()

	def run(self):
		config.osd.dst_left.save()
		config.osd.dst_width.save()
		config.osd.dst_top.save()
		config.osd.dst_height.save()
		configfile.save()
		self.close()


class OSD3DCalibration(Setup):
	def __init__(self, session):
		Setup.__init__(self, session, "OSD3DCalibration")
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Defaults"))
		self["actions"] = HelpableActionMap(self, ["SetupActions", "ColorActions"], {
			"cancel": (self.keyCancel, _("Reset all settings to the default values")),
			"save": (self.keySave, _("Reset all settings to the default values")),
			"yellow": (self.keyDefault, _("Reset all settings to the default values"))
		}, prio=0, description=_("OSD 3D Calibration Setup Actions"))

	def keyDefault(self):
		config.osd.threeDmode.setValue(config.osd.threeDmode.default)
		config.osd.threeDznorm.setValue(config.osd.threeDznorm.default)
		config.osd.show3dextensions.setValue(config.osd.show3dextensions.default)
		print("[OSDCalibration] OSD 3D settings restored to defaults.")
		for entry in self["config"].getList():
			self["config"].invalidate(entry)

	def saveAll(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	# keySave and keyCancel are just provided in case you need them.
	# you have to call them by yourself.
	def keySave(self):
		self.saveAll()
		self.close()

	def cancelConfirm(self, result):
		if not result:
			return

		for x in self["config"].list:
			x[1].cancel()
		self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), default=False)
		else:
			self.close()
