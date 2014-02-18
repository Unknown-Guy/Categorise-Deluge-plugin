#
# core.py
#
# Copyright (C) 2009 ledzgio <ledzgio@writeme.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
#     The Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor
#     Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.core.core import Core
import os
import mimetypes as mt
#from send_message import send_msg
import datetime
from deluge.ui.client import client
import re

DEFAULT_PREFS = {
    #sub directories
    "download_path": "",
    "sub_audio":"audio",
    "sub_video":"video",
    "sub_tv":"tv",
    "sub_documents":"documents",
    "sub_unsorted":"unsorted",
    
    "jabber_id":"",
    "jabber_password":"",
    "jabber_recpt_id":"",
    "enable_notification":False
}
#file formats extension
TV_SUBSTR = ['HDTV']
TV_REGEX = ['S\d\dE\d\d\d?', 'Season \d\d?', '[. ]S\d\d?']
VIDEO_SUBSTR = ['XviD', 'x264', 'x265', 'DVD', 'BR..[. ]', 'BluRay']
GREY_SUBSTR = ['XXX']

DOC_FORMAT = [".pdf", ".doc", ".ods", ".odt", ".xls", ".docx"]
GREY_LIST = [".txt", ".nfo", ".jpg", ".bmp", ".gif", ".m3u" ".sfv", ".url",
              ".sub", ".srt", ".idx", ".rtf", ".htm", ".log"]

class CategoriseCore(CorePluginBase):
    def enable(self):
        log.debug("Enabling Categorise plugin")
        self.config = deluge.configmanager.ConfigManager("categorise.conf", DEFAULT_PREFS)
                
        #setting event
        component.get("EventManager").register_event_handler("TorrentFinishedEvent", self._on_torrent_finished)
    
    def disable(self):
        log.debug("Disabling Categorise plugin")
        
    def update(self):
        pass
        
    def _on_torrent_finished(self, torrent_id):
        
        log.debug("called on torrent finished event: %s", torrent_id)
        
        """called on torrent finished event"""
        #get the torrent by torrent_id
        torrent = component.get("TorrentManager")[torrent_id]
        
        log.debug("called on torrent finished event: %s", torrent)
        
        total_download_byte = torrent.get_status(["total_payload_download"])["total_payload_download"]
        
        log.debug("called on torrent finished event: %s", total_download_byte)
        
        total_download_converted = self._convert_bytes(total_download_byte)
        
        log.debug("called on torrent finished event: %s", total_download_converted)
        
        torrent_name = torrent.get_status(["name"])["name"]
        
        log.debug("completed torrent: %s", torrent_name)
        
        files = torrent.get_files()
        
        #create torrent details string
        torrent_details = "\nTorrent name: "+torrent_name+"\nSize: "+ total_download_converted +"\nContained file(s): "+`len(files)`+"\n"
                
        #get destination path
        dest = self._guess_destination(files)
        for f in files:
            downloaded_file_path = f["path"]
            torrent_details = torrent_details + " * " +downloaded_file_path + "\n"
            if files.index(f) == 3:
                torrent_details = torrent_details + "..."+`len(files) - files.index(f)`+" more\n"
                break
	    now = datetime.datetime.now()
	    date_time = now.strftime("%Y-%m-%d, %H:%M")
        tracker = torrent.get_tracker_host()
        torrent_details = torrent_details + "Tracker: "+ tracker +"\nPeers: "+ `len(torrent.get_peers())`
        torrent_details = torrent_details + "\nIdentified type: "+dest[1]+"\nCompleted at: "+ date_time +"\nMoved to folder: "+dest[0]
        
        if not os.path.exists(dest[0]):
            log.debug("directory "+ dest[0] +" does not exists, it will be created")
            os.makedirs(dest[0])
            
        #moving torrent storage to final destination and updating torrent state
        torrent.move_storage(dest[0])
        torrent.is_finished = True
        torrent.update_state()

        log.debug("moving completed torrent containing "+`len(files)`+" file(s) to %s", dest[0])
       
        #sending message to the jabber user
        decoded_password = self._decode_password(self.config["jabber_password"])
        
        if(self.config["enable_notification"] and self.config["jabber_id"] and decoded_password and self.config["jabber_recpt_id"]):
            #import send_message only when necessary to avoid missing python-pyxmpp library
            from send_message import send_msg
            sent = send_msg(torrent_details, self.config["jabber_id"], decoded_password, self.config["jabber_recpt_id"])
            if not sent:
                log.debug("Notification not sent. Check if you have pyxmpp module installed on you system")
            
    def _guess_destination(self, torrent_files):
        """
        try to identify the correct category of the finished torrent 
        and return the destination path where the torrent has to be moved
        """
        download_path = self.config["download_path"]

        tv_regexs = []
        for regex in TV_REGEX:
            tv_regexs.append(re.compile(regex))

        for file in torrent_files:
            for substr in GREY_SUBSTR:
                if file['path'].find(substr) != -1:
                    continue

            for substr in TV_SUBSTR:
                if file['path'].find(substr) != -1:
                    return [os.path.join(download_path, self.config["sub_tv"]), "tv"]
            for regex in tv_regexs:
                if regex.search(file['path']):
                    return [os.path.join(download_path, self.config["sub_tv"]), "tv"]
            for substr in VIDEO_SUBSTR:
                if file['path'].find(substr) != -1:
                    return [os.path.join(download_path, self.config["sub_video"]), "video"]

            try:
                ext = os.path.splitext(file["path"])[1]
                ext = ext.lower()
                mt.guess_extension(ext)
                res = mt.types_map[ext]
                if res in GREY_LIST:
                    log.debug("skipping GREY_LIST extension %s", res)
                    continue

                if (res.startswith("audio")):
                    return [os.path.join(download_path, self.config["sub_audio"]), "audio"]
                elif (res.startswith("video")):
                    return [os.path.join(download_path, self.config["sub_video"]), "video"]
                elif(ext in DOC_FORMAT):
                    return [os.path.join(download_path, self.config["sub_documents"]), "doc"]

            except KeyError:
                    log.debug("unknown extension %s, trying again", ext)
                    continue
                    
        return [os.path.join(download_path, self.config["sub_unsorted"]), "unsorted"]
    
    
    def _convert_bytes(self, bytes):
        """return the size of the finished torrent"""
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = "%.2fTb" % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = "%.2fGb" % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = "%.2fMb" % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = "%.2fKb" % kilobytes
        else:
            size = "%.2fbytes" % bytes
        return size
    
    def _decode_password(self, enc_passwd):
        import base64
        return base64.b64decode(enc_passwd)
        
    @export
    def set_config(self, config):
        "sets the config dictionary"
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        "returns the config dictionary"
        return self.config.config
