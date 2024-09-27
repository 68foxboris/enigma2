from Screens.Screen import Screen
from Screens.Setup import Setup, setupDom
from Screens.InputBox import PinInput
from Screens.MessageBox import MessageBox
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ActionMap import NumberActionMap, HelpableActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigNothing, ConfigSelection, ConfigYesNo, ConfigOnOff
from Components.Label import Label
from Components.Sources.List import List
from Components.Sources.Boolean import Boolean
from Components.SystemInfo import BoxInfo
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Components.Converter.VAudioInfo import StdAudioDesc
from Components.UsageConfig import originalAudioTracks, visuallyImpairedCommentary
from Tools.ISO639 import LanguageCodes
from Tools.Directories import resolveFilename, SCOPE_GUISKIN
from Tools.LoadPixmap import LoadPixmap
from Tools.BoundFunction import boundFunction
from Tools.AVHelper import pChoice

from enigma import iPlayableService, eTimer, eSize, eDVBDB, eServiceReference, eServiceCenter, iServiceInformation

MODEL = BoxInfo.getItem("model")
PLATFORM = BoxInfo.getItem("platform")
DreamBoxAudio = BoxInfo.getItem("DreamBoxAudio")

FOCUS_CONFIG, FOCUS_STREAMS = range(2)
[PAGE_AUDIO, PAGE_SUBTITLES] = ["audio", "subtitles"]

selectionpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_GUISKIN, "icons/audioselectionmark.png"))

def isIPTV(service):
	path = service and service.getPath()
	return path and not path.startswith("/") and service.type in [0x1, 0x1001, 0x138A, 0x1389]


def getConfigMenuItem(configElementName):
	configElement = f"config.subtitles.{configElementName}"
	for item in setupDom().findall(".//item"):
		if item.text == configElement:
			return _(item.attrib["text"]), getattr(config.subtitles, configElementName)  # eval(configElement)
	return "", None


class AudioSelection(ConfigListScreen, Screen):
	def __init__(self, session, infobar=None, page=PAGE_AUDIO):
		Screen.__init__(self, session, enableHelp=True)
		self["streams"] = List([], enableWrapAround=True)
		self["key_red"] = Boolean(False)
		self["key_green"] = Boolean(False)
		self["key_yellow"] = Boolean(True)
		self["key_blue"] = Boolean(False)
		self.protectContextMenu = True
		ConfigListScreen.__init__(self, [])
		self.infobar = infobar or self.session.infobar
		if not hasattr(self.infobar, "selected_subtitle"):
			self.infobar.selected_subtitle = None

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
			iPlayableService.evUpdatedInfo: self.__updatedInfo
		})
		self.cached_subtitle_checked = False
		self.__selected_subtitle = None
		self["actions"] = NumberActionMap(["AudioSelectionActions", "SetupActions", "DirectionActions", "MenuActions", "InfobarAudioSelectionActions", "InfobarSubtitleSelectionActions"], {
			"red": self.keyRed,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"subtitleSelection": self.keyAudioSubtitle,
			"audioSelection": self.keyAudioSubtitle,
			"blue": self.keyBlue,
			"ok": self.keyOk,
			"cancel": self.cancel,
			"up": self.keyUp,
			"down": self.keyDown,
			"menu": self.openAutoLanguageSetup,
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
		}, -2)
		self["help"] = HelpableActionMap(self, ["MenuActions", "InfobarAudioSelectionActions", "InfobarSubtitleSelectionActions"],
			{
			"audioSelectionLong": (self.audioSelectionLong, _("Toggle digital downmix")),
			"subtitleSelection": (self.keyAudioSubtitle, _("Subtitle selection")),
			"menu": (self.openAutoLanguageSetup, _("Automatic Language and Subtitle Setup"))
		}, description=_("Audio and subtitles actions"))
		self.settings = ConfigSubsection()
		choicelist = [
			(PAGE_AUDIO, ""),
			(PAGE_SUBTITLES, "")
		]
		self.settings.menupage = ConfigSelection(choices=choicelist, default=page)
		self.onLayoutFinish.append(self.__layoutFinished)

	def audioSelectionLong(self):
		from Screens.InfoBar import InfoBar
		if InfoBar and InfoBar.instance:
			InfoBar.instance.audioSelectionLong()

	def __layoutFinished(self):
		self["config"].instance.setSelectionEnable(False)
		self.focus = FOCUS_STREAMS
		self.settings.menupage.addNotifier(self.fillList)

	def saveAVDict(self):
		eDVBDB.getInstance().saveIptvServicelist()

	def fillList(self, arg=None):
		streams = []
		conflist = []
		selectedidx = 0
		self.subtitlelist = []
		self["key_red"].setBoolean(False)
		self["key_green"].setBoolean(False)
		self["key_yellow"].setBoolean(False)
		self["key_blue"].setBoolean(False)

		self.subtitlelist = self.getSubtitleList()
		print("[AudiSelection] fillList subtitlelist=%s" % (self.subtitlelist))
		if self.settings.menupage.value == PAGE_AUDIO:
			self.setTitle(_("Select audio track"))
			service = self.session.nav.getCurrentService()
			self.audioTracks = audio = service and service.audioTracks()
			n = audio and audio.getNumberOfTracks() or 0
			if self.subtitlelist:
				conflist.append((_("To subtitle selection"), self.settings.menupage))

			if BoxInfo.getItem("CanDownmixAC3"):
				if DreamBoxAudio:
					choice_list = [
						(pChoice("downmix")),
						(pChoice("passthrough")),
						(pChoice("multichannel")),
						(pChoice("hdmi_best"))
					]
				elif PLATFORM == "dmamlogic":
					choice_list = [
						("0", _("Downmix")),
						("1", _("Passthrough")),
						("2", _("Use best / Controlled by HDMI"))
					]
				else:
					choice_list = [
						(pChoice("downmix")),
						(pChoice("passthrough"))
					]
				self.settings.downmix_ac3 = ConfigSelection(choices=choice_list, default=config.av.downmix_ac3.value)
				self.settings.downmix_ac3.addNotifier(self.changeAC3Downmix, initial_call=False)
				conflist.append((_("AC3 downmix"), self.settings.downmix_ac3, None))

			if BoxInfo.getItem("CanDownmixAAC"):
				if DreamBoxAudio:
					choice_list = [
						(pChoice("downmix")),
						(pChoice("passthrough")),
						(pChoice("multichannel")),
						(pChoice("hdmi_best"))
					]
				elif MODEL == "gbx34k":
					choice_list = [
						(pChoice("downmix")),
						(pChoice("passthrough")),
						(pChoice("multichannel")),
						(pChoice("force_ac3")),
						(pChoice("force_dts")),
						(pChoice("use_hdmi_cacenter")),
						(pChoice("wide")),
						(pChoice("extrawide"))
					]
				else:
					choice_list = [
						(pChoice("downmix")),
						(pChoice("passthrough"))
					]
				self.settings.downmix_aac = ConfigSelection(choices=choice_list, default=config.av.downmix_aac.value)
				self.settings.downmix_aac.addNotifier(self.changeAACDownmix, initial_call=False)
				conflist.append((_("AAC downmix"), self.settings.downmix_aac, None))

			if BoxInfo.getItem("CanDownmixAACPlus"):
				choice_list = [
					(pChoice("downmix")),
					(pChoice("passthrough")),
					(pChoice("multichannel")),
					(pChoice("force_ac3")),
					(pChoice("force_dts")),
					(pChoice("use_hdmi_cacenter")),
					(pChoice("wide")),
					(pChoice("extrawide"))
				]
				self.settings.downmix_aacplus = ConfigSelection(choices=choice_list, default=config.av.downmix_aacplus.value)
				self.settings.downmix_aacplus.addNotifier(self.changeAACDownmixPlus, initial_call=False)
				conflist.append((_("AAC+ downmix"), self.settings.downmix_aacplus, None))

			if BoxInfo.getItem("CanDownmixDTS"):
				choice_list = [
					(pChoice("downmix")),
					(pChoice("passthrough"))
				]
				self.settings.downmix_dts = ConfigSelection(choices=choice_list, default=config.av.downmix_dts.value)
				self.settings.downmix_dts.addNotifier(self.changeDTSDownmix, initial_call=False)
				conflist.append((_("DTS downmix"), self.settings.downmix_dts, None))

			if BoxInfo.getItem("CanDTSHD"):
				if MODEL in ("dm7080", "dm820"):
					choice_list = [
						(pChoice("force_dts")),
						(pChoice("use_hdmi_caps"))
					]
				else:
					choice_list = [
						(pChoice("downmix")),
						(pChoice("force_dts")),
						(pChoice("use_hdmi_caps")),
						(pChoice("multichannel")),
						(pChoice("hdmi_best"))
					]
				self.settings.dtshd = ConfigSelection(choices=choice_list, default=config.av.dtshd.value)
				self.settings.dtshd.addNotifier(self.changeDTSHD, initial_call=False)
				conflist.append((_("DTS-HD HR/DTS-HD MA/DTS"), self.settings.dtshd, None))

			if BoxInfo.getItem("CanAACTranscode"):
				choice_list = [
					(pChoice("off")),
					(pChoice("ac3")),
					(pChoice("dts"))
				]
				self.settings.transcodeaac = ConfigSelection(choices=choice_list, default=config.av.transcodeaac.value)
				self.settings.transcodeaac.addNotifier(self.setAACTranscode, initial_call=False)
				conflist.append((_("AAC transcoding"), self.settings.transcodeaac, None))

			if BoxInfo.getItem("CanAC3PlusTranscode"):
				if DreamBoxAudio:
					choice_list = [
						(pChoice("use_hdmi_caps")),
						(pChoice("force_ac3")),
						(pChoice("multichannel")),
						(pChoice("hdmi_best")),
						(pChoice("force_ddp"))
					]
				elif PLATFORM == "gb7252" or MODEL == "gbx34k":
					choice_list = [
						(pChoice("downmix")),
						(pChoice("passthrough")),
						(pChoice("force_ac3")),
						(pChoice("multichannel")),
						(pChoice("force_dts"))
					]
				else:
					choice_list = [
						(pChoice("use_hdmi_caps")),
						(pChoice("force_ac3"))
					]
				self.settings.transcodeac3plus = ConfigSelection(choices=choice_list, default=config.av.transcodeac3plus.value)
				self.settings.transcodeac3plus.addNotifier(self.setAC3plusTranscode, initial_call=False)
				conflist.append((_("AC3+ transcoding"), self.settings.transcodeac3plus, None))

			if BoxInfo.getItem("CanWMAPRO"):
				choice_list = [
					(pChoice("downmix")),
					(pChoice("passthrough")),
					(pChoice("multichannel")),
					(pChoice("hdmi_best"))
				]
				self.settings.wmapro = ConfigSelection(choices=choice_list, default=config.av.wmapro.value)
				self.settings.wmapro.addNotifier(self.changeWMAPro, initial_call=False)
				conflist.append((_("WMA pro downmix"), self.settings.wmapro, None))

			if BoxInfo.getItem("CanBTAudio"):
				choice_list = [
					(pChoice("off")),
					(pChoice("on"))
				]
				self.settings.btaudio = ConfigSelection(choices=choice_list, default=config.av.btaudio.value)
				self.settings.btaudio.addNotifier(self.changeBTAudio, initial_call=False)
				conflist.append((_("Enable bluetooth audio"), self.settings.btaudio, None))

			if BoxInfo.getItem("Has3DSurround"):
				choice_list = [
					(pChoice("none")),
					(pChoice("hdmi")),
					(pChoice("spdif")),
					(pChoice("dac"))
				]
				self.settings.surround_3d = ConfigSelection(choices=choice_list, default=config.av.surround_3d.value)
				self.settings.surround_3d.addNotifier(self.change3DSurround, initial_call=False)
				conflist.append((_("3D surround"), self.settings.surround_3d, None))

			if BoxInfo.getItem("Has3DSpeaker") and config.av.surround_3d.value != "none":
				choice_list = [
					(pChoice("center")),
					(pChoice("wide")),
					(pChoice("extrawide"))
				]
				self.settings.speaker_3d = ConfigSelection(choices=choice_list, default=config.av.speaker_3d.value)
				self.settings.speaker_3d.addNotifier(self.change3DSpeaker, initial_call=False)
				conflist.append((_("3D surround speaker position"), self.settings.speaker_3d, None))

			if BoxInfo.getItem("Has3DSurroundSpeaker"):
				choice_list = [
					(pChoice("disabled")),
					(pChoice("center")),
					(pChoice("wide")),
					(pChoice("extrawide"))
				]
				self.settings.surround_3d_speaker = ConfigSelection(choices=choice_list, default=config.av.surround_3d_speaker.value)
				self.settings.surround_3d_speaker.addNotifier(self.change3DSurroundSpeaker, initial_call=False)
				conflist.append((_("3D surround speaker position on or off"), self.settings.surround_3d_speaker, None))

			if BoxInfo.getItem("HasAutoVolume"):
				choice_list = [
					(pChoice("none")),
					(pChoice("hdmi")),
					(pChoice("spdif")),
					(pChoice("dac"))
				]
				self.settings.autovolume = ConfigSelection(choices=choice_list, default=config.av.autovolume.value)
				self.settings.autovolume.addNotifier(self.changeAutoVolume, initial_call=False)
				conflist.append((_("Audio auto volume level"), self.settings.autovolume, None))

			if BoxInfo.getItem("HasAutoVolumeLevel"):
				choice_list = [
					(pChoice("disabled")),
					(pChoice("enabled"))
				]
				self.settings.autovolumelevel = ConfigSelection(choices=choice_list, default=config.av.autovolumelevel.value)
				self.settings.autovolumelevel.addNotifier(self.changeAutoVolumeLevel, initial_call=False)
				conflist.append((_("Audio auto volume level"), self.settings.autovolumelevel, None))

			if BoxInfo.getItem("CanPcmMultichannel"):
				if DreamBoxAudio:
					choice_list = [
						(pChoice("downmix")),
						(pChoice("passthrough")),
						(pChoice("multichannel")),
						(pChoice("hdmi_best"))
					]
					self.settings.multichannel_pcm = ConfigSelection(choices=choice_list, default=config.av.multichannel_pcm.value)
				else:
					self.settings.multichannel_pcm = ConfigOnOff(default=config.av.multichannel_pcm.value)
				self.settings.multichannel_pcm.addNotifier(self.changePCMMultichannel, initial_call=False)
				conflist.append((_("PCM multichannel"), self.settings.multichannel_pcm, None))

			if n > 0:
				self.audioChannel = service.audioChannel()
				if self.audioChannel:
					choicelist = [
						("0", _("Left")),
						("1", _("Stereo")),
						("2", _("Right"))
					]
					self.settings.channelmode = ConfigSelection(choices=choicelist, default=str(self.audioChannel.getCurrentChannel()))
					self.settings.channelmode.addNotifier(self.changeMode, initial_call=False)
					conflist.append((_("Audio channel"), self.settings.channelmode, None))
				selectedAudio = self.audioTracks.getCurrentTrack()
				for x in range(n):
					number = str(x + 1)
					i = audio.getTrackInfo(x)
					languages = i.getLanguage().split('/')
					description = StdAudioDesc(i.getDescription())
					selected = ""
					language = ""
					if selectedAudio == x:
						selected = "X"
						selectedidx = x
					cnt = 0
					for lang in languages:
						if cnt:
							language += " / "
						if lang == "":
							language += _("Not defined")
						elif lang in originalAudioTracks:
							language += _("Original language")
						elif lang in LanguageCodes:
							language += _(LanguageCodes[lang][0])
						elif lang in visuallyImpairedCommentary:
							language += _("Narration")
						else:
							language += lang
						cnt += 1
					streams.append((x, "", number, description, language, selected, selectionpng if selected == "X" else None))
			else:
				conflist.append(("",))
			if BoxInfo.getItem("HasBypassEdidChecking"):
				choice_list = [
					("00000000", _("Off")),
					("00000001", _("On"))
				]
				self.settings.bypass_edid_checking = ConfigSelection(choices=choice_list, default=config.av.bypass_edid_checking.value)
				self.settings.bypass_edid_checking.addNotifier(self.changeEDIDChecking, initial_call=False)
				conflist.append((_("Bypass HDMI EDID checking"), self.settings.bypass_edid_checking, None))
			if hasattr(self.infobar, "runPlugin"):
				class PluginCaller:
					def __init__(self, fnc, *args):
						self.fnc = fnc
						self.args = args

					def __call__(self, *args, **kwargs):
						self.fnc(*self.args)

				for item in [(p.name, PluginCaller(self.infobar.runPlugin, p)) for p in plugins.getPlugins(where=PluginDescriptor.WHERE_AUDIOMENU) if p.key != "AudioEffect"]:  # Ignore AudioEffect because it's always Blue button.
					conflist.append(getConfigListEntry(item[0], ConfigNothing(), item[1]))

		elif self.settings.menupage.value == PAGE_SUBTITLES:
			self.setTitle(_("Subtitle selection"))
			idx = 0
			if self.subtitlelist is not None:
				for x in self.subtitlelist:
					number = str(x[1])
					description = "?"
					language = ""
					selected = ""
					if self.selectedSubtitle and x[:4] == self.selectedSubtitle[:4]:
						selected = "X"
						selectedidx = idx
					try:
						if x[4] != "und":
							if x[4] in LanguageCodes:
								language = _(LanguageCodes[x[4]][0])
							else:
								language = x[4]
					except Exception:
						language = ""

					languagetype = ""
					if language and len(x) == 6 and x[5]:
						languagetype = x[5].split()
						if languagetype and len(languagetype) == 2:
							language = "%s (%s)" % (language, languagetype[1])

					if x[0] == 0:
						description = "DVB"
						number = "%x" % (x[1])
					elif x[0] == 1:
						description = "teletext"
						number = "%x%02x" % (x[3] and x[3] or 8, x[2])
					elif x[0] == 2:
						types = (_("unknown"), _("embedded"), _("SSA file"), _("ASS file"), _("SRT file"), _("VOB file"), _("PGS file"))
						try:
							description = types[x[2]]
						except Exception:
							description = _("unknown") + ": %s" % x[2]
						number = str(int(number) + 1)
					streams.append((x, "", number, description, language, selected, selectionpng if selected == "X" else None))
					idx += 1
			conflist.append((_("To audio selection"), self.settings.menupage))

			if self.infobar.selected_subtitle and self.infobar.selected_subtitle != (0, 0, 0, 0) and not ".DVDPlayer'>" not in repr(self.infobar):
				conflist.append((_("Subtitle quickmenu"), ConfigNothing(), None))

		if len(conflist) > 0 and conflist[0][0]:
			self["key_red"].setBoolean(True)
		if len(conflist) > 1 and conflist[1][0]:
			self["key_green"].setBoolean(True)
		if len(conflist) > 2 and conflist[2][0]:
			self["key_yellow"].setBoolean(True)
		if len(conflist) > 3 and conflist[3][0]:
			self["key_blue"].setBoolean(True)
		self["config"].list = conflist
		self["streams"].list = streams
		self["streams"].setIndex(selectedidx)

	def __updatedInfo(self):
		self.fillList()

	def getSubtitleList(self):
		service = self.session.nav.getCurrentService()
		subtitle = service and service.subtitle()
		subtitlelist = subtitle and subtitle.getSubtitleList()
		self.selectedSubtitle = None
		if self.subtitlesEnabled():
			self.selectedSubtitle = self.infobar.selected_subtitle
			if self.selectedSubtitle and self.selectedSubtitle[:4] == (0, 0, 0, 0):
				self.selectedSubtitle = None
			elif subtitlelist is not None and self.selectedSubtitle and not self.selectedSubtitle[:4] in (x[:4] for x in subtitlelist):
				subtitlelist.append(self.selectedSubtitle)
		return subtitlelist

	def subtitlesEnabled(self):
		try:
			return self.infobar.subtitle_window.shown
		except Exception:
			return False

	def enableSubtitle(self, subtitle):
		if self.infobar.selected_subtitle != subtitle:
			self.infobar.enableSubtitle(subtitle)

	def change3DSurround(self, surround_3d):
		if surround_3d.value:
			config.av.surround_3d.value = surround_3d.value
		config.av.surround_3d.save()
		self.fillList()

	def change3DSpeaker(self, speaker_3d):
		if speaker_3d.value:
			config.av.speaker_3d.value = speaker_3d.value
		config.av.speaker_3d.save()

	def change3DSurroundSpeaker(self, surround_3d_speaker):
		if surround_3d_speaker.value:
			config.av.surround_3d_speaker.value = surround_3d_speaker.value
		config.av.surround_3d_speaker.save()

	def changeAutoVolume(self, autovolume):
		if autovolume.value:
			config.av.autovolume.value = autovolume.value
		config.av.autovolume.save()

	def changeAutoVolumeLevel(self, autovolumelevel):
		if autovolumelevel.value:
			config.av.autovolumelevel.value = autovolumelevel.value
		config.av.autovolumelevel.save()

	def changePCMMultichannel(self, multichan):
		if DreamBoxAudio:
			config.av.multichannel_pcm.setValue(multichan.value)
		else:
			if multichan.value:
				config.av.multichannel_pcm.setValue(True)
			else:
				config.av.multichannel_pcm.setValue(False)
		config.av.multichannel_pcm.save()
		self.fillList()

	def changeAC3Downmix(self, downmix):
		HasMultichannelPCM = BoxInfo.getItem("HasMultichannelPCM")
		if DreamBoxAudio or PLATFORM == "dmamlogic":
			config.av.downmix_ac3.setValue(downmix.value)
		else:
			if downmix.value:
				config.av.downmix_ac3.setValue(True)
				if HasMultichannelPCM:
					config.av.multichannel_pcm.setValue(False)
			else:
				config.av.downmix_ac3.setValue(False)
		config.av.downmix_ac3.save()
		if HasMultichannelPCM:
			config.av.multichannel_pcm.save()
		self.fillList()

	def changeDTSDownmix(self, downmix):
		config.av.downmix_dts.setValue(downmix.value)
		config.av.downmix_dts.save()

	def changeDTSHD(self, downmix):
		config.av.dtshd.setValue(downmix.value)
		config.av.dtshd.save()

	def changeAACDownmix(self, downmix):
		if DreamBoxAudio or MODEL == "gbx34k":
			config.av.downmix_aac.setValue(downmix.value)
		else:
			if downmix.value:
				config.av.downmix_aac.setValue(True)
			else:
				config.av.downmix_aac.setValue(False)
		config.av.downmix_aac.save()

	def changeAACDownmixPlus(self, downmix):
		config.av.downmix_aacplus.setValue(downmix.value)
		config.av.downmix_aacplus.save()

	def changeWMAPro(self, downmix):
		config.av.wmapro.setValue(downmix.value)
		config.av.wmapro.save()

	def setAC3plusTranscode(self, transcode):
		config.av.transcodeac3plus.setValue(transcode.value)
		config.av.transcodeac3plus.save()

	def setAACTranscode(self, transcode):
		config.av.transcodeaac.setValue(transcode.value)
		config.av.transcodeaac.save()

	def changeBTAudio(self, btaudio):
		if btaudio.value:
			config.av.btaudio.value = btaudio.value
		config.av.btaudio.save()

	def changeEDIDChecking(self, edidchecking):
		if edidchecking.value:
			config.av.bypass_edid_checking.value = edidchecking.value
		config.av.bypass_edid_checking.save()

	def changeMode(self, mode):
		if mode is not None and self.audioChannel:
			self.audioChannel.selectChannel(int(mode.value))

	def changeAudio(self, audio):
		track = int(audio)
		if isinstance(track, int):
			service = self.session.nav.getCurrentService()
			ref = self.session.nav.getCurrentlyPlayingServiceReference()
			#ref = ref and eServiceReference(ref.toString())
			if service.audioTracks().getNumberOfTracks() > track:
				self.audioTracks.selectTrack(track)
				if isIPTV(ref):
					self.saveAVDict()

	def keyLeft(self):
		if self.focus == FOCUS_CONFIG:
			ConfigListScreen.keyLeft(self)
		elif self.focus == FOCUS_STREAMS:
			self["streams"].setIndex(0)

	def keyRight(self, config=False):
		if config or self.focus == FOCUS_CONFIG:
			index = self["config"].getCurrentIndex()
			if self.settings.menupage.value == PAGE_AUDIO:
				if self.subtitlelist and index == 0:  # Subtitle selection screen
					self.keyAudioSubtitle()
					self.__updatedInfo()
				elif self["config"].getCurrent()[2]:
					self["config"].getCurrent()[2]()
				else:
					ConfigListScreen.keyRight(self)
			elif self.settings.menupage.value == PAGE_SUBTITLES and self.infobar.selected_subtitle and self.infobar.selected_subtitle != (0, 0, 0, 0):
				if index == 0:  # Audio selection screen
					self.keyAudioSubtitle()
					self.__updatedInfo()
				else:
					self.session.open(QuickSubtitlesConfigMenu, self.infobar)  # sub title config screen
			else:
				ConfigListScreen.keyRight(self)
		if self.focus == FOCUS_STREAMS and self["streams"].count() and not config:
			self["streams"].setIndex(self["streams"].count() - 1)

	def keyRed(self):
		if self["key_red"].getBoolean():
			self.colorkey(0)
		else:
			return 0

	def keyGreen(self):
		if self["key_green"].getBoolean():
			self.colorkey(1)
		else:
			return 0

	def keyYellow(self):
		if self["key_yellow"].getBoolean():
			self.colorkey(2)
		else:
			return 0

	def keyBlue(self):
		if self["key_blue"].getBoolean():
			self.colorkey(3)
		else:
			return 0

	def keyAudioSubtitle(self):
		if self.settings.menupage.value == PAGE_AUDIO:
			self.settings.menupage.setValue("subtitles")
		else:
			self.settings.menupage.setValue("audio")

	def colorkey(self, idx):
		self["config"].setCurrentIndex(idx)
		self.keyRight(True)

	def keyUp(self):
		if self.focus == FOCUS_CONFIG:
			self["config"].instance.moveSelection(self["config"].instance.moveUp)
		elif self.focus == FOCUS_STREAMS:
			if self["streams"].getIndex() == 0:
				self["config"].instance.setSelectionEnable(True)
				self["streams"].style = "notselected"
				self["config"].setCurrentIndex(len(self["config"].getList()) - 1)
				self.focus = FOCUS_CONFIG
			else:
				self["streams"].selectPrevious()

	def keyDown(self):
		if self.focus == FOCUS_CONFIG:
			configList = self["config"].getList()
			count = len(configList)
			for x in configList:
				if x[0] == "":
					count -= 1
			if self["config"].getCurrentIndex() < count - 1:
				self["config"].instance.moveSelection(self["config"].instance.moveDown)
			else:
				self["config"].instance.setSelectionEnable(False)
				self["streams"].style = "default"
				self.focus = FOCUS_STREAMS
		elif self.focus == FOCUS_STREAMS:
			self["streams"].selectNext()

	def keyNumberGlobal(self, number):
		if number <= len(self["streams"].list):
			self["streams"].setIndex(number - 1)
			self.keyOk()

	def keyOk(self):
		if self.focus == FOCUS_STREAMS and self["streams"].list:
			cur = self["streams"].getCurrent()
			if self.settings.menupage.value == PAGE_AUDIO and cur[0] is not None:
				self.changeAudio(cur[0])
				self.__updatedInfo()
			ref = self.session.nav.getCurrentlyPlayingServiceReference()
			#ref = ref and eServiceReference(ref.toString())
			if self.settings.menupage.value == PAGE_SUBTITLES and cur[0] is not None:
				if self.infobar.selected_subtitle and self.infobar.selected_subtitle[:4] == cur[0][:4]:
					self.enableSubtitle(None)
					selectedidx = self["streams"].getIndex()
					self.__updatedInfo()
					self["streams"].setIndex(selectedidx)
				else:
					self.enableSubtitle(cur[0][:5])
					self.__updatedInfo()
				if isIPTV(ref):
					self.saveAVDict()
			self.close(0)
		elif self.focus == FOCUS_CONFIG:
			self.keyRight()

	def openAutoLanguageSetup(self):
		if self.protectContextMenu and config.ParentalControl.setuppinactive.value and config.ParentalControl.config_sections.context_menus.value:
			self.session.openWithCallback(self.protectResult, PinInput, pinList=[x.value for x in config.ParentalControl.servicepin], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the correct PIN code"), windowTitle=_("Enter PIN code"))
		else:
			self.protectResult(True)

	def protectResult(self, answer):
		if answer:
			self.session.open(Setup, "AutoLanguage")
			self.protectContextMenu = False
		elif answer is not None:
			self.session.openWithCallback(self.close, MessageBox, _("The PIN code you entered is wrong."), MessageBox.TYPE_ERROR)

	def cancel(self):
		self.close(0)

	def doNothing(self):
		pass


class SubtitleSelection(AudioSelection):
	def __init__(self, session, infobar=None):
		AudioSelection.__init__(self, session, infobar, page=PAGE_SUBTITLES)
		self.skinName = ["AudioSelection"]


class QuickSubtitlesConfigMenu(ConfigListScreen, Screen):
	skin = """
	<screen position="50,50" size="480,305" title="Subtitle settings" backgroundColor="#7f000000" flags="wfNoBorder">
		<widget name="config" position="5,5" size="470,275" font="Regular;18" zPosition="1" transparent="1" selectionPixmap="buttons/sel.png" verticalAlignment="center" />
		<widget name="videofps" position="5,280" size="470,20" backgroundColor="secondBG" transparent="1" zPosition="1" font="Regular;16" verticalAlignment="center" horizontalAlignment="left" foregroundColor="blue"/>
	</screen>"""

	FLAG_CENTER_DVB_SUBS = 2048

	def __init__(self, session, infobar):
		Screen.__init__(self, session)
		self.skin = QuickSubtitlesConfigMenu.skin
		self.infobar = infobar or self.session.infobar
		self.wait = eTimer()
		self.wait.timeout.get().append(self.resyncSubtitles)
		self.resume = eTimer()
		self.resume.timeout.get().append(self.resyncSubtitlesResume)
		self.service = self.session.nav.getCurrentlyPlayingServiceReference()
		servicepath = self.service and self.service.getPath()
		if servicepath and servicepath.startswith("/") and self.service.toString().startswith("1:"):
			info = eServiceCenter.getInstance().info(self.service)
			self.service_string = info and info.getInfoString(self.service, iServiceInformation.sServiceref)
		else:
			self.service_string = self.service.toString()
		self.center_dvb_subs = ConfigYesNo(default=(eDVBDB.getInstance().getFlag(eServiceReference(self.service_string)) & self.FLAG_CENTER_DVB_SUBS) and True)
		self.center_dvb_subs.addNotifier(self.setCenterDvbSubs)
		self["videofps"] = Label("")
		self["key_red"] = Label(_("Exit"))
		self["save"] = Label(_("Save"))

		sub = self.infobar.selected_subtitle
		menu = []
		if sub[0] in (0, 1) and BoxInfo.getItem("AISubs"):
			menu.extend([
				getConfigMenuItem("ai_enabled"),
				getConfigMenuItem("ai_translate_to"),
				getConfigMenuItem("ai_subtitle_colors")
			])
		if sub[0] == 0:  # dvb
			menu.extend([
				getConfigMenuItem("dvb_subtitles_yellow"),
				getConfigMenuItem("dvb_subtitles_backtrans"),
				getConfigMenuItem("dvb_subtitles_original_position"),
				(_("Center DVB subtitles"), self.center_dvb_subs),
				getConfigMenuItem("subtitle_position"),
				getConfigMenuItem("subtitle_bad_timing_delay"),
				getConfigMenuItem("subtitle_noPTSrecordingdelay"),
			])
		elif sub[0] == 1:  # teletext
			menu.extend([
				getConfigMenuItem("ttx_subtitle_colors"),
				getConfigMenuItem("ttx_subtitle_original_position"),
				getConfigMenuItem("subtitle_position"),
				getConfigMenuItem("subtitle_fontsize"),
				getConfigMenuItem("subtitle_rewrap"),
				getConfigMenuItem("subtitle_borderwidth"),
				getConfigMenuItem("subtitles_backtrans"),
				getConfigMenuItem("subtitle_alignment"),
				getConfigMenuItem("subtitle_bad_timing_delay"),
				getConfigMenuItem("subtitle_noPTSrecordingdelay"),
			])
		else: 		# pango
			menu.extend([
				getConfigMenuItem("pango_subtitles_delay"),
				getConfigMenuItem("pango_subtitle_colors"),
				getConfigMenuItem("pango_subtitle_fontswitch"),
				getConfigMenuItem("colourise_dialogs"),
				getConfigMenuItem("subtitle_fontsize"),
				getConfigMenuItem("subtitle_position"),
				getConfigMenuItem("subtitle_alignment"),
				getConfigMenuItem("subtitle_rewrap"),
				getConfigMenuItem("pango_subtitle_removehi"),
				getConfigMenuItem("subtitle_borderwidth"),
				getConfigMenuItem("subtitles_backtrans"),
				getConfigMenuItem("pango_subtitles_fps"),
			])
			self["videofps"].setText(_("Video: %s fps") % (self.getFps().rstrip(".000")))

		ConfigListScreen.__init__(self, menu, self.session, on_change=self.changedEntry)

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"cancel": self.cancel,
			"ok": self.ok,
		}, -2)

		self.onLayoutFinish.append(self.layoutFinished)

	def setCenterDvbSubs(self, configElement):
		if configElement.value:
			eDVBDB.getInstance().addFlag(eServiceReference(self.service_string), self.FLAG_CENTER_DVB_SUBS)
			config.subtitles.dvb_subtitles_centered.value = True
		else:
			eDVBDB.getInstance().removeFlag(eServiceReference(self.service_string), self.FLAG_CENTER_DVB_SUBS)
			config.subtitles.dvb_subtitles_centered.value = False

	def layoutFinished(self):
		if not self["videofps"].text:
			self.instance.resize(eSize(self.instance.size().width(), self["config"].l.getItemSize().height() * len(self["config"].getList()) + 10))

	def changedEntry(self):
		if self["config"].getCurrent() in [getConfigMenuItem("pango_subtitles_delay"), getConfigMenuItem("pango_subtitles_fps")]:
			self.wait.start(500, True)

	def resyncSubtitles(self):
		self.infobar.setSeekState(self.infobar.SEEK_STATE_PAUSE)
		self.resume.start(100, True)

	def resyncSubtitlesResume(self):
		self.infobar.setSeekState(self.infobar.SEEK_STATE_PLAY)

	def getFps(self):
		from enigma import iServiceInformation
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		if not info:
			return ""
		fps = info.getInfo(iServiceInformation.sFrameRate)
		if fps > 0:
			return "%6.3f" % (fps / 1000.)
		return ""

	def cancel(self):
		self.center_dvb_subs.removeNotifier(self.setCenterDvbSubs)
		self.close()

	def ok(self):
		config.subtitles.save()
		self.close()
