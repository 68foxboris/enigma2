AC_INIT([enigma2],[4],[forum@openpli.org])
AM_INIT_AUTOMAKE([dist-bzip2 no-define tar-pax -Wno-portability])
AC_CONFIG_HEADERS([enigma2_config.h])

# Silent rules are available since 1.11, but older versions
# are still in use. So don't use them unconditionally.
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_USE_SYSTEM_EXTENSIONS
AC_SYS_LARGEFILE

AC_PROG_CC
AC_PROG_CXX
m4_ifdef([LT_INIT], [LT_INIT], [AC_PROG_LIBTOOL])
AC_CONFIG_MACRO_DIR([m4])
AC_OPENMP()

AC_PATH_PROG(MSGFMT, msgfmt, AC_MSG_ERROR(Could not find msgfmt))

AM_PATH_PYTHON
AX_PYTHON_DEVEL
AX_PKG_SWIG
AX_SWIG_ENABLE_CXX
AX_SWIG_PYTHON
AX_PTHREAD

TUXBOX_APPS_DVB

AM_CONDITIONAL(HAVE_GIT_DIR, test -d "$srcdir/.git")
AM_CONDITIONAL(HAVE_FAKE_GIT_DIR, test -f "$srcdir/.git/last_commit_info")

dnl versions of plugins-base
PKG_CHECK_MODULES(TUXTXT, tuxbox-tuxtxt)
PKG_CHECK_MODULES(BASE, [freetype2 fribidi glib-2.0 libdvbsi++ libpng libxml-2.0 sigc++-3.0 libssl libcrypto libcurl])
PKG_CHECK_MODULES(LIBDDVD, libdreamdvd, HAVE_LIBDDVD="yes", HAVE_LIBDDVD="no")
AM_CONDITIONAL(HAVE_LIBDDVD, test "$HAVE_LIBDDVD" = "yes")
PKG_CHECK_MODULES(AVAHI, avahi-client)

AC_CHECK_LIB([udfread], [udfread_init])
AC_CHECK_LIB([dl], [dlopen], [LIBDL_LIBS="-ldl"], [AC_MSG_ERROR([Could not find libdl])])
AC_SUBST(LIBDL_LIBS)
AC_CHECK_LIB([jpeg], [jpeg_set_defaults], [LIBJPEG_LIBS="-ljpeg"], [AC_MSG_ERROR([Could not find libjpeg])])
AC_SUBST(LIBJPEG_LIBS)
AC_CHECK_LIB([ungif], [DGifOpen], [LIBGIF_LIBS="-lungif"], [AC_CHECK_LIB([gif], [DGifOpen], [LIBGIF_LIBS="-lgif"], [AC_MSG_ERROR([Could not find libgif or libungif])])])
AC_SUBST(LIBGIF_LIBS)

AC_ARG_WITH(crashlogemail,
	[  --with-crashlogemail=crash log email address],
	[CRASHLOGEMAIL="$withval"],[CRASHLOGEMAIL="the OpenPLi forum"])
AC_SUBST(CRASHLOGEMAIL)
AC_DEFINE_UNQUOTED(CRASH_EMAILADDR,"$CRASHLOGEMAIL",[crash log email address])

AC_ARG_WITH(boxtype,
	AS_HELP_STRING([--with-boxtype],[build for BOXTYPE, $withval]),
	[BOXTYPE="$withval"],[BOXTYPE=""])
AC_SUBST(BOXTYPE)
AC_DEFINE_UNQUOTED(BOXTYPE,"$BOXTYPE",[box type])

AC_ARG_WITH(boxbrand,
	AS_HELP_STRING([--with-boxbrand],[build for BOXBRAND, $withval]),
	[BOXBRAND="$withval"],[BOXBRAND=""])
AC_SUBST(BOXBRAND)
AC_DEFINE_UNQUOTED(BOXBRAND,"$BOXBRAND",[box brand])

AM_CONDITIONAL(HAVE_TEMPFANCONTROL, test "$BOXTYPE" == dm8000 -o "$BOXTYPE" == dm800se -o "$BOXTYPE" == dm500hd)
AM_CONDITIONAL(DAGS, test `echo "$BOXTYPE" | cut -b 1-4` == "dags")
AM_CONDITIONAL(DREAMBOX, test `echo "$BOXTYPE" | cut -b 1-2` == "dm" -o `echo "$BOXTYPE" | cut -b 1-5` == "dream")
AM_CONDITIONAL(VUPLUS, test `echo "$BOXTYPE" | cut -b 1-2` == "vu")
AM_CONDITIONAL(XTREND, test `echo "$BOXTYPE" | cut -b 1-2` == "et")
AM_CONDITIONAL(DAGS1, test "$BOXTYPE" == dags1)
AM_CONDITIONAL(DAGS2, test "$BOXTYPE" == dags2)
AM_CONDITIONAL(DAGS3, test "$BOXTYPE" == dags3)
AM_CONDITIONAL(DAGS4, test "$BOXTYPE" == dags4)
AM_CONDITIONAL(DAGS5, test "$BOXTYPE" == dags5)
AM_CONDITIONAL(DM900, test "$BOXTYPE" == dm900)
AM_CONDITIONAL(DM920, test "$BOXTYPE" == dm920)
AM_CONDITIONAL(DM8000, test "$BOXTYPE" == dm8000)
AM_CONDITIONAL(DM7080, test "$BOXTYPE" == dm7080)
AM_CONDITIONAL(DM820, test "$BOXTYPE" == dm820)
AM_CONDITIONAL(DM520, test "$BOXTYPE" == dm520)
AM_CONDITIONAL(DM7020HD, test "$BOXTYPE" == dm7020hd)
AM_CONDITIONAL(DM7020HDV2, test "$BOXTYPE" == dm7020hdv2)
AM_CONDITIONAL(DM800, test "$BOXTYPE" == dm800)
AM_CONDITIONAL(DM800SE, test "$BOXTYPE" == dm800se)
AM_CONDITIONAL(DM800SEV2, test "$BOXTYPE" == dm800sev2)
AM_CONDITIONAL(DM500HD, test "$BOXTYPE" == dm500hd)
AM_CONDITIONAL(DM500HDV2, test "$BOXTYPE" == dm500hdv2)
AM_CONDITIONAL(DREAMONE, test "$BOXTYPE" == dreamone)
AM_CONDITIONAL(DREAMTWO, test "$BOXTYPE" == dreamtwo)
AM_CONDITIONAL(E3HD, test "$BOXTYPE" == e3hd)
AM_CONDITIONAL(FORMULER3, test "$BOXTYPE" == formuler3)
AM_CONDITIONAL(GB7252, test "$BOXTYPE" == gb7252)
AM_CONDITIONAL(VUUNO, test "$BOXTYPE" == vuuno)
AM_CONDITIONAL(VUULTIMO, test "$BOXTYPE" == vuultimo)
AM_CONDITIONAL(VUSOLO, test "$BOXTYPE" == vusolo)
AM_CONDITIONAL(VUSOLOSE, test "$BOXTYPE" == vusolose)
AM_CONDITIONAL(VUDUO, test "$BOXTYPE" == vuduo)
AM_CONDITIONAL(VUSOLO2, test "$BOXTYPE" == vusolo2)
AM_CONDITIONAL(VUSOLO4K, test "$BOXTYPE" == vusolo4k)
AM_CONDITIONAL(VUUNO4K, test "$BOXTYPE" == vuuno4k)
AM_CONDITIONAL(VUUNO4KSE, test "$BOXTYPE" == vuuno4kse)
AM_CONDITIONAL(VUULTIMO4K, test "$BOXTYPE" == vuultimo4k)
AM_CONDITIONAL(VUZERO4K, test "$BOXTYPE" == vuzero4k)
AM_CONDITIONAL(VUDUO2, test "$BOXTYPE" == vuduo2)
AM_CONDITIONAL(VUDUO4K, test "$BOXTYPE" == vuduo4k)
AM_CONDITIONAL(VUDUO4KSE, test "$BOXTYPE" == vuduo4kse)
AM_CONDITIONAL(VUZERO, test "$BOXTYPE" == vuzero)
AM_CONDITIONAL(HAVE_COLORLCD3, test "$BOXTYPE" == dm7080)
AM_CONDITIONAL(HAVE_COLORLCD240, test "$BOXTYPE" == dreamtwo)
AM_CONDITIONAL(HAVE_COLORLCD2, test "$BOXTYPE" == dm800se -o "$BOXTYPE" == dm800sev2 -o "$BOXTYPE" == dm820)
AM_CONDITIONAL(HAVE_COLORLCD1, test "$BOXTYPE" == dm8000 -o "$BOXTYPE" == dm800 -o "$BOXTYPE" == dm7020hd -o "$BOXTYPE" == dm7020hdv2)
AM_CONDITIONAL(HAVE_GRAUTEC8000, test "$BOXTYPE" == dm8000)
AM_CONDITIONAL(HAVE_GRAUTEC70X0, test "$BOXTYPE" == dm7020hd -o "$BOXTYPE" == dm7020hdv2 -o "$BOXTYPE" == dm7080)
AM_CONDITIONAL(LCD_FRAMEBUFFER_MODE, test "$BOXTYPE" == et8500 -o "$BOXTYPE" == et8500s -o "$BOXTYPE" == 8100s)

AS_IF([test "$BOXTYPE" == "dreamone"],[AC_DEFINE(HWDREAMONE, 1,[dreamone])])
AS_IF([test "$BOXTYPE" == "dreamtwo"],[AC_DEFINE(HWDREAMTWO, 1,[dreamtwo])])
AS_IF([test "$BOXTYPE" == "dm8000"],[AC_DEFINE(HWDM8000, 1,[dm8000])])
AS_IF([test "$BOXTYPE" == "dm7020hd" -o "$BOXTYPE" == "dm7020hdv2"],[AC_DEFINE(HWDM7020HD, 1,[dm7020hd])])
AS_IF([test "$BOXTYPE" == "dm7080"],[AC_DEFINE(HWDM7080, 1,[dm7080])])
AS_IF([test "$BOXTYPE" == "dm820"],[AC_DEFINE(HWDM820, 1,[dm820])])
AS_IF([test "$BOXTYPE" == "dm520" -o "$BOXTYPE" == "dm525"],[AC_DEFINE(HWDM520, 1,[dm520])])
AS_IF([test "$BOXTYPE" == "dm900"],[AC_DEFINE(HWDM900, 1,[dm900])])
AS_IF([test "$BOXTYPE" == "dm920"],[AC_DEFINE(HWDM920, 1,[dm920])])
AS_IF([test "$BOXTYPE" == "dm800se"],[AC_DEFINE(HWDM800SE, 1,[dm800se])])
AS_IF([test "$BOXTYPE" == "dm500hd"],[AC_DEFINE(HWDM500HD, 1,[dm500hd])])
AS_IF([test "$BOXTYPE" == "dm800sev2"],[AC_DEFINE(HWDM800SEV2, 1,[dm800sev2])])
AS_IF([test "$BOXTYPE" == "dm500hdv2"],[AC_DEFINE(HWDM500HDV2, 1,[dm500hdv2])])
AS_IF([test "$BOXTYPE" == "vusolo4k"],[AC_DEFINE(HWVUSOLO4K, 1,[vusolo4k])])
AS_IF([test "$BOXTYPE" == "vuultimo4k"],[AC_DEFINE(HWULTIMO4K, 1,[vuultimo4k])])
AS_IF([test "$BOXTYPE" == "h7"],[AC_DEFINE(HWH7, 1,[h7])])
AS_IF([test "$BOXTYPE" == "pulse4k"],[AC_DEFINE(HWPULSE4K, 1,[pulse4k])])
AS_IF([test "$BOXTYPE" == "pulse4kmini"],[AC_DEFINE(HWPULSE4KMINI, 1,[pulse4kmini])])
AS_IF([test "$BOXBRAND" == "gbue4k"],[AC_DEFINE(HWGBUE4K, 1,[gbue4k])])
AS_IF([test "$BOXBRAND" == "gbtrio4kpro"],[AC_DEFINE(HWGBTRIO4KPRO, 1,[gbtrio4kpro])])

AS_IF([test "$BOXTYPE" == "classm" -o "$BOXTYPE" == "axodin" -o "$BOXTYPE" == "axodinc" -o "$BOXTYPE" == "starsatlx" -o "$BOXTYPE" == "evo" -o "$BOXTYPE" == "genius" -o "$BOXTYPE" == "galaxym6"],[AC_DEFINE(PROFILE1, 1,[profile1])])
AS_IF([test "$BOXTYPE" == "gb800solo" -o "$BOXTYPE" == "gb800se" -o "$BOXTYPE" == "gb800seplus" -o "$BOXTYPE" == "gbultrase"],[AC_DEFINE(PROFILE2, 1,[profile2])])
AS_IF([test "$BOXTYPE" == "osmini" -o "$BOXTYPE" == "spycatmini" -o "$BOXTYPE" == "osminiplus" -o "$BOXTYPE" == "spycatminiplus"],[AC_DEFINE(PROFILE3, 1,[profile3])])
AS_IF([test "$BOXTYPE" == "xpeedlx3" -o "$BOXTYPE" == "sezammarvel" -o "$BOXTYPE" == "atemionemesis"],[AC_DEFINE(PROFILE4, 1,[profile4])])

AC_ARG_WITH(alphablendingacceleration,
	AS_HELP_STRING([--with-alphablendingacceleration=never/always/auto], [alphablending acceleration strategy: never accelerate / always accelerate / automatically decide when to accelerate (default)]),
	[[with_alphablendingacceleration=$withval]],
	[[with_alphablendingacceleration=auto]]
)
if test x"$with_alphablendingacceleration" = xnever ; then
	AC_DEFINE_UNQUOTED(FORCE_NO_BLENDING_ACCELERATION, 1, [Do not attempt to accelerate alphablending blits])
elif test x"$with_alphablendingacceleration" = xalways ; then
	AC_DEFINE_UNQUOTED(FORCE_ALPHABLENDING_ACCELERATION, 1, [Accelerate alphablending blits])
fi

AC_ARG_WITH(accelerationthreshold,
	AS_HELP_STRING([--with-accelerationthreshold=n], [use acceleration threshold of n bytes]),
	[[with_accelerationthreshold=$withval]],
	[[with_accelerationthreshold=48000]]
)
AC_DEFINE_UNQUOTED(GFX_SURFACE_ACCELERATION_THRESHOLD, $with_accelerationthreshold,[Configure threshold for accelerated surfaces (in bytes)])

AC_ARG_WITH(fillaccelerationthreshold,
	AS_HELP_STRING([--with-fillaccelerationthreshold=n], [use fill acceleration threshold of n bytes]),
	[[with_fillaccelerationthreshold=$withval]],
	[[with_fillaccelerationthreshold=80000]]
)
AC_DEFINE_UNQUOTED(GFX_SURFACE_FILL_ACCELERATION_THRESHOLD, $with_fillaccelerationthreshold,[Configure threshold for accelerated fill operations (in bytes)])

AC_ARG_WITH(blitaccelerationthreshold,
	AS_HELP_STRING([--with-blitaccelerationthreshold=n], [use blit acceleration threshold of n bytes]),
	[[with_blitaccelerationthreshold=$withval]],
	[[with_blitaccelerationthreshold=0]]
)
AC_DEFINE_UNQUOTED(GFX_SURFACE_BLIT_ACCELERATION_THRESHOLD, $with_blitaccelerationthreshold,[Configure threshold for accelerated blit operations (in bytes)])

AC_ARG_WITH(accelerationaccumulation,
	AS_HELP_STRING([--with-accelerationaccumulation], [accumulate blit/fill acceleration operations]),
	[[with_accelerationaccumulation=$withval]],
	[[with_accelerationaccumulation=no]]
)
if test x"$with_accelerationaccumulation" = xyes ; then
	AC_DEFINE(SUPPORT_ACCUMULATED_ACCELERATION_OPERATIONS, 1,[Accumulate blit/fill acceleration operations])
fi

AC_ARG_WITH(libvugles2,
	AS_HELP_STRING([--with-libvugles2],[use libvugles2, yes or no]),
	[with_libvugles2=$withval],[with_libvugles2=no])
if test "$with_libvugles2" = "yes"; then
	PKG_CHECK_MODULES(LIBVUGLES2, [libvugles2])
	GLES_CFLAGS="-DUSE_LIBVUGLES2"
fi
AM_CONDITIONAL(HAVE_LIBVUGLES2, test "$with_libvugles2" = "yes")

AC_ARG_WITH(osdanimation,
	AS_HELP_STRING([--with-osdanimation], [use osd animation, yes or no]),
	[[withosdanimation=$withval]],
	[[withosdanimation=no]]
)
if test x"$withosdanimation" != xno ; then
	AC_DEFINE(HAVE_OSDANIMATION, 1,[Define if driver supports animation of osd])
fi
AM_CONDITIONAL(HAVE_OSDANIMATION, test x"$withosdanimation" != xno)

if test `echo "$BOXTYPE" | cut -b 1-2` == "dm" -o `echo "$BOXTYPE" | cut -b 1-5` == "dream"; then
	AC_DEFINE(DREAMBOX, 1, [Dreambox hardware])
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
fi

AC_ARG_WITH(nolcd,
	AS_HELP_STRING([--with-nolcd], [disable ascii based lcd, yes or no]),
	[[withnolcd=$withval]],
	[[withnolcd=no]]
)
if test x"$withnolcd" != xno ; then
	AC_DEFINE(NO_LCD, 1,[Define when disable an ascii based lcd device])
fi
AM_CONDITIONAL(NO_LCD, test x"$withnolcd" != xno)

AC_ARG_WITH(textlcd,
	AS_HELP_STRING([--with-textlcd], [use ascii based lcd, yes or no]),
	[[withtextlcd=$withval]],
	[[withtextlcd=no]]
)
if test x"$withtextlcd" != xno ; then
	AC_DEFINE(HAVE_TEXTLCD, 1,[Define when using an ascii based lcd device])
fi
AM_CONDITIONAL(HAVE_TEXTLCD, test x"$withtextlcd" != xno)

AC_ARG_WITH(7segment,
	AS_HELP_STRING([--with-7segment], [use ascii based lcd, yes or no]),
	[[with7segment=$withval]],
	[[with7segment=no]]
)
if test x"$with7segment" != xno ; then
	AC_DEFINE(HAVE_7SEGMENT, 1,[Define when using an ascii based lcd device])
fi
AM_CONDITIONAL(HAVE_7SEGMENT, test x"$with7segment" != xno)

AC_ARG_WITH(bwlcd96,
	AS_HELP_STRING([--with-bwlcd96], [use 96x64 1bpp black and white display, yes or no]),
	[[withbwlcd96=$withval]],
	[[withbwlcd96=no]]
)
if test x"$withbwlcd96" != xno ; then
	AC_DEFINE(HAVE_BWLCD96, 1,[Define when using a 96x64 black and white display device])
fi
AM_CONDITIONAL(HAVE_BWLCD96, test x"$withbwlcd96" != xno)

AC_ARG_WITH(colorlcd,
	AS_HELP_STRING([--with-colorlcd], [use 96x64 16bpp color display, yes or no]),
	[[withcolorlcd=$withval]],
	[[withcolorlcd=no]]
)
if test x"$withcolorlcd" != xno ; then
	AC_DEFINE(HAVE_COLORLCD, 1,[Define when using a 96x64 color display device])
fi
AM_CONDITIONAL(HAVE_COLORLCD, test x"$withcolorlcd" != xno)

AC_ARG_WITH(colorlcd128,
	AS_HELP_STRING([--with-colorlcd128], [use 128x64 16bpp color display, yes or no]),
	[[withcolorlcd128=$withval]],
	[[withcolorlcd128=no]]
)
if test x"$withcolorlcd128" != xno ; then
	AC_DEFINE(HAVE_COLORLCD128, 1,[Define when using a 128x64 color display device])
fi
AM_CONDITIONAL(HAVE_COLORLCD128, test x"$withcolorlcd" != xno)

AC_ARG_WITH(colorlcd220,
	AS_HELP_STRING([--with-colorlcd220], [use 220x176 16bpp color display, yes or no]),
	[[withcolorlcd220=$withval]],
	[[withcolorlcd220=no]]
)
if test x"$withcolorlcd220" != xno ; then
	AC_DEFINE(HAVE_COLORLCD220, 1,[Define when using a 220x176 color display device])
fi
AM_CONDITIONAL(HAVE_COLORLCD220, test x"$withcolorlcd220" != xno)

AC_ARG_WITH(colorlcd240,
	AS_HELP_STRING([--with-colorlcd240], [use 240x80 16bpp color display, yes or no]),
	[[withcolorlcd240=$withval]],
	[[withcolorlcd240=no]]
)
if test x"$withcolorlcd240" != xno ; then
	AC_DEFINE(HAVE_COLORLCD240, 1,[Define when using a 240x80 color display device])
fi
AM_CONDITIONAL(HAVE_COLORLCD240, test x"$withcolorlcd240" != xno)

AC_ARG_WITH(colorlcd390,
	AS_HELP_STRING([--with-colorlcd390], [use 390x240 16bpp color display, yes or no]),
	[[withcolorlcd390=$withval]],
	[[withcolorlcd390=no]]
)
if test x"$withcolorlcd390" != xno ; then
	AC_DEFINE(HAVE_COLORLCD390, 1,[Define when using a 390x240 color display device])
fi

AM_CONDITIONAL(HAVE_COLORLCD390, test x"$withcolorlcd390" != xno)

AC_ARG_WITH(colorlcd400,
	AS_HELP_STRING([--with-colorlcd400], [use 400x176 16bpp color display, yes or no]),
	[[withcolorlcd400=$withval]],
	[[withcolorlcd400=no]]
)
if test x"$withcolorlcd400" != xno ; then
	AC_DEFINE(HAVE_COLORLCD400, 1,[Define when using a 400x176 color display device])
fi

AM_CONDITIONAL(HAVE_COLORLCD400, test x"$withcolorlcd400" != xno)

AC_ARG_WITH(colorlcd480,
	AS_HELP_STRING([--with-colorlcd480], [use 480x320 16bpp color display, yes or no]),
	[[withcolorlcd480=$withval]],
	[[withcolorlcd480=no]]
)
if test x"$withcolorlcd480" != xno ; then
	AC_DEFINE(HAVE_COLORLCD480, 1,[Define when using a 480x320 color display device])
fi

AM_CONDITIONAL(HAVE_COLORLCD480, test x"$withcolorlcd480" != xno)

AC_ARG_WITH(colorlcd720,
	AS_HELP_STRING([--with-colorlcd720], [use 720x576 16bpp color display, yes or no]),
	[[withcolorlcd720=$withval]],
	[[withcolorlcd720=no]]
)
if test x"$withcolorlcd720" != xno ; then
	AC_DEFINE(HAVE_COLORLCD720, 1,[Define when using a 720x576 color display device])
fi

AM_CONDITIONAL(HAVE_COLORLCD720, test x"$withcolorlcd720" != xno)

AC_ARG_WITH(colorlcd800,
	AS_HELP_STRING([--with-colorlcd800], [use 800x480 16bpp color display, yes or no]),
	[[withcolorlcd800=$withval]],
	[[withcolorlcd800=no]]
)
if test x"$withcolorlcd800" != xno ; then
	AC_DEFINE(HAVE_COLORLCD800, 1,[Define when using a 800x480 color display device])
fi

AM_CONDITIONAL(HAVE_COLORLCD800, test x"$withcolorlcd800" != xno)

AC_ARG_WITH(bwlcd255,
	AS_HELP_STRING([--with-bwlcd255], [use 255x64 1bpp black and white display, yes or no]),
	[[withbwlcd255=$withval]],
	[[withbwlcd255=no]]
)
if test x"$withbwlcd255" != xno ; then
	AC_DEFINE(HAVE_BWLCD255, 1,[Define when using a 255x64 black and white display device])
fi
AM_CONDITIONAL(HAVE_BWLCD255, test x"$withbwlcd255" != xno)

AC_ARG_WITH(bwlcd140,
	AS_HELP_STRING([--with-bwlcd140], [use 140x32 1bpp black and white display, yes or no]),
	[[withbwlcd140=$withval]],
	[[withbwlcd140=no]]
)
if test x"$withbwlcd140" != xno ; then
	AC_DEFINE(HAVE_BWLCD140, 1,[Define when using a 140x32 black and white display device])
fi
AM_CONDITIONAL(HAVE_BWLCD140, test x"$withbwlcd140" != xno)

AC_ARG_WITH(bwlcd128,
	AS_HELP_STRING([--with-bwlcd128], [use 128x32 1bpp black and white display, yes or no]),
	[[withbwlcd128=$withval]],
	[[withbwlcd128=no]]
)
if test x"$withbwlcd128" != xno ; then
	AC_DEFINE(HAVE_BWLCD128, 1,[Define when using a 128x32 black and white display device])
fi
AM_CONDITIONAL(HAVE_BWLCD128, test x"$withbwlcd128" != xno)

AC_ARG_WITH(libsdl,
	AS_HELP_STRING([--with-libsdl],[use libsdl, yes or no]),
	[with_libsdl=$withval],[with_libsdl=no])
if test "$with_libsdl" = "yes"; then
	PKG_CHECK_MODULES(LIBSDL, sdl)
fi
AM_CONDITIONAL(HAVE_LIBSDL, test "$with_libsdl" = "yes")

AC_ARG_WITH(libxine,
	AS_HELP_STRING([--with-libxine],[use libxine, yes or no]),
	[with_libxine=$withval],[with_libxine=no])
if test "$with_libxine" = "yes"; then
	PKG_CHECK_MODULES(LIBXINE, libxine)
	AC_DEFINE([WITH_XINE],[1],[Define to 1 if you have libxine])
fi
AM_CONDITIONAL(HAVE_LIBXINE, test "$with_libxine" = "yes")

AC_ARG_WITH(debug,
	AS_HELP_STRING([--without-debug],[disable debugging code]),
	[with_debug="$withval"],[with_debug="yes"])
if test "$with_debug" = "yes"; then
	AC_DEFINE([DEBUG],[1],[Define to 1 to enable debugging code])
fi

AC_ARG_WITH(memcheck,
	AS_HELP_STRING([--with-memcheck],[enable memory leak checks]),
	[with_memcheck="$withval"],[with_memcheck="no"])
if test "$with_memcheck" = "yes"; then
	AC_DEFINE([MEMLEAK_CHECK],[1],[Define to 1 to enable memory leak checks])
fi

AC_ARG_WITH(po,
	AS_HELP_STRING([--with-po],[enable updating of po files]),
	[with_po="$withval"],[with_po="no"])
if test "$with_po" = "yes"; then
	AC_PATH_PROG(MSGINIT, msginit)
	AC_PATH_PROG(MSGMERGE, msgmerge)
	AC_PATH_PROG(MSGUNIQ, msguniq)
	AC_PATH_PROG(MSGATTRIB, msgattrib)
	AC_PATH_PROG(XGETTEXT, xgettext)
	if test -z "$MSGINIT" -o -z "$MSGMERGE" -o -z "$MSGUNIQ" -o -z "$MSGATTRIB" -o -z "$XGETTEXT"; then
		AC_MSG_ERROR([Could not find required gettext tools])
	fi
fi
AM_CONDITIONAL(UPDATE_PO, test "$with_po" = "yes")

AC_ARG_WITH(alsa,
	AS_HELP_STRING([--with-alsa], [Enable ALSA support]),
	[[with_alse=$withval]],
	[[with_alse=no]]
)
if test x"$with_alsa" == xyes ; then
	AC_DEFINE(HAVE_ALSA, 1,[Enables ALSA support])
	PKG_CHECK_MODULES(ALSA, alsa)
fi

AC_ARG_WITH(alsacard,
	AS_HELP_STRING([--with-alsacard=card], [use 'card' for alsa card device, e.g. hw:0]),
	[[with_alsacard=$withval]],
	[[with_alsacard=no]]
)
if test x"$with_alsacard" != xno ; then
	AC_DEFINE_UNQUOTED(ALSA_CARD, "$withval",[Defines which alsa card to use])
fi

AC_ARG_WITH(alsamixer,
	AS_HELP_STRING([--with-alsamixer=mixername], [use alsa 'mixername' for volume control, e.g. Master]),
	[[with_alsamixer=$withval]],
	[[with_alsamixer=no]]
)
if test x"$with_alsamixer" != xno ; then
	AC_DEFINE_UNQUOTED(ALSA_VOLUME_MIXER, "$withval",[Defines which alsa mixer to use for volume control])
fi

AC_ARG_WITH(fbdev,
	AS_HELP_STRING([--with-fbdev=devicename], [use devicename for framebuffer device, e.g. /dev/fb0 ]),
	[[with_fbdev=$withval]],
	[[with_fbdev=no]]
)
if test x"$with_fbdev" != xno ; then
	AC_DEFINE_UNQUOTED(FB_DEV, "$withval", [Defines which device to use for main framebuffer (e.g. /dev/fb0)])
fi

AC_ARG_WITH(lcddev,
	AS_HELP_STRING([--with-lcddev=devicename], [use devicename for lcd framebuffer device, e.g. /dev/fb1 ]),
	[[with_lcddev=$withval]],
	[[with_lcddev=no]]
)
if test x"$with_lcddev" != xno ; then
	AC_DEFINE_UNQUOTED(LCD_DEV, "$withval", [Defines which device to use for lcd (e.g. /dev/fb1)])
fi

AC_ARG_WITH(fhdskin,
	AS_HELP_STRING([--with-fhdskin], [use full hd skin, yes or no]),
	[[withfhdskin=$withval]],
	[[withfhdskin=no]]
)
if test x"$with_fhdskin" != xno ; then
	AC_DEFINE(HAVE_FHDSKIN, 1,[Define if box supports full hd skin])
fi
AM_CONDITIONAL(HAVE_FHDSKIN, test x"$withfhdskin" != xno)

AC_ARG_WITH(amlogic,
	AS_HELP_STRING([--with-amlogic], [use amlogic MPEG decoder]),
	[[with_amlogic=$withval]],
	[[with_amlogic=no]]
)

AM_CONDITIONAL(DREAMNEXTGEN, test "$BOXTYPE" == dreamone -o "$BOXTYPE" == dreamtwo)
if test "$BOXTYPE" == "dreamone" -o "$BOXTYPE" == "dreamtwo"; then
	ALSA_CFLAGS="-lasound"
	FFMPEG_CFLAGS=" -lavdevice -lavformat -lavcodec -lswresample -lswscale -lavutil -lm "
	#AC_DEFINE(DREAMNEXTGEN, 1, [Dreambox NexT Generation Hardware])
fi

if test "$BOXTYPE" == "vusolo4k" -o "$BOXTYPE" == "vuuno4k" -o "$BOXTYPE" == "vuuno4kse" -o "$BOXTYPE" == "vuultimo4k" -o "$BOXTYPE" == "vuzero4k" -o "$BOXTYPE" == "vuduo4k" -o "$BOXTYPE" == "vuduo4kse" -o "$BOXTYPE" == "sf8008" -o "$BOXTYPE" == "sf8008m" -o "$BOXTYPE" == "sx988" -o "$BOXTYPE" == "ip8" -o "$BOXTYPE" == "ustym4kpro" -o "$BOXTYPE" == "ustym4kottpremium" -o "$BOXTYPE" == "ustym4ks2ottx" -o "$BOXTYPE" == "gbmv200" -o "$BOXTYPE" == "beyonwizv2" -o "$BOXTYPE" == "viper4k" -o "$BOXTYPE" == "dagsmv200" -o "$BOXTYPE" == "og2ott4k" -o "$BOXTYPE" == "og2s4k" -o "$BOXTYPE" == "sfx6008" -o "$BOXTYPE" == "sx88v2"; then
	AC_DEFINE(VMSG_TYPE2, 1,[define vtuner_message type 2])
fi

if test "$BOXTYPE" == "vuzero" -o "$BOXTYPE" == "vuuno" -o "$BOXTYPE" == "vuultimo" -o "$BOXTYPE" == "vusolose" -o "$BOXTYPE" == "vusolo2" -o "$BOXTYPE" == "vusolo" -o "$BOXTYPE" == "vuduo2" -o "$BOXTYPE" == "vuduo"; then
	AC_DEFINE(FORCE_AUTO_INV, 1,[force Inversion auto for vu mipsel boxes])
fi

if test "$BOXTYPE" == "vuduo" -o "$BOXTYPE" == "vusolo" -o "$BOXTYPE" == "vuduo2" -o "$BOXTYPE" == "vusolo2" -o "$BOXTYPE" == "vuuno" -o "$BOXTYPE" == "vuultimo" -o "$BOXTYPE" == "vusolose" -o "$BOXTYPE" == "vuzero" -o "$BOXTYPE" == "vusolo4k" -o "$BOXTYPE" == "vuuno4k" -o "$BOXTYPE" == "vuuno4kse" -o "$BOXTYPE" == "vuultimo4k" -o "$BOXTYPE" == "vuzero4k" -o "$BOXTYPE" == "vuduo4k" -o "$BOXTYPE" == "vuduo4kse"; then
	AC_DEFINE(FORCE_NO_BLENDING_ACCELERATION, 1,[define when the framebuffer acceleration does not have alphablending support, though the autodetection might indicate that it does])
	AC_DEFINE(FORCE_ADVANCED_REMOTE, 1,[define to fixup the input device identification when the remote control is actually an 'advanced' remote (with play/forward/rewind keys)])
	AC_DEFINE(KEY_HELP_TO_KEY_INFO, 1,[define when rc sends a KEY_HELP event we need KEY_INFO])
	AC_DEFINE(KEY_INFO_TO_KEY_EPG, 1,[define when rc sends a KEY_INFO event for its KEY_EPG key])
	AC_DEFINE(KEY_EDIT_TO_KEY_TIME, 1,[define when rc sends a KEY_TIME event for its KEY_EDIT key])
fi

if test "$BOXTYPE" == "dm7080" -o "$BOXTYPE" == "dm820" -o "$BOXTYPE" == "dm800se" -o "$BOXTYPE" == "dm800sev2" -o "$BOXTYPE" == "dm7020hd" -o "$BOXTYPE" == "dm7020hdv2" -o "$BOXTYPE" == "dreamone" -o "$BOXTYPE" == "dreamtwo" -o "$BOXTYPE" == "dm900" -o "$BOXTYPE" == "dm920"; then
	AC_DEFINE(DREAMBOX_DUAL_TUNER, 1,[define BOXTYPE DM7080])
fi

if test "$BOXTYPE" == "dm7080" -o "$BOXTYPE" == "dm820" -o "$BOXTYPE" == "dm900" -o "$BOXTYPE" == "dm920" -o "$BOXTYPE" == "dm520"; then
	AC_DEFINE(CONFIG_ION, 1,[define BOX use ION Allocator])
fi

if test "$BOXTYPE" == "dm7080" -o "$BOXTYPE" == "dm820" -o "$BOXTYPE" == "dm900" -o "$BOXTYPE" == "dm920"; then
	AC_DEFINE(HAVE_HDMIIN_DM, 1,[has hdmi in dm])
fi

if test "$BOXTYPE" == "dm900" -o "$BOXTYPE" == "dm920"; then
	AC_DEFINE(LCD_DM900_Y_OFFSET, 4,[define LCD Y offset for dm900 and dm920])
fi

if test "$BOXTYPE" == "sf8008" -o "$BOXTYPE" == "sf8008m" -o "$BOXTYPE" == "sx988" -o "$BOXTYPE" == "ip8" -o "$BOXTYPE" == "ustym4kpro" -o "$BOXTYPE" == "ustym4kottpremium" -o "$BOXTYPE" == "ustym4ks2ottx" -o "$BOXTYPE" == "gbmv200" -o "$BOXTYPE" == "beyonwizv2" -o "$BOXTYPE" == "viper4k" -o "$BOXTYPE" == "dagsmv200" -o "$BOXTYPE" == "og2ott4k" -o "$BOXTYPE" == "og2s4k" -o "$BOXTYPE" == "sfx6008" -o "$BOXTYPE" == "sx88v2"; then
	AC_DEFINE(HAVE_HISILICON, 1,[define add HISILICON chip])
	AC_DEFINE(CONFIG_HISILICON_FB, 1,[define add HISILICON framebuffer blit])
	AC_DEFINE(FORCE_ALPHABLENDING_ACCELERATION, 1,[define when the framebuffer acceleration has alphablending support, but detection slow down all])
fi

if test "$BOXTYPE" == "ultramini" -o "$BOXTYPE" == "et1x000" -o "$BOXTYPE" == "et7x00"; then
	AC_DEFINE(KEY_F1_TO_KEY_F2, 1,[define when rc sends a KEY_F1 event for its KEY_F2 key])
	AC_DEFINE(FORCE_ALPHABLENDING_ACCELERATION, 1,[define when the framebuffer acceleration has alphablending support, but detection slow down all])
fi

if test "$BOXTYPE" == "g300" -o "$BOXTYPE" == "g100" -o "$BOXTYPE" == "sf4008" -o "$BOXTYPE" == "g101" -o "$BOXTYPE" == "et1x000"; then
	AC_DEFINE(FORCE_ALPHABLENDING_ACCELERATION, 1,[define when the framebuffer acceleration has alphablending support, but detection slow down all])
fi

if test "$BOXTYPE" == "osnino" -o "$BOXTYPE" == "osninoplus" -o "$BOXTYPE" == "osninopro" -o "$BOXTYPE" == "osmio4k" -o "$BOXTYPE" == "osmio4kplus" -o "$BOXTYPE" == "osmini4k"; then
	AC_DEFINE(KEY_MEDIA_TO_KEY_LIST, 1,[define MEDIA to LIST])
	AC_DEFINE(KEY_VIDEO_TO_KEY_ANGLE, 1,[define VIDEO to ANGLE])
fi

if test "$BOXTYPE" == "osmio4k" -o "$BOXTYPE" == "osmio4kplus" -o "$BOXTYPE" == "osmini4k"; then
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
fi

if test "$BOXTYPE" == "formuler1" -o "$BOXTYPE" == "formuler3" -o "$BOXTYPE" == "formuler4" -o "$BOXTYPE" == "formuler4turbo" -o "$BOXTYPE" == "triplex" -o "$BOXTYPE" == "sf108" -o "$BOXTYPE" == "ultrabox" -o "$BOXTYPE" == "formuler1tc" -o "$BOXTYPE" == "formuler3ip" -o "$BOXTYPE" == "formuler4ip"; then
	AC_DEFINE(KEY_F3_TO_KEY_LIST, 1,[define when rc sends a KEY_F3 event for its KEY_LIST key])
	AC_DEFINE(KEY_LAST_TO_KEY_BACK, 1,[define when rc sends a KEY_LAST event for its KEY_BACK key])
	AC_DEFINE(KEY_BOOKMARKS_TO_KEY_MEDIA, 1,[define when rc Playlist sends a KEY_BOOKMARKS event for its KEY_MEDIA key])
	AC_DEFINE(KEY_VIDEO_TO_KEY_FAVORITES, 1,[define when rc FAV key sends a KEY_VIDEO event for its KEY_FAVORITES key])
fi

if test "$BOXTYPE" == "sf4008" -o "$BOXTYPE" == "beyonwizu4"; then
	AC_DEFINE(LCD_SCROLL_HEX, 1,[define LCD scroll values in hex])
AS_IF([test "$BOXTYPE" == "classm" -o "$BOXTYPE" == "axodin" -o "$BOXTYPE" == "axodinc" -o "$BOXTYPE" == "starsatlx" -o "$BOXTYPE" == "evo" -o "$BOXTYPE" == "genius" -o "$BOXTYPE" == "galaxym6"],[AC_DEFINE(PROFILE1, 1,[profile1])])
AS_IF([test "$BOXTYPE" == "gb800solo" -o "$BOXTYPE" == "gb800se" -o "$BOXTYPE" == "gb800seplus" -o "$BOXTYPE" == "gbultrase"],[AC_DEFINE(PROFILE2, 1,[profile2])])
AS_IF([test "$BOXTYPE" == "osmini" -o "$BOXTYPE" == "spycatmini" -o "$BOXTYPE" == "osminiplus" -o "$BOXTYPE" == "spycatminiplus"],[AC_DEFINE(PROFILE3, 1,[profile3])])
AS_IF([test "$BOXTYPE" == "xpeedlx3" -o "$BOXTYPE" == "sezammarvel" -o "$BOXTYPE" == "atemionemesis"],[AC_DEFINE(PROFILE4, 1,[profile4])])

# VFD Symbols Poll Time
if test "$BOXTYPE" == "9910lx" -o "$BOXTYPE" == "9911lx" -o "$BOXTYPE" == "9920lx" -o "$BOXTYPE" == "dm7020hd" -o "$BOXTYPE" == "dm7020hdv2" -o "$BOXTYPE" == "dual" -o "$BOXTYPE" == "e4hd" -o "$BOXTYPE" == "e4hdhybrid" -o "$BOXTYPE" == "force3uhd" -o "$BOXTYPE" == "mbmicro" -o "$BOXTYPE" == "mbmicrov2" -o "$BOXTYPE" == "osnino" -o "$BOXTYPE" == "osninoplus" -o "$BOXTYPE" == "osninopro" -o "$BOXTYPE" == "revo4k" -o "$BOXTYPE" == "tmtwin4k" -o "$BOXTYPE" == "beyonwizv2" -o "$BOXTYPE" == "dags7362" -o "$BOXTYPE" == "dags73625" -o "$BOXTYPE" == "gbmv200" -o "$BOXTYPE" == "sf8008" -o "$BOXTYPE" == "sf8008m" -o "$BOXTYPE" == "sfx6008" -o "$BOXTYPE" == "sx888" -o "$BOXTYPE" == "sx88v2" -o "$BOXTYPE" == "ustym4kpro" -o "$BOXTYPE" == "ustym4ks2ottx" -o "$BOXTYPE" == "viper4k"; then
	AC_DEFINE(VFDSymbolsPoll, 1,[define VFD Symbols Poll])
else
	if test "$BOXTYPE" == "u41" -o "$BOXTYPE" == "alphatriple" -o "$BOXTYPE" == "atemio5x00" -o "$BOXTYPE" == "beyonwizt3" -o "$BOXTYPE" == "et7500" -o "$BOXTYPE" == "maram9" -o "$BOXTYPE" == "mbmini" -o "$BOXTYPE" == "mbtwin" -o "$BOXTYPE" == "osmega" -o "$BOXTYPE" == "osminiplus" -o "$BOXTYPE" == "sezam1000hd" -o "$BOXTYPE" == "sezam5000hd" -o "$BOXTYPE" == "sf3038" -o "$BOXTYPE" == "spycat" -o "$BOXTYPE" == "spycat4kmini" -o "$BOXTYPE" == "uniboxhd1" -o "$BOXTYPE" == "uniboxhd2" -o "$BOXTYPE" == "uniboxhd3"; then
		AC_DEFINE(VFDSymbolsPoll, 5,[define VFD Symbols Poll])
	else
		AC_DEFINE(VFDSymbolsPoll, 0,[define VFD Symbols Poll])
	fi
fi

if test "$BOXTYPE" == "hd2400" -o "$BOXTYPE" == "hd11" -o "$BOXTYPE" == "hd1100" -o "$BOXTYPE" == "hd1200" -o "$BOXTYPE" == "hd500c" -o "$BOXTYPE" == "hd530c" -o "$BOXTYPE" == "hd1265" -o "$BOXTYPE" == "hd1500" -o "$BOXTYPE" == "hd51" -o "$BOXTYPE" == "hd60" -o "$BOXTYPE" == "hd61" -o "$BOXTYPE" == "hd66se" -o "$BOXTYPE" == "pulse4k" -o "$BOXTYPE" == "pulse4kmini" -o "$BOXTYPE" == "hd52" -o "$BOXTYPE" == "vs1000" -o "$BOXTYPE" == "vs1500"; then
	AC_DEFINE(KEY_PLAY_ACTUALLY_IS_KEY_PLAYPAUSE, 1,[define when rc sends a KEY_PLAY event for its KEY_PLAYPAUSE key])
	AC_DEFINE(KEY_F3_TO_KEY_LIST, 1,[define when rc sends a KEY_F3 event for its KEY_LIST key])
fi

AC_CHECK_HEADERS([sys/klog.h])
AC_CHECK_FUNCS([klogctl])

AC_CHECK_HEADERS([shadow.h])
AC_CHECK_LIB([crypt], [crypt], [BASE_LIBS+=" -lcrypt"], [AC_MSG_ERROR([Could not find crypt])])
AC_CHECK_LIB([rt], [clock_gettime], [BASE_LIBS+=" -lrt"], [AC_MSG_ERROR([Could not find rt])])

ENIGMA2_CFLAGS="-fno-rtti -fno-exceptions -rdynamic -funwind-tables"
AC_SUBST(ENIGMA2_CFLAGS)

AX_CXX_COMPILE_STDCXX_17([ext],[mandatory])

AX_CHECK_COMPILE_FLAG([-Wattribute-alias], [CXXFLAGS="$CXXFLAGS -Wattribute-alias"])
AX_CHECK_COMPILE_FLAG([-Wattribute-alias=1], [CXXFLAGS="$CXXFLAGS -Wattribute-alias=1"])

CPPFLAGS="$CPPFLAGS $PYTHON_CPPFLAGS"
CFLAGS="$CFLAGS -Wall"
CXXFLAGS="$CXXFLAGS -Wall $BASE_CFLAGS $ENIGMA2_CFLAGS $PTHREAD_CFLAGS $OPENMP_CFLAGS $GLES_CFLAGS $ALSA_CFLAGS $AMCODEC_CFLAGS $AMADEC_CFLAGS $DVBCSA_CFLAGS $FFMPEG_CFLAGS"

AX_SWIG_PYTHON_OPT="$AX_SWIG_PYTHON_OPT -DSWIG_PYTHON_LEGACY_BOOL"

ARFLAGS="cr"
AC_SUBST(ARFLAGS)
AR_FLAGS="cr"
AC_SUBST(AR_FLAGS)

AC_CONFIG_FILES([
Makefile
data/Makefile
data/fonts/Makefile
data/countries/Makefile
data/display/Makefile
data/display/7segment/Makefile
data/display/display/Makefile
data/display/display96/Makefile
data/display/display128/Makefile
data/display/display128dm/Makefile
data/display/display220/Makefile
data/display/display240/Makefile
data/display/display390/Makefile
data/display/display400/Makefile
data/display/display480/Makefile
data/display/display720/Makefile
data/display/display800/Makefile
data/display/displaytext/Makefile
data/display/grautec70x0/Makefile
data/display/grautec70x0/fonts/Makefile
data/display/grautec8000/Makefile
data/display/grautec8000/fonts/Makefile
data/display/vfd128/Makefile
data/display/vfd140/Makefile
data/display/vfd255/Makefile
data/extensions/Makefile
data/keymaps/Makefile
data/rc_models/Makefile
data/skin_default/Makefile
data/skin_default/menu/Makefile
data/skin_default/icons/Makefile
data/skin_default/buttons/Makefile
data/skin_default/epg/Makefile
data/skin_default/spinner/Makefile
data/skin_default/LCDIcons/Makefile
include/Makefile
lib/Makefile
lib/base/eenv.cpp
lib/python/Makefile
lib/python/Components/Makefile
lib/python/Components/Addons/Makefile
lib/python/Components/Converter/Makefile
lib/python/Components/Renderer/Makefile
lib/python/Components/Sources/Makefile
lib/python/Screens/Makefile
lib/python/Plugins/Makefile
lib/python/Plugins/SystemPlugins/CableScan/Makefile
lib/python/Plugins/SystemPlugins/FastScan/Makefile
lib/python/Plugins/SystemPlugins/OSDPositionSetup/Makefile
lib/python/Plugins/SystemPlugins/OSD3DSetup/Makefile
lib/python/Plugins/SystemPlugins/HdmiCEC/Makefile
lib/python/Plugins/SystemPlugins/VideoClippingSetup/Makefile
lib/python/Plugins/Extensions/CutListEditor/Makefile
lib/python/Plugins/Extensions/CutListEditor/meta/Makefile
lib/python/Plugins/Extensions/DVDBurn/Makefile
lib/python/Plugins/Extensions/DVDBurn/meta/Makefile
lib/python/Plugins/Extensions/DVDPlayer/Makefile
lib/python/Plugins/Extensions/DVDPlayer/meta/Makefile
lib/python/Plugins/Extensions/GraphMultiEPG/Makefile
lib/python/Plugins/Extensions/GraphMultiEPG/meta/Makefile
lib/python/Plugins/Extensions/Makefile
lib/python/Plugins/Extensions/MediaPlayer/Makefile
lib/python/Plugins/Extensions/MediaPlayer/meta/Makefile
lib/python/Plugins/Extensions/MediaScanner/Makefile
lib/python/Plugins/Extensions/MediaScanner/meta/Makefile
lib/python/Plugins/Extensions/MiniTV/Makefile
lib/python/Plugins/Extensions/PicturePlayer/Makefile
lib/python/Plugins/Extensions/PicturePlayer/meta/Makefile
lib/python/Plugins/Extensions/PicturePlayer/data/Makefile
lib/python/Plugins/Extensions/SocketMMI/Makefile
lib/python/Plugins/Extensions/SocketMMI/meta/Makefile
lib/python/Plugins/Extensions/SocketMMI/src/Makefile
lib/python/Plugins/Extensions/QuadPip/Makefile
lib/python/Plugins/PLi/Makefile
lib/python/Plugins/SystemPlugins/AnimationSetup/Makefile
lib/python/Plugins/SystemPlugins/AnimationSetup/meta/Makefile
lib/python/Plugins/SystemPlugins/CommonInterfaceAssignment/Makefile
lib/python/Plugins/SystemPlugins/CommonInterfaceAssignment/meta/Makefile
lib/python/Plugins/SystemPlugins/DefaultServicesScanner/Makefile
lib/python/Plugins/SystemPlugins/DefaultServicesScanner/meta/Makefile
lib/python/Plugins/SystemPlugins/DiseqcTester/Makefile
lib/python/Plugins/SystemPlugins/DiseqcTester/meta/Makefile
lib/python/Plugins/SystemPlugins/FastChannelChange/Makefile
lib/python/Plugins/SystemPlugins/FastChannelChange/meta/Makefile
lib/python/Plugins/SystemPlugins/Hotplug/Makefile
lib/python/Plugins/SystemPlugins/Hotplug/meta/Makefile
lib/python/Plugins/SystemPlugins/Makefile
lib/python/Plugins/SystemPlugins/TempFanControl/Makefile
lib/python/Plugins/SystemPlugins/TempFanControl/meta/Makefile
lib/python/Plugins/SystemPlugins/NetworkWizard/Makefile
lib/python/Plugins/SystemPlugins/NetworkWizard/meta/Makefile
lib/python/Plugins/SystemPlugins/PositionerSetup/Makefile
lib/python/Plugins/SystemPlugins/PositionerSetup/meta/Makefile
lib/python/Plugins/SystemPlugins/SatelliteEquipmentControl/Makefile
lib/python/Plugins/SystemPlugins/SatelliteEquipmentControl/meta/Makefile
lib/python/Plugins/SystemPlugins/Satfinder/Makefile
lib/python/Plugins/SystemPlugins/Satfinder/meta/Makefile
lib/python/Plugins/SystemPlugins/SoftwareManager/Makefile
lib/python/Plugins/SystemPlugins/SoftwareManager/meta/Makefile
lib/python/Plugins/SystemPlugins/VideoEnhancement/Makefile
lib/python/Plugins/SystemPlugins/VideoEnhancement/meta/Makefile
lib/python/Plugins/SystemPlugins/VideoTune/Makefile
lib/python/Plugins/SystemPlugins/VideoTune/meta/Makefile
lib/python/Plugins/SystemPlugins/Videomode/Makefile
lib/python/Plugins/SystemPlugins/Videomode/meta/Makefile
lib/python/Plugins/SystemPlugins/WirelessLan/Makefile
lib/python/Plugins/SystemPlugins/WirelessLan/meta/Makefile
lib/python/Tools/Makefile
po/Makefile
main/Makefile
tools/Makefile
tools/enigma2.sh
enigma2.pc
])
AC_OUTPUT
