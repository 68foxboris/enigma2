installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = CutListEditor PicturePlayer MediaScanner MediaPlayer GraphMultiEPG SocketMMI DVDBurn

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VUSOLO4K
SUBDIRS += MiniTV QuadPip
endif

if VUULTIMO4K
SUBDIRS += MiniTV QuadPip
endif

if GB7252
SUBDIRS += QuadPip
endif

if VUUNO4K
SUBDIRS += QuadPip
endif

if VUUNO4KSE
SUBDIRS += MiniTV QuadPip
endif

if VUDUO4K
SUBDIRS += MiniTV QuadPip
endif

if VUDUO4KSE
SUBDIRS += MiniTV QuadPip
endif

install_PYTHON =	\
	__init__.py
