installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = CutListEditor FileCommander PicturePlayer MediaScanner MediaPlayer GraphMultiEPG SocketMMI DVDBurn StreamlinkWrapper YTDLWrapper YTDLPWrapper

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VUSOLO4K
SUBDIRS += MiniTV
endif

if VUULTIMO4K
SUBDIRS += MiniTV
endif

if VUUNO4KSE
SUBDIRS += MiniTV
endif

if VUDUO4K
SUBDIRS += MiniTV
endif

if VUDUO4KSE
SUBDIRS += MiniTV
endif

install_PYTHON =	\
	__init__.py
