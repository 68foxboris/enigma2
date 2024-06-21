from os.path import isdir, islink, join
import sys  # This is needed for the twisted redirection access to stderr and stdout.
from time import time
import Tools.RedirectOutput

import enigma  # Establish enigma2 connections to processing methods.
import eBaseImpl
import eConsoleImpl
enigma.eTimer = eBaseImpl.eTimer
enigma.eSocketNotifier = eBaseImpl.eSocketNotifier
enigma.eConsoleAppContainer = eConsoleImpl.eConsoleAppContainer

MODULE_NAME = "StartEnigma"  # This is done here as "__name__.split(".")[-1]" returns "__main__" for this module.


# Session.open:
# * Push current active dialog ("current_dialog") onto stack.
# * Call execEnd for this dialog.
#   * Clear in_exec flag.
#   * Hide screen.
# * Instantiate new dialog into "current_dialog".
#   * Create screens, components.
#   * Read and apply skin.
#   * Create GUI for screen.
# * Call execBegin for new dialog.
#   * Set in_exec.
#   * Show GUI screen.
#   * Call components' / screen's onExecBegin.
# ... Screen is active, until it calls "close"...
#
# Session.close:
# * Assert in_exec.
# * Save return value.
# * Start deferred close handler ("onClose").
# * Call execEnd.
#   * Clear in_exec.
#   * Hide screen.
# .. a moment later:
# Session.doClose:
# * Destroy screen.
#


class Session:
	def __init__(self, desktop=None, summaryDesktop=None, navigation=None):
		self.desktop = desktop
		self.summaryDesktop = summaryDesktop
		self.nav = navigation
		self.delay_timer = enigma.eTimer()
		self.delay_timer.callback.append(self.processDelay)
		self.current_dialog = None
		self.dialog_stack = []
		self.summary_stack = []
		self.summary = None
		self.in_exec = False
		self.screen = SessionGlobals(self)

		for plugin in plugins.getPlugins(PluginDescriptor.WHERE_SESSIONSTART):
			try:
				plugin(reason=0, session=self)
			except:
				print("[StartEnigma] Error: Plugin raised exception at WHERE_SESSIONSTART!")
				from traceback import print_exc
				print_exc()

	def processDelay(self):
		callback = self.current_dialog.callback
		retVal = self.current_dialog.returnValue
		if self.current_dialog.isTmp:
			self.current_dialog.doClose()
			# dump(self.current_dialog)
			del self.current_dialog
		else:
			del self.current_dialog.callback
		self.popCurrent()
		if callback is not None:
			callback(*retVal)

	def execBegin(self, first=True, do_show=True):
		if self.in_exec:
			raise AssertionError("[StartEnigma] Error: Already in exec!")
		self.in_exec = True
		currentDialog = self.current_dialog
		# When this is an execbegin after a execEnd of a "higher" dialog,
		# popSummary already did the right thing.
		if first:
			self.instantiateSummaryDialog(currentDialog)
		currentDialog.saveKeyboardMode()
		currentDialog.execBegin()
		# When execBegin opened a new dialog, don't bother showing the old one.
		if currentDialog == self.current_dialog and do_show:
			currentDialog.show()

	def execEnd(self, last=True):
		assert self.in_exec
		self.in_exec = False
		self.current_dialog.execEnd()
		self.current_dialog.restoreKeyboardMode()
		self.current_dialog.hide()
		if last and self.summary is not None:
			self.current_dialog.removeSummary(self.summary)
			self.popSummary()

	def instantiateDialog(self, screen, *arguments, **kwargs):
		return self.doInstantiateDialog(screen, arguments, kwargs, self.desktop)

	def deleteDialog(self, screen):
		screen.hide()
		screen.doClose()

	def deleteDialogWithCallback(self, callback, screen, *retVal):
		screen.hide()
		screen.doClose()
		if callback is not None:
			callback(*retVal)

	def instantiateSummaryDialog(self, screen, **kwargs):
		if self.summaryDesktop is not None:
			self.pushSummary()
			summary = screen.createSummary() or ScreenSummary
			arguments = (screen,)
			self.summary = self.doInstantiateDialog(summary, arguments, kwargs, self.summaryDesktop)
			self.summary.show()
			screen.addSummary(self.summary)

	def doInstantiateDialog(self, screen, arguments, kwargs, desktop):
		dialog = screen(self, *arguments, **kwargs)  # Create dialog.
		if dialog is None:
			return
		readSkin(dialog, None, dialog.skinName, desktop)  # Read skin data.
		dialog.setDesktop(desktop)  # Create GUI view of this dialog.
		dialog.applySkin()
		return dialog

	def pushCurrent(self):
		if self.current_dialog is not None:
			self.dialog_stack.append((self.current_dialog, self.current_dialog.shown))
			self.execEnd(last=False)

	def popCurrent(self):
		if self.dialog_stack:
			(self.current_dialog, do_show) = self.dialog_stack.pop()
			self.execBegin(first=False, do_show=do_show)
		else:
			self.current_dialog = None

	def execDialog(self, dialog):
		self.pushCurrent()
		self.current_dialog = dialog
		self.current_dialog.isTmp = False
		self.current_dialog.callback = None  # Would cause re-entrancy problems.
		self.execBegin()

	def openWithCallback(self, callback, screen, *arguments, **kwargs):
		dialog = self.open(screen, *arguments, **kwargs)
		if dialog != "config.crash.bsodpython.value=True":
			dialog.callback = callback
			return dialog

	def open(self, screen, *arguments, **kwargs):
		if self.dialog_stack and not self.in_exec:
			raise RuntimeError("[StartEnigma] Error: Modal open are allowed only from a screen which is modal!")  # ...unless it's the very first screen.
		self.pushCurrent()
		if config.crash.bsodpython.value:
			try:
				dialog = self.current_dialog = self.instantiateDialog(screen, *arguments, **kwargs)
			except:
				self.popCurrent()
				raise
				return "config.crash.bsodpython.value=True"
		else:
			dialog = self.current_dialog = self.instantiateDialog(screen, *arguments, **kwargs)
		dialog.isTmp = True
		dialog.callback = None
		self.execBegin()
		return dialog

	def close(self, screen, *retVal):
		if not self.in_exec:
			print("[StartEnigma] Close after exec!")
			return
		# Be sure that the close is for the right dialog!  If it's
		# not, you probably closed after another dialog was opened.
		# This can happen if you open a dialog onExecBegin, and
		# forget to do this only once.  After close of the top
		# dialog, the underlying dialog will gain focus again (for
		# a short time), thus triggering the onExec, which opens the
		# dialog again, closing the loop.
		if not screen == self.current_dialog:
			raise AssertionError("[StartEnigma] Error: Attempt to close non-current screen!")
		self.current_dialog.returnValue = retVal
		self.delay_timer.start(0, 1)
		self.execEnd()

	def pushSummary(self):
		if self.summary is not None:
			self.summary.hide()
			self.summary_stack.append(self.summary)
			self.summary = None

	def popSummary(self):
		if self.summary is not None:
			self.summary.doClose()
		if not self.summary_stack:
			self.summary = None
		else:
			self.summary = self.summary_stack.pop()
		if self.summary is not None:
			self.summary.show()


class PowerKey:
	"""PowerKey code - Handles the powerkey press and powerkey release actions."""

	def __init__(self, session):
		self.session = session
		globalActionMap.actions["power_down"] = lambda *args: None
		globalActionMap.actions["power_up"] = self.powerup
		globalActionMap.actions["power_long"] = self.powerlong
		globalActionMap.actions["deepstandby"] = self.shutdown  # Frontpanel long power button press.
		globalActionMap.actions["discrete_off"] = self.standby

	def powerup(self):
		if not Screens.Standby.inStandby and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND and self.session.in_exec:
			self.doAction(config.misc.hotkey.power.value)
		else:
			return 0

	def powerlong(self):
		if not Screens.Standby.inStandby and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND and self.session.in_exec:
			self.doAction(config.misc.hotkey.power_long.value)
		else:
			return 0

	def shutdown(self):
		print("[StartEnigma] Power off, now!")
		if not Screens.Standby.inTryQuitMainloop and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND:
			self.session.open(Screens.Standby.TryQuitMainloop, 1)  # Shutdown
		else:
			return 0

	def standby(self):
		if not Screens.Standby.inStandby and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND and self.session.in_exec:
			self.session.open(Screens.Standby.Standby)
		else:
			return 0

	def doAction(self, selected):
		if selected:
			selected = selected.split("/")
			if selected[0] == "Module":
				try:
					exec("from " + selected[1] + " import *")
					exec("self.session.open(" + ",".join(selected[2:]) + ")")
				except:
					print("[StartEnigma] Error during executing module %s, screen %s" % (selected[1], selected[2]))
			elif selected[0] == "Menu":
				root = mdom.getroot()
				for x in root.findall("menu"):
					if x.get("key") == "shutdown":
						self.session.infobar = self
						menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, x)
						menu_screen.setTitle(_("Standby / restart"))
						break


if enigma.eAVControl.getInstance().hasScartSwitch():
	enigma.eProfileWrite("Scart")
	print("[StartEnigma] Initialising Scart module")
	from Screens.Scart import Scart


class AutoScartControl:
	def __init__(self, session):
		self.hasScart = BoxInfo.getItem("SCART")
		if self.hasScart:
			self.force = False
			self.current_vcr_sb = enigma.eAVControl.getInstance().getVCRSlowBlanking()
			if self.current_vcr_sb and config.av.vcrswitch.value:
				self.scartDialog = session.instantiateDialog(Scart, True)
			else:
				self.scartDialog = session.instantiateDialog(Scart, False)
			config.av.vcrswitch.addNotifier(self.recheckVCRSb)
			enigma.eAVControl.getInstance().vcr_sb_notifier.get().append(self.VCRSbChanged)

	def recheckVCRSb(self, configElement):
		self.VCRSbChanged(self.current_vcr_sb)

	def VCRSbChanged(self, value):
		if self.hasScart:
			# print("[StartEnigma] VCR SB changed to '%s'." % value)
			self.current_vcr_sb = value
			if config.av.vcrswitch.value or value > 2:
				if value:
					self.scartDialog.showMessageBox()
				else:
					self.scartDialog.switchToTV()
def runScreenTest():
	config.misc.startCounter.value += 1
	config.misc.startCounter.save()
	enigma.eProfileWrite("ReadPluginList")
	enigma.pauseInit()
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
	enigma.resumeInit()
	enigma.eProfileWrite("Session")
	nav = Navigation()
	session = Session(desktop=enigma.getDesktop(0), summaryDesktop=enigma.getDesktop(1), navigation=nav)
	CiHandler.setSession(session)
	powerOffTimer.setSession(session)
	screensToRun = [p.fnc for p in plugins.getPlugins(PluginDescriptor.WHERE_WIZARD)]
	enigma.eProfileWrite("Wizards")
	screensToRun += wizardManager.getWizards()
	screensToRun.append((100, InfoBar.InfoBar))
	screensToRun.sort(key=lambda x: x[0])  # works in both Pythons but let's not use sort method here first we must see if we have work network in the wizard.
	enigma.ePythonConfigQuery.setQueryFunc(configfile.getResolvedKey)

	def runNextScreen(session, screensToRun, *result):
		if result:
			enigma.quitMainloop(*result)
			return
		screen = screensToRun[0][1]
		args = screensToRun[0][2:]
		if screensToRun:
			session.openWithCallback(boundFunction(runNextScreen, session, screensToRun[1:]), screen, *args)
		else:
			session.open(screen, *args)
	runNextScreen(session, screensToRun)
	enigma.eProfileWrite("VolumeControl")
	vol = VolumeControl(session)
	enigma.eProfileWrite("Processing Screen")
	processing = Processing(session)
	enigma.eProfileWrite("PowerKey")
	power = PowerKey(session)
	if enigma.getVFDSymbolsPoll():
		enigma.eProfileWrite("VFDSymbolsCheck")
		from Components.VfdSymbols import SymbolsCheck
		SymbolsCheck(session)
	# we need session.scart to access it from within menu.xml
	session.scart = AutoScartControl(session) if enigma.eAVControl.getInstance().hasScartSwitch() else None
	enigma.eProfileWrite("Trashcan")
	import Tools.Trashcan
	Tools.Trashcan.init(session)
	enigma.eProfileWrite("RunReactor")
	enigma.eProfileDone()
	runReactor()
	from Screens.SleepTimerEdit import isNextWakeupTime
	# get currentTime
	nowTime = time()
	wakeupList = sorted([
		x for x in ((session.nav.RecordTimer.getNextRecordingTime(), 0),
					(session.nav.RecordTimer.getNextZapTime(isWakeup=True), 1),
					(plugins.getNextWakeupTime(), 2),
					(isNextWakeupTime(), 3))
		if x[0] != -1
	])
	if wakeupList:
		from time import strftime
		startTime = wakeupList[0]
		if (startTime[0] - nowTime) < 270:  # no time to switch box back on
			wptime = nowTime + 30  # so switch back on in 30 seconds
		else:
			wptime = startTime[0] - 240
		if config.misc.SyncTimeUsing.value != "0":
			print("[StartEnigma] DVB time sync disabled, so set RTC now to current Linux time!  (%s)" % strftime("%Y/%m/%d %H:%M", localtime(nowTime)))
			setRTCtime(nowTime)
		setFPWakeuptime(wptime)
		config.misc.prev_wakeup_time.value = int(startTime[0])
		config.misc.prev_wakeup_time_type.value = startTime[1]
		config.misc.prev_wakeup_time_type.save()
	else:
		config.misc.prev_wakeup_time.value = 0
	config.misc.prev_wakeup_time.save()
	session.nav.stopService()
	session.nav.shutdown()
	configfile.save()
	from Screens.InfoBarGenerics import saveResumePoints
	saveResumePoints()
	return 0


def setLoadUnlinkedUserbouquets(configElement):
	enigma.eDVBDB.getInstance().setLoadUnlinkedUserbouquets(configElement.value)


def dump(dir, p=""):
	had = dict()
	if isinstance(dir, dict):
		for (entry, val) in dir.items():
			dump(val, p + "(dict)/" + entry)
	if hasattr(dir, "__dict__"):
		for name, value in dir.__dict__.items():
			if str(value) not in had:
				had[str(value)] = 1
				dump(value, p + "/" + str(name))
			else:
				print("[StartEnigma] Dump: %s/%s:%s(cycle)" % (p, str(name), str(dir.__class__)))
	else:
		print("[StartEnigma] Dump: %s:%s" % (p, str(dir)))  # + ":" + str(dir.__class__)


# Demo code for use of standby enter leave callbacks.
#
# def leaveStandby():
# 	print("[StartEnigma] Leaving standby.")
#
#
# def standbyCountChanged(configElement):
# 	print("[StartEnigma] Enter standby number %s." % configElement.value)
# 	from Screens.Standby import inStandby
# 	inStandby.onClose.append(leaveStandby)
#
#
# config.misc.standbyCounter.addNotifier(standbyCountChanged, initial_call=False)

#################################
#                               #
#  Code execution starts here!  #
#                               #
#################################

enigma.eProfileWrite("Twisted")
print("[StartEnigma] Initializing Twisted.")
try:  # Configure the twisted processor.
	from twisted.python.runtime import platform
	platform.supportsThreads = lambda: True
	from e2reactor import install
	install()
	from twisted.internet import reactor

	def runReactor():
		reactor.run(installSignalHandlers=False)

except ImportError:
	print("[StartEnigma] Error: Twisted not available!")

	def runReactor():
		enigma.runMainloop()

try:  # Configure the twisted logging.
	from twisted.python import log, util

	def quietEmit(self, eventDict):
		text = log.textFromEventDict(eventDict)
		if text is None:
			return
		if "/api/statusinfo" in text:  # Do not log OpenWebif status info.
			return
		# Log with time stamp.
		#
		# timeStr = self.formatTime(eventDict["time"])
		# fmtDict = {
		# 	"ts": timeStr,
		# 	"system": eventDict["system"],
		# 	"text": text.replace("\n", "\n\t")
		# }
		# msgStr = log._safeFormat("%(ts)s [%(system)s] %(text)s\n", fmtDict)
		#
		# Log without time stamp.
		#
		fmtDict = {
			"text": text.replace("\n", "\n\t")
		}
		msgStr = log._safeFormat("%(text)s\n", fmtDict)
		util.untilConcludes(self.write, msgStr)
		util.untilConcludes(self.flush)

	logger = log.FileLogObserver(sys.stdout)
	log.FileLogObserver.emit = quietEmit
	stdoutBackup = sys.stdout  # Backup stdout and stderr redirections.
	stderrBackup = sys.stderr
	log.startLoggingWithObserver(logger.emit)
	sys.stdout = stdoutBackup  # Restore stdout and stderr redirections because of twisted redirections.
	sys.stderr = stderrBackup

except ImportError:
	print("[StartEnigma] Error: Twisted not available!")


enigma.eProfileWrite("BoxInfo")
from Components.SystemInfo import BoxInfo

BRAND = BoxInfo.getItem("brand")
BOX_TYPE = BoxInfo.getItem("machinebuild")
MODEL = BoxInfo.getItem("model")
DISPLAYBRAND = BoxInfo.getItem("displaybrand")

print("[StartEnigma] Receiver name = %s %s" % (DISPLAYBRAND, BoxInfo.getItem("displaymodel")))
print("[StartEnigma] Build Brand = %s" % BRAND)
print("[StartEnigma] Build Model = %s" % MODEL)
print("[StartEnigma] Platform = %s" % BoxInfo.getItem("platform"))
print("[StartEnigma] SoC family = %s" % BoxInfo.getItem("socfamily"))

if BoxInfo.getItem("architecture") in ("aarch64"):
	# import usb.core
	from usb.backend.libusb1 import get_backend
	get_backend(find_library=lambda x: "/lib64/libusb-1.0.so.0")

from traceback import print_exc
from Components.config import config, configfile, ConfigText, ConfigYesNo, ConfigInteger, ConfigSelection, ConfigSubsection, NoSave


# These entries should be moved back to UsageConfig.py when it is safe to bring UsageConfig init to this location in StartEnigma.py.
#
config.crash = ConfigSubsection()
config.crash.debugMultiBoot = ConfigYesNo(default=False)
config.crash.debugKeyboards = ConfigYesNo(default=False)
config.crash.debugOpkg = ConfigYesNo(default=False)
config.crash.debugRemoteControls = ConfigYesNo(default=False)
config.crash.debugScreens = ConfigYesNo(default=False)
config.crash.debugSkin = ConfigYesNo(default=False)
config.crash.debugDVBScan = ConfigYesNo(default=False)


# config.plugins needs to be defined before InputDevice < HelpMenu < MessageBox < InfoBar
config.plugins = ConfigSubsection()
config.plugins.remotecontroltype = ConfigSubsection()
config.plugins.remotecontroltype.rctype = ConfigInteger(default=0)

enigma.eProfileWrite("InitSetupDevices")
import Components.SetupDevices
Components.SetupDevices.InitSetupDevices()

enigma.eProfileWrite("InfoBar")
from Screens import InfoBar

def setEPGCachePath(configElement):
	if isdir(configElement.value) or islink(configElement.value):
		configElement.value = join(configElement.value, "epg.dat")
	enigma.eEPGCache.getInstance().setCacheFile(configElement.value)

enigma.eProfileWrite("ScreenSummary")
# from Screens.SimpleSummary import SimpleSummary
from Screens.Screen import ScreenSummary

enigma.eProfileWrite("LoadBouquets")
config.misc.load_unlinked_userbouquets = ConfigYesNo(default=True)
config.misc.load_unlinked_userbouquets.addNotifier(setLoadUnlinkedUserbouquets)
enigma.eDVBDB.getInstance().reloadBouquets()

enigma.eProfileWrite("ParentalControl")
import Components.ParentalControl
Components.ParentalControl.InitParentalControl()

enigma.eProfileWrite("Navigation")
from Navigation import Navigation

enigma.eProfileWrite("ReadSkin")
from skin import readSkin

enigma.eProfileWrite("InitFallbackFiles")
from Tools.Directories import InitFallbackFiles, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN
InitFallbackFiles()

enigma.eProfileWrite("ConfigMisc")
config.misc.radiopic = ConfigText(default=resolveFilename(SCOPE_CURRENT_SKIN, "radio.mvi"))
config.misc.blackradiopic = ConfigText(default=resolveFilename(SCOPE_CURRENT_SKIN, "black.mvi"))
config.misc.startCounter = ConfigInteger(default=0)  # number of e2 starts...
config.misc.standbyCounter = NoSave(ConfigInteger(default=0))  # number of standby
config.misc.DeepStandby = NoSave(ConfigYesNo(default=False))  # detect deepstandby
config.misc.RestartUI = ConfigYesNo(default=False)  # detect user interface restart
config.misc.prev_wakeup_time = ConfigInteger(default=0)
# config.misc.prev_wakeup_time_type is only valid when wakeup_time is not 0
config.misc.prev_wakeup_time_type = ConfigInteger(default=0)
# 0 = RecordTimer, 1 = ZapTimer, 2 = Plugins, 3 = WakeupTimer
config.misc.epgcache_filename = ConfigText(default="/media/hdd/epg.dat", fixed_size=False)
config.misc.SyncTimeUsing = ConfigSelection(default="0", choices=[
	("0", _("Transponder Time")),
	("1", _("NTP"))
])
config.misc.NTPserver = ConfigText(default="pool.ntp.org", fixed_size=False)

enigma.eProfileWrite("AutoRunPlugins")
# Initialize autorun plugins and plugin menu entries.
from Components.PluginComponent import plugins

enigma.eProfileWrite("StartWizard")
from Screens.Wizard import wizardManager
from Screens.StartWizard import *
from Tools.BoundFunction import boundFunction
from Plugins.Plugin import PluginDescriptor

enigma.eProfileWrite("ScreenGlobals")
from Screens.Globals import Globals
from Screens.SessionGlobals import SessionGlobals
from Screens.Screen import Screen
Screen.globalScreen = Globals()

enigma.eProfileWrite("Standby")
import Screens.Standby
from Screens.Menu import MainMenu, mdom

enigma.eProfileWrite("GlobalActionMap")
from GlobalActions import globalActionMap

enigma.eProfileWrite("Scart")
from Screens.Scart import Scart

enigma.eProfileWrite("CIHandler")
from Screens.Ci import CiHandler

enigma.eProfileWrite("VolumeControl")
from Components.VolumeControl import VolumeControl

enigma.eProfileWrite("Processing")
from Screens.Processing import Processing

enigma.eProfileWrite("StackTracePrinter")
from Components.StackTrace import StackTracePrinter
StackTracePrinterInst = StackTracePrinter()

from time import localtime, strftime
from Tools.StbHardware import setFPWakeuptime, setRTCtime

enigma.eProfileWrite("InitSkins")
from skin import InitSkins
InitSkins()

enigma.eProfileWrite("InitServiceList")
from Components.ServiceList import InitServiceListSettings
InitServiceListSettings()

enigma.eProfileWrite("InitInputDevices")
from Components.InputDevice import InitInputDevices
InitInputDevices()
import Components.InputHotplug

enigma.eProfileWrite("InitAVSwitch")
from Components.AVSwitch import InitAVSwitch
InitAVSwitch()

enigma.eProfileWrite("InitHDMIRecord")
from Components.HdmiRecord import InitHdmiRecord
InitHdmiRecord()

enigma.eProfileWrite("InitRecordingConfig")
from Components.RecordingConfig import InitRecordingConfig
InitRecordingConfig()

enigma.eProfileWrite("InitUsageConfig")
from Components.UsageConfig import InitUsageConfig
InitUsageConfig()

enigma.eProfileWrite("InitTimeZones")
from Components.Timezones import InitTimeZones
InitTimeZones()

enigma.eProfileWrite("AutoLogManager")
from Screens.LogManager import AutoLogManager
AutoLogManager()

enigma.eProfileWrite("Keymapparser")
import keymapparser
keymapparser.readKeymap(config.usage.keymap.value)

enigma.eProfileWrite("NTPSyncPoller")
from Components.NetworkTime import ntpSyncPoller
ntpSyncPoller.startTimer()

enigma.eProfileWrite("InitNetwork")
from Components.Network import InitNetwork
InitNetwork()

enigma.eProfileWrite("InitLCD")
from Components.Lcd import IconCheck, InitLcd
InitLcd()
IconCheck()

enigma.eAVControl.getInstance().disableHDMIIn()

enigma.eProfileWrite("RcModel")
import Components.RcModel

enigma.eProfileWrite("PowerOffTimer")
from Components.PowerOffTimer import powerOffTimer

enigma.eProfileWrite("InitOSDCalibration")
from Screens.OSDCalibration import InitOSDCalibration
InitOSDCalibration()

enigma.eProfileWrite("EPGCacheCheck")
from Components.EpgLoadSave import EpgCacheLoadCheck, EpgCacheSaveCheck
EpgCacheSaveCheck()
EpgCacheLoadCheck()

enigma.eProfileWrite("InitRFmod")
from Components.RFmod import InitRFmod
InitRFmod()

enigma.eProfileWrite("InitCiConfig")
from Screens.Ci import InitCiConfig
InitCiConfig()

# from enigma import dump_malloc_stats
# t = eTimer()
# t.callback.append(dump_malloc_stats)
# t.start(1000)

# Lets get going and load a screen.
#
try:
	runScreenTest()  # Start running the first screen.
	plugins.shutdown()  # Shutdown all plugins.
	from Components.ParentalControl import parentalControl
	parentalControl.save()  # Save parental control settings.
except Exception:
	print("Error: Exception in Python StartEnigma startup code:")
	print("=" * 52)
	print_exc(file=sys.stdout)
	print("[StartEnigma] Exiting via quitMainloop #4.")
	enigma.quitMainloop(5)  # QUIT_ERROR_RESTART
	print("-" * 52)
