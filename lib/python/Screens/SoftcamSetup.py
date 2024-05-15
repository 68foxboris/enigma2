# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config, ConfigNothing, ConfigAction, ConfigSelection, NoSave
from Components.ScrollLabel import ScrollLabel
from Screens.Setup import Setup
from Screens.InfoBarGenerics import streamrelay
from Screens.OScamInfo import OSCamInfo
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.GetEcmInfo import GetEcmInfo
from Components.Sources.StaticText import StaticText

import os
from Tools.camcontrol import CamControl
from enigma import eTimer


class SoftcamSetup(Screen, ConfigListScreen):
	skin = """
	<screen name="SoftcamSetup" position="center,center" size="560,550" >
		<widget name="config" position="5,10" size="550,180" />
		<widget name="info" position="5,200" size="550,340" font="Fixed;18" />
		<ePixmap name="red" position="0,510" zPosition="1" size="140,40" pixmap="buttons/red.png" transparent="1" alphaTest="on" />
		<ePixmap name="green" position="140,510" zPosition="1" size="140,40" pixmap="buttons/green.png" transparent="1" alphaTest="on" />
		<widget objectTypes="key_red,StaticText" source="key_red" render="Label" position="0,510" zPosition="2" size="140,40" verticalAlignment="center" horizontalAlignment="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget objectTypes="key_green,StaticText" source="key_green" render="Label" position="140,510" zPosition="2" size="140,40" verticalAlignment="center" horizontalAlignment="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget objectTypes="key_blue,StaticText" source="key_blue" render="Label"  position="420,510" zPosition="2" size="140,40" verticalAlignment="center" horizontalAlignment="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1"/>
		<widget objectTypes="key_blue,StaticText" source="key_blue" render="Pixmap" pixmap="buttons/blue.png"  position="420,510" zPosition="1" size="140,40" transparent="1" alphaTest="on">
			<convert type="ConditionalShowHide"/>
		</widget>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self.setTitle(_("Softcam setup"))

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "CiSelectionActions"],
			{
				"cancel": self.cancel,
				"green": self.save,
				"red": self.cancel,
				"blue": self.ppanelShortcut,
			}, -1)

		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)

		self.softcam = CamControl('softcam')
		self.cardserver = CamControl('cardserver')

		self.ecminfo = GetEcmInfo()
		(newEcmFound, ecmInfo) = self.ecminfo.getEcm()
		self["info"] = ScrollLabel("".join(ecmInfo))
		self.EcmInfoPollTimer = eTimer()
		self.EcmInfoPollTimer.callback.append(self.setEcmInfo)
		self.EcmInfoPollTimer.start(1000)

		softcams = self.softcam.getList()
		cardservers = self.cardserver.getList()

		self.softcams = ConfigSelection(choices=softcams)
		self.softcams.value = self.softcam.current()

		self.softcams_text = _("Select Softcam")
		self.list.append((self.softcams_text, self.softcams))
		if cardservers:
			self.cardservers = ConfigSelection(choices=cardservers)
			self.cardservers.value = self.cardserver.current()
			self.list.append((_("Select Card Server"), self.cardservers))

		self.list.append((_("Restart softcam"), ConfigAction(self.restart, "s")))
		if cardservers:
			self.list.append((_("Restart cardserver"), ConfigAction(self.restart, "c")))
			self.list.append((_("Restart both"), ConfigAction(self.restart, "sc")))

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["key_blue"] = StaticText()
		self.onShown.append(self.blueButton)

	def changedEntry(self):
		if self["config"].getCurrent()[0] == self.softcams_text:
			self.blueButton()

	def blueButton(self):
		if self.softcams.value and self.softcams.value.lower() != "none":
			self["key_blue"].setText(_("Info"))
		else:
			self["key_blue"].setText("")

	def setEcmInfo(self):
		(newEcmFound, ecmInfo) = self.ecminfo.getEcm()
		if newEcmFound:
			self["info"].setText("".join(ecmInfo))

	def ppanelShortcut(self):
		ppanelFileName = '/etc/ppanels/' + self.softcams.value + '.xml'
		if "oscam" in self.softcams.value.lower() and os.path.isfile(resolveFilename(SCOPE_PLUGINS, 'Extensions/OscamStatus/plugin.pyc')):
			from Plugins.Extensions.OscamStatus.plugin import OscamStatus
			self.session.open(OscamStatus)
		elif "oscam" or "ncam" in self.softcams.value.lower() and os.path.isfile('/usr/lib/enigma2/python/Screens/OScamInfo.pyc'):
			self.session.open(OSCamInfo)
		elif "cccam" in self.softcams.value.lower() and os.path.isfile(resolveFilename(SCOPE_PLUGINS, 'Extensions/CCcamInfo/plugin.pyc')):
			from Plugins.Extensions.CCcamInfo.plugin import CCcamInfoMain
			self.session.open(CCcamInfoMain)
		elif os.path.isfile(ppanelFileName) and os.path.isfile(resolveFilename(SCOPE_PLUGINS, 'Extensions/PPanel/plugin.pyc')):
			from Plugins.Extensions.PPanel.ppanel import PPanel
			self.session.open(PPanel, name=self.softcams.value + ' PPanel', node=None, filename=ppanelFileName, deletenode=None)
		else:
			return 0

	def restart(self, what):
		self.what = what
		if "s" in what:
			if "c" in what:
				msg = _("Please wait, restarting softcam and cardserver.")
			else:
				msg = _("Please wait, restarting softcam.")
		elif "c" in what:
			msg = _("Please wait, restarting cardserver.")
		self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doStop)
		self.activityTimer.start(100, False)

	def doStop(self):
		self.activityTimer.stop()
		if "c" in self.what:
			self.cardserver.command('stop')
		if "s" in self.what:
			self.softcam.command('stop')
		self.oldref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		self.session.nav.stopService()
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doStart)
		self.activityTimer.start(1000, False)

	def doStart(self):
		self.activityTimer.stop()
		del self.activityTimer
		if "c" in self.what:
			self.cardserver.select(self.cardservers.value)
			self.cardserver.command('start')
		if "s" in self.what:
			self.softcam.select(self.softcams.value)
			self.softcam.command('start')
		if self.mbox:
			self.mbox.close()
		self.close()
		self.session.nav.playService(self.oldref, adjust=False)

	def restartCardServer(self):
		if hasattr(self, 'cardservers'):
			self.restart("c")

	def restartSoftcam(self):
		self.restart("s")

	def save(self):
		what = ''
		if hasattr(self, 'cardservers') and (self.cardservers.value != self.cardserver.current()):
			what = 'sc'
		elif self.softcams.value != self.softcam.current():
			what = 's'
		if what:
			self.restart(what)
		else:
			self.close()

	def cancel(self):
		self.close()


class CamSetupHelper:
	def getOrbPos(self, sref):
		orbpos = 0
		orbposText = ""
		try:
			orbpos = int(sref.split(":")[6], 16) >> 16
			if 1 <= orbpos <= 3600:
				if orbpos > 1800:  # West.
					orbpos = 3600 - orbpos
					direction = _("W")
				else:
					direction = _("E")
				orbposText = "%d.%d %s%s" % (orbpos / 10, orbpos % 10, "\u00B0", direction)
		except:
			pass
		return orbpos, orbposText

	def sortService(self, item):
		return (item[3], item[0].lower() if item and item[0] and ord(item[0].lower()[0]) in range(97, 123) else f"zzzzz{item[0].lower()}")


class StreamRelaySetup(Setup, CamSetupHelper):
	def __init__(self, session):
		self.serviceitems = []
		self.services = streamrelay.data.copy()
		Setup.__init__(self, session=session, setup="StreamRelay")
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText()
		self["addActions"] = HelpableActionMap(self, ["ColorActions"], {
			"yellow": (self.keyAddService, _("Play service with Stream Relay"))
		}, prio=0, description=_("Stream Relay Setup Actions"))
		self["removeActions"] = HelpableActionMap(self, ["ColorActions"], {
			"blue": (self.keyRemoveService, _("Play service without Stream Relay"))
		}, prio=0, description=_("Stream Relay Setup Actions"))
		self["removeActions"].setEnabled(False)

	def layoutFinished(self):
		Setup.layoutFinished(self)
		self.createItems()

	def createItems(self):
		self.serviceitems = []
		for serviceref in self.services:
			service = ServiceReference(serviceref)
			orbPos, orbPosText = self.getOrbPos(serviceref)
			self.serviceitems.append((f"{service and service.getServiceName() or serviceref} / {orbPosText}", NoSave(ConfigNothing()), serviceref, orbPos))
		if self.serviceitems:
			self.serviceitems.sort(key=self.sortService)
			self.serviceitems.insert(0, ("**************************",))
		self.createSetup()

	def createSetup(self):  # NOSONAR silence S2638
		Setup.createSetup(self, appendItems=self.serviceitems)

	def selectionChanged(self):
		self.updateButtons()
		Setup.selectionChanged(self)

	def updateButtons(self):
		if self.services and isinstance(self.getCurrentItem(), ConfigNothing):
			self["removeActions"].setEnabled(True)
			self["key_blue"].setText(_("Remove"))
		else:
			self["removeActions"].setEnabled(False)
			self["key_blue"].setText("")
		self["key_yellow"].setText(_("Add service"))

	def keySelect(self):
		if not isinstance(self.getCurrentItem(), ConfigNothing):
			Setup.keySelect(self)

	def keyMenu(self):
		if not isinstance(self.getCurrentItem(), ConfigNothing):
			Setup.keyMenu(self)

	def keyRemoveService(self):
		currentItem = self.getCurrentItem()
		if currentItem:
			serviceref = self["config"].getCurrent()[2]
			self.services.remove(serviceref)
			index = self["config"].getCurrentIndex()
			self.createItems()
			self["config"].setCurrentIndex(index)

	def keyAddService(self):
		def keyAddServiceCallback(*result):
			if result:
				service = ServiceReference(result[0])
				serviceref = service.ref.toCompareString()
				if serviceref not in self.services:
					self.services.append(serviceref)
					self.createItems()
					self["config"].setCurrentIndex(2)

		from Screens.ChannelSelection import SimpleChannelSelection  # This must be here to avoid a boot loop!
		self.session.openWithCallback(keyAddServiceCallback, SimpleChannelSelection, _("Select"), currentBouquet=False)

	def keySave(self):
		if streamrelay.data != self.services:
			streamrelay.data = self.services
		streamrelay.data = self.services
		Setup.keySave(self)
