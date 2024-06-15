# -*- coding: utf-8 -*-
from enigma import eTimer

from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import MultiPixmap, Pixmap
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen, ScreenSummary


class MessageBox(Screen):
	skin = """
	<screen name="MessageBox" position="center,center" size="520,225" resolution="1280,720">
		<widget name="icon" pixmaps="icons/input_question.png,icons/input_info.png,icons/input_warning.png,icons/input_error.png,icons/input_message.png" position="10,10" size="53,53" alphaTest="blend" conditional="icon" scale="1" transparent="1" />
		<widget name="text" position="75,10" size="435,55" font="Regular;22" transparent="1" />
		<widget name="list" position="10,75" size="500,140" conditional="list" enableWrapAround="1" font="Regular;25" itemHeight="35" scrollbarMode="showOnDemand" transparent="1" />
	</screen>"""

	TYPE_NOICON = 0
	TYPE_YESNO = 1
	TYPE_INFO = 2
	TYPE_WARNING = 3
	TYPE_ERROR = 4
	TYPE_MESSAGE = 5
	TYPE_PREFIX = {
		TYPE_YESNO: _("Question"),
		TYPE_INFO: _("Information"),
		TYPE_WARNING: _("Warning"),
		TYPE_ERROR: _("Error"),
		TYPE_MESSAGE: _("Message")
	}

	def __init__(self, session, text, type=TYPE_YESNO, timeout=-1, list=None, default=True, closeOnAnyKey=False, enableInput=True, msgBoxID=None, typeIcon=None, timeoutDefault=None, windowTitle=None, skinName=None, close_on_any_key=False, enable_input=True, timeout_default=None, title=None, picon=None, skin_name=None, simple=None):
		Screen.__init__(self, session, enableHelp=True)
		self.timerRunning = False
		self["autoresize"] = Label("")
		self.text = text
		self["text"] = Label(text)
		self.type = type
		if type == self.TYPE_YESNO:
			self.list = [(_("Yes"), True), (_("No"), False)] if list is None else list
			self["list"] = MenuList(self.list)
			if isinstance(default, int):
				self["list"].moveToIndex(default)
			elif default in (True, False):
				self["list"].moveToIndex(0 if default else 1)
			else:
				print("[MessageBox] Error: The context of the default (%s) can't be determined!" % default)
		else:
			self.list = []
			self["list"] = MenuList([])
			self["list"].hide()
		self.timeout = timeout
		if close_on_any_key == True:  # Process legacy close_on_any_key argument.
			closeOnAnyKey = True
		self.closeOnAnyKey = closeOnAnyKey
		if enable_input == False:  # Process legacy enable_input argument.
			enableInput = False
		if enableInput:
			if self.list:
				self["actions"] = HelpableActionMap(self, ["MsgBoxActions", "NavigationActions", "DirectionActions"], {
					"cancel": (self.cancel, _("Select the No / False response")),
					"select": (self.select, _("Return the current selection response")),
					"selectOk": (self.selectOk, _("Select the Yes / True response")),
					"top": (self.top, _("Move to first line")),
					"pageUp": (self.pageUp, _("Move up a page")),
					"up": (self.up, _("Move up a line")),
					"upUp": self.doNothing,
					"left": (self.pageUp, _("Move up a page")),
					"right": (self.pageDown, _("Move down a page")),
					# "first": (self.top, _("Move to first line")),
					# "last": (self.bottom, _("Move to last line")),
					"down": (self.down, _("Move down a line")),
					"downUp": self.doNothing,
					"leftUp": self.pageUp,
					"rightUp": self.pageDown,
					"pageDown": (self.pageDown, _("Move down a page")),
					"bottom": (self.bottom, _("Move to last line"))
				}, prio=0, description=_("Message Box Actions"))
			else:
				self["actions"] = HelpableActionMap(self, ["OkCancelActions"], {
					"cancel": (self.cancel, _("Close the window")),
					"ok": (self.select, _("Close the window"))
				}, prio=0, description=_("Message Box Actions"))
		self.msgBoxID = msgBoxID
		if picon is not None:  # Process legacy picon argument.
			typeIcon = picon
		if typeIcon is None:
			typeIcon = type
		self.typeIcon = typeIcon
		self.picon = (typeIcon != self.TYPE_NOICON)  # Legacy picon argument to support old skins.
		if typeIcon:
			self["icon"] = MultiPixmap()  # These line can go with new skins that only use self["icon"]...
			self["QuestionPixmap"] = Pixmap()  # These lines are to be compatible with the old Pixmaps.
			self["QuestionPixmap"].hide()
			self["InfoPixmap"] = Pixmap()
			self["InfoPixmap"].hide()
			self["WarningPixmap"] = Pixmap()
			self["WarningPixmap"].hide()
			self["ErrorPixmap"] = Pixmap()
			self["ErrorPixmap"].hide()
			if typeIcon == self.TYPE_YESNO:
				self["QuestionPixmap"].show()
			elif typeIcon == self.TYPE_WARNING:
				self["WarningPixmap"].show()
			elif typeIcon == self.TYPE_INFO:
				self["InfoPixmap"].show()
			elif typeIcon == self.TYPE_ERROR:
				self["ErrorPixmap"].show()
		if timeout_default is not None:  # Process legacy timeout_default argument.
			timeoutDefault = timeout_default
		self.timeoutDefault = timeoutDefault
		if title is not None:  # Process legacy title argument.
			windowTitle = title
		self.windowTitle = windowTitle or self.TYPE_PREFIX.get(type, _("Message"))
		self.baseTitle = self.windowTitle
		self.activeTitle = self.windowTitle
		if skin_name is not None:  # Process legacy skin_name argument.
			skinName = skin_name
		self.skinName = ["MessageBox"]
		if simple:  # Process legacy simple argument, use skinName instead.
			self.skinName.insert(0, "MessageBoxSimple")
		if skinName:
			if isinstance(skinName, str):
				self.skinName.insert(0, skinName)
			else:
				self.skinName = skinName + self.skinName
		self.timer = eTimer()
		self.timer.callback.append(self.processTimer)
		self.onLayoutFinish.append(self.layoutFinished)

	def __repr__(self):
		return "%s(%s)" % (str(type(self)), self.text if hasattr(self, "text") else "<title>")

	def layoutFinished(self):
		if self.list:
			self["list"].enableAutoNavigation(False)  # Override listbox navigation.
			# self["list"].moveToIndex(self.startIndex)
		if self.typeIcon:
			self["icon"].setPixmapNum(self.typeIcon - 1)
		prefix = self.TYPE_PREFIX.get(self.type, _("Unknown"))
		if self.baseTitle is None:
			title = self.getTitle()
			if title:
				self.baseTitle = title % prefix if "%s" in title else title
			else:
				self.baseTitle = prefix
		elif "%s" in self.baseTitle:
			self.baseTitle = self.baseTitle % prefix
		self.setTitle(self.baseTitle, showPath=False)
		if self.timeout > 0:
			print("[MessageBox] Timeout set to %d seconds." % self.timeout)
			self.timer.start(25)

	def processTimer(self):
		if self.activeTitle is None:  # Check if the title has been externally changed and if so make it the dominant title.
			self.activeTitle = self.getTitle()
			if "%s" in self.activeTitle:
				self.activeTitle = self.activeTitle % self.TYPE_PREFIX.get(self.type, _("Unknown"))
		if self.baseTitle != self.activeTitle:
			self.baseTitle = self.activeTitle
		if self.timeout > 0:
			if self.baseTitle:
				self.setTitle("%s (%d)" % (self.baseTitle, self.timeout), showPath=False)
			self.timer.start(1000)
			self.timeout -= 1
		else:
			self.stopTimer("Timeout!")
			if self.timeoutDefault is not None:
				self.close(self.timeoutDefault)
			else:
				self.select()

	def stopTimer(self, reason):
		print("[MessageBox] %s" % reason)
		self.timer.stop()
		self.timeout = 0
		if self.baseTitle is not None:
			self.setTitle(self.baseTitle, showPath=False)

	def cancel(self):
		self.close(False)

	def select(self):
		if self.list:
			self.close(self["list"].getCurrent()[1])
		else:
			self.close(True)

	def selectOk(self):
		self.close(True)

	def top(self):
		self.move(self["list"].instance.moveTop)

	def pageUp(self):
		self.move(self["list"].instance.pageUp)

	def up(self):
		self.move(self["list"].instance.moveUp)

	def down(self):
		self.move(self["list"].instance.moveDown)

	def pageDown(self):
		self.move(self["list"].instance.pageDown)

	def doNothing(self):
		pass

	def bottom(self):
		self.move(self["list"].instance.moveEnd)

	def move(self, step):
		self["list"].instance.moveSelection(step)
		if self.timeout > 0:
			self.stopTimer("Timeout stopped by user input!")
		if self.closeOnAnyKey:
			self.close(True)

	def autoResize(self):  # Dummy method place holder for some legacy skins.
		pass

	def getListWidth(self):  # keep text autoresize compatible for others skins MessageBoxSimple.
		def getListLineTextWidth(text):
			self["autoresize"].setText(text)
			return self["autoresize"].getSize()[0]
		return max([getListLineTextWidth(line[0]) for line in self.list]) if self.list else 0

	def createSummary(self):
		return MessageBoxSummary


class MessageBoxSummary(ScreenSummary):
	def __init__(self, session, parent):
		ScreenSummary.__init__(self, session, parent=parent)
		self["text"] = StaticText(parent.text)
		self["option"] = StaticText("")
		if hasattr(self, "list"):
			if self.addWatcher not in self.onShow:
				self.onShow.append(self.addWatcher)
			if self.removeWatcher not in self.onHide:
				self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		if self.selectionChanged not in self.parent["list"].onSelectionChanged:
			self.parent["list"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def removeWatcher(self):
		if self.selectionChanged in self.parent["list"].onSelectionChanged:
			self.parent["list"].onSelectionChanged.remove(self.selectionChanged)

	def selectionChanged(self):
		self["option"].setText(self.parent["list"].getCurrent()[0])
