# -*- coding: utf-8 -*-
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.genre import getGenreStringSub
from Components.config import config
from Components.UsageConfig import dropEPGNewLines, replaceEPGSeparator
from time import localtime, mktime, strftime
from time import time, localtime


class ETSIClassifications(dict):
	#            0         1         2          3        4         5          6         7         8         9        10        11        12        13        14        15
	COLORS = (0x000000, 0x00A822, 0x00A822, 0x00A822, 0x007DCA, 0x007DCA, 0x007DCA, 0xFF7900, 0xFF7900, 0xFF7900, 0xFF5594, 0xFF5594, 0xFF5594, 0xD70723, 0xD70723, 0xD70723)

	def shortRating(self, age):
		if age == 0:
			return _("All ages")
		elif age <= 15:
			age += 3
			return " %d+" % age

	def longRating(self, age):
		if age == 0:
			return _("Rating undefined")
		elif age <= 15:
			age += 3
			return _("Minimum age %d years") % age

	def imageRating(self, age):
		if age == 0:
			return "ratings/ETSI-ALL.png"
		elif age <= 15:
			age += 3
			return "ratings/ETSI-%d.png" % age

	def colorRating(self, age):
		return self.COLORS[age]

	def __init__(self):
		self.update([(i, (self.shortRating(c), self.longRating(c), self.imageRating(c), self.colorRating(i))) for i, c in enumerate(range(0, 16))])


class AusClassifications(dict):
	# In Australia "Not Classified" (NC) is to be displayed as an empty string.
	#            0   1   2    3    4    5    6    7    8     9     10   11   12    13    14    15
	SHORTTEXT = ("", "", "P", "P", "C", "C", "G", "G", "PG", "PG", "M", "M", "MA", "MA", "AV", "R")
	LONGTEXT = {
		"": _("Not Classified"),
		"P": _("Preschool"),
		"C": _("Children"),
		"G": _("General"),
		"PG": _("Parental Guidance Recommended"),
		"M": _("Mature Audience 15+"),
		"MA": _("Mature Adult Audience 15+"),
		"AV": _("Adult Audience, Strong Violence 15+"),
		"R": _("Restricted 18+")
	}
	IMAGES = {
		"": "ratings/blank.png",
		"P": "ratings/AUS-P.png",
		"C": "ratings/AUS-C.png",
		"G": "ratings/AUS-G.png",
		"PG": "ratings/AUS-PG.png",
		"M": "ratings/AUS-M.png",
		"MA": "ratings/AUS-MA.png",
		"AV": "ratings/AUS-AV.png",
		"R": "ratings/AUS-R.png"
	}

	#            0         1         2          3        4         5          6         7         8         9        10        11        12        13        14        15
	COLORS = (0x000000, 0x00A822, 0x00A822, 0x00A822, 0x007DCA, 0x007DCA, 0x007DCA, 0xFF7900, 0xFF7900, 0xFF7900, 0xFF5594, 0xFF5594, 0xFF5594, 0xD70723, 0xD70723, 0xD70723)

	def __init__(self):
		self.update([(i, (c, self.LONGTEXT[c], self.IMAGES[c], self.COLORS[i])) for i, c in enumerate(self.SHORTTEXT)])


class GBrClassifications(dict):
	# British Board of Film Classification
	#            0   1   2    3    4    5    6     7     8     9     10    11    12    13    14    15
	SHORTTEXT = ("", "", "", "U", "U", "U", "PG", "PG", "PG", "12", "12", "12", "15", "15", "15", "18")
	LONGTEXT = {
		"": _("Not Classified"),
		"U": _("U - Suitable for all"),
		"PG": _("PG - Parental Guidance"),
		"12": _("Suitable for ages 12+"),
		"15": _("Suitable for ages 15+"),
		"18": _("Suitable only for Adults")
	}
	IMAGES = {
		"": "ratings/blank.png",
		"U": "ratings/GBR-U.png",
		"PG": "ratings/GBR-PG.png",
		"12": "ratings/GBR-12.png",
		"15": "ratings/GBR-15.png",
		"18": "ratings/GBR-18.png"
	}

	#            0         1         2          3        4         5          6         7         8         9        10        11        12        13        14        15
	COLORS = (0x000000, 0x000000, 0x000000, 0x00A822, 0x00A822, 0x00A822, 0xFAB800, 0xFAB800, 0xFAB800, 0xFF7900, 0xFF7900, 0xFF7900, 0xFF5594, 0xFF5594, 0xFF5594, 0xD70723)

	def __init__(self):
		self.update([(i, (c, self.LONGTEXT[c], self.IMAGES[c], self.COLORS[i])) for i, c in enumerate(self.SHORTTEXT)])


class ItaClassifications(dict):
	# The classifications used by Sky Italia
	#            0   1   2    3    4    5    6     7     8     9     10    11    12    13    14    15
	SHORTTEXT = ("", "", "", "T", "T", "T", "BA", "BA", "BA", "12", "12", "12", "14", "14", "14", "18")
	LONGTEXT = {
		"": _("Non Classificato"),
		"T": _("Per Tutti"),
		"BA": _("Bambini Accompagnati"),
		"12": _("Dai 12 anni in su"),
		"14": _("Dai 14 anni in su"),
		"18": _("Dai 18 anni in su")
	}
	IMAGES = {
		"": "ratings/blank.png",
		"T": "ratings/ITA-T.png",
		"BA": "ratings/ITA-BA.png",
		"12": "ratings/ITA-12.png",
		"14": "ratings/ITA-14.png",
		"18": "ratings/ITA-18.png"
	}

	#            0         1         2          3        4         5          6         7         8         9        10        11        12        13        14        15
	COLORS = (0x000000, 0x00A822, 0x00A822, 0x00A822, 0x007DCA, 0x007DCA, 0x007DCA, 0xFF7900, 0xFF7900, 0xFF7900, 0xFF5594, 0xFF5594, 0xFF5594, 0xD70723, 0xD70723, 0xD70723)

	def __init__(self):
		self.update([(i, (c, self.LONGTEXT[c], self.IMAGES[c], self.COLORS[i])) for i, c in enumerate(self.SHORTTEXT)])


# Each country classification object in the map tuple must be an object that
# supports obj.get(key[, default]). It need not actually be a dict object.
#
# The other element is how the rating number should be formatted if there
# is no match in the classification object.
#
# If there is no matching country then the default ETSI should be selected.

countries = {
	"ETSI": (ETSIClassifications(), lambda age: (_("bc%d") % age, _("Rating defined by broadcaster - %d") % age, "ratings/ETSI-na.png")),
	"AUS": (AusClassifications(), lambda age: (_("BC%d") % age, _("Rating defined by broadcaster - %d") % age, "ratings/AUS-na.png")),
	"GBR": (GBrClassifications(), lambda age: (_("BC%d") % age, _("Rating defined by broadcaster - %d") % age, "ratings/GBR-na.png")),
	"ITA": (ItaClassifications(), lambda age: (_("BC%d") % age, _("Rating defined by broadcaster - %d") % age, "ratings/ITA-na.png"))
}


# OpenTV country codes: epgchanneldata.cpp
# eEPGChannelData::getOpenTvParentalRating
opentv_countries = {
	"OT1": "GBR",
	"OT2": "ITA",
	"OT3": "AUS",
	"OT4": "NZL",
	"OTV": "ETSI"
}


class EventName(Converter):
	NAME = 0
	SHORT_DESCRIPTION = 1
	EXTENDED_DESCRIPTION = 2
	FULL_DESCRIPTION = 3
	ID = 4
	NAME_NOW = 5
	NAME_NEXT = 6
	GENRE = 7
	RATING = 8
	SRATING = 9
	PDC = 10
	PDCTIME = 11
	PDCTIMESHORT = 12
	ISRUNNINGSTATUS = 13
	FORMAT_STRING = 14
	RAWRATING = 15

	RAWRATINGANDCOUNTRY = 30

	RATSHORT = 0
	RATLONG = 1
	RATICON = 2
	RATCOLOR = 3

	RATNORMAL = 0
	RATDEFAULT = 1

	def __init__(self, type):
		Converter.__init__(self, type)
		self.parts = [(arg.strip() if i else arg) for i, arg in enumerate(type.split(","))]
		if len(self.parts) > 1:
			self.type = self.FORMAT_STRING
			self.separator = self.parts[0]
		else:
			if type == "Description":
				self.type = self.SHORT_DESCRIPTION
			elif type == "ExtendedDescription":
				self.type = self.EXTENDED_DESCRIPTION
			elif type == "FullDescription":
				self.type = self.FULL_DESCRIPTION
			elif type == "ID":
				self.type = self.ID
			elif type == "NameNow":
				self.type = self.NAME_NOW
			elif type == "NameNext":
				self.type = self.NAME_NEXT
			elif type == "Genre":
				self.type = self.GENRE
			elif type == "Rating":
				self.type = self.RATING
			elif type == "SmallRating":
				self.type = self.SRATING
			elif type == "Pdc":
				self.type = self.PDC
			elif type == "PdcTime":
				self.type = self.PDCTIME
			elif type == "PdcTimeShort":
				self.type = self.PDCTIMESHORT
			elif type == "IsRunningStatus":
				self.type = self.ISRUNNINGSTATUS
			elif type == "RawRating":
				self.type = self.RAWRATING
			elif type == "RawRatingAndCountry":
				self.type = self.RAWRATINGANDCOUNTRY
			else:
				self.type = self.NAME

	@cached
	def getBoolean(self):
		event = self.source.event
		if event is None:
			return False
		if self.type == self.NAME:
			return bool(self.getText())
		if self.type == self.PDC:
			if event.getPdcPil():
				return True
		return False

	boolean = property(getBoolean)

	@cached
	def getText(self):
		event = self.source.event
		if event is None:
			return ""

		if self.type == self.NAME:
			return event.getEventName()
		elif self.type == self.SRATING:
			rating = event.getParentalData()
			if rating is None:
				return ""
			else:
				country = rating.getCountryCode()
				age = rating.getRating()
				if age == 0:
					return _("All ages")
				elif age > 15:
					return _("bc%s") % age
				else:
					age += 3
					return " %d+" % age
		elif self.type == self.RATING:
			rating = event.getParentalData()
			if rating is None:
				return ""
			else:
				country = rating.getCountryCode()
				age = rating.getRating()
				if age == 0:
					return _("Rating undefined")
				elif age > 15:
					return _("Rating defined by broadcaster - %d") % age
				else:
					age += 3
					return _("Minimum age %d years") % age
		elif self.type == self.GENRE:
			genre = event.getGenreData()
			if genre is None:
				return ""
			else:
				return getGenreStringSub(genre.getLevel1(), genre.getLevel2())
		elif self.type == self.NAME_NOW:
			return pgettext("now/next: 'now' event label", "Now") + ": " + event.getEventName()
		elif self.type == self.NAME_NEXT:
			return pgettext("now/next: 'next' event label", "Next") + ": " + event.getEventName()
		elif self.type == self.SHORT_DESCRIPTION:
			return dropEPGNewLines(event.getShortDescription())
		elif self.type == self.EXTENDED_DESCRIPTION:
			return dropEPGNewLines(event.getExtendedDescription()) or dropEPGNewLines(event.getShortDescription())
		elif self.type == self.FULL_DESCRIPTION:
			description = dropEPGNewLines(event.getShortDescription())
			extended = dropEPGNewLines(event.getExtendedDescription().rstrip())
			if description and extended:
				if description.replace('\n', '') == extended.replace('\n', ''):
					return extended
				description += replaceEPGSeparator(config.epg.fulldescription_separator.value)
			return description + extended
		elif self.type == self.ID:
			return str(event.getEventId())
		elif self.type == self.PDC:
			if event.getPdcPil():
				return _("PDC")
			return ""
		elif self.type in (self.PDCTIME, self.PDCTIMESHORT):
			pil = event.getPdcPil()
			if pil:
				begin = localtime(event.getBeginTime())
				start = localtime(mktime([begin.tm_year, (pil & 0x7800) >> 11, (pil & 0xF8000) >> 15, (pil & 0x7C0) >> 6, (pil & 0x3F), 0, begin.tm_wday, begin.tm_yday, begin.tm_isdst]))
				if self.type == self.PDCTIMESHORT:
					return strftime(config.usage.time.short.value, start)
				return strftime(config.usage.date.short.value + " " + config.usage.time.short.value, start)
		elif self.type == self.ISRUNNINGSTATUS:
			if event.getPdcPil():
				running_status = event.getRunningStatus()
				if running_status == 1:
					return _("not running")
				if running_status == 2:
					return _("starts in a few seconds")
				if running_status == 3:
					return _("pausing")
				if running_status == 4:
					return _("running")
				if running_status == 5:
					return _("service off-air")
				if running_status in (6, 7):
					return _("reserved for future use")
				return _("undefined")
			return ""
		elif self.type == self.RAWRATING:
			rating = event.getParentalData()
			if rating:
				return "%d" % rating.getRating()
		elif self.type == self.RAWRATINGANDCOUNTRY:
			rating = event.getParentalData()
			if rating:
				age = rating.getRating()
				country = rating.getCountryCode().upper()
				if country in opentv_countries:
					country = opentv_countries[country]
				if country in countries:
					c = countries[country]
				else:
					c = countries["ETSI"]
				rating = c[self.RATNORMAL].get(age, c[self.RATDEFAULT](age))
				ageText = rating[self.RATSHORT].strip().replace("+", "")
				color = rating[self.RATCOLOR]
				return "%s;%s" % (ageText, hex(color))
		elif self.type == self.FORMAT_STRING:
			begin = event.getBeginTime()
			end = begin + event.getDuration()
			now = int(time())
			t_start = localtime(begin)
			t_end = localtime(end)
			if begin <= now <= end:
				duration = end - now
				duration_str = "+%d min" % (duration / 60)
			else:
				duration = event.getDuration()
				duration_str = "%d min" % (duration / 60)
			start_time_str = "%2d:%02d" % (t_start.tm_hour, t_start.tm_min)
			end_time_str = "%2d:%02d" % (t_end.tm_hour, t_end.tm_min)
			name = event.getEventName()
			res_str = ""
			for x in self.parts[1:]:
				if x == "NAME" and name:
					res_str = self.appendToStringWithSeparator(res_str, name)
				if x == "STARTTIME" and start_time_str:
					res_str = self.appendToStringWithSeparator(res_str, start_time_str)
				if x == "ENDTIME" and end_time_str:
					res_str = self.appendToStringWithSeparator(res_str, end_time_str)
				if x == "TIMERANGE" and start_time_str and end_time_str:
					res_str = self.appendToStringWithSeparator(res_str, "%s - %s" % (start_time_str, end_time_str))
				if x == "DURATION" and duration_str:
					res_str = self.appendToStringWithSeparator(res_str, duration_str)
			return res_str

	text = property(getText)
