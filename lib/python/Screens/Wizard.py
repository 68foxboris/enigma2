# -*- coding: utf-8 -*-
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from enigma import eEnv, eTimer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import ACTIONKEY_0, ACTIONKEY_ASCII, ACTIONKEY_BACKSPACE, ACTIONKEY_DELETE, ACTIONKEY_LEFT, ACTIONKEY_RIGHT, ConfigPassword, ConfigText, config

from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Slider import Slider
from Components.ActionMap import NumberActionMap
from Components.MenuList import MenuList
from Components.ConfigList import ConfigList
from Components.Sources.List import List
from Components.SystemInfo import BoxInfo, DISPLAYMODEL
from Tools.Directories import fileWriteLine

BRAND = BoxInfo.getItem("brand")


class WizardSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent)
		self["text"] = StaticText("")
		self.onShow.append(self.setCallback)

	def setCallback(self):
		self.parent.setLCDTextCallback(self.setText)

	def setText(self, text):
		self["text"].setText(text)


class Wizard(Screen):
	instance = None

	def createSummary(self):
		print("[Wizard] In createSummary.")
		return WizardSummary

	class parseWizard(ContentHandler):
		def __init__(self, wizard):
			self.isPointsElement = 0
			self.isReboundsElement = 0
			self.wizard = wizard
			self.currContent = ""
			self.lastStep = 0

		def startElement(self, name, attrs):
			# print("[Wizard] Start element='%s'." % name)
			self.currContent = name
			if name == "step":
				self.lastStep += 1
				if 'id' in attrs:
					id = str(attrs.get('id'))
				else:
					id = ""
				# print("[Wizard] id='%s'." % id)
				if 'nextstep' in attrs:
					nextstep = str(attrs.get('nextstep'))
				else:
					nextstep = None
				if 'timeout' in attrs:
					timeout = int(attrs.get('timeout'))
				else:
					timeout = None
				if 'timeoutaction' in attrs:
					timeoutaction = str(attrs.get('timeoutaction'))
				else:
					timeoutaction = 'nextpage'

				if 'timeoutstep' in attrs:
					timeoutstep = str(attrs.get('timeoutstep'))
				else:
					timeoutstep = ''
				self.wizard[self.lastStep] = {"id": id, "condition": "", "text": "", "timeout": timeout, "timeoutaction": timeoutaction, "timeoutstep": timeoutstep, "list": [], "config": {"screen": None, "args": None, "type": ""}, "code": "", "codeafter": "", "code_async": "", "codeafter_async": "", "nextstep": nextstep}
				if 'laststep' in attrs:
					self.wizard[self.lastStep]["laststep"] = str(attrs.get('laststep'))
			elif name == "text":
				self.wizard[self.lastStep]["text"] = str(attrs.get('value')).replace("\\n", "\n")
			elif name == "displaytext":
				self.wizard[self.lastStep]["displaytext"] = str(attrs.get('value')).replace("\\n", "\n")
			elif name == "list":
				if 'type' in attrs:
					if attrs["type"] == "dynamic":
						self.wizard[self.lastStep]["dynamiclist"] = attrs.get("source")
					# self.wizard[self.lastStep]["list"].append(("Hallo", "test"))
				if "evaluation" in attrs:
					# print("[Wizard] Evaluation.")
					self.wizard[self.lastStep]["listevaluation"] = attrs.get("evaluation")
				if "onselect" in attrs:
					self.wizard[self.lastStep]["onselect"] = attrs.get("onselect")
			elif name == "listentry":
				self.wizard[self.lastStep]["list"].append((str(attrs.get('caption')), str(attrs.get('step'))))
			elif name == "config":
				type = str(attrs.get('type'))
				self.wizard[self.lastStep]["config"]["type"] = type
				if type == "ConfigList" or type == "standalone":
					try:
						exec("from Screens." + str(attrs.get('module')) + " import *")
					except:
						exec("from " + str(attrs.get('module')) + " import *")

					self.wizard[self.lastStep]["config"]["screen"] = eval(str(attrs.get('screen')))
					if 'args' in attrs:
						# print("[Wizard] Has args.")
						self.wizard[self.lastStep]["config"]["args"] = str(attrs.get('args'))
				elif type == "dynamic":
					self.wizard[self.lastStep]["config"]["source"] = str(attrs.get('source'))
					if 'evaluation' in attrs:
						self.wizard[self.lastStep]["config"]["evaluation"] = str(attrs.get('evaluation'))
			elif name == "code":
				self.async_code = 'async' in attrs and str(attrs.get('async')) == "yes"
				if 'pos' in attrs and str(attrs.get('pos')) == "after":
					self.codeafter = True
				else:
					self.codeafter = False
			elif name == "condition":
				pass

		def endElement(self, name):
			self.currContent = ""
			if name == 'code':
				if self.async_code:
					if self.codeafter:
						self.wizard[self.lastStep]["codeafter_async"] = self.wizard[self.lastStep]["codeafter_async"].strip()
					else:
						self.wizard[self.lastStep]["code_async"] = self.wizard[self.lastStep]["code_async"].strip()
				else:
					if self.codeafter:
						self.wizard[self.lastStep]["codeafter"] = self.wizard[self.lastStep]["codeafter"].strip()
					else:
						self.wizard[self.lastStep]["code"] = self.wizard[self.lastStep]["code"].strip()
			elif name == 'condition':
				self.wizard[self.lastStep]["condition"] = self.wizard[self.lastStep]["condition"].strip()
			elif name == 'step':
				# print("[Wizard] Step number %d: '%s'." % (self.lastStep, self.wizard[self.lastStep]))
				pass

		def characters(self, ch):
			if self.currContent == "code":
				if self.async_code:
					if self.codeafter:
						self.wizard[self.lastStep]["codeafter_async"] = self.wizard[self.lastStep]["codeafter_async"] + ch
					else:
						self.wizard[self.lastStep]["code_async"] = self.wizard[self.lastStep]["code_async"] + ch
				else:
					if self.codeafter:
						self.wizard[self.lastStep]["codeafter"] = self.wizard[self.lastStep]["codeafter"] + ch
					else:
						self.wizard[self.lastStep]["code"] = self.wizard[self.lastStep]["code"] + ch
			elif self.currContent == "condition":
				self.wizard[self.lastStep]["condition"] = self.wizard[self.lastStep]["condition"] + ch

	def __init__(self, session, showSteps=True, showStepSlider=True, showList=True, showConfig=True):
		Screen.__init__(self, session)

		self.isLastWizard = False  # Can be used to skip a "goodbye"-screen in a wizard.

		self.stepHistory = []

		self.wizard = {}
		parser = make_parser()
		if not isinstance(self.xmlfile, list):
			self.xmlfile = [self.xmlfile]
		print("[Wizard] Reading '%s'." % self.xmlfile)
		wizardHandler = self.parseWizard(self.wizard)
		parser.setContentHandler(wizardHandler)
		for xmlfile in self.xmlfile:
			if xmlfile[0] != '/':
				parser.parse(eEnv.resolve('${datadir}/enigma2/') + xmlfile)
			else:
				parser.parse(xmlfile)

		self.showSteps = showSteps
		self.showStepSlider = showStepSlider
		self.showList = showList
		self.showConfig = showConfig

		self.numSteps = len(self.wizard)
		self.currStep = self.getStepWithID("start") + 1

		self.timeoutTimer = eTimer()
		self.timeoutTimer.callback.append(self.timeoutCounterFired)

		self["text"] = Label()

		if showConfig:
			self["config"] = ConfigList([], session=session)

		if self.showSteps:
			self["step"] = Label()

		if self.showStepSlider:
			self["stepslider"] = Slider(1, self.numSteps)

		if self.showList:
			self.list = []
			self["list"] = List(self.list, enableWrapAround=True)
			self["list"].onSelectionChanged.append(self.selChanged)
			# self["list"] = MenuList(self.list, enableWrapAround = True)

		self.onShown.append(self.updateValues)

		self.configInstance = None
		self.currentConfigIndex = None

		Wizard.instance = self

		self.lcdCallbacks = []

		self.disableKeys = False

		self["actions"] = NumberActionMap(["WizardActions", "NumberActions", "ColorActions", "SetupActions", "InputAsciiActions", "KeyboardInputActions"],
		{
			"gotAsciiCode": self.keyGotAscii,
			"ok": self.ok,
			"back": self.back,
			"left": self.left,
			"right": self.right,
			"up": self.up,
			"down": self.down,
			"red": self.red,
			"green": self.green,
			"yellow": self.yellow,
			"blue": self.blue,
			"deleteBackward": self.deleteBackward,
			"deleteForward": self.deleteForward,
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			"0": self.keyNumberGlobal
		}, -1)

		self["VirtualKB"] = NumberActionMap(["VirtualKeyboardActions"],
		{
			"showVirtualKeyboard": self.KeyText,
		}, -2)

		self["VirtualKB"].setEnabled(False)

	def red(self):
		print("[Wizard] In red.")
		if self.wizard[self.currStep]["config"]["screen"] is not None and hasattr(self.configInstance, "red") and callable(self.configInstance.red):
			self.configInstance.red()

	def green(self):
		print("[Wizard] In green.")
		if self.wizard[self.currStep]["config"]["screen"] is not None and hasattr(self.configInstance, "green") and callable(self.configInstance.green):
			self.configInstance.green()

	def yellow(self):
		print("[Wizard] In yellow.")
		if self.wizard[self.currStep]["config"]["screen"] is not None and hasattr(self.configInstance, "yellow") and callable(self.configInstance.yellow):
			self.configInstance.yellow()

	def blue(self):
		print("[Wizard] In blue.")
		if self.wizard[self.currStep]["config"]["screen"] is not None and hasattr(self.configInstance, "blue") and callable(self.configInstance.blue):
			self.configInstance.blue()

	def deleteForward(self):
		self.resetCounter()
		if self.wizard[self.currStep]["config"]["screen"] is not None:
			self.configInstance.keyDelete()
		elif self.wizard[self.currStep]["config"]["type"] == "dynamic":
			self["config"].handleKey(ACTIONKEY_DELETE)
		print("[Wizard] In deleteForward.")

	def deleteBackward(self):
		self.resetCounter()
		if self.wizard[self.currStep]["config"]["screen"] is not None:
			self.configInstance.keyBackspace()
		elif self.wizard[self.currStep]["config"]["type"] == "dynamic":
			self["config"].handleKey(ACTIONKEY_BACKSPACE)
		print("[Wizard] In deleteBackward.")

	def setLCDTextCallback(self, callback):
		self.lcdCallbacks.append(callback)

	def back(self):
		if self.disableKeys:
			return
		print("[Wizard] Going back...")
		print("[Wizard] stepHistory: '%s'." % self.stepHistory)
		if len(self.stepHistory) > 1:
			self.currStep = self.stepHistory[-2]
			self.stepHistory = self.stepHistory[:-2]
		else:
			self.session.openWithCallback(self.exitWizardQuestion, MessageBox, (_("Are you sure you want to exit this wizard?")))
		if self.currStep < 1:
			self.currStep = 1
		print("[Wizard] currStep: '%s'." % self.currStep)
		print("[Wizard] New stepHistory: '%s'." % self.stepHistory)
		self.updateValues()
		print("[Wizard] After updateValues stepHistory: '%s'." % self.stepHistory)

	def exitWizardQuestion(self, ret=False):
		if ret:
			self.markDone()
			self.exit()

	def markDone(self):
		pass

	def exit(self):
		Wizard.instance = None
		self.close()

	def getStepWithID(self, id):
		try:  # test avoid FATAL SIGNAL
			print("[Wizard] getStepWithID: '%s'." % id)
			count = 0
			for x in self.wizard.keys():
				if self.wizard[x]["id"] == id:
					print("[Wizard] result=%d." % count)
					return count
				count += 1
			print("[Wizard] Result=Nothing.")
			return 0
		except:
			pass

	def finished(self, gotoStep=None, *args, **kwargs):
		print("[Wizard] In finished.")
		currStep = self.currStep

		if self.updateValues not in self.onShown:
			self.onShown.append(self.updateValues)

		if self.showConfig:
			if self.wizard[currStep]["config"]["type"] == "dynamic":
				eval("self." + self.wizard[currStep]["config"]["evaluation"])()

		if self.showList:
			if len(self.wizard[currStep]["evaluatedlist"]) > 0:
				print("[Wizard] current: '%s'." % str(self["list"].current))
				nextStep = self["list"].current[1]
				if "listevaluation" in self.wizard[currStep]:
					exec("self." + self.wizard[self.currStep]["listevaluation"] + "('" + nextStep + "')")
				else:
					self.currStep = self.getStepWithID(nextStep)

		print_now = True
		if (currStep == self.numSteps and self.wizard[currStep]["nextstep"] is None) or self.wizard[currStep]["id"] == "end":  # wizard finished
			print("[Wizard] Wizard finished.")
			self.markDone()
			self.exit()
		else:
			self.codeafter = True
			self.runCode(self.wizard[currStep]["codeafter"])
			self.prevStep = currStep
			self.gotoStep = gotoStep
			if not self.runCode(self.wizard[currStep]["codeafter_async"]):
				self.afterAsyncCode()
			else:
				if self.updateValues in self.onShown:
					self.onShown.remove(self.updateValues)
		fileWriteLine("/proc/progress", "100")
		if print_now:
			print("[Wizard] Now: '%s'." % str(self.currStep))

	def ok(self):
		print("[Wizard] In ok.")
		if self.disableKeys:
			return
		currStep = self.currStep

		if self.showConfig:
			if self.wizard[currStep]["config"]["screen"] is not None:
				if self.configInstance.__class__.__name__ == "NimSetup" and self.configInstance["config"].getCurrent()[1].__class__.__name__ == "ConfigNothing":
					self.configInstance.keyRight()
					return
				# TODO: don't die, if no run() is available
				# there was a try/except here, but i can't see a reason
				# for this. If there is one, please do a more specific check
				# and/or a comment in which situation there is no run()
				elif callable(getattr(self.configInstance, "runAsync", None)):
					if self.updateValues in self.onShown:
						self.onShown.remove(self.updateValues)
					self.configInstance.runAsync(self.finished)
					return
				else:
					self.configInstance.run()
					if hasattr(self.configInstance, "doNextStep") and not self.configInstance.doNextStep:
						return
		self.finished()

	def keyNumberGlobal(self, number):
		if self.wizard[self.currStep]["config"]["screen"] is not None:
			self.configInstance.keyNumberGlobal(number)
		elif self.wizard[self.currStep]["config"]["type"] == "dynamic":
			self["config"].handleKey(ACTIONKEY_0 + number)

	def keyGotAscii(self):
		if self.wizard[self.currStep]["config"]["screen"] is not None:
			self["config"].handleKey(ACTIONKEY_ASCII)
		elif self.wizard[self.currStep]["config"]["type"] == "dynamic":
			self["config"].handleKey(ACTIONKEY_ASCII)

	def left(self):
		self.resetCounter()
		if self.wizard[self.currStep]["config"]["screen"] is not None:
			self.configInstance.keyLeft()
		elif self.wizard[self.currStep]["config"]["type"] == "dynamic":
			self["config"].handleKey(ACTIONKEY_LEFT)
		print("[Wizard] In left.")

	def right(self):
		self.resetCounter()
		if self.wizard[self.currStep]["config"]["screen"] is not None:
			self.configInstance.keyRight()
		elif self.wizard[self.currStep]["config"]["type"] == "dynamic":
			self["config"].handleKey(ACTIONKEY_RIGHT)
		print("[Wizard] In right.")

	def up(self):
		self.resetCounter()
		if self.showConfig and self.wizard[self.currStep]["config"]["screen"] is not None or self.wizard[self.currStep]["config"]["type"] == "dynamic":
			self["config"].instance.moveSelection(self["config"].instance.moveUp)
			self.handleInputHelpers()
		elif self.showList and len(self.wizard[self.currStep]["evaluatedlist"]) > 0:
			self["list"].selectPrevious()
			if "onselect" in self.wizard[self.currStep]:
				print("[Wizard] current: '%s'." % str(self["list"].current))
				self.selection = self["list"].current[-1]
				# self.selection = self.wizard[self.currStep]["evaluatedlist"][self["list"].l.getCurrentSelectionIndex()][1]
				exec("self." + self.wizard[self.currStep]["onselect"] + "()")
		print("[Wizard] In up.")

	def down(self):
		self.resetCounter()
		if self.showConfig and self.wizard[self.currStep]["config"]["screen"] is not None or self.wizard[self.currStep]["config"]["type"] == "dynamic":
			self["config"].instance.moveSelection(self["config"].instance.moveDown)
			self.handleInputHelpers()
		elif self.showList and len(self.wizard[self.currStep]["evaluatedlist"]) > 0:
			# self["list"].instance.moveSelection(self["list"].instance.moveDown)
			self["list"].selectNext()
			if "onselect" in self.wizard[self.currStep]:
				print("[Wizard] current: '%s'." % str(self["list"].current))
				# self.selection = self.wizard[self.currStep]["evaluatedlist"][self["list"].l.getCurrentSelectionIndex()][1]
				# exec("self." + self.wizard[self.currStep]["onselect"] + "()")
				self.selection = self["list"].current[-1]
				# self.selection = self.wizard[self.currStep]["evaluatedlist"][self["list"].l.getCurrentSelectionIndex()][1]
				exec("self." + self.wizard[self.currStep]["onselect"] + "()")
		print("[Wizard] In down.")

	def selChanged(self):
		self.resetCounter()

		if self.showConfig and self.wizard[self.currStep]["config"]["screen"] is not None:
			self["config"].instance.moveSelection(self["config"].instance.moveUp)
		elif self.showList and len(self.wizard[self.currStep]["evaluatedlist"]) > 0:
			if "onselect" in self.wizard[self.currStep]:
				self.selection = self["list"].current[-1]
				print("[Wizard] self.selection: '%s'." % self.selection)
				exec("self." + self.wizard[self.currStep]["onselect"] + "()")

	def resetCounter(self):
		self.timeoutCounter = self.wizard[self.currStep]["timeout"]

	def runCode(self, code):
		if code != "":
			print("[Wizard] code='%s'." % code)
			exec(code)
			return True
		return False

	def getTranslation(self, text):
		text = _(text)
		brandmodel = "%s %s" % (BRAND, DISPLAYMODEL)
		if "[TUNER]" in text and self.currStep and self.currStep in self.wizard:
			currStep = self.wizard[self.currStep].get("id", "")
			tuner = currStep[-1].upper() if len(currStep) == 4 and currStep.startswith("nim") else _("N/A")
		else:
			tuner = ""
		textSubstitutions = [
			("%s %s", brandmodel),
			("[BRANDMODEL]", brandmodel),
			("[TUNER]", tuner)
		]
		for marker, substitute in textSubstitutions:
			text = text.replace(marker, substitute)
		return text

	def updateText(self, firstset=False):
		text = self.getTranslation(self.wizard[self.currStep]["text"])
		if "[timeout]" in text:
			text = text.replace("[timeout]", str(self.timeoutCounter))
			self["text"].setText(text)
		else:
			if firstset:
				self["text"].setText(text)

	def updateValues(self):
		print("[Wizard] Updating values in step '%s'." % str(self.currStep))
		# calling a step which doesn't exist can only happen if the condition in the last step is not fulfilled
		# if a non-existing step is called, end the wizard
		if self.currStep > len(self.wizard):
			self.markDone()
			self.exit()
			return

		self.timeoutTimer.stop()

		if self.configInstance is not None:
			# remove callbacks
			self.configInstance["config"].onSelectionChanged = []
			del self.configInstance["config"]
			self.configInstance.doClose()
			self.configInstance = None

		self.condition = True
		exec(self.wizard[self.currStep]["condition"])
		if not self.condition:
			print("keys*******************: %s" % list(self.wizard[self.currStep].keys()))
			if "laststep" in self.wizard[self.currStep]:  # exit wizard, if condition of laststep doesn't hold
				self.markDone()
				self.exit()
				return
			else:
				self.currStep += 1
				self.updateValues()
		else:
			if "displaytext" in self.wizard[self.currStep]:
				displaytext = self.wizard[self.currStep]["displaytext"]
				print("[Wizard] Set LCD text.")
				for x in self.lcdCallbacks:
					x(displaytext)
			if len(self.stepHistory) == 0 or self.stepHistory[-1] != self.currStep:
				self.stepHistory.append(self.currStep)
			print("[Wizard] Wizard step: '%s'." % self.wizard[self.currStep])

			if self.showSteps:
				self["step"].setText(self.getTranslation("Step ") + str(self.currStep) + "/" + str(self.numSteps))
			if self.showStepSlider:
				self["stepslider"].setValue(self.currStep)

			if self.wizard[self.currStep]["timeout"] is not None:
				self.resetCounter()
				self.timeoutTimer.start(1000)
			print("[Wizard] Wizard text '%s'." % self.getTranslation(self.wizard[self.currStep]["text"]))

			self.updateText(firstset=True)
			if "displaytext" in self.wizard[self.currStep]:
				displaytext = self.wizard[self.currStep]["displaytext"]
				print("[Wizard] Set LCD text.")
				for x in self.lcdCallbacks:
					x(displaytext)

			self.codeafter = False
			self.runCode(self.wizard[self.currStep]["code"])
			if self.runCode(self.wizard[self.currStep]["code_async"]):
				if self.updateValues in self.onShown:
					self.onShown.remove(self.updateValues)
			else:
				self.afterAsyncCode()

	def afterAsyncCode(self):
		if not self.updateValues in self.onShown:
			self.onShown.append(self.updateValues)

		if self.codeafter:
			if self.wizard[self.prevStep]["nextstep"] is not None:
				self.currStep = self.getStepWithID(self.wizard[self.prevStep]["nextstep"])
			if self.gotoStep is not None:
				self.currStep = self.getStepWithID(self.gotoStep)
			self.currStep += 1
			self.updateValues()
			print("[Wizard] Now: '%s'." % str(self.currStep))
		else:
			if self.showList:
				print("[Wizard] Showing list '%s'." % self.currStep)
				for renderer in self.renderer:
					rootrenderer = renderer
					while renderer.source is not None:
						# print("[Wizard] self.list: '%s'." % str(self["list"]))
						if renderer.source is self["list"]:
							print("[Wizard] setZPosition.")
							rootrenderer.instance.setZPosition(1)
						renderer = renderer.source

				# self["list"].instance.setZPosition(1)
				self.list = []
				if "dynamiclist" in self.wizard[self.currStep]:
					print("[Wizard] Dynamic list, calling '%s'." % self.wizard[self.currStep]["dynamiclist"])
					newlist = eval("self." + self.wizard[self.currStep]["dynamiclist"] + "()")
					# self.wizard[self.currStep]["evaluatedlist"] = []
					for entry in newlist:
						# self.wizard[self.currStep]["evaluatedlist"].append(entry)
						self.list.append(entry)
					# del self.wizard[self.currStep]["dynamiclist"]
				if len(self.wizard[self.currStep]["list"]) > 0:
					# self["list"].instance.setZPosition(2)
					for x in self.wizard[self.currStep]["list"]:
						self.list.append((self.getTranslation(x[0]), x[1]))
				self.wizard[self.currStep]["evaluatedlist"] = self.list
				self["list"].list = self.list
				self["list"].index = 0
			else:
				self["list"].hide()

			if self.showConfig:
				print("[Wizard] Showing config.")
				self["config"].instance.setZPosition(1)
				if self.wizard[self.currStep]["config"]["type"] == "dynamic":
					print("[Wizard] Config type is dynamic.")
					self["config"].instance.setZPosition(2)
					self["config"].setList(eval("self." + self.wizard[self.currStep]["config"]["source"])())
				elif self.wizard[self.currStep]["config"]["screen"]:
					if self.wizard[self.currStep]["config"]["type"] == "standalone":
						print("[Wizard] Type is standalone.")
						self.session.openWithCallback(self.ok, self.wizard[self.currStep]["config"]["screen"])
					else:
						self["config"].instance.setZPosition(2)
						print("[Wizard] Screen '%s'." % self.wizard[self.currStep]["config"]["screen"])
						if not self.wizard[self.currStep]["config"]["args"]:
							self.configInstance = self.session.instantiateDialog(self.wizard[self.currStep]["config"]["screen"])
						elif self.wizard[self.currStep]["config"]["args"] == "SetupAccessLevels":
							self.configInstance = self.session.instantiateDialog(self.wizard[self.currStep]["config"]["screen"], self.wizard[self.currStep]["config"]["args"])
						else:
							self.configInstance = self.session.instantiateDialog(self.wizard[self.currStep]["config"]["screen"], eval(self.wizard[self.currStep]["config"]["args"]))

						self.configInstance.setAnimationMode(0)

						self["config"].l.setList(self.configInstance["config"].list)
						callbacks = self.configInstance["config"].onSelectionChanged
						self.configInstance["config"].destroy()
						self.configInstance["config"] = self["config"]
						self.configInstance["config"].onSelectionChanged = callbacks
						self["config"].setCurrentIndex(0)
				else:
					self["config"].setList([])
					self.handleInputHelpers()
			else:
				if "config" in self:
					self["config"].hide()

	def timeoutCounterFired(self):
		self.timeoutCounter -= 1
		print("[Wizard] timeoutCounter: '%s'." % self.timeoutCounter)
		if self.timeoutCounter == 0:
			if self.wizard[self.currStep]["timeoutaction"] == "selectnext":
				print("[Wizard] Selection next item.")
				self.down()
			else:
				if self.wizard[self.currStep]["timeoutaction"] == "changestep":
					self.finished(gotoStep=self.wizard[self.currStep]["timeoutstep"])
		self.updateText()

	def handleInputHelpers(self):
		if self["config"].getCurrent() is not None:
			if isinstance(self["config"].getCurrent()[1], ConfigText) or isinstance(self["config"].getCurrent()[1], ConfigPassword):
				if "VKeyIcon" in self:
					self["VirtualKB"].setEnabled(True)
					self["VKeyIcon"].boolean = True
				if "HelpWindow" in self:
					if self["config"].getCurrent()[1].help_window.instance is not None:
						helpwindowpos = self["HelpWindow"].getPosition()
						from enigma import ePoint
						self["config"].getCurrent()[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))
			else:
				if "VKeyIcon" in self:
					self["VirtualKB"].setEnabled(False)
					self["VKeyIcon"].boolean = False
		else:
			if "VKeyIcon" in self:
				self["VirtualKB"].setEnabled(False)
				self["VKeyIcon"].boolean = False

	def KeyText(self):
		from Screens.VirtualKeyBoard import VirtualKeyBoard
		self.currentConfigIndex = self["config"].getCurrentIndex()
		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].getValue())

	def VirtualKeyBoardCallback(self, callback=None):
		if callback is not None and len(callback):
			if isinstance(self["config"].getCurrent()[1], (ConfigPassword, ConfigText)):
				if "HelpWindow" in self:
					if self["config"].getCurrent()[1].help_window.instance is not None:
						helpwindowpos = self["HelpWindow"].getPosition()
						from enigma import ePoint
						self["config"].getCurrent()[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))
			self["config"].instance.moveSelectionTo(self.currentConfigIndex)
			self["config"].setCurrentIndex(self.currentConfigIndex)
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())


class WizardManager:
	def __init__(self):
		self.wizards = []

	def registerWizard(self, wizard, precondition, priority=0):
		self.wizards.append((wizard, precondition, priority))

	def getWizards(self):
		# x[1] is a precondition.
		for wizard in self.wizards:
			wizard[0].isLastWizard = False
		if len(self.wizards) > 0:
			self.wizards[-1][0].isLastWizard = True
		return [(x[2], x[0]) for x in self.wizards if x[1] == 1]


wizardManager = WizardManager()
