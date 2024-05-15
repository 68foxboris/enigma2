# -*- coding: utf-8 -*-
import os
from Tools.Directories import SCOPE_SKINS, resolveFilename
from Tools.StbHardware import getFPVersion, getBoxProc
from Components.SystemInfo import BoxInfo

fp_version = str(getFPVersion())
procmodel = getBoxProc()


class RcModel:
	def __init__(self):
		self.model = BoxInfo.getItem("model")

	def getRcFile(self, ext):
		remote = BoxInfo.getItem("rcname")
		if self.model == "et9x00" and not procmodel == "et9500":
			remote = "et9x00"
		elif procmodel == "et9500":
			remote = "et9500"
		elif self.model in ("et5x00", "et6x00") and not procmodel == "et6500":
			remote = "et6x00"
		elif procmodel == "et6500":
			remote = "et6500"
		elif self.model == "azboxhd" and not procmodel in ("elite", "ultra"):
			remote = "azboxhd"
		elif procmodel in ("elite", "ultra"):
			remote = "azboxelite"
		elif self.model == "ventonhdx" or procmodel == "ini-3000" and fp_version.startswith('1'):
			remote = "ini0"
		elif procmodel in ("ini-5000", "ini-7000", "ini-7012"):
			remote = "ini1"
		elif self.model == "ventonhdx" or procmodel == "ini-3000" and not fp_version.startswith('1'):
			remote = "ini2"
		f = resolveFilename(SCOPE_SKINS, 'rc_models/' + remote + '.' + ext)
		if not os.path.exists(f):
			f = resolveFilename(SCOPE_SKINS, 'rc_models/dmm1.' + ext)
		return f

	def getRcImg(self):
		return self.getRcFile('png')

	def getRcPositions(self):
		return self.getRcFile('xml')


rc_model = RcModel()
