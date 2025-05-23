# -*- coding: utf-8 -*-
from enigma import iRecordableService
from Components.Element import cached
from Components.Sources.Source import Source


class RecordState(Source):
	def __init__(self, session):
		Source.__init__(self)
		self.session = session
		self.records_running = 0
		session.nav.record_event.append(self.gotRecordEvent)
		self.gotRecordEvent(None, None)  # Get initial state.

	def gotRecordEvent(self, service, event):
		prev_records = self.records_running
		if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
			self.recordRunning = self.session.nav.getIndicatorRecordingsCount()
			if self.records_running != prev_records:
				self.changed((self.CHANGED_ALL,))

	def destroy(self):
		self.session.nav.record_event.remove(self.gotRecordEvent)
		Source.destroy(self)

	@cached
	def getBoolean(self):
		return self.records_running and True or False
	boolean = property(getBoolean)

	@cached
	def getValue(self):
		return self.records_running
	value = property(getValue)
