# -*- coding: utf-8 -*-
# the implementation here is a bit crappy.
import time
from Tools.Directories import resolveFilename, SCOPE_CONFIG

PERCENTAGE_START = 0
PERCENTAGE_END = 100

profile_start = time.time()

profile_data = {}
total_time = 1
profile_file = None
# model = BoxInfo.get("machinebuild")  # For when we can use BoxInfo.
model = None

try:
	profile_old = open(resolveFilename(SCOPE_CONFIG, "profile")).readlines()

	t = None
	for line in profile_old:
		(t, id) = line[:-1].split('\t')
		t = float(t)
		total_time = t
		profile_data[id] = t
except:
	print("no profile data available")

try:
	profile_file = open(resolveFilename(SCOPE_CONFIG, "profile"), "w")
except IOError:
	print("WARNING: couldn't open profile file!")


def profile(id):
	now = time.time() - profile_start
	if profile_file:
		profile_file.write("%7.3f\t%s\n" % (now, id))

		if id in profile_data:
			t = profile_data[id]
			if total_time:
				perc = t * (PERCENTAGE_END - PERCENTAGE_START) / total_time + PERCENTAGE_START
			else:
				perc = PERCENTAGE_START
			try:
				if model == "axodin":
					open("/dev/dbox/oled0", "w").write("%d" % perc)
				elif model in ("gb800solo", "gb800se", "gb800seplus", "gbultrase"):
					open("/dev/mcu", "w").write("%d  \n" % perc)
				elif model in ("ebox5000", "osmini", "spycatmini", "osminiplus", "spycatminiplus"):
					open("/proc/progress", "w").write("%d" % perc)
				elif model in ("sezammarvel", "xpeedlx3", "atemionemesis"):
					open("/proc/vfd", "w").write("Loading %d %%" % perc)
				elif model == "beyonwizu4":
					open("/dev/dbox/oled0", "w").write("Loading %d%%\n" % perc)
				else:
					open("/proc/progress", "w").write("%d \n" % perc)
			except IOError:
				pass


def profile_final():
	global profile_file
	if profile_file is not None:
		profile_file.close()
		profile_file = None
