# -*- coding: utf-8 -*-
from os import listdir
from os.path import exists, getsize, isdir, join
from re import sub
from enigma import ePixmap, ePicLoad, eServiceReference
from Components.config import config, ConfigSubsection, ConfigSelection
from Components.Harddisk import harddiskmanager
from Components.Renderer.Renderer import Renderer
from Tools.Alternatives import GetWithAlternative
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename, sanitizeFilename

config.picon = ConfigSubsection()
config.picon.foldername = ConfigSelection(default="1", choices=[
		("1", _("picon")),
		("2", _("ZZPicon")),
		("3", _("XPicon"))
	])

class PiconLocator:
	def __init__(self, piconDirectories=["picon"]):
		harddiskmanager.on_partition_list_change.append(self.onPartitionChange)
		if config.picon.foldername.value == "1":
			self.piconDirectories = piconDirectories
		if config.picon.foldername.value == "2":
			self.piconDirectories = ["ZZPicon"]
		elif config.picon.foldername.value == "3":
			self.piconDirectories = ["XPicon"]
		else:
			self.piconDirectories = piconDirectories
		self.activePiconPath = None
		self.searchPaths = []
		for mp in ("/usr/share/enigma2/", "/"):
			self.onMountpointAdded(mp)
		for part in harddiskmanager.getMountedPartitions():
			mp = join(part.mountpoint, "usr/share/enigma2")
			self.onMountpointAdded(part.mountpoint)
			self.onMountpointAdded(mp)


	def onMountpointAdded(self, mountpoint):
		for piconDirectory in self.piconDirectories:
			try:
				path = join(mountpoint, piconDirectory) + "/"
				if isdir(path) and path not in self.searchPaths:
					for fn in listdir(path):
						if fn.endswith(".png") or fn.endswith(".svg"):
							print(f"[Picon] adding path: {path}")
							self.searchPaths.append(path)
							break
			except Exception as err:
				print(f"[Picon] Failed to investigate {mountpoint}:{str(err)}")

	def onMountpointRemoved(self, mountpoint):
		for piconDirectory in self.piconDirectories:
			path = join(mountpoint, piconDirectory) + "/"
			try:
				self.searchPaths.remove(path)
				print(f"[Picon] removed path: {path}")
			except Exception:
				pass

	def onPartitionChange(self, why, part):
		if why == "add":
			self.onMountpointAdded(part.mountpoint)
		elif why == "remove":
			self.onMountpointRemoved(part.mountpoint)

	def findPicon(self, service):
		if self.activePiconPath is not None:
			for ext in (".png", ".svg"):
				pngname = f"{self.activePiconPath}{service}{ext}"
				return pngname if exists(pngname) else ""
		else:
			for path in self.searchPaths:
				for ext in (".png", ".svg"):
					pngname = f"{path}{service}{ext}"
					if exists(pngname):
						self.activePiconPath = path
						return pngname
		return ""

	def addSearchPath(self, value):
		if exists(value):
			if not value.endswith("/"):
				value += "/"
			if not value.startswith("/media/net") and not value.startswith("/media/autofs") and value not in self.searchPaths:
				self.searchPaths.append(value)

	def getPiconName(self, serviceRef):
		if serviceRef is None:
			return ""
		# remove the path and name fields, and replace ":" by "_"
		fields = GetWithAlternative(serviceRef).split(":", 10)[:10]
		if not fields or len(fields) < 10:
			return ""
		pngname = self.findPicon("_".join(fields))
		if not pngname and not fields[6].endswith("0000"):
			#remove "sub-network" from namespace
			fields[6] = fields[6][:-4] + "0000"
			pngname = self.findPicon("_".join(fields))
		if not pngname and fields[0] != "1":
			#fallback to 1 for IPTV streams
			fields[0] = "1"
			pngname = self.findPicon("_".join(fields))
		if not pngname and fields[2] != "1":
			#fallback to 1 for TV services with non-standard service types. And radio services.
			fields[2] = "1"
			pngname = self.findPicon("_".join(fields))
		if not pngname:  # picon by channel name
			if (sname := eServiceReference(serviceRef).getServiceName().replace('\x80', '').replace('\x86', '').replace('\x87', '')) and "SID 0x" not in sname and (utf8_name := sanitizeFilename(sname).lower()) and utf8_name != "__":  # avoid lookups on zero length service names
				legacy_name = sub("[^a-z0-9]", "", utf8_name.replace("&", "and").replace("+", "plus").replace("*", "star"))  # legacy ascii service name picons
				pngname = self.findPicon(utf8_name) or legacy_name and self.findPicon(legacy_name) or self.findPicon(sub(r"(fhd|uhd|hd|sd|4k)$", "", utf8_name).strip()) or legacy_name and self.findPicon(sub(r"(fhd|uhd|hd|sd|4k)$", "", legacy_name).strip())
				if not pngname and len(legacy_name) > 6:
					series = sub(r"s[0-9]*e[0-9]*$", "", legacy_name)
					pngname = self.findPicon(series)
		if not pngname:  # picon default
			tmp = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png") # picon_default in current active skin
			tmp2 = self.findPicon("picon_default") # picon_default in picon folder
			if exists(tmp2):
				pngname = tmp2
			else:
				if exists(tmp):
					pngname = tmp
				else:
					pngname = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
		return pngname


piconLocator = None


def initPiconPaths():
	global piconLocator
	piconLocator = PiconLocator()


initPiconPaths()


def getPiconName(serviceRef):
	return piconLocator.getPiconName(serviceRef)


class Picon(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.pngname = None
		self.defaultpngname = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
		self.usePicLoad = False
		self.PicLoad = ePicLoad()
		self.PicLoad.PictureData.get().append(self.updatePicon)
		self.piconsize = (0, 0)
		self.service_text = ""
		self.lastPath = None
		self.showPicon = True

	def addPath(self, value):
		if pathExists(value):
			if not value.endswith('/'):
				value += '/'
			if value not in piconLocator.searchPaths:
				piconLocator.searchPaths.append(value)

	def applySkin(self, desktop, parent):
		attribs = self.skinAttributes[:]
		for (attrib, value) in self.skinAttributes:
			if attrib == "path":
				self.addPath(value)
				attribs.remove((attrib, value))
			elif attrib == "isFrontDisplayPicon":
				self.showPicon = value == "0"
				attribs.remove((attrib, value))
			elif attrib == "usePicLoad":
				self.usePicLoad = value == "1"
				attribs.remove((attrib, value))
			elif attrib == "size":
				self.piconsize = value
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def updatePicon(self, picInfo=None):
		ptr = self.PicLoad.getData()
		if ptr is not None and self.instance:
			self.instance.setPixmap(ptr.__deref__())
			self.instance.show()

	def changed(self, what):
		if self.instance:
			if self.showPicon or config.usage.show_picon_in_display.value:
				pngname = ""
				if what[0] in (self.CHANGED_ALL, self.CHANGED_SPECIFIC):
					if self.usePicLoad and self.source.text and self.service_text and self.source.text == self.service_text:
						return
					self.service_text = self.source.text
					pngname = piconLocator.getPiconName(self.source.text)
				else:
					if what[0] == self.CHANGED_CLEAR:
						self.service_text = self.pngname = ""
						if self.visible:
							self.instance.hide()
					return
				if not pngname:  # no picon for service found
					pngname = self.defaultpngname
				if self.pngname != pngname:
					if pngname:
						if self.usePicLoad:
							self.PicLoad.setPara((self.piconsize[0], self.piconsize[1], 0, 0, 1, 1, "#FF000000"))
							self.PicLoad.startDecode(pngname)
						else:
							self.instance.setScale(1)
							self.instance.setPixmapFromFile(pngname)
							self.instance.show()
					else:
						self.instance.hide()
					self.pngname = pngname
			elif self.visible:
				self.instance.hide()
