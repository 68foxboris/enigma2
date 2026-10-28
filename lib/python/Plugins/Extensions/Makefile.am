installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = CutListEditor FileCommander PicturePlayer MediaScanner MediaPlayer GraphMultiEPG SocketMMI DVDBurn StreamlinkWrapper YTDLWrapper YTDLPWrapper

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VU7376
SUBDIRS += MiniTV QuadPip
endif

if VUUNO4K
SUBDIRS += QuadPip
endif

if VUUNO4KSE
SUBDIRS += MiniTV QuadPip
endif

if VU7376DUO
SUBDIRS += MiniTV QuadPip
endif

if DREAMNEXTGEN
SUBDIRS += QuadPip
endif

install_PYTHON =	\
	__init__.py
