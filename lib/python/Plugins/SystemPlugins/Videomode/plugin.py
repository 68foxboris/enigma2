from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.SystemInfo import BoxInfo
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigBoolean, ConfigNothing
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Tools.Directories import isPluginInstalled

from Plugins.SystemPlugins.Videomode.VideoHardware import video_hw

config.misc.videowizardenabled = ConfigBoolean(default=True)


class VideoSetup(ConfigListScreen, Screen):

	def __init__(self, session, hw):
		Screen.__init__(self, session)
		# for the skin: first try VideoSetup, then Setup, this allows individual skinning
		self.skinName = ["VideoSetup", "Setup"]
		self.setTitle(_("A/V settings"))
		self.hw = hw
		self.onChangedEntry = []

		# handle hotplug by re-creating setup
		self.onShow.append(self.startHotplug)
		self.onHide.append(self.stopHotplug)

		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session)

		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["SetupActions", "MenuActions"],
			{
				"cancel": self.keyCancel,
				"save": self.apply,
				"menu": self.closeRecursive,
				"left": self.keyLeft,
				"right": self.keyRight
			}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["description"] = Label("")

		self.createSetup()
		self.grabLastGoodMode()

	def startHotplug(self):
		self.hw.on_hotplug.append(self.createSetup)

	def stopHotplug(self):
		self.hw.on_hotplug.remove(self.createSetup)

	def createSetup(self):
		level = config.usage.setup_level.index

		self.list = [
			(_("Video output"), config.av.videoport, _("Configures which video output connector will be used."))
		]

		# if we have modes for this port:
		if config.av.videoport.value in config.av.videomode:
			# add mode- and rate-selection:
			self.list.append((pgettext("Video output mode", "Mode"), config.av.videomode[config.av.videoport.value], _("Set the video output mode (or resolution).\n\nWARNING: If the chosen video mode causes a loss of signal on your video port, long press EXIT button.")))
			if config.av.videomode[config.av.videoport.value].value == 'PC':
				self.list.append((_("Resolution"), config.av.videorate[config.av.videomode[config.av.videoport.value].value], _("Configure the screen resolution in PC output mode.")))
			else:
				self.list.append((_("Refresh rate"), config.av.videorate[config.av.videomode[config.av.videoport.value].value], _("Configure the refresh rate of the screen.")))

		self.list.append((_("Aspect ratio"), config.av.aspect, _("Configure the aspect ratio of the screen.")))
		self.list.append((_("Display 4:3 content as"), config.av.policy_43, _("When the content has an aspect ratio of 4:3, choose whether to scale/stretch the picture.")))
		try:
			if hasattr(config.av, 'policy_169'):
				self.list.append((_("Display 16:9 content as"), config.av.policy_169, _("When the content has an aspect ratio of 16:9, choose whether to scale/stretch the picture.")))
		except:
			pass

		self.list.append((_("Force frame"), config.av.force, _("Allow forcing the frames per second.")))

		if config.av.videoport.value == "HDMI":
			if level >= 1:
				self.list.append((_("Allow unsupported modes"), config.av.edid_override, _("When selected this allows video modes to be selected even if they are not reported as supported.")))
				if BoxInfo.getItem("HasBypassEdidChecking"):
					self.list.append((_("Bypass HDMI EDID checking"), config.av.bypass_edid_checking, _("Configure if the HDMI EDID checking should be bypassed as this might solve issue with some TVs.")))
				if BoxInfo.getItem("HasColorspace"):
					self.list.append((_("HDMI Colorspace"), config.av.hdmicolorspace, _("This option allows you to configure the Colorspace from Auto to RGB")))
				if BoxInfo.getItem("HasColordepth"):
					self.list.append((_("HDMI Colordepth"), config.av.hdmicolordepth, _("This option allows you to configure the Colordepth for UHD")))
				if BoxInfo.getItem("HasColorimetry"):
					self.list.append((_("HDMI Colorimetry"), config.av.hdmicolorimetry, _("This option allows you to configure the Colorimetry for HDR.")))
				if BoxInfo.getItem("HasHdrType"):
					self.list.append((_("HDMI HDR Type"), config.av.hdmihdrtype, _("This option allows you to configure the HDR type.")))
				if BoxInfo.getItem("HasHDMIpreemphasis"):
					self.list.append((_("Use HDMI pre-emphasis"), config.av.hdmipreemphasis, _("This option can be useful for long HDMI cables.")))
				if BoxInfo.getItem("HDRSupport"):
					self.list.append((_("HLG support"), config.av.hlg_support, _("This option allows you to force the HLG modes for UHD")))
					self.list.append((_("HDR10 support"), config.av.hdr10_support, _("This option allows you to force the HDR10 modes for UHD")))
					self.list.append((_("Allow 12bit"), config.av.allow_12bit, _("This option allows you to enable or disable the 12 bit color mode")))
					self.list.append((_("Allow 10bit"), config.av.allow_10bit, _("This option allows you to enable or disable the 10 bit color mode")))
				if BoxInfo.getItem("AmlHDRSupport"):
					self.list.append((_("Amlogic HLG Support"), config.av.amlhlg_support, _("This option allows you to force the HLG modes for UHD")))
					self.list.append((_("Amlogic HDR10 Support"), config.av.amlhdr10_support, _("This option allows you to force the HDR10 modes for UHD")))
				if BoxInfo.getItem("CanSyncMode"):
					self.list.append((_("Video sync mode"), config.av.sync_mode, _("This option allows you to use video sync mode.")))

		if config.av.videoport.value == "Scart":
			self.list.append((_("Scart Color format"), config.av.colorformat, _("Configure which color format should be used on the SCART output.")))
			if level >= 1:
				self.list.append((_("WSS on 4:3"), config.av.wss, _("When enabled, content with an aspect ratio of 4:3 will be stretched to fit the screen.")))
				if BoxInfo.getItem("ScartSwitch"):
					self.list.append((_("Auto scart switching"), config.av.vcrswitch, _("When enabled, your receiver will detect activity on the VCR SCART input.")))

		if level >= 1:
			self.list.append((_("Audio volume step size"), config.av.volume_stepsize, _("Configure the general audio volume step size (limit 1-10).")))
			if BoxInfo.getItem("CanDownmixAC3"):
				self.list.append((_("AC3 downmix"), config.av.downmix_ac3, _("Configure whether multi channel sound tracks should be downmixed to stereo.")))
			if BoxInfo.getItem("CanAC3PlusTranscode"):
				self.list.append((_("AC3+ transcoding"), config.av.transcodeac3plus, _("Choose whether AC3 Plus sound tracks should be transcoded to AC3.")))
			if BoxInfo.getItem("CanDownmixDTS"):
				self.list.append((_("DTS downmix"), config.av.downmix_dts, _("Configure whether multi channel sound tracks should be downmixed to stereo.")))
			if BoxInfo.getItem("CanDTSHD"):
				self.list.append((_("DTS-HD HR/DTS-HD MA/DTS"), config.av.dtshd, _("Choose whether DTS channel sound tracks should be downmixed or transcoded.")))
			if BoxInfo.getItem("CanWMAPRO"):
				self.list.append((_("WMA Pro downmix"), config.av.wmapro, _("Choose whether WMA Pro channel sound tracks should be downmixed or transcoded.")))
			if BoxInfo.getItem("CanDownmixAAC"):
				self.list.append((_("AAC downmix"), config.av.downmix_aac, _("Configure whether multi channel sound tracks should be downmixed to stereo.")))
			if BoxInfo.getItem("CanDownmixAACPlus"):
				self.list.append((_("AAC+ downmix"), config.av.downmix_aacplus, _("Configure whether multi channel sound tracks should be downmixed to stereo.")))
			if BoxInfo.getItem("HDMIAudioSource"):
				self.list.append((_("Audio Source"), config.av.hdmi_audio_source, _("Choose whether multi channel sound tracks should be convert to PCM or SPDIF.")))
			if BoxInfo.getItem("CanAACTranscode"):
				self.list.append((_("AAC transcoding"), config.av.transcodeaac, _("Choose whether AAC sound tracks should be transcoded.")))
			self.list.extend((
				(_("General AC3 delay"), config.av.generalAC3delay, _("Configure the general audio delay of Dolby Digital sound tracks.")),
				(_("General PCM delay"), config.av.generalPCMdelay, _("Configure the general audio delay of stereo sound tracks."))
			))
			if BoxInfo.getItem("HasMultichannelPCM"):
				self.list.append((_("Multichannel PCM"), config.av.multichannel_pcm, _("Configure whether multi channel PCM sound should be enabled.")))
			if BoxInfo.getItem("HasAutoVolumeLevel"):
				self.list.append((_("Audio auto volume level"), config.av.autovolumelevel, _("This option allows you can to set the auto volume level.")))
			if BoxInfo.getItem("Has3DSurround"):
				self.list.append((_("3D surround"), config.av.surround_3d, _("This option allows you to enable 3D surround sound.")))
				if BoxInfo.getItem("Has3DSpeaker") and config.av.surround_3d.value != "none":
					self.list.append((_("3D surround speaker position"), config.av.speaker_3d, _("This option allows you to change the virtuell loadspeaker position.")))
				elif BoxInfo.getItem("Has3DSurroundSpeaker"):
					self.list.append((_("3D surround speaker position on or off"), config.av.surround_3d_speaker, _("This option allows you to disable or change the virtuell loadspeaker position.")))
				elif BoxInfo.getItem("Has3DSurroundSoftLimiter") and config.av.surround_3d_speaker.value != "disabled":
					self.list.append((_("3D surround softlimiter"), config.av.surround_softlimiter_3d, _("This option allows you to enable 3D surround softlimiter.")))
			if BoxInfo.getItem("CanAudioDelay"):
				self.list.append((_("General audio delay"), config.av.audiodelay, _("This option configures the general audio delay.")))
			if BoxInfo.getItem("CanBTAudio"):
				self.list.append((_("Enable BT audio"), config.av.btaudio, _("This option allows you to switch audio to bluetooth speakers.")))
				if BoxInfo.getItem("CanBTAudioDelay") and config.av.btaudio.value != "off":
					self.list.append(getConfigListEntry(_("General bluetooth audio delay"), config.av.btaudiodelay, _("This option configures the general audio delay for bluetooth speakers.")))

		if BoxInfo.getItem("CanChangeOsdAlpha"):
			self.list.append((_("OSD transparency"), config.av.osd_alpha, _("Configure the transparency of the OSD.")))
			self.list.append((_("Teletext base visibility"), config.osd.alpha_teletext, _("Base transparency for teletext, more options available within teletext screen.")))
		if BoxInfo.getItem("CanChangeOsdPlaneAlpha"):
			self.list.append((_("OSD plane transparency"), config.av.osd_planealpha, _("Configure the transparency of the OSD.")))

		if not isinstance(config.av.scaler_sharpness, ConfigNothing) and not isPluginInstalled("VideoEnhancement"):
			self.list.append((_("Scaler sharpness"), config.av.scaler_sharpness, _("Configure the sharpness of the video scaling.")))

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def confirm(self, confirmed):
		if not confirmed:
			config.av.videoport.value = self.last_good[0]
			config.av.videomode[self.last_good[0]].value = self.last_good[1]
			config.av.videorate[self.last_good[1]].value = self.last_good[2]
			self.hw.setMode(*self.last_good)
		else:
			self.keySave()

	def grabLastGoodMode(self):
		port = config.av.videoport.value
		mode = config.av.videomode[port].value
		rate = config.av.videorate[mode].value
		self.last_good = (port, mode, rate)

	def apply(self):
		port = config.av.videoport.value
		mode = config.av.videomode[port].value
		rate = config.av.videorate[mode].value
		if (port, mode, rate) != self.last_good:
			self.hw.setMode(port, mode, rate)
			from Screens.MessageBox import MessageBox
			self.session.openWithCallback(self.confirm, MessageBox, _("Is this video mode ok?"), MessageBox.TYPE_YESNO, timeout=20, default=False)
		else:
			self.keySave()


class VideomodeHotplug:
	def __init__(self, hw):
		self.hw = hw

	def start(self):
		self.hw.on_hotplug.append(self.hotplug)

	def stop(self):
		self.hw.on_hotplug.remove(self.hotplug)

	def hotplug(self, what):
		print("[Videomode] hotplug detected on port '%s'" % (what))
		port = config.av.videoport.value
		mode = config.av.videomode[port].value
		rate = config.av.videorate[mode].value

		if not self.hw.isModeAvailable(port, mode, rate):
			print("[Videomode] mode %s/%s/%s went away!" % (port, mode, rate))
			modelist = self.hw.getModeList(port)
			if not len(modelist):
				print("[Videomode] sorry, no other mode is available (unplug?). Doing nothing.")
				return
			mode = modelist[0][0]
			rate = modelist[0][1]
			print("[Videomode] setting %s/%s/%s" % (port, mode, rate))
			self.hw.setMode(port, mode, rate)


hotplug = None


def startHotplug():
	global hotplug, video_hw
	hotplug = VideomodeHotplug(video_hw)
	hotplug.start()


def stopHotplug():
	global hotplug
	hotplug.stop()


def autostart(reason, session=None, **kwargs):
	if session is not None:
		global my_global_session
		my_global_session = session
		return

	if reason == 0:
		startHotplug()
	elif reason == 1:
		stopHotplug()


def videoSetupMain(session, **kwargs):
	session.open(VideoSetup, video_hw)


def startSetup(menuid):
	if menuid != "video":
		return []

	return [(_("A/V settings"), videoSetupMain, "av_setup", 40)]


def VideoWizard(*args, **kwargs):
	from Plugins.SystemPlugins.Videomode.VideoWizard import VideoWizard
	return VideoWizard(*args, **kwargs)


def Plugins(**kwargs):
	list = [
		# PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart),
		PluginDescriptor(name=_("Video setup"), description=_("Advanced video setup"), where=PluginDescriptor.WHERE_MENU, needsRestart=False, fnc=startSetup)
	]
	if config.misc.videowizardenabled.value:
		list.append(PluginDescriptor(name=_("Video wizard"), where=PluginDescriptor.WHERE_WIZARD, needsRestart=False, fnc=(20, VideoWizard)))
	return list
