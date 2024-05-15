from os.path import isfile, join

from enigma import ePixmap, iServiceInformation

from Components.Renderer.Renderer import Renderer
from Tools.Directories import SCOPE_GUISKIN, resolveFilename, fileReadLines

MODULE_NAME = __name__.split(".")[-1]


class PicEmu2(Renderer):
	__module__ = __name__
	searchPaths = ("/usr/share/enigma2/", "/media/hdd/", "/media/usb/", "/media/ba/")
	camds = {
		"ChID": "wicardd",
		"chid": "oscam",
		"Sign": "mgcamd",
		"hops": "cccam"
	}
	ncam = {
		"chid": "ncam"
	}

	def __init__(self):
		Renderer.__init__(self)
		self.path = "emu"
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
		from process import ProcessList
		ncam = str(ProcessList().named("ncam")).strip("[]")
		lines = []
		try:
			for line in fileReadLines("/tmp/ecm.info", lines, source=MODULE_NAME):
				if not ncam:
					for caid in caids:
						sName = self.camds.get(line[0:4])
						if sName:
							return sName
				else:
					for caid in caids:
						sName = self.ncam.get(line[0:4])
						if sName:
							return sName
		except IOError as err:
			print("[PicEmu2] %s" % err)

	def findPicon(self, serviceName):
		for path in self.searchPaths:
			pngName = join(path, self.path, "%s.png" % serviceName)
			if isfile(pngName):
				return pngName
		return ""
