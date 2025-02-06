import os
from os.path import isfile
from enigma import eAVControl, eDVBVolumecontrol, getDesktop
from Components.config import config, ConfigSlider, ConfigSelection, ConfigSubDict, ConfigYesNo, ConfigEnableDisable, ConfigOnOff, ConfigSubsection, ConfigSelectionNumber, ConfigBoolean, ConfigNothing, NoSave, ConfigInteger
from Components.About import about, getChipSetNumber
from Components.SystemInfo import BoxInfo
from Tools.CList import CList
from Tools.Directories import fileReadLine, fileWriteLine

MODULE_NAME = __name__.split(".")[-1]
AMLOGIC = BoxInfo.getItem("AmlogicFamily")
MODEL = BoxInfo.getItem("model")
BRAND = BoxInfo.getItem("brand")
socfamily = BoxInfo.getItem("socfamily").lower().replace('bcm', '').replace('hisi', '').replace('advca', '').replace('smp', '').replace('aml', '')
has_dvi = BoxInfo.getItem("DreamBoxDVI")
has_scart = BoxInfo.getItem("HasScart")
has_yuv = BoxInfo.getItem("yuv")
has_rca = BoxInfo.getItem("rca")
has_avjack = BoxInfo.getItem("avjack")

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
	if AMLOGIC:
		rates["480i"] = {
			"60Hz": {60: "480i60hz"}
		}
		rates["576i"] = {
			"50Hz": {50: "576i50hz"}
		}
		rates["480p"] = {
			"60Hz": {60: "480p60hz"}
		}
		rates["576p"] = {
			"50Hz": {50: "576p50hz"}
		}
		rates["720p"] = {
			"50Hz": {50: "720p50hz"},
			"60Hz": {60: "720p60hz"},
			"auto": {60: "720p60hz"}
		}
		rates["1080i"] = {
			"50Hz": {50: "1080i50hz"},
			"60Hz": {60: "1080i60hz"},
			"auto": {60: "1080i60hz"}
		}
		rates["1080p"] = {
			"50Hz": {50: "1080p50hz"},
			"60Hz": {60: "1080p60hz"},
			"30Hz": {30: "1080p30hz"},
			"25Hz": {25: "1080p25hz"},
			"24Hz": {24: "1080p24hz"},
			"auto": {60: "1080p60hz"}
		}
		rates["2160p"] = {
			"50Hz": {50: "2160p50hz"},
			"60Hz": {60: "2160p60hz"},
			"30Hz": {30: "2160p30hz"},
			"25Hz": {25: "2160p25hz"},
			"24Hz": {24: "2160p24hz"},
			"auto": {60: "2160p60hz"}
		}
		rates["2160p30"] = {
			"25Hz": {50: "2160p25hz"},
			"30Hz": {60: "2160p30hz"},
			"auto": {60: "2160p30hz"}
		}
	else:
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
			"multi": {50: "1080p50", 60: "1080p"},
			"auto": {50: "1080p50", 60: "1080p", 24: "1080p24"}
		}
		rates["2160p"] = {
			"50Hz": {50: "2160p50"},
			"60Hz": {60: "2160p"},
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
		"50Hz": {50: "smpte50hz"},
		"60Hz": {60: "smpte60hz"},
		"30Hz": {30: "smpte30hz"},
		"25Hz": {25: "smpte25hz"},
		"24Hz": {24: "smpte24hz"},
		"auto": {60: "smpte60hz"}
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
	if BoxInfo.getItem("HasScart"):
		modes["Scart"] = ["PAL", "NTSC", "Multi"]
	if BoxInfo.getItem("HasComposite"):
		modes["RCA"] = ["576i", "PAL", "NTSC", "Multi"]
	if BoxInfo.getItem("HasYPbPr"):
		modes["YPbPr"] = ["720p", "1080i", "576p", "480p", "576i", "480i"]
	if BoxInfo.getItem("Has2160p"):
		modes["HDMI"] = ["720p", "1080p", "2160p", "1080i", "576p", "480p", "576i", "480i"]
	if AMLOGIC:
		modes["HDMI"] = ["720p", "1080p", "smpte", "2160p30", "2160p", "1080i", "576p", "576i", "480p", "480i"]
	elif getChipSetNumber() in ("7376", "7444", "7366", "5272s", "7445", "7445s"):
		modes["HDMI"] = ["720p", "1080p", "2160p", "1080i", "576p", "576i", "480p", "480i"]
	elif getChipSetNumber() in ("7252", "7251", "7251S", "7252S", "7251s", "7252s", "7278", "7444s", "3798mv200", "3798mv200h", "3798cv200", "hisi3798mv200", "hi3798mv200h", "hi3798cv200", "hi3798mv300", "3798mv300"):
		modes["HDMI"] = ["720p", "1080p", "2160p", "2160p30", "1080i", "576p", "576i", "480p", "480i"]
	elif getChipSetNumber() == "s905":
		modes["HDMI"] = ["720p", "1080p", "2160p", "2160p30", "1080i"]
	elif getChipSetNumber() in ("7241", "7358", "7362", "73625", "7356", "73565", "7424", "7425", "7435", "7581", "3716mv410", "3716cv100", "3716mv430", "pnx8471", "8634", "8655", "8653", "7346", "7552", "7584", "75845", "7585", "7162", "7111"):
		modes["HDMI"] = ["720p", "1080p", "1080i", "576p", "576i", "480p", "480i"]
	elif getChipSetNumber() == "8726":
		modes["HDMI"] = ["720p", "1080p", "1080i"]
	else:
		modes["HDMI"] = ["720p", "1080p", "2160p", "2160p30", "1080i", "576p", "480p", "576i", "480i"]
	modes["YPbPr"] = modes["HDMI"]
	if BoxInfo.getItem("scartyuv", False):
		modes["Scart-YPbPr"] = modes["HDMI"]
	if "YPbPr" in modes and not BoxInfo.getItem("yuv", False):
		del modes["YPbPr"]
	if "Scart" in modes and not BoxInfo.getItem("scart", False) and not BoxInfo.getItem("rca", False) and not BoxInfo.getItem("avjack", False):
		del modes["Scart"]
	if MODEL == "mutant2400":
		mode = fileReadLine("/proc/stb/info/board_revision", default="", source=MODULE_NAME)
		if mode >= "2":
			del modes["YPbPr"]
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
			print("[Videomode] VideoHardware current port not available in getOutputAspect!!! force 16:9")
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
				if aspect_str == "1": # 4:3
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

		if "YPbPr" in self.modes and not has_yuv:
			del self.modes["YPbPr"]
		if "Scart" in self.modes and not has_scart and not has_rca and not has_avjack:
			del self.modes["Scart"]

		self.createConfig()

		# take over old AVSwitch component :)
		from Components.AVSwitch import AVSwitch
		config.av.aspectratio.notifiers = []
		config.av.tvsystem.notifiers = []
		config.av.wss.notifiers = []
		AVSwitch.getOutputAspect = self.getOutputAspect

		config.av.aspect.addNotifier(self.updateAspect)
		config.av.wss.addNotifier(self.updateAspect)
		config.av.policy_43.addNotifier(self.updateAspect)
		if hasattr(config.av, "policy_169"):
			config.av.policy_169.addNotifier(self.updateAspect)

	def readAvailableModes(self):
		modes = eAVControl.getInstance().getAvailableModes()
		return modes.split()

	def is24hzAvailable(self):
		BoxInfo.setItem("have24hz", eAVControl.getInstance().has24hz())

	def readPreferredModes(self, saveMode=False, readOnly=False):
		modes = ""
		if config.av.edid_override.value is False:
			modes = eAVControl.getInstance().getPreferredModes(1)
			if saveMode:
				modes = modes.split()
				return modes if len(modes) > 1 else []

			print(f"[AVSwitch] getPreferredModes: '{modes}'.")
			self.modes_preferred = modes.split()
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
		port = config.av.videoport.value
		mode = config.av.videomode[port].value
		return self.axis[mode]

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
					if rate == "auto" and not BoxInfo.getItem("have24hz"):
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

	def isPortAvailable(self, port):  # Fix me!  What needs to be done here?
		return True

	def isModeAvailable(self, port, mode, rate, availableModes):  # Check if a high-level mode with a given rate is available.
		rate = self.rates[mode][rate]
		for mode in rate.values():
			if port != "HDMI":
				if mode not in availableModes:
					return False
			elif mode not in self.modes_preferred:
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
	def setVideoModeDirect(self, mode):
		if BoxInfo.getItem("AmlogicFamily"):
			rate = mode[-4:].replace("hz", "Hz")
			force = int(rate[:-2])
			mode = mode[:-4]
			self.setMode("HDMI", mode, rate, force)
		else:
			eAVControl.getInstance().setVideoMode(mode)

	def setMode(self, port, mode, rate, force=None):
		print(f"[AVSwitch] Setting mode for port '{port}', mode '{mode}', rate '{rate}'.")
		modes = self.rates[mode][rate]
		mode50 = modes.get(50)
		mode60 = modes.get(60)
		mode24 = modes.get(24)
		if mode50 is None or force == 60:
			mode50 = mode60
		if mode60 is None or force == 50:
			mode60 = mode50
		if mode24 is None or force:
			mode24 = mode60
			if force == 50:
				mode24 = mode50
		if AMLOGIC:
			amlmode = list(modes.values())[0]
			fileWriteLine("/sys/class/display/mode", amlmode, source=MODULE_NAME)
			print(f"[AVSwitch] Amlogic setting videomode to mode '{amlmode}'.")
			fileWriteLine("/etc/u-boot.scr.d/000_hdmimode.scr", f"setenv hdmimode {amlmode}", source=MODULE_NAME)
			fileWriteLine("/etc/u-boot.scr.d/000_outputmode.scr", f"setenv outputmode {amlmode}", source=MODULE_NAME)
			system("update-autoexec")
			fileWriteLine("/sys/class/ppmgr/ppscaler", "1", source=MODULE_NAME)
			fileWriteLine("/sys/class/ppmgr/ppscaler", "0", source=MODULE_NAME)
			fileWriteLine("/sys/class/video/axis", self.axis[mode], source=MODULE_NAME)
			stride = fileReadLine("/sys/class/graphics/fb0/stride", default="", source=MODULE_NAME)
			if self.current_mode is None:
				self.current_mode = mode
			if self.axis[self.current_mode] != self.axis[mode]:
				limits = [int(x) for x in self.axis[mode].split()]
				config.osd.dst_left.setChoices(default=limits[0], first=limits[0] - 255, last=limits[0] + 255)
				config.osd.dst_top.setChoices(default=limits[1], first=limits[1] - 255, last=limits[1] + 255)
				config.osd.dst_width.setChoices(default=limits[2], first=limits[2] - 255, last=limits[2] + 255)
				config.osd.dst_height.setChoices(default=limits[3], first=limits[3] - 255, last=limits[3] + 255)
				config.osd.dst_left.setValue(limits[2])
				config.osd.dst_top.setValue(limits[3])
				config.osd.dst_width.setValue(limits[0])
				config.osd.dst_height.setValue(limits[1])
				config.osd.dst_left.save()
				config.osd.dst_top.save()
				config.osd.dst_width.save()
				config.osd.dst_height.save()
			print(f"[AVSwitch] Framebuffer mode '{getDesktop(0).size().width()}', stride {stride}, axis '{self.axis[mode]}'.")
		else:
			success = fileWriteLine("/proc/stb/video/videomode_50hz", mode50, source=MODULE_NAME)
			if success:
				success = fileWriteLine("/proc/stb/video/videomode_60hz", mode60, source=MODULE_NAME)
			if not success:  # Fallback if no possibility to setup 50/60 hz mode
				fileWriteLine("/proc/stb/video/videomode", mode50, source=MODULE_NAME)
			if BoxInfo.getItem("have24hz"):
				fileWriteLine("/proc/stb/video/videomode_24hz", mode24, source=MODULE_NAME)
			if BRAND == "gigablue":  # Use 50Hz mode (if available) for booting.
				fileWriteLine("/etc/videomode", mode50, source=MODULE_NAME)
			self.setColorFormat(config.av.colorformat.value)
		self.current_mode = mode
		self.current_port = port

		self.updateAspect(None)

	def saveMode(self, port, mode, rate):
		config.av.videoport.value = port
		config.av.videoport.save()
		if port in config.av.videomode:
			config.av.videomode[port].value = mode
			config.av.videomode[port].save()
		if mode in config.av.videorate:
			config.av.videorate[mode].value = rate
			config.av.videorate[mode].save()

	def getAMLMode(self):
		f = open("/sys/class/display/mode", "r")
		currentmode = f.read().strip()
		f.close()
		return currentmode[:-4]

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

		if BoxInfo.getItem("AmlogicFamily"):
			arw = "0"
			if config.av.policy_43.value == "bestfit":
				arw = "10"
			if config.av.policy_43.value == "panscan":
				arw = "11"
			if config.av.policy_43.value == "letterbox":
				arw = "12"
			try:
				open("/sys/class/video/screen_mode", "w").write(arw)
			except IOError:
				print("[VideoHardware] Write to /sys/class/video/screen_mode failed.")
		elif BoxInfo.getItem("AmlogicFamily"):
			arw = "0"
			if config.av.policy_43.value == "bestfit":
				arw = "10"
			if config.av.policy_43.value == "letterbox":
				arw = "11"
			if config.av.policy_43.value == "panscan":
				arw = "12"
			try:
				open("/sys/class/video/screen_mode", "w").write(arw)
			except IOError:
				print("[VideoHardware] Write to /sys/class/video/screen_mode failed.")

		if isfile("/proc/stb/video/aspect"):
			try:
				open("/proc/stb/video/aspect", "w").write(aspect)
			except IOError:
				print("[VideoHardware] Write to /proc/stb/video/aspect failed!")
		if isfile("/proc/stb/video/policy"):
			try:
				open("/proc/stb/video/policy", "w").write(policy)
			except IOError:
				print("[VideoHardware] Write to /proc/stb/video/policy failed!")
		if isfile("/proc/stb/denc/0/wss"):
			try:
				open("/proc/stb/denc/0/wss", "w").write(wss)
			except IOError:
				print("[VideoHardware] Write to /proc/stb/denc/0/wss failed!")
		if isfile("/proc/stb/video/policy2") and hasattr(config.av, "policy_169"):
			try:
				open("/proc/stb/video/policy2", "w").write(policy2)
			except IOError:
				print("[VideoHardware] Write to /proc/stb/video/policy2 failed!")


video_hw = VideoHardware()
video_hw.setConfiguredMode()
