# -*- coding: utf-8 -*-
from enigma import iRecordableService
from Components.Element import cached
import Components.RecordingConfig
from Components.Sources.Source import Source
from Components.config import config
from Components.SystemInfo import BoxInfo


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
			recordings = self.session.nav.getRecordings(False, Components.RecordingConfig.recType(config.recording.show_rec_symbol_for_rec_types.getValue()))
			if BoxInfo.getItem("LCDsymbol_circle_recording"):
				open(BoxInfo.getItem("LCDsymbol_circle_recording"), "w").write(recs and "1" or "0")
			self.records_running = len(recordings)
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
