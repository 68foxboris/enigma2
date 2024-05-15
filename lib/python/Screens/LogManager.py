# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.GUIComponent import GUIComponent
from Components.VariableText import VariableText
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Components.MenuList import MenuList
from Components.config import config, configfile
from Components.FileList import MultiFileSelectList
from Screens.MessageBox import MessageBox
from os import remove, walk, stat, rmdir, listdir
from os.path import join, getsize, isdir, exists
from time import time, ctime, sleep
from enigma import eTimer, eBackgroundFileEraser, eLabel, getDesktop, gFont, fontRenderClass
from Tools.TextBoundary import getTextBoundarySize

import Components.Task
import sys

_session = None

def get_size(start_path=None):
	total_size = 0
	if start_path:
		for dirpath, dirnames, filenames in walk(start_path):
			for f in filenames:
				fp = join(dirpath, f)
				total_size += getsize(fp)
		return total_size
	return 0

def AutoLogManager(session=None, **kwargs):
	global debuglogcheckpoller
	debuglogcheckpoller = LogManagerPoller()
	debuglogcheckpoller.start()


class LogManagerPoller:
	"""Automatically Poll LogManager"""

	def __init__(self):
		# Init Timer
		self.TrimTimer = eTimer()
		self.TrashTimer = eTimer()

	def start(self):
		if self.TrashTimerJob not in self.TrashTimer.callback:
			self.TrashTimer.callback.append(self.TrashTimerJob)
		self.TrashTimer.startLongTimer(0)

	def stop(self):
		if self.TrashTimerJob in self.TrashTimer.callback:
			self.TrashTimer.callback.remove(self.TrashTimerJob)
		self.TrashTimer.stop()

	def TrashTimerJob(self):
		print("[LogManager] Trash Poll Started")
		Components.Task.job_manager.AddJob(self.createTrashJob())

	def createTrashJob(self):
		job = Components.Task.Job(_("LogManager"))
		task = Components.Task.PythonTask(job, _("Checking Logs..."))
		task.work = self.JobTrash
		task.weighting = 1
		return job

	def openFiles(self, ctimeLimit, allowedBytes):
		ctimeLimit = ctimeLimit
		allowedBytes = allowedBytes

	def JobTrash(self):
		try:
			sys.set_int_max_str_digits(0)
		except AttributeError:
			pass
		ctimeLimit = int(time()) - int(config.crash.daysloglimit.value * 3600 * 24)
		allowedBytes = 1024 * 1024 * int(config.crash.sizeloglimit.value)

		mounts = []
		matches = []
		print("[LogManager] probing folders")
		with open("/proc/mounts") as f:
			for line in f.readlines():
				parts = line.strip().split()
				mounts.append(parts[1])

		for mount in mounts:
			if isdir(join(mount, "logs")):
				matches.append(join(mount, "logs"))
		matches.append("/home/root/logs")

		print("[LogManager] found following log(s):", matches)
		if len(matches):
			for logsfolder in matches:
				print("[LogManager] looking in:", logsfolder)
				logssize = get_size(logsfolder)
				bytesToRemove = logssize - allowedBytes
				candidates = []
				size = 0
				for root, dirs, files in walk(logsfolder, topdown=False):
					for name in files:
						try:
							fn = join(root, name)
							st = stat(fn)
							if st.st_ctime < ctimeLimit:
								print("[LogManager] " + str(fn) + ": Too old:", name, st.st_ctime)
								eBackgroundFileEraser.getInstance().erase(fn)
								bytesToRemove -= st.st_size
							else:
								candidates.append((st.st_ctime, fn, st.st_size))
								size += st.st_size
						except Exception as e:
							print("[LogManager] Failed to stat %s:" % name, e)
					# Remove empty directories if possible
					for name in dirs:
						try:
							rmdir(join(root, name))
						except:
							pass
					candidates.sort()
					# Now we have a list of ctime, candidates, size. Sorted by ctime (=deletion time)
					for st_ctime, fn, st_size in candidates:
						print("[LogManager] " + str(logsfolder) + ": bytesToRemove", bytesToRemove)
						if bytesToRemove < 0:
							break
						eBackgroundFileEraser.getInstance().erase(fn)
						bytesToRemove -= st_size
						size -= st_size
		self.TrashTimer.startLongTimer(43200)  # twice a day


class LogManager(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.logs = listdir(config.crash.debug_path.value)
		self.logtype = 'crashlogs'
		self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'],
			{
				'ok': self.changeSelectionState,
				'cancel': self.close,
				'red': self.changelogtype,
				'green': self.showLog,
				'yellow': self.deletelog,
				"blue": self.deleteAllLogs,
				"left": self.left,
				"right": self.right,
				"down": self.down,
				"up": self.up
			}, -1)

		if self.logs:
			self["key_red"] = StaticText(_("Debug Logs"))
			self["key_green"] = StaticText(_("View"))
			self["key_yellow"] = StaticText(_("Delete"))
			self["key_blue"] = StaticText(_("Delete all"))
		else:
			self["key_red"] = StaticText("")
			self["key_green"] = StaticText("")
			self["key_yellow"] = StaticText("")
			self["key_blue"] = StaticText("")
		self.onChangedEntry = []
		self.sentsingle = ""
		self.selectedFiles = config.logmanager.sentfiles.value
		self.previouslySent = config.logmanager.sentfiles.value
		self.defaultDir = config.crash.debug_path.value
		self.matchingPattern = '(-enigma-crash.log|enigma2-crash)'
		self.filelist = MultiFileSelectList(self.selectedFiles, self.defaultDir, showDirectories=False, matchingPattern=self.matchingPattern)
		self["list"] = self.filelist
		self["LogsSize"] = self.logsinfo = LogInfo(config.crash.debug_path.value, LogInfo.USED, update=False)
		self.onLayoutFinish.append(self.layoutFinished)
		if not self.selectionChanged in self["list"].onSelectionChanged:
			self["list"].onSelectionChanged.append(self.selectionChanged)

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary
		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["list"].getCurrent()
		desc = ""
		if item:
			name = str(item[0][0])
		else:
			name = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def layoutFinished(self):
		self["LogsSize"].update(config.crash.debug_path.value)
		idx = 0
		self["list"].moveToIndex(idx)
		self.setWindowTitle()

	def setWindowTitle(self):
		self.setTitle(self.defaultDir)

	def up(self):
		self["list"].up()

	def down(self):
		self["list"].down()

	def left(self):
		self["list"].pageUp()

	def right(self):
		self["list"].pageDown()

	def saveSelection(self):
		self.selectedFiles = self["list"].getSelectedList()
		config.logmanager.sentfiles.setValue(self.selectedFiles)
		config.logmanager.sentfiles.save()
		configfile.save()

	def exit(self):
		self.close(None)

	def changeSelectionState(self):
		try:
			self.sel = self["list"].getCurrent()[0]
		except:
			self.sel = None
		if self.sel:
			self["list"].changeSelectionState()
			self.selectedFiles = self["list"].getSelectedList()

	def changelogtype(self):
		self["LogsSize"].update(config.crash.debug_path.value)
		import re
		if self.logtype == "crashlogs":
			self["key_red"].setText(_("Crash Logs"))
			self.logtype = "debuglogs"
			self.matchingPattern = '(Enigma2|enigma2-debug)'
		else:
			self["key_red"].setText(_("Debug Logs"))
			self.logtype = "crashlogs"
			self.matchingPattern = '(-enigma-crash.log|enigma2-crash)'
		self["list"].matchingPattern = re.compile(self.matchingPattern)
		self["list"].changeDir(self.defaultDir)
		if not listdir(config.crash.debug_path.value):
			self["key_red"].setText("")
			self["key_green"].setText("")
			self["key_yellow"].setText("")

	def showLog(self):
		if self.logs:
			try:
				self.sel = self["list"].getCurrent()[0]
			except:
				self.sel = None
			if self.sel:
				self.session.open(LogManagerViewLog, self.sel[0])
			else:
				self.session.open(MessageBox, _("You have not selected any logs to view."), MessageBox.TYPE_INFO, timeout=10)

	def deletelog(self):
		if self.logs:
			try:
				self.sel = self["list"].getCurrent()[0]
			except:
				self.sel = None
			self.selectedFiles = self["list"].getSelectedList()
			if self.selectedFiles:
				message = _("Do you want to delete all the selected files?\n\nchoose \"No\" to only delete the currently selected file.")
				ybox = self.session.openWithCallback(self.doDelete1, MessageBox, message, MessageBox.TYPE_YESNO)
				ybox.setTitle(_("Delete Confirmation"))
			elif self.sel:
				message = _("You want to delete this log?\n\n") + str(self.sel[0])
				ybox = self.session.openWithCallback(self.doDelete3, MessageBox, message, MessageBox.TYPE_YESNO)
				ybox.setTitle(_("Delete Confirmation"))
			else:
				self.session.open(MessageBox, _("You have not selected any logs to delete."), MessageBox.TYPE_INFO, timeout=10)

	def deleteAllLogs(self):
		if self.logs:
			allfiles = ",".join(self.logs).replace(",", "\n")
			message = _("You want to delete all files?\n\n") + str(allfiles)
			self.session.openWithCallback(self.doDeleteAllLogs, MessageBox, message, MessageBox.TYPE_YESNO)

	def doDeleteAllLogs(self, answer):
		if answer:
			from enigma import eConsoleAppContainer
			eConsoleAppContainer().execute("rm -f " + config.crash.debug_path.value + "*")
			sleep(0.3)
			self["list"].changeDir(self.defaultDir)
			self["LogsSize"].update(config.crash.debug_path.value)
			self["key_red"].setText("")
			self["key_green"].setText("")
			self["key_yellow"].setText("")
			self["key_blue"].setText("")

	def doDelete1(self, answer):
		self.selectedFiles = self["list"].getSelectedList()
		self.selectedFiles = ",".join(self.selectedFiles).replace(",", "\n").replace(config.crash.debug_path.value, "")
		self.sel = self["list"].getCurrent()[0]
		if answer is True:
			message = _("You want to delete all the selected logs?\n\n") + self.selectedFiles
			ybox = self.session.openWithCallback(self.doDelete2, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle(_("Delete Confirmation"))
		else:
			message = _("You want to delete this log?\n\n") + str(self.sel[0])
			ybox = self.session.openWithCallback(self.doDelete3, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle(_("Delete Confirmation"))

	def doDelete2(self, answer):
		if answer is True:
			self.selectedFiles = self["list"].getSelectedList()
			self["list"].instance.moveSelectionTo(0)
			for file in self.selectedFiles:
				if exists(file):
					remove(file)
					self.changelogtype()
			config.logmanager.sentfiles.setValue("")
			config.logmanager.sentfiles.save()
			configfile.save()
			self["list"].changeDir(self.defaultDir)

	def doDelete3(self, answer):
		if answer is True:
			self.sel = self["list"].getCurrent()[0]
			self["list"].instance.moveSelectionTo(0)
			if exists(self.defaultDir + self.sel[0]):
				remove(self.defaultDir + self.sel[0])
				self.changelogtype()
			self["list"].changeDir(self.defaultDir)
			self["LogsSize"].update(config.crash.debug_path.value)


class LogManagerViewLog(Screen):
	def __init__(self, session, selected):
		Screen.__init__(self, session)
		self.session = session
		self.setTitle(selected)
		self.logfile = config.crash.debug_path.value + selected
		self.log = []
		self["list"] = MenuList(self.log)
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
		{
			"ok": self.gotoFirstPage,
			"cancel": self.cancel,
			"red": self.gotoFirstPage,
			"green": self["list"].pageDown,
			"yellow": self["list"].pageUp,
			"blue": self.gotoLastPage,
			"up": self["list"].up,
			"down": self["list"].down,
			"right": self["list"].pageDown,
			"left": self["list"].pageUp,
			"moveUp": self.gotoFirstPage,
			"moveDown": self.gotoLastPage
		}, -2)
		self["key_red"] = StaticText(_("First page"))
		self["key_green"] = StaticText(_("Page forward"))
		self["key_yellow"] = StaticText(_("Page back"))
		self["key_blue"] = StaticText(_("Last page"))
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		font = gFont("Console", 25)
		if not int(fontRenderClass.getInstance().getLineHeight(font)):
			font = gFont("Regular")
		self["list"].instance.setFont(font)
		fontwidth = getTextBoundarySize(self.instance, font, self["list"].instance.size(), _(" ")).width()
		listwidth = int(self["list"].instance.size().width() / fontwidth) - 2
		if exists(self.logfile):
			try:
				for line in open(self.logfile).readlines():
					line = line.replace("\t", " " * 9)
					if len(line) > listwidth:
						pos = 0
						offset = 0
						readyline = True
						while readyline:
							a = " " * offset + line[pos:pos + listwidth - offset]
							self.log.append(a)
							if len(line[pos + listwidth - offset:]):
								pos += listwidth - offset
								offset = 19
							else:
								readyline = False
					else:
						self.log.append(line)
			except UnicodeDecodeError:
				for line in open(self.logfile, encoding="ISO 8859-1").readlines():
					line = line.replace("\t", " " * 9)
					if len(line) > listwidth:
						pos = 0
						offset = 0
						readyline = True
						while readyline:
							a = " " * offset + line[pos:pos + listwidth - offset]
							self.log.append(a)
							if len(line[pos + listwidth - offset:]):
								pos += listwidth - offset
								offset = 19
							else:
								readyline = False
					else:
						self.log.append(line)
		else:
			self.log = [_("File can not displayed - File not found")]
		self["list"].setList(self.log)

	def gotoFirstPage(self):
		self["list"].moveToIndex(0)

	def gotoLastPage(self):
		self["list"].moveToIndex(len(self.log) - 1)

	def cancel(self):
		self.close()


class LogInfo(VariableText, GUIComponent):
	FREE = 0
	USED = 1
	SIZE = 2

	def __init__(self, path, type, update=True):
		GUIComponent.__init__(self)
		VariableText.__init__(self)
		self.logs = listdir(path)
		self.type = type
# 		self.path = config.crash.debug_path.value
		if update:
			self.update(path)

	def update(self, path):
		try:
			total_size = get_size(path)
		except OSError:
			return -1

		if self.type == self.USED:
			try:
				if total_size < 10000000:
					total_size = _("%d kB") % (total_size >> 10)
				elif total_size < 10000000000:
					total_size = _("%d MB") % (total_size >> 20)
				else:
					total_size = _("%d GB") % (total_size >> 30)
				self.setText(_("Exist are debug or crash files.\nSpace used:") + " " + total_size) if self.logs and get_size(path) > 0 else self.setText(_("Exist are no debug files or crash."))
			except:
				# occurs when f_blocks is 0 or a similar error
				self.setText("-?-")

	GUI_WIDGET = eLabel
