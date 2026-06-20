# -*- coding: utf-8 -*-
from enigma import eAVControl, getDesktop
from Components.config import config, ConfigSlider, ConfigSelection, ConfigSubDict, ConfigInteger, ConfigYesNo, ConfigEnableDisable, ConfigOnOff, ConfigSubsection, ConfigSelectionNumber, ConfigBoolean, ConfigNothing, NoSave
from Components.SystemInfo import BoxInfo
from Components.Console import Console
from Tools.CList import CList
from Tools.Directories import fileExists, fileReadLine, fileWriteLine
from os import system
from os.path import isfile

MODULE_NAME = __name__.split(".")[-1]

model = BoxInfo.getItem("model")
AMLOGIC = BoxInfo.getItem("AmlogicFamily")
has_dvi = BoxInfo.getItem("DreamBoxDVI")
has_scart = BoxInfo.getItem("HasScart")
has_yuv = BoxInfo.getItem("yuv")
has_rca = BoxInfo.getItem("rca")
has_avjack = BoxInfo.getItem("avjack")

# The "VideoHardware" is the interface to /proc/stb/video.
# It generates hotplug events, and gives you the list of
# available and preferred modes, as well as handling the currently
# selected mode. No other strict checking is done.

config.av.edid_override = ConfigYesNo(default=False)


class VideoHardware:
	axis = {
		"480i": "0 0 719 479",
		"480p": "0 0 719 479",
		"576i": "0 0 719 575",
		"576p": "0 0 719 575",
		"720p": "0 0 1279 719",
		"1080i": "0 0 1919 1079",
		"1080p": "0 0 1919 1079",
		"2160p30": "0 0 3839 2159",
		"2160p": "0 0 3839 2159",
		"smpte": "0 0 4095 2159"
	}
	rates = {}  # High-level, use selectable modes.
	rates["PAL"] = {
		"50Hz": {50: "pal"},
		"60Hz": {60: "pal60"},
		"multi": {50: "pal", 60: "pal60"}
	}
	rates["NTSC"] = {
		"60Hz": {60: "ntsc"}
	}
	rates["Multi"] = {
		"multi": {50: "pal", 60: "ntsc"}
	}
	rates["480i"] = {"60Hz": {60: "480i"}}
	rates["576i"] = {"50Hz": {50: "576i"}}
	rates["480p"] = {"60Hz": {60: "480p"}}
	rates["576p"] = {"50Hz": {50: "576p"}}
	rates["720p"] = {
		"50Hz": {50: "720p50"},
		"60Hz": {60: "720p"},
		"multi": {50: "720p50", 60: "720p"},
		"auto": {50: "720p50", 60: "720p", 24: "720p24"}
	}
	rates["1080i"] = {
		"50Hz": {50: "1080i50"},
		"60Hz": {60: "1080i"},
		"multi": {50: "1080i50", 60: "1080i"},
		"auto": {50: "1080i50", 60: "1080i", 24: "1080i24"}
	}
	rates["1080p"] = {
		"50Hz": {50: "1080p50"},
		"60Hz": {60: "1080p"},
		"30Hz": {30: "1080p30"},
		"25Hz": {25: "1080p25"},
		"24Hz": {24: "1080p24"},
		"multi": {50: "1080p50", 60: "1080p"},
		"auto": {50: "1080p50", 60: "1080p", 24: "1080p24"}
	}
	rates["2160p"] = {
		"50Hz": {50: "2160p50"},
		"60Hz": {60: "2160p"},
		"30Hz": {30: "2160p30"},
		"25Hz": {25: "2160p25"},
		"24Hz": {24: "2160p24"},
		"multi": {50: "2160p50", 60: "2160p"},
		"auto": {50: "2160p50", 60: "2160p", 24: "2160p24"}
	}
	rates["2160p30"] = {
		"25Hz": {50: "2160p25"},
		"30Hz": {60: "2160p30"},
		"multi": {50: "2160p25", 60: "2160p30"},
		"auto": {50: "2160p25", 60: "2160p30", 24: "2160p24"}
	}
	rates["smpte"] = {
		"50Hz": {50: "smpte50"},
		"60Hz": {60: "smpte60"},
		"30Hz": {30: "smpte30"},
		"25Hz": {25: "smpte25"},
		"24Hz": {24: "smpte24"},
		"auto": {60: "smpte60"}
	}
	rates["PC"] = {
		"1024x768": {60: "1024x768"},
		"800x600": {60: "800x600"},  # also not possible
		"720x480": {60: "720x480"},
		"720x576": {60: "720x576"},
		"1280x720": {60: "1280x720"},
		"1280x720 multi": {50: "1280x720_50", 60: "1280x720"},
		"1920x1080": {60: "1920x1080"},
		"1920x1080 multi": {50: "1920x1080", 60: "1920x1080_50"},
		"1280x1024": {60: "1280x1024"},
		"1366x768": {60: "1366x768"},
		"1366x768 multi": {50: "1366x768", 60: "1366x768_50"},
		"1280x768": {60: "1280x768"},
		"640x480": {60: "640x480"}
	}
	modes = {}  # A list of (high-level) modes for a certain port.
	modes["Scart"] = [
		"PAL",
		"NTSC",
		"Multi"
	]
	modes["HDMI"] = ["720p", "1080p", "smpte", "2160p30", "2160p", "1080i", "576p", "576i", "480p", "480i"]
	modes["YPbPr"] = modes["HDMI"]
	if BoxInfo.getItem("scartyuv", False):
		modes["Scart-YPbPr"] = modes["HDMI"]
	if "YPbPr" in modes and not BoxInfo.getItem("yuv", False):
		del modes["YPbPr"]
	if "Scart" in modes and not BoxInfo.getItem("scart", False) and not BoxInfo.getItem("rca", False) and not BoxInfo.getItem("avjack", False):
		del modes["Scart"]

	widescreenModes = tuple([x for x in modes["HDMI"] if x not in ("576p", "576i", "480p", "480i")])
	letterbox = _("Letterbox")
	ASPECT_SWITCH_MSG = (_("16:9 reset to normal"),
		f"1.85:1 {letterbox}",
		f"2.00:1 {letterbox}",
		f"2.21:1 {letterbox}",
		f"2.35:1 {letterbox}"
	)

	def getOutputAspect(self):
		ret = (16, 9)
		port = config.av.videoport.value
		if port not in config.av.videomode:
			print("[VideoHardware] Current port not available in getOutputAspect!!! force 16:9")
		else:
			mode = config.av.videomode[port].value
			force_widescreen = self.isWidescreenMode(port, mode)
			is_widescreen = force_widescreen or config.av.aspect.value in ("16_9", "16_10")
			is_auto = config.av.aspect.value == "auto"
			if is_widescreen:
				if force_widescreen:
					pass
				else:
					aspect = {"16_9": "16:9", "16_10": "16:10"}[config.av.aspect.value]
					if aspect == "16:10":
						ret = (16, 10)
			elif is_auto:
				if isfile("/proc/stb/vmpeg/0/aspect"):
					try:
						aspect_str = open("/proc/stb/vmpeg/0/aspect", "r").read()
					except IOError:
						print("[VideoHardware] Read /proc/stb/vmpeg/0/aspect failed!")
				elif isfile("/sys/class/video/screen_mode"):
					try:
						aspect_str = open("/sys/class/video/screen_mode", "r").read()
					except IOError:
						print("[VideoHardware] Read /sys/class/video/screen_mode failed!")
				if aspect_str == "1":  # 4:3
					ret = (4, 3)
			else:  # 4:3
				ret = (4, 3)
		return ret

	def __init__(self):
		self.last_modes_preferred = []
		self.on_hotplug = CList()
		self.current_mode = None
		self.current_port = None
		print(f"[AVSwitch] getAvailableModes: '{eAVControl.getInstance().getAvailableModes()}'.")
		self.is24hzAvailable()
		self.readPreferredModes()
		self.createConfig()

	def readAvailableModes(self):
		modes = eAVControl.getInstance().getAvailableModes()
		return modes.split()

	def is24hzAvailable(self):
		BoxInfo.setItem("Has24hz", eAVControl.getInstance().has24hz())

	def readPreferredModes(self, saveMode=False, readOnly=False):
		modes = ""
		if config.av.edid_override.value is False:
			modes = eAVControl.getInstance().getPreferredModes(1)
			if saveMode:
				modes = modes.split()
				return modes if len(modes) > 1 else []

			print(f"[AVSwitch] getPreferredModes: '{modes}'.")
			seen = set()
			self.modes_preferred = [m for m in modes.split() if 'x' not in m and not (m in seen or seen.add(m))]  # Remove duplicates and modes with 'x' in the name, which are not real modes.
		if len(modes) < 2:
			self.modes_preferred = self.readAvailableModes()
			print(f"[AVSwitch] Used default modes: {self.modes_preferred}.")
		if len(self.modes_preferred) <= 2:
			print(f"[AVSwitch] Preferend modes not okay, possible driver failer, length={len(self.modes_preferred)}.")
			self.modes_preferred = self.readAvailableModes()
		if readOnly:
			return self.modes_preferred
		if self.modes_preferred != self.last_modes_preferred:
			self.last_modes_preferred = self.modes_preferred
			self.on_hotplug("HDMI")  # must be HDMI

	def getWindowsAxis(self):
		port = getattr(config.av.videoport, "value", None)
		mode = None
		if port and port in config.av.videomode:
			mode = config.av.videomode[port].value
		elif "HDMI" in config.av.videomode:
			port = "HDMI"
			mode = config.av.videomode[port].value
		else:
			for fallbackPort in config.av.videomode.keys():
				port = fallbackPort
				mode = config.av.videomode[fallbackPort].value
				break

		if eAVControl.getInstance().hasVideoAxis():
			return eAVControl.getInstance().getVideoAxis(mode or "720p")

		if mode not in self.axis:
			print(f"[AVSwitch] getWindowsAxis: Missing port/mode mapping for port='{port}', mode='{mode}', fallback to 720p.")
			mode = "720p"

		return self.axis.get(mode, self.axis["720p"])

	def createConfig(self, *args):
		config.av.videomode = ConfigSubDict()
		config.av.videorate = ConfigSubDict()
		portList = []  # Create list of output ports.
		for port in self.getPortList():
			if "HDMI" in port:
				portList.insert(0, (port, port))
			else:
				portList.append((port, port))
			modes = self.getModeList(port)
			if len(modes):
				config.av.videomode[port] = ConfigSelection(choices=[mode for (mode, rates) in modes])
			for (mode, rates) in modes:
				rateList = []
				for rate in rates:
					if rate == "auto" and not BoxInfo.getItem("Has24hz"):
						continue
					rateList.append((rate, rate))
				config.av.videorate[mode] = ConfigSelection(choices=rateList)
		config.av.videoport = ConfigSelection(choices=portList)
		config.av.aspectswitch = ConfigSubsection()
		config.av.aspectswitch.enabled = ConfigYesNo(default=False)
		defaults = (  # The preset values for the offset heights.
			0,
			62,  # 1.85:1
			100,  # 2.00:1
			144,  # 2.21:1
			170  # 2.35:1
		)
		config.av.aspectswitch.offsets = ConfigSubDict()
		for aspect in range(5):
			config.av.aspectswitch.offsets[str(aspect)] = ConfigInteger(default=defaults[aspect], limits=(0, 170))

	def isPortAvailable(self, port):  # Fix me!
		return True

	def isModeAvailable(self, port, mode, rate, availableModes):  # Check if a high-level mode with a given rate is available.
		rate = self.rates[mode][rate]
		for mode in rate.values():
			if port != "HDMI":
				if mode not in availableModes:
					return False
			elif mode not in availableModes or mode not in self.modes_preferred:
				return False
		return True

	def isPortUsed(self, port):
		if port == "HDMI":
			self.readPreferredModes()
			return len(self.modes_preferred) != 0
		else:
			return True

	def isWidescreenMode(self, port, mode):  # This is only used in getOutputAspect.
		return mode in self.widescreenModes

	def getAspectRatioSetting(self):  # TODO AML.  What needs to be done here?
		return {
			"4_3_letterbox": 0,
			"4_3_panscan": 1,
			"16_9": 2,
			"16_9_always": 3,
			"16_10_letterbox": 4,
			"16_10_panscan": 5,
			"16_9_letterbox": 6
		}.get(config.av.aspectratio.value, config.av.aspectratio.value)

	def getFramebufferScale(self):
		return (1, 1)

	def getModeList(self, port):  # Get a list with all modes, with all rates, for a given port.
		results = []
		availableModes = self.readAvailableModes()
		for mode in self.modes[port]:
			rates = [rate for rate in self.rates[mode] if self.isModeAvailable(port, mode, rate, availableModes)]  # List all rates which are completely valid.
			if len(rates):  # If at least one rate is OK then add this mode.
				results.append((mode, rates))
		return results

	def getPortList(self):
		return [port for port in self.modes if self.isPortAvailable(port)]

	def setAspect(self, configElement):
		eAVControl.getInstance().setAspect(configElement.value, 1)

	def setAspectRatio(self, value):
		if value < 100:
			eAVControl.getInstance().setAspectRatio(value)
		else:  # Aspect switcher.
			value -= 100
			offset = config.av.aspectswitch.offsets[str(value)].value
			newTop = offset // 2
			newHeight = 576 - offset
			if value:
				newWidth = 720
			else:
				newTop = 0
				newWidth = 0
				newHeight = 0
			eAVControl.getInstance().setAspectRatio(2)  # 16:9.
			eAVControl.getInstance().setVideoSize(newTop, 0, newWidth, newHeight)

	def setColorFormat(self, value):
		if not self.current_port:
			self.current_port = config.av.videoport.value
		if self.current_port in ("YPbPr", "Scart-YPbPr"):
			eAVControl.getInstance().setColorFormat("yuv")
		elif self.current_port == "RCA":
			eAVControl.getInstance().setColorFormat("cvbs")
		else:
			eAVControl.getInstance().setColorFormat(value)

	def setConfiguredMode(self):
		port = config.av.videoport.value
		if port in config.av.videomode:
			mode = config.av.videomode[port].value
			if mode in config.av.videorate:
				rate = config.av.videorate[mode].value
				self.setMode(port, mode, rate)
			else:
				print("[AVSwitch] Current mode not available, not setting video mode!")
		else:
			print("[AVSwitch] Current port not available, not setting video mode!")

	def setInput(self, input):
		eAVControl.getInstance().setInput(input, 1)

	def setVideoModeDirect(self, mode):
		eAVControl.getInstance().setVideoMode(mode)

	def setMode(self, port, mode, rate, force=None):
		print(f"[AVSwitch] Setting mode for port '{port}', mode '{mode}', rate '{rate}'.")
		modes = self.rates[mode][rate]
		selectedMode = next(iter(modes.values()), mode)
		mode50 = modes.get(50)
		mode60 = modes.get(60)
		mode24 = modes.get(24)
		if mode50 is None or force == 60:
			mode50 = mode60 or selectedMode
		if mode60 is None or force == 50:
			mode60 = mode50
		if mode24 is None or force:
			mode24 = mode60
			if force == 50:
				mode24 = mode50
		eAVControl.getInstance().setVideoModeMulti(mode50, mode60, mode24, 1)
		if eAVControl.getInstance().hasVideoAxis():
			limits = [int(x) for x in eAVControl.getInstance().getVideoAxis(mode).split()]
			config.osd.dst_left.setChoices(default=limits[0], first=limits[0] - 255, last=limits[0] + 255)
			config.osd.dst_top.setChoices(default=limits[1], first=limits[1] - 255, last=limits[1] + 255)
			config.osd.dst_width.setChoices(default=limits[2], first=limits[2] - 255, last=limits[2] + 255)
			config.osd.dst_height.setChoices(default=limits[3], first=limits[3] - 255, last=limits[3] + 255)
			print(f"[AVSwitch] Framebuffer mode '{getDesktop(0).size().width()}', axis '{eAVControl.getInstance().getVideoAxis(mode)}'.")
		self.setColorFormat(config.av.colorformat.value)
		self.current_mode = mode
		self.current_port = port

	def setPolicy43(self, configElement):
		eAVControl.getInstance().setPolicy43(configElement.value, 1)

	def setPolicy169(self, configElement):
		eAVControl.getInstance().setPolicy169(configElement.value, 1)

	def setWss(self, configElement):
		eAVControl.getInstance().setWSS(configElement.value, 1)

	def saveMode(self, port, mode, rate):
		config.av.videoport.value = port
		config.av.videoport.save()
		if port in config.av.videomode:
			config.av.videomode[port].value = mode
			config.av.videomode[port].save()
		if mode in config.av.videorate:
			config.av.videorate[mode].value = rate
			config.av.videorate[mode].save()


	def updateAspect(self, cfgelement):
		port = config.av.videoport.value
		if port not in config.av.videomode:
			print("[VideoHardware] Current port not available, not setting videomode")
			return
		mode = config.av.videomode[port].value
		aspect = config.av.aspect.value

		if not config.av.wss.value:
			wss = "auto(4:3_off)"
		else:
			wss = "auto"

		policy = config.av.policy_43.value
		if hasattr(config.av, "policy_169"):
			policy2 = config.av.policy_169.value
			print("[VideoHardware] -> setting aspect, policy, policy2, wss", aspect, policy, policy2, wss)
		else:
			print("[VideoHardware] -> setting aspect, policy, wss", aspect, policy, wss)


video_hw = VideoHardware()
video_hw.setConfiguredMode()
