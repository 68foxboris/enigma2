# -*- coding: utf-8 -*-
from fcntl import ioctl
from os.path import isfile
from struct import pack, unpack
from time import localtime, time, timezone

from Tools.Directories import fileReadLine, fileWriteLine

MODULE_NAME = __name__.split(".")[-1]
wasTimerWakeup = None


def getBoxProcType():
	return fileReadLine("/proc/stb/info/type", "unknown", source=MODULE_NAME).strip().lower()


def getBoxProc():
	if isfile("/proc/stb/info/hwmodel"):
		procmodel = fileReadLine("/proc/stb/info/hwmodel", "unknown", source=MODULE_NAME)
	elif isfile("/proc/stb/info/azmodel"):
		procmodel = fileReadLine("/proc/stb/info/model", "unknown", source=MODULE_NAME)
	elif isfile("/proc/stb/info/gbmodel"):
		procmodel = fileReadLine("/proc/stb/info/gbmodel", "unknown", source=MODULE_NAME)
	elif isfile("/proc/stb/info/vumodel") and not isfile("/proc/stb/info/boxtype"):
		procmodel = fileReadLine("/proc/stb/info/vumodel", "unknown", source=MODULE_NAME)
	elif isfile("/proc/stb/info/boxtype") and not isfile("/proc/stb/info/vumodel"):
		procmodel = fileReadLine("/proc/stb/info/boxtype", "unknown", source=MODULE_NAME)
	elif isfile("/proc/boxtype"):
		procmodel = fileReadLine("/proc/boxtype", "unknown", source=MODULE_NAME)
	elif isfile("/proc/device-tree/model"):
		procmodel = fileReadLine("/proc/device-tree/model", "unknown", source=MODULE_NAME).strip()[0:12]
	elif isfile("/sys/firmware/devicetree/base/model"):
		procmodel = fileReadLine("/sys/firmware/devicetree/base/model", "unknown", source=MODULE_NAME)
	else:
		procmodel = fileReadLine("/proc/stb/info/model", "unknown", source=MODULE_NAME)
	return procmodel.strip().lower()


def getHWSerial():
	if isfile("/proc/stb/info/sn"):
		hwserial = fileReadLine("/proc/stb/info/sn", "unknown", source=MODULE_NAME)
	elif isfile("/proc/stb/info/serial"):
		hwserial = fileReadLine("/proc/stb/info/serial", "unknown", source=MODULE_NAME)
	elif isfile("/proc/stb/info/serial_number"):
		hwserial = fileReadLine("/proc/stb/info/serial_number", "unknown", source=MODULE_NAME)
	else:
		hwserial = fileReadLine("/sys/class/dmi/id/product_serial", "unknown", source=MODULE_NAME)
	return hwserial.strip()


def getBoxRCType():
	return fileReadLine("/proc/stb/ir/rc/type", "unknown", source=MODULE_NAME).strip()


def getFPVersion():
	version = "unknown"
	if isfile("/proc/stb/info/micomver"):
		version = fileReadLine("/proc/stb/info/micomver", "unknown", source=MODULE_NAME)
	elif isfile("/proc/stb/fp/version"):
		version = fileReadLine("/proc/stb/fp/version", "unknown", source=MODULE_NAME)
	elif isfile("/proc/stb/fp/fp_version"):
		version = fileReadLine("/proc/stb/fp/fp_version", "unknown", source=MODULE_NAME)
	elif isfile("/sys/firmware/devicetree/base/bolt/tag"):
		version = fileReadLine("/sys/firmware/devicetree/base/bolt/tag", "unknown", source=MODULE_NAME).rstrip("\0")
	else:
		try:
			with open("/dev/dbox/fp0") as fd:
				version = ioctl(fd.fileno(), 0)
		except:
			pass
	return version


def setFPWakeuptime(wutime):
	if not fileWriteLine("/proc/stb/fp/wakeup_time", str(wutime), source=MODULE_NAME):
		try:
			with open("/dev/dbox/fp0") as fd:
				ioctl(fd.fileno(), 6, pack('L', wutime))  # Set wake up time.
		except OSError as err:
			print("[StbHardware] Error %d: Unable to write to '/dev/dbox/fp0', setFPWakeuptime failed!  (%s)" % (err.errno, err.strerror))


def setRTCoffset(forsleep=None):
	forsleep = 7200 + timezone if localtime().tm_isdst == 0 else 3600 - timezone
	# t_local = localtime(int(time()))  # This line does nothing!
	# Set RTC OFFSET (diff. between UTC and Local Time)
	if fileWriteLine("/proc/stb/fp/rtc_offset", str(forsleep), source=MODULE_NAME):
		print("[StbHardware] Set RTC offset to %s sec." % forsleep)
	else:
		print("[StbHardware] Error: Write to '/proc/stb/fp/rtc_offset' failed!")


def setRTCtime(wutime):
	if isfile("/proc/stb/fp/rtc_offset"):
		setRTCoffset()
	if not fileWriteLine("/proc/stb/fp/rtc", str(wutime), source=MODULE_NAME):
		try:
			with open("/dev/dbox/fp0") as fd:
				ioctl(fd.fileno(), 0x101, pack('L', wutime))  # Set time.
		except OSError as err:
			print("[StbHardware] Error %d: Unable to write to '/dev/dbox/fp0', setRTCtime failed!  (%s)" % (err.errno, err.strerror))


def getFPWakeuptime():
	wakeup = fileReadLine("/proc/stb/fp/wakeup_time", source=MODULE_NAME)
	if wakeup is None:
		try:
			with open("/dev/dbox/fp0") as fd:
				wakeup = unpack('L', ioctl(fd.fileno(), 5, '    '))[0]  # Get wakeup time.
		except OSError as err:
			wakeup = 0
			print("[StbHardware] Error %d: Unable to read '/dev/dbox/fp0', getFPWakeuptime failed!  (%s)" % (err.errno, err.strerror))
	return wakeup


def getFPWasTimerWakeup(check=False):
	global wasTimerWakeup
	isError = False
	if wasTimerWakeup is not None:
		if check:
			return wasTimerWakeup, isError
		return wasTimerWakeup
	wasTimerWakeup = fileReadLine("/proc/stb/fp/was_timer_wakeup", source=MODULE_NAME)
	if wasTimerWakeup is not None and wasTimerWakeup != "":
		wasTimerWakeup = int(wasTimerWakeup) and True or False
		if not fileWriteLine("/tmp/was_timer_wakeup.txt", str(wasTimerWakeup), source=MODULE_NAME):
			try:
				with open("/dev/dbox/fp0") as fd:
					wasTimerWakeup = unpack('B', ioctl(fd.fileno(), 9, ' '))[0] and True or False
			except OSError as err:
				isError = True
				print("[StbHardware] Error %d: Unable to read '/dev/dbox/fp0', getFPWasTimerWakeup failed!  (%s)" % (err.errno, err.strerror))
	if wasTimerWakeup:
		clearFPWasTimerWakeup()  # Clear hardware status.
	if check:
		return wasTimerWakeup, isError
	return wasTimerWakeup


def clearFPWasTimerWakeup():
	if not fileWriteLine("/proc/stb/fp/was_timer_wakeup", "0", source=MODULE_NAME):
		try:
			with open("/dev/dbox/fp0") as fd:
				ioctl(fd.fileno(), 10)
		except OSError as err:
			print("[StbHardware] Error %d: Unable to update '/dev/dbox/fp0', clearFPWasTimerWakeup failed!  (%s)" % (err.errno, err.strerror))
