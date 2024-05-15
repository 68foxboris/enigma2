from os.path import isfile, join

from enigma import ePixmap, iServiceInformation

from Components.Renderer.Renderer import Renderer
from Tools.Directories import SCOPE_GUISKIN, resolveFilename, fileReadLines

MODULE_NAME = __name__.split(".")[-1]


class PicCript(Renderer):
	__module__ = __name__
	searchPaths = ("/usr/share/enigma2/", "/media/hdd/", "/media/usb/", "/media/ba/")
	condAccessIds = {
		"26": "BiSS",
		"01": "SEC",
		"10": "SEC",
		"x6": "IRD",
		"06": "IRD",
		"64": "IRD",
		"17": "BET",
		"18": "NAG",
		"05": "VIA",
		"50": "VIA",
		"09": "NDS",
		"9c": "NDS",
		"98": "NDS",
		"0B": "CONN",
		"b0": "CONN",
		"d9": "CRW",
		"0D": "CRW",
		"4A": "DRE",
		"0E": "PowerVU",
		"22": "Codicrypt",
		"07": "DigiCipher",
		"A1": "Rosscrypt",
		"56": "Verimatrix"
	}
	condAccessIdsMgcamd = {
		"26": "BiSS",
		"10": "SEC",
		"x0": "IRD",
		"17": "BET",
		"18": "NAG",
		" 0": "VIA",
		"09": "NDS",
		"0B": "CONN",
		"aI": "CRW",
		"4A": "DRE",
		"0E": "PowerVU",
		"22": "Codicrypt",
		"07": "DigiCipher",
		"A1": "Rosscrypt",
		"56": "Verimatrix"
	}

	def __init__(self):
		Renderer.__init__(self)
		self.path = "cript"
		self.nameCache = {}
		self.pngName = ""
		self.picon_default = "picon_default.png"

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if (attrib == "path"):
				self.path = value
			elif (attrib == "picon_default"):
				self.picon_default = value
			else:
				attribs.append((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			pngName = ""
			if (what[0] != self.CHANGED_CLEAR) and isfile("/tmp/ecm.info"):
				sName = ""
				service = self.source.service
				if service:
					info = service and service.info()
					if info:
						caids = info.getInfoObject(iServiceInformation.sCAIDs)
						if caids and len(caids) > 0:
							sName = self.matchCAId(caids)
				pngName = self.nameCache.get(sName, "")
				if (pngName == ""):
					pngName = self.findPicon(sName)
					if (pngName != ""):
						self.nameCache[sName] = pngName
			if (pngName == ""):
				pngName = self.nameCache.get("default", "")
				if (pngName == ""):
					pngName = self.findPicon("picon_default")
					if (pngName == ""):
						tmp = resolveFilename(SCOPE_GUISKIN, "picon_default.png")
						if isfile(tmp):
							pngName = tmp
						self.nameCache["default"] = pngName
			if (self.pngName != pngName):
				self.pngName = pngName
				self.instance.setPixmapFromFile(self.pngName)

	def matchCAId(self, caids):
		lines = []
		from process import ProcessList
		mgcamd = str(ProcessList().named("mgcamd_1.38")).strip("[]")
		cccam = str(ProcessList().named("CCcam")).strip("[]")
		try:
			for line in fileReadLines("/tmp/ecm.info", lines, source=MODULE_NAME):
				if not mgcamd and not cccam:
					for caid in caids:
						sName = self.condAccessIds.get(line[8:10])
						if sName:
							return sName
				if cccam:
					for caid in caids:
						sName = self.condAccessIds.get(line[14:16])
						if sName:
							return sName
				else:
					for caid in caids:
						sName = self.condAccessIdsMgcamd.get(line[26:28])
						if sName:
							return sName
		except IOError as err:
			print("[PicCript] %s" % err)

	def findPicon(self, serviceName):
		for path in self.searchPaths:
			pngName = join(path, self.path, "%s.png" % serviceName)
			if isfile(pngName):
				return pngName
		return ""
