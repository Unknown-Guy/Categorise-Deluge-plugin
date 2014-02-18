#
# gtkui.py
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

import gtk

from deluge.log import LOG as log
from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common
import os
import base64

from common import get_resource

class GtkUI(GtkPluginBase):
    def enable(self):
        self.glade = gtk.glade.XML(get_resource("config.glade"))

        component.get("Preferences").add_page("Categorise", self.glade.get_widget("prefs_box"))
        component.get("PluginManager").register_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").register_hook("on_show_prefs", self.on_show_prefs)
        self.on_show_prefs()

    def disable(self):
        component.get("Preferences").remove_page("Categorise")
        component.get("PluginManager").deregister_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").deregister_hook("on_show_prefs", self.on_show_prefs)
        del self.glade
    
    def on_apply_prefs(self):
        log.debug("Applying prefs for Categorise")
        download_path = self.glade.get_widget("download_folder").get_text()
        audio_path = self.glade.get_widget("audio_folder").get_text()
        video_path = self.glade.get_widget("video_folder").get_text()
        tv_path = self.glade.get_widget("tv_folder").get_text()
        doc_path = self.glade.get_widget("doc_folder").get_text()
        unsorted_path = self.glade.get_widget("unsorted_folder").get_text()
        
        #jabber notification
        jabber_id = self.glade.get_widget("jabber_id").get_text()
        jabber_password = self.glade.get_widget("jabber_password").get_text()
        jabber_recpt_id = self.glade.get_widget("jabber_recpt_id").get_text()
        enable_notification = self.glade.get_widget("enable_notification").get_active()
        
        config = {
            "download_path": download_path,
            "sub_audio": audio_path,
            "sub_video": video_path,
            "sub_tv": tv_path,
            "sub_unsorted":unsorted_path,
            "sub_documents": doc_path,
            "jabber_id":jabber_id,
            "jabber_password":self.encode_password(jabber_password),
            "jabber_recpt_id":jabber_recpt_id,
            "enable_notification":enable_notification
        }
        client.categorise.set_config(config)
        
    def encode_password(self, passwd):
        return base64.b64encode(passwd)
    
    def decode_password(self, passwd):
        return base64.b64decode(passwd)

    def on_show_prefs(self):
        self.glade.get_widget("download_folder").show()
        self.glade.get_widget("audio_folder").show()
        self.glade.get_widget("video_folder").show()
        self.glade.get_widget("tv_folder").show()
        self.glade.get_widget("doc_folder").show()
        self.glade.get_widget("unsorted_folder").show()
        
        self.glade.get_widget("jabber_id").show()
        self.glade.get_widget("jabber_password").show()
        self.glade.get_widget("jabber_recpt_id").show()
        self.glade.get_widget("enable_notification").show()
        
        def on_get_config(config):
            self.glade.get_widget("download_folder").set_text(config["download_path"])
            self.glade.get_widget("audio_folder").set_text(config["sub_audio"])
            self.glade.get_widget("video_folder").set_text(config["sub_video"])
            self.glade.get_widget("tv_folder").set_text(config["sub_tv"])
            self.glade.get_widget("doc_folder").set_text(config["sub_documents"])
            self.glade.get_widget("unsorted_folder").set_text(config["sub_unsorted"])
            
            self.glade.get_widget("jabber_id").set_text(config["jabber_id"])
            self.glade.get_widget("jabber_password").set_text(self.decode_password(config["jabber_password"]))
            self.glade.get_widget("jabber_recpt_id").set_text(config["jabber_recpt_id"])
            self.glade.get_widget("enable_notification").set_active(config["enable_notification"])
            
        client.categorise.get_config().addCallback(on_get_config)
     
