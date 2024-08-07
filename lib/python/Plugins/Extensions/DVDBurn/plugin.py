# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor


def main(session, **kwargs):
	from . import TitleList
	# project.addService(service)
	return session.open(TitleList.TitleList)


def main_add(session, service, **kwargs):
	dvdburn = main(session, **kwargs)
	dvdburn.selectedSource(service)


def Plugins(**kwargs):
	descr = _("Burn to DVD")
	return [PluginDescriptor(name=_("DVD Burn"), description=descr, where=PluginDescriptor.WHERE_MOVIELIST, needsRestart=True, fnc=main_add, icon="dvdburn.png"),
		PluginDescriptor(name=_("DVD Burn"), description=descr, where=PluginDescriptor.WHERE_PLUGINMENU, needsRestart=True, fnc=main, icon="dvdburn.png")]
