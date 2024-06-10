#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <libsig_comp.h>
#include <linux/dvb/version.h>

#include <lib/actions/action.h>
#include <lib/driver/rc.h>
#include <lib/base/ioprio.h>
#include <lib/base/e2avahi.h>
#include <lib/base/ebase.h>
#include <lib/base/eenv.h>
#include <lib/base/eerror.h>
#include <lib/base/esimpleconfig.h>
#include <lib/base/init.h>
#include <lib/base/init_num.h>
#include <lib/base/nconfig.h>
#include <lib/gdi/gmaindc.h>
#include <lib/gdi/glcddc.h>
#include <lib/gdi/grc.h>
#include <lib/gdi/epng.h>
#include <lib/gdi/font.h>
#include <lib/gui/ebutton.h>
#include <lib/gui/elabel.h>
#include <lib/gui/elistboxcontent.h>
#include <lib/gui/ewidget.h>
#include <lib/gui/ewidgetdesktop.h>
#include <lib/gui/ewindow.h>
#include <lib/gui/evideo.h>
#include <lib/python/connections.h>
#include <lib/python/python.h>
#include <lib/python/pythonconfig.h>
#include <lib/service/servicepeer.h>
#include <lib/base/profile.h>

#include "bsod.h"
#include "version_info.h"

#ifdef OBJECT_DEBUG
int object_total_remaining;

void object_dump()
{
	printf("%d items left\n", object_total_remaining);
}
#endif

static eWidgetDesktop *wdsk, *lcddsk;

static int prev_ascii_code;

int getPrevAsciiCode()
{
	int ret = prev_ascii_code;
	prev_ascii_code = 0;
	return ret;
}

void keyEvent(const eRCKey &key)
{
	static eRCKey last(0, 0, 0);
	static int num_repeat;

	ePtr<eActionMap> ptr;
	eActionMap::getInstance(ptr);

	if ((key.code == last.code) && (key.producer == last.producer) && key.flags & eRCKey::flagRepeat)
		num_repeat++;
	else
	{
		num_repeat = 0;
		last = key;
	}

	if (num_repeat == 4)
	{
		ptr->keyPressed(key.producer->getIdentifier(), key.code, eRCKey::flagLong);
		num_repeat++;
	}

	if (key.flags & eRCKey::flagAscii)
	{
		prev_ascii_code = key.code;
		ptr->keyPressed(key.producer->getIdentifier(), 510 /* faked KEY_ASCII */, 0);
	}
	else
		ptr->keyPressed(key.producer->getIdentifier(), key.code, key.flags);
}

/************************************************/
#include <lib/components/scan.h>
#include <lib/dvb/idvb.h>
#include <lib/dvb/dvb.h>
#include <lib/dvb/db.h>
#include <lib/dvb/dvbtime.h>
#include <lib/dvb/epgcache.h>
#include <lib/dvb/epgtransponderdatareader.h>

/* Defined in eerror.cpp */
void setDebugTime(int level);
class eMain : public eApplication, public sigc::trackable
{
	eInit init;
	ePythonConfigQuery config;

	ePtr<eDVBDB> m_dvbdb;
	ePtr<eDVBResourceManager> m_mgr;
	ePtr<eDVBLocalTimeHandler> m_locale_time_handler;
	ePtr<eEPGCache> m_epgcache;
	ePtr<eEPGTransponderDataReader> m_epgtransponderdatareader;

public:
	eMain()
	{
		e2avahi_init(this);
		init_servicepeer();
		init.setRunlevel(eAutoInitNumbers::main);
		/* TODO: put into init */
		m_dvbdb = new eDVBDB();
		m_mgr = new eDVBResourceManager();
		m_locale_time_handler = new eDVBLocalTimeHandler();
		m_epgcache = new eEPGCache();
		m_epgtransponderdatareader = new eEPGTransponderDataReader();
		m_mgr->setChannelList(m_dvbdb);
	}

	~eMain()
	{
		m_dvbdb->saveServicelist();
		m_mgr->releaseCachedChannel();
		done_servicepeer();
		e2avahi_close();
	}
};

bool replace(std::string &str, const std::string &from, const std::string &to)
{
	size_t start_pos = str.find(from);
	if (start_pos == std::string::npos)
		return false;
	str.replace(start_pos, from.length(), to);
	return true;
}

static const std::string getConfigCurrentSpinner(const char *key)
{
	auto value = eSimpleConfig::getString(key);

	// if value is not empty, means config.skin.primary_skin exist in settings file

	if (!value.empty())
	{
		replace(value, "skin.xml", "spinner");
		std::string png_location = eEnv::resolve("${datadir}/enigma2/" + value + "/wait1.png");
		std::ifstream png(png_location.c_str());
		if (png.good())
		{
			png.close();
			return value; // if value is NOT empty, means config.skin.primary_skin exist in settings file, so return SCOPE_GUISKIN + "/spinner" ( /usr/share/enigma2/MYSKIN/spinner/wait1.png exist )
		}
	}

	// try to find spinner in skin_default/spinner subfolder
	value = "skin_default/spinner";

	// check /usr/share/enigma2/skin_default/spinner/wait1.png
	std::string png_location = eEnv::resolve("${datadir}/enigma2/" + value + "/wait1.png");
	std::ifstream png(png_location.c_str());
	if (png.good())
	{
		png.close();
		return value; // ( /usr/share/enigma2/skin_default/spinner/wait1.png exist )
	}
	else
		return "spinner"; // ( /usr/share/enigma2/skin_default/spinner/wait1.png DOES NOT exist )
}

int exit_code;

void quitMainloop(int exitCode)
{
	FILE *f = fopen("/proc/stb/fp/was_timer_wakeup", "w");
	if (f)
	{
		fprintf(f, "%d", 0);
		fclose(f);
	}
	else
	{
		int fd = open("/dev/dbox/fp0", O_WRONLY);
		if (fd >= 0)
		{
			if (ioctl(fd, 10 /*FP_CLEAR_WAKEUP_TIMER*/) < 0)
				eDebug("[Enigma] quitMainloop FP_CLEAR_WAKEUP_TIMER failed!  (%m)");
			close(fd);
		}
		else
			eDebug("[Enigma] quitMainloop open /dev/dbox/fp0 for wakeup timer clear failed!  (%m)");
	}
	exit_code = exitCode;
	eApp->quit(0);
}

void pauseInit()
{
	eInit::pauseInit();
}

void resumeInit()
{
	eInit::resumeInit();
}

static void sigterm_handler(int num)
{
	quitMainloop(128 + num);
}

void catchTermSignal()
{
	struct sigaction act = {};

	act.sa_handler = sigterm_handler;
	act.sa_flags = SA_RESTART;

	if (sigemptyset(&act.sa_mask) == -1)
		perror("sigemptyset");
	if (sigaction(SIGTERM, &act, 0) == -1)
		perror("SIGTERM");
}

int main(int argc, char **argv)
{
#ifdef MEMLEAK_CHECK
	atexit(DumpUnfreed);
#endif

#ifdef OBJECT_DEBUG
	atexit(object_dump);
#endif

	// set pythonpath if unset
	setenv("PYTHONPATH", eEnv::resolve("${libdir}/enigma2/python").c_str(), 0);

	// get enigma2 debug level settings
	debugLvl = getenv("ENIGMA_DEBUG_LVL") ? atoi(getenv("ENIGMA_DEBUG_LVL")) : 4;
	if (debugLvl < 0)
		debugLvl = 0;
	if (getenv("ENIGMA_DEBUG_TIME"))
		setDebugTime(atoi(getenv("ENIGMA_DEBUG_TIME")));

	eLog(0, "[Enigma] Python path is '%s'.", getenv("PYTHONPATH"));
	eLog(0, "[Enigma] DVB API version %d, DVB API version minor %d.", DVB_API_VERSION, DVB_API_VERSION_MINOR);
	eLog(0, "[Enigma] Enigma debug level %d.", debugLvl);

	ePython python;
	eMain main;

	ePtr<gMainDC> my_dc;
	gMainDC::getInstance(my_dc);

	// int double_buffer = my_dc->haveDoubleBuffering();

	ePtr<gLCDDC> my_lcd_dc;
	gLCDDC::getInstance(my_lcd_dc);

		/* ok, this is currently hardcoded for arabic. */
			/* some characters are wrong in the regular font, force them to use the replacement font */
	for (int i = 0x60c; i <= 0x66d; ++i)
		eTextPara::forceReplacementGlyph(i);
	eTextPara::forceReplacementGlyph(0xfdf2);
	for (int i = 0xfe80; i < 0xff00; ++i)
		eTextPara::forceReplacementGlyph(i);

	eWidgetDesktop dsk(my_dc->size());
	eWidgetDesktop dsk_lcd(my_lcd_dc->size());

	dsk.setStyleID(0);
	dsk_lcd.setStyleID(1);

	/*
	if (double_buffer)
	{
		eDebug("[Enigma] Double buffering found, enable buffered graphics mode.");
		dsk.setCompositionMode(eWidgetDesktop::cmBuffered);
	}
	*/

	wdsk = &dsk;
	lcddsk = &dsk_lcd;

	dsk.setDC(my_dc);
	dsk_lcd.setDC(my_lcd_dc);

	dsk.setBackgroundColor(gRGB(0, 0, 0, 0xFF));

	/* redrawing is done in an idle-timer, so we have to set the context */
	dsk.setRedrawTask(main);
	dsk_lcd.setRedrawTask(main);

	std::string active_skin = getConfigCurrentSpinner("config.skin.primary_skin");
	std::string spinnerPostion = eSimpleConfig::getString("config.misc.spinnerPosition", "50,50");
	int spinnerPostionX, spinnerPostionY;
	if (sscanf(spinnerPostion.c_str(), "%d,%d", &spinnerPostionX, &spinnerPostionY) != 2)
	{
		spinnerPostionX = spinnerPostionY = 50;
	}

	eDebug("[Enigma] Loading spinners.");
	{
#define MAX_SPINNER 64
		int i = 0;
		char filename[64];
		std::string rfilename;
		std::string skinpath = "${datadir}/enigma2/" + active_skin;
		std::string defpath = "${datadir}/enigma2/spinner";
		std::string userpath = "${sysconfdir}/enigma2/spinner";
		bool def = (skinpath.compare(defpath) == 0);

		snprintf(filename, sizeof(filename), "%s/wait%d.png", userpath.c_str(), i + 1);
		rfilename = eEnv::resolve(filename);

		struct stat st;
		if (::stat(rfilename.c_str(), &st) == 0)
		{
			def = true;
			skinpath = userpath;
		}

		ePtr<gPixmap> wait[MAX_SPINNER];
		while (i < MAX_SPINNER)
		{
			snprintf(filename, sizeof(filename), "%s/wait%d.png", skinpath.c_str(), i + 1);
			rfilename = eEnv::resolve(filename);

			wait[i] = 0;
			if (::stat(rfilename.c_str(), &st) == 0)
				loadPNG(wait[i], rfilename.c_str());

			if (!wait[i])
			{
				// spinner failed
				if (i == 0)
				{
					// retry default spinner only once
					if (!def)
					{
						def = true;
						skinpath = defpath;
						continue;
					}
				}
				// exit loop because of no more spinners
				break;
			}
			i++;
		}
		eDebug("[Enigma] Found %d spinners. Position x=%d y=%d", i, spinnerPostionX, spinnerPostionY);
		if (i == 0)
			my_dc->setSpinner(eRect(spinnerPostionX, spinnerPostionY, 0, 0), wait, 1);
		else
		{
			my_dc->setSpinner(eRect(ePoint(spinnerPostionX, spinnerPostionY), wait[0]->size()), wait, i);
			float scale = my_dc->size().width() == 1920 ? 1.5 : 1.0;
			my_dc->setSpinnerScale(scale);
		}
	}

	gRC::getInstance()->setSpinnerDC(my_dc);

	eRCInput::getInstance()->keyEvent.connect(sigc::ptr_fun(&keyEvent));

	eDebug("[Enigma] Executing StartEnigma.py");

	eProfile::getInstance().write("StartPython");

	bsodCatchSignals();
	catchTermSignal();

	setIoPrio(IOPRIO_CLASS_BE, 3);

	/* start at full size */
	eVideoWidget::setFullsize(true);

	python.execFile(eEnv::resolve("${libdir}/enigma2/python/StartEnigma.py").c_str());

	/* restore both decoders to full size */
	eVideoWidget::setFullsize(true);

	if (exit_code == 5) /* python crash */
	{
		eDebug("[Enigma] Exit code 5!");
		bsodFatal(0);
	}

	dsk.paint();
	dsk_lcd.paint();

	{
		gPainter p(my_lcd_dc);
		p.resetClip(eRect(ePoint(0, 0), my_lcd_dc->size()));
		p.clear();
		p.flush();
	}
	return exit_code;
}

eWidgetDesktop *getDesktop(int which)
{
	return which ? lcddsk : wdsk;
}

eApplication *getApplication()
{
	return eApp;
}

void runMainloop()
{
	catchTermSignal();
	eApp->runLoop();
}

const char *getEnigmaVersionString()
{
	return enigma2_version;
}

const char *getBoxType()
{
	return BOXTYPE;
}

const char *getBoxBrand()
{
	return BOXBRAND;
}

#include <malloc.h>

void dump_malloc_stats(void)
{
#ifdef __GLIBC__
#if __GLIBC__ > 2 || (__GLIBC__ == 2 && __GLIBC_MINOR__ >= 33)
	struct mallinfo2 mi = mallinfo2();
	eDebug("[Enigma] MALLOC: %u total", mi.uordblks);
#else
	struct mallinfo mi = mallinfo();
	eDebug("[Enigma] MALLOC: %d total", mi.uordblks);
#endif
#else
	eDebug("[Enigma] MALLOC: info not exposed");
#endif
}

#ifdef USE_LIBVUGLES2
#include <vuplus_gles.h>
void setAnimation_current(int a)
{
	gles_set_animation_func(a);
}

void setAnimation_speed(int speed)
{
	gles_set_animation_speed(speed);
}

void setAnimation_current_listbox(int a)
{
	gles_set_animation_listbox_func(a);
}
#else
#ifndef HAVE_OSDANIMATION
void setAnimation_current(int a) {}
void setAnimation_speed(int speed) {}
void setAnimation_current_listbox(int a) {}
#endif
#endif
