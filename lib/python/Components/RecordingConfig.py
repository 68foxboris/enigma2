# -*- coding: utf-8 -*-
from time import localtime, mktime
from Components.config import ConfigClock, ConfigEnableDisable, ConfigNumber, ConfigYesNo, ConfigSubsection, ConfigSelection, config
from Components.SystemInfo import BoxInfo
from enigma import pNavigation


def calculateTime(hours, minutes, day_offset=0):
	cur_time = localtime()
	unix_time = mktime((cur_time.tm_year, cur_time.tm_mon, cur_time.tm_mday, hours, minutes, 0, cur_time.tm_wday, cur_time.tm_yday, cur_time.tm_isdst)) + day_offset
	return unix_time


def InitRecordingConfig():
	if hasattr(config, "recording"):
		return
	config.recording = ConfigSubsection()
	# actually this is "recordings always have priority". "Yes" does mean: don't ask. The RecordTimer will ask when value is 0.
	config.recording.asktozap = ConfigYesNo(default=True)
	config.recording.margin_before = ConfigNumber(default=3)
	config.recording.margin_after = ConfigNumber(default=5)
	config.recording.debug = ConfigYesNo(default=False)
	config.recording.ascii_filenames = ConfigYesNo(default=False)
	config.recording.keep_timers = ConfigNumber(default=7)
	config.recording.filename_composition = ConfigSelection(default="standard", choices=[
		("standard", _("standard")),
		("event", _("Event name first")),
		("short", _("Short filenames")),
		("long", _("Long filenames"))])
	config.recording.always_ecm = ConfigYesNo(default=False)
	config.recording.never_decrypt = ConfigYesNo(default=False)
	config.recording.zap_record_service_in_standby = ConfigYesNo(default=False)
	config.recording.offline_decode_delay = ConfigNumber(default=1000)
	config.recording.timer_default_type = ConfigSelection(choices=[("zap", _("zap")), ("record", _("record")), ("zap+record", _("zap and record"))], default="record")
	choices = [
		("any", _("Any recordings")),
		("real", _("Real recordings")),
		("real_streaming", _("Real recordings or streaming")),
		("real_pseudo", _("Real or pseudo recordings"))
	]
	config.recording.show_rec_symbol_for_rec_types = ConfigSelection(default="real", choices=choices)
	config.recording.warn_box_restart_rec_types = ConfigSelection(default="real", choices=choices)

	if BoxInfo.getItem("CanDescrambleInStandby"):
		config.recording.standbyDescramble = ConfigEnableDisable(default=True)
		config.recording.standbyDescrambleShutdown = ConfigEnableDisable(default=True)
	else:
		config.recording.standbyDescramble = ConfigEnableDisable(default=False)
		config.recording.standbyDescrambleShutdown = ConfigEnableDisable(default=False)
	config.recording.standbyDescrambleStart = ConfigClock(default=calculateTime(0, 1))
	config.recording.standbyDescrambleEnd = ConfigClock(default=calculateTime(23, 59))


def recType(configString):
	return {
		"any": pNavigation.isAnyRecording,
		"real": pNavigation.isRealRecording,
		"real_streaming": pNavigation.isRealRecording | pNavigation.isStreaming,
		"real_pseudo": pNavigation.isRealRecording | pNavigation.isPseudoRecording
	}.get(configString)
