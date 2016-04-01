# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import os
import sys
import shutil
import urllib2
import urllib
import re
import time
import ntpath
import requests
import posixpath
import urlparse 
import zipfile
import sqlite3
import json

MetaSettingsUrl = 'http://www.the-vibe.co.il/Wizard/wtf/?category=addonsettings&Id=102';
QuasarSettingsUrl = 'http://www.the-vibe.co.il/Wizard/wtf/?category=addonsettings&Id=33'
Package_Definition_Url = "http://www.the-vibe.co.il/Skin/GetSkinBackupPath";
BASEURL = 'http://www.the-vibe.co.il'
APIurl = 'http://www.the-vibe.co.il/api'
UPLOAD_URL = 'http://www.the-vibe.co.il/Files/Log'
CUSTOM_BACKUP_URL = 'http://www.the-vibe.co.il/files/download/'
KODI_VERSION = xbmc.getInfoLabel( "System.BuildVersion" )

URL= requests.get(Package_Definition_Url).text
log_path = xbmc.translatePath('special://logpath')
NAME='emzeev.zip'
CUSTOM_NAME='personal.zip'
path = xbmc.translatePath(os.path.join('special://skin/extras','back-up'))
dialog= xbmcgui.Dialog()
ENABLE_PVR_COMMAND='delete from disabled where addonID="pvr.iptvsimple"'
metasettingsPath = xbmc.translatePath(os.path.join('special://home','userdata','addon_data','plugin.video.meta','players'))
quasarsettingsPath = xbmc.translatePath(os.path.join('special://home','userdata','addon_data','plugin.video.quasar','settings.xml'))
USERDATA     =  xbmc.translatePath(os.path.join('special://home/userdata',''))


def find_str(s, char):
    index = 0

    if char in s:
        c = char[0] 
        for ch in s:
            if ch == c:
                if s[index:index+len(char)] == char:
                    return index

            index += 1

    return -1

def all(_in, _out, dp=None):
    if dp:
        return allWithProgress(_in, _out, dp)

    return allNoProgress(_in, _out)

def allNoProgress(_in, _out):
    try:
        zin = zipfile.ZipFile(_in, 'r')
        zin.extractall(_out)
    except Exception, e:
        print str(e)
        return False

    return True

def allWithProgress(_in, _out, dp):

    zin = zipfile.ZipFile(_in,  'r')

    nFiles = float(len(zin.infolist()))
    count  = 0

    try:
        for item in zin.infolist():
            count += 1
            update = count / nFiles * 100
            dp.update(int(update))
            zin.extract(item, _out)
    except Exception, e:
        print str(e)
        return False

    return True

def downloadMetaSettings(url, dest, dp = None):
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create("התקנת הגדרות","מוריד קובץ הגדרות, אנא המתן!",' ', ' ')
    dp.update(0)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
 
def download(url, dest, dp = None):
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create("The Vibe Team","Downloading & Copying File",' ', ' ')
    dp.update(0)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
 
def _pbhook(numblocks, blocksize, filesize, url, dp):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        raise Exception("Canceled")
        dp.close()

def wizard(name,url):
    dp = xbmcgui.DialogProgress()
    dp.create("Eminenece Zeev - גיבוי מעטפת","מוריד ",'', 'אנא המתן')
    lib = os.path.join(path, name)
    try:
       os.remove(lib)
    except:
       pass
    download(url, lib, dp)

def clear():
 
    for root, dirs, files in os.walk(path):
        file_count = 0
        file_count += len(files)
        
    # Count files and give option to delete
        if file_count > 0:
                        
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

def dowork():
    xbmc.log("Starting...")
    xbmc.log("Starting Download")
    wizard(NAME,URL)
    if validateZip(NAME):
        xbmc.log("Extracting...")
        xbmc.executebuiltin("XBMC.RunScript(script.skin.helper.service,action=restore,silent=special://skin/extras/back-up/" + NAME + ")")
    else:
        dialog.ok("שגיאה בשחזור מעטפת", 'אירעה שגיאה בעת שחזור המעטפת, אנא בדוק את החיבור לאינטרנט או נסה במעוד מאוחר יותר')
    xbmc.log("Done...")

def GetUserBackup():
    keyboard = xbmcgui.Dialog()
    userId = keyboard.numeric(0, 'נא להכניס ID');
    xbmc.log("Starting...")
    xbmc.log("Starting Download")
    wizard(CUSTOM_NAME,CUSTOM_BACKUP_URL + userId )
    if validateZip(CUSTOM_NAME):
        xbmc.log("Extracting...")
        xbmc.executebuiltin("XBMC.RunScript(script.skin.helper.service,action=restore,silent=special://skin/extras/back-up/" + CUSTOM_NAME + ")")
    else:
        dialog.ok("שגיאה בשחזור מעטפת", 'אירעה שגיאה בעת פעולת השחזור, אנא בדוק את ה ID  שהכנסת , וודא כי הועלו קבצים')
    xbmc.log("Done...")

def validateZip(zipName):
    ZipFile = xbmc.translatePath(os.path.join(path,zipName))
    try:
        with open(ZipFile) as file:
            if zipfile.is_zipfile(ZipFile):
                return True
        return False
    except Exception, e:
        xbmc.log(str(e))
        return False

def getAddonDbName():
	if find_str(KODI_VERSION,"16.0")>-1:
		return 'Addons20.db'
	else:
		return 'Addons19.db'
ADDON_DB = xbmc.translatePath(os.path.join(USERDATA,'Database',getAddonDbName()))

def enablePvr():
    try:
        conn = sqlite3.connect(ADDON_DB)
        conn.execute(ENABLE_PVR_COMMAND)
        conn.commit()
        conn.close()
        xbmc.executebuiltin("UpdateLocalAddons");xbmc.executebuiltin("UpdateAddonRepos")
        xbmcgui.Dialog().ok('הפעלת לקוח טלויזיה חיה','לקוח טלויזיה חיה הופעל בהצלחה','יש לאתחל את הקודי על מנת שהשינוי יכנס לתוקף')
    except:
        pass

def GetMetaSettings(name,url):
        path = xbmc.translatePath(os.path.join('special://home','addons','packages'))
        dp = xbmcgui.DialogProgress() 
        dp.create("הפעלה ראשונה:","מתקין הגדרת נגנים עבור הרחבת חיפוש META ",'','רץ בפתיחה ראשונה בלבד') 
        lib = os.path.join(path,name + '.zip')
        try: os.remove(lib)
        except: pass
        downloadMetaSettings(url,lib,dp)
        time.sleep(2)
        #dp.update(0,"","Installing selections.....")
        all(lib,xbmc.translatePath('special://home'),'')
        xbmc.executebuiltin("UpdateLocalAddons")
        xbmc.executebuiltin("UpdateAddonRepos")

def GetQuasarSettings(name,url):
        path = xbmc.translatePath(os.path.join('special://home','addons','packages'))
        dp = xbmcgui.DialogProgress() 
        dp.create("הפעלה ראשונה:","מתקין הגדרת נגנים עבור הרחבת  Quasar ",'','רץ בפתיחה ראשונה בלבד') 
        lib = os.path.join(path,name + '.zip')
        try: os.remove(lib)
        except: pass
        downloadMetaSettings(url,lib,dp)
        time.sleep(2)
        #dp.update(0,"","Installing selections.....")
        all(lib,xbmc.translatePath('special://home'),'')
        xbmc.executebuiltin("UpdateLocalAddons")
        xbmc.executebuiltin("UpdateAddonRepos")


def installMetaSettings():
    if not os.path.exists(metasettingsPath):
            GetMetaSettings('MetaSettings',MetaSettingsUrl)

def installQuasarSettings():
    if not os.path.exists(quasarsettingsPath):
            GetQuasarSettings('QuasarSettings',QuasarSettingsUrl)



#

def SendLog():
    try:
        dp = xbmcgui.DialogProgress()
        dp.create("שולח לוג לאתר","אנא המתן בזמן שהלוג נשלח לשרת!",' ', ' ')
        logfile = xbmc.translatePath(os.path.join(log_path,'kodi.log'))
        file_content = open(logfile,'r').read()
        post_dict = {
                'data': file_content,
                'project': 'The-Vibe Wizard',
                'language': 'text',
                'expire': 1209600,
            }
        post_data = json.dumps(post_dict)
        headers = {
            'User-Agent': '%s-%s' % ('Skin.Eminence.Zeev', '1.0.0'),
            'Content-Type': 'application/json',
        }
        req = urllib2.Request(UPLOAD_URL, post_data, headers)
        response = urllib2.urlopen(req).read()
        dp.update(100)
        if response!='error':
            xbmcgui.Dialog().ok('השליחה הצליחה','הלוג נשלח לשרת בהצלחה','על מנת לצפות בלוג עליך להכנס לאתר בכתובת http://www.the-vibe.co.il/Log','ולהכניס את ה ID הבא: '+ response)
    except Exception as e:
        dp.update(100)
        xbmcgui.Dialog().ok('שגיאה בשליחת לוג','אירעה שגיאה בעת שליחת הלוג','אנא נסה שוב במועד מאוחר יותר')
        xbmc.log(str(e))