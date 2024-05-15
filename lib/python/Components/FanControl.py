# -*- coding: utf-8 -*-
import os
from enigma import iRecordableService
from Components.config import config, ConfigSubList, ConfigSubsection, ConfigSlider
from Tools.BoundFunction import boundFunction

import NavigationInstance
from Components.SystemInfo import BoxInfo

model = BoxInfo.getItem("model")


class FanControl:
	# ATM there's only support for one fan
	def __init__(self):
		if os.path.exists("/proc/stb/fp/fan_vlt") or os.path.exists("/proc/stb/fp/fan_pwm") or os.path.exists("/proc/stb/fp/fan_speed"):
			self.fancount = 1
		else:
			self.fancount = 0
		self.createConfig()
		config.misc.standbyCounter.addNotifier(self.standbyCounterChanged, initial_call=False)

	def setVoltage_PWM(self):
		for fanid in range(self.getFanCount()):
			cfg = self.getConfig(fanid)
			self.setVoltage(fanid, cfg.vlt.value)
			self.setPWM(fanid, cfg.pwm.value)
			print("[FanControl] setting fan values: fanid = %d, voltage = %d, pwm = %d" % (fanid, cfg.vlt.value, cfg.pwm.value))

	def setVoltage_PWM_Standby(self):
		for fanid in range(self.getFanCount()):
			cfg = self.getConfig(fanid)
			self.setVoltage(fanid, cfg.vlt_standby.value)
			self.setPWM(fanid, cfg.pwm_standby.value)
			print("[FanControl] setting fan values (standby mode): fanid = %d, voltage = %d, pwm = %d" % (fanid, cfg.vlt_standby.value, cfg.pwm_standby.value))

	def getRecordEvent(self, recservice, event):
		recordings = len(NavigationInstance.instance.getRecordings())
		if event == iRecordableService.evEnd:
			if recordings == 0:
				self.setVoltage_PWM_Standby()
		elif event == iRecordableService.evStart:
			if recordings == 1:
				self.setVoltage_PWM()

	def leaveStandby(self):
		NavigationInstance.instance.record_event.remove(self.getRecordEvent)
		recordings = NavigationInstance.instance.getRecordings()
		if not recordings:
			self.setVoltage_PWM()

	def standbyCounterChanged(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.leaveStandby)
		recordings = NavigationInstance.instance.getRecordings()
		NavigationInstance.instance.record_event.append(self.getRecordEvent)
		if not recordings:
			self.setVoltage_PWM_Standby()

	def createConfig(self):
		def setVlt(fancontrol, fanid, configElement):
			fancontrol.setVoltage(fanid, configElement.value)

		def setPWM(fancontrol, fanid, configElement):
			fancontrol.setPWM(fanid, configElement.value)

		config.fans = ConfigSubList()
		for fanid in range(self.getFanCount()):
			fan = ConfigSubsection()
			fan.vlt = ConfigSlider(default=15, increment=5, limits=(0, 255))
			if model == "tm2t":
				fan.pwm = ConfigSlider(default=150, increment=5, limits=(0, 255))
			elif model == "tmsingle":
				fan.pwm = ConfigSlider(default=100, increment=5, limits=(0, 255))
			elif model == "beyonwizu4":
				fan.pwm = ConfigSlider(default=0xcc, increment=0x11, limits=(0x22, 0xff))
			elif model == "beyonwizt4":
				fan.pwm = ConfigSlider(default=200, increment=5, limits=(0, 255))
			else:
				fan.pwm = ConfigSlider(default=50, increment=5, limits=(0, 255))
			fan.vlt_standby = ConfigSlider(default=5, increment=5, limits=(0, 255))
			if model == "beyonwizu4":
				fan.pwm_standby = ConfigSlider(default=0x44, increment=0x11, limits=(0x22, 0xff))
			elif model == "beyonwizt4":
				fan.pwm_standby = ConfigSlider(default=10, increment=5, limits=(0, 0xff))
			else:
				fan.pwm_standby = ConfigSlider(default=0, increment=5, limits=(0, 255))
			fan.vlt.addNotifier(boundFunction(setVlt, self, fanid))
			fan.pwm.addNotifier(boundFunction(setPWM, self, fanid))
			config.fans.append(fan)

	def getConfig(self, fanid):
		return config.fans[fanid]

	def getFanCount(self):
		return self.fancount

	def hasRPMSensor(self, fanid):
		return os.path.exists("/proc/stb/fp/fan_speed")

	def hasFanControl(self, fanid):
		return os.path.exists("/proc/stb/fp/fan_vlt") or os.path.exists("/proc/stb/fp/fan_pwm")

	def getFanSpeed(self, fanid):
		print("[FanControl] Read /proc/stb/fp/fan_speed")
		return int(open("/proc/stb/fp/fan_speed").readline().strip()[:-4])

	def getVoltage(self, fanid):
		print("[FanControl] Read /proc/stb/fp/fan_vlt")
		return int(open("/proc/stb/fp/fan_vlt").readline().strip(), 16)

	def setVoltage(self, fanid, value):
		if model == "beyonwizu4":
			return
		if value > 255:
			return
		print("[FanControl] Write to /proc/stb/fp/fan_vlt")
		open("/proc/stb/fp/fan_vlt", "w").write("%x" % value)

	def getPWM(self, fanid):
		print("[FanControl] Read /proc/stb/fp/fan_pwm")
		return int(open("/proc/stb/fp/fan_pwm").readline().strip(), 16)

	def setPWM(self, fanid, value):
		if value > 255:
			return
		print("[FanControl] Write to /proc/stb/fp/fan_pwm")
		open("/proc/stb/fp/fan_pwm", "w").write("%x" % value)


fancontrol = FanControl()
