# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from enigma import eTimer, eSize


class MessageBox(Screen):
	TYPE_YESNO = 0
	TYPE_INFO = 1
	TYPE_WARNING = 2
	TYPE_ERROR = 3
	TYPE_MESSAGE = 4
	TYPE_PREFIX = {
		TYPE_YESNO: _("Question"),
		TYPE_INFO: _("Information"),
		TYPE_WARNING: _("Warning"),
		TYPE_ERROR: _("Error"),
		TYPE_MESSAGE: _("Message")
	}

	def __init__(self, session, text, type=TYPE_YESNO, timeout=-1, close_on_any_key=False, default=True, enable_input=True, msgBoxID=None, picon=None, simple=False, list=[], timeout_default=None, windowTitle=None, title=None, showYESNO=False):
		self.type = type
		Screen.__init__(self, session)
		self.skinName = ["MessageBox"]
		if simple:
			self.skinName = ["MessageBoxSimple"] + self.skinName

		self.msgBoxID = msgBoxID

		self["text"] = Label(text)
		self["Text"] = StaticText(text)
		self["selectedChoice"] = StaticText()

		self["key_help"] = StaticText(_("HELP"))

		self.text = text
		self.close_on_any_key = close_on_any_key
		self.timeout_default = timeout_default

		self["ErrorPixmap"] = Pixmap()
		self["QuestionPixmap"] = Pixmap()
		self["InfoPixmap"] = Pixmap()
		self["WarningPixmap"] = Pixmap()
		self.timerRunning = False
		self.initTimeout(timeout)

		picon = picon or type
		if picon != self.TYPE_ERROR:
			self["ErrorPixmap"].hide()
		if picon != self.TYPE_YESNO:
			self["QuestionPixmap"].hide()
		if picon != self.TYPE_INFO:
			self["InfoPixmap"].hide()
		if picon != self.TYPE_WARNING:
			self["WarningPixmap"].hide()
		if title is not None:  # Process legacy title argument.
			windowTitle = title
		self.windowTitle = windowTitle or self.TYPE_PREFIX.get(type, _("Message"))
		self.title = title or self.type < self.TYPE_MESSAGE and [_("Question"), _("Information"), _("Warning"), _("Error")][self.type] or _("Message")
		if type == self.TYPE_YESNO or showYESNO:
			if list:
				self.list = list
			elif default:
				self.list = [(_("yes"), True), (_("no"), False)]
			else:
				self.list = [(_("no"), False), (_("yes"), True)]
		else:
			self.list = []

		self["list"] = MenuList(self.list)
		if self.list:
			self["selectedChoice"].setText(self.list[0][0])
		else:
			self["list"].hide()

		if enable_input:
			self.createActionMap(0)

	def initTimeout(self, timeout):
		self.timeout = timeout
		if timeout > 0:
			self.timer = eTimer()
			self.timer.callback.append(self.timerTick)
			self.onExecBegin.append(self.startTimer)
			self.origTitle = None
			if self.execing:
				self.timerTick()
			else:
				self.onShown.append(self.__onShown)
			self.timerRunning = True
		else:
			self.timerRunning = False

	def __onShown(self):
		self.onShown.remove(self.__onShown)
		self.timerTick()

	def startTimer(self):
		self.timer.start(1000)

	def stopTimer(self):
		if self.timerRunning:
			del self.timer
			self.onExecBegin.remove(self.startTimer)
			self.setTitle(self.origTitle, showPath=False)
			self.timerRunning = False

	def timerTick(self):
		if self.execing:
			self.timeout -= 1
			if self.origTitle is None:
				self.origTitle = self.instance.getTitle()
			self.setTitle(self.origTitle + " (" + str(self.timeout) + ")", showPath=False)
			if self.timeout == 0:
				self.timer.stop()
				self.timerRunning = False
				self.timeoutCallback()

	def timeoutCallback(self):
		if self.timeout_default is not None:
			self.close(self.timeout_default)
		else:
			self.ok()

	def cancel(self):
		self.close(False)

	def ok(self):
		if self.list:
			self.close(self["list"].getCurrent()[1])
		else:
			self.close(True)

	def alwaysOK(self):
		self.close(True)

	def up(self):
		self.move(self["list"].instance.moveUp)

	def down(self):
		self.move(self["list"].instance.moveDown)

	def left(self):
		self.move(self["list"].instance.pageUp)

	def right(self):
		self.move(self["list"].instance.pageDown)

	def move(self, direction):
		if self.close_on_any_key:
			self.close(True)
		self["list"].instance.moveSelection(direction)
		if self.list:
			self["selectedChoice"].setText(self["list"].getCurrent()[0])
		self.stopTimer()

	def createActionMap(self, prio):
		if self.list:
			self["actions"] = HelpableActionMap(self, ["MsgBoxActions", "NavigationActions"], {
				"cancel": (self.cancel, _("Select the No / False response")),
				"select": (self.select, _("Return the current selection response")),
				"selectOk": (self.selectOk, _("Select the Yes / True response")),
				"top": (self.top, _("Move to first line")),
				"pageUp": (self.pageUp, _("Move up a page")),
				"up": (self.up, _("Move up a line")),
				# "first": (self.top, _("Move to first line")),
				# "last": (self.bottom, _("Move to last line")),
				"down": (self.down, _("Move down a line")),
				"pageDown": (self.pageDown, _("Move down a page")),
				"bottom": (self.bottom, _("Move to last line"))
			}, prio=prio, description=_("Message Box Actions"))
		else:
			self["actions"] = HelpableActionMap(self, ["OkCancelActions"], {
				"cancel": (self.cancel, _("Close the window")),
				"ok": (self.select, _("Close the window"))
			}, prio=prio, description=_("Message Box Actions"))

	def __repr__(self):
		return "%s(%s)" % (str(type(self)), self.text if hasattr(self, "text") else "<title>")

	def getListWidth(self):
		return self["list"].instance.getMaxItemTextWidth()

	def reloadLayout(self):
		for method in self.onLayoutFinish:
			if not isinstance(method, type(self.close)):
				exec(method, globals(), locals())
			else:
				method()
		self.layoutFinished()


class ModalMessageBox:
	instance = None
	def __init__(self, session):
		if ModalMessageBox.instance:
			print("[ModalMessageBox] Error: Only one ModalMessageBox instance is allowed!")
		else:
			ModalMessageBox.instance = self
			self.dialog = session.instantiateDialog(MessageBox, "", enableInput=False, skinName="MessageBoxModal")
			self.dialog.setAnimationMode(0)
	def showMessageBox(self, text=None, timeout=-1, list=None, default=True, closeOnAnyKey=False, timeoutDefault=None, windowTitle=None, msgBoxID=None, typeIcon=MessageBox.TYPE_YESNO, enableInput=True, callback=None):
		self.dialog.text = text
		self.dialog["text"].setText(text)
		self.dialog.typeIcon = typeIcon
		self.dialog.type = typeIcon
		self.dialog.picon = (typeIcon != MessageBox.TYPE_NOICON)  # Legacy picon argument to support old skins.
		if typeIcon == MessageBox.TYPE_YESNO:
			self.dialog.list = [(_("Yes"), True), (_("No"), False)] if list is None else list
			self.dialog["list"].setList(self.dialog.list)
			if isinstance(default, bool):
				self.dialog.startIndex = 0 if default else 1
			elif isinstance(default, int):
				self.dialog.startIndex = default
			else:
				print(f"[MessageBox] Error: The context of the default ({default}) can't be determined!")
			self.dialog["list"].show()
		else:
			self.dialog["list"].hide()
			self.dialog.list = None
		self.callback = callback
		self.dialog.timeout = timeout
		self.dialog.msgBoxID = msgBoxID
		self.dialog.enableInput = enableInput
		if enableInput:
			self.dialog.createActionMap(-20)
			self.dialog["actions"].execBegin()
		self.dialog.closeOnAnyKey = closeOnAnyKey
		self.dialog.timeoutDefault = timeoutDefault
		self.dialog.windowTitle = windowTitle or self.dialog.TYPE_PREFIX.get(type, _("Message"))
		self.dialog.baseTitle = self.dialog.windowTitle
		self.dialog.activeTitle = self.dialog.windowTitle
		self.dialog.reloadLayout()
		self.dialog.close = self.close
		self.dialog.show()
	def close(self, *retVal):
		if self.callback and callable(self.callback):
			self.callback(*retVal)
		if self.dialog.enableInput:
			self.dialog["actions"].execEnd()
		self.dialog.hide()
