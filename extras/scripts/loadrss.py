# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import backgroundworker
import sys, getopt

def main(id,name):
   backgroundworker.GetRss(str(id),str(name))

main(sys.argv[1],sys.argv[2])
