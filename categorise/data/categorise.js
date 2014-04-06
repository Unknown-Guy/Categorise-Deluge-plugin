/*
Script: categorise.js
    The client-side javascript code for the Categorise plugin.

Copyright:
    (C) ledzgio 2009 <ledzgio@writeme.com>
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, write to:
        The Free Software Foundation, Inc.,
        51 Franklin Street, Fifth Floor
        Boston, MA  02110-1301, USA.

    In addition, as a special exception, the copyright holders give
    permission to link the code of portions of this program with the OpenSSL
    library.
    You must obey the GNU General Public License in all respects for all of
    the code used other than OpenSSL. If you modify file(s) with this
    exception, you may extend this exception to your version of the file(s),
    but you are not obligated to do so. If you do not wish to do so, delete
    this exception statement from your version. If you delete this exception
    statement from all source files in the program, then also delete it here.
*/

Ext.ns('Deluge.ux.preferences');

Deluge.ux.preferences.CategorisePage = Ext.extend(Ext.Panel, {

  border: false,
  title: _('Categorise'),
  layout: 'fit',

  initComponent: function() {
    Deluge.ux.preferences.CategorisePage.superclass.initComponent.call(this);

    this.form = this.add({
      xtype: 'form',
      layout: 'form',
      border: false,
      autoHeight: true
    });

    this.base_dir_fieldset = this.form.add({
      xtype: 'fieldset',
      border: false,
      title: _('Root directory'),
      defaults: {
        width: 195
      }
    });

    this.download_path = this.base_dir_fieldset.add({
      xtype: 'textfield',
      fieldLabel: _('Downloads'),
      name: 'download_path',
      allowBlank: false
    });

    this.sub_dir_fieldset = this.form.add({
      xtype: 'fieldset',
      border: false,
      title: _('Subdirectories'),
      defaults: {
        width: 195,
        allowBlank: false
      }
    });

    this.sub_tv = this.sub_dir_fieldset.add({
      xtype: 'textfield',
      fieldLabel: _('TV Series'),
      name: 'sub_tv'
    });

    this.sub_audio = this.sub_dir_fieldset.add({
      xtype: 'textfield',
      fieldLabel: _('Audio'),
      name: 'sub_audio'
    });

    this.sub_video = this.sub_dir_fieldset.add({
      xtype: 'textfield',
      fieldLabel: _('Video'),
      name: 'sub_video'
    });

    this.sub_documents = this.sub_dir_fieldset.add({
      xtype: 'textfield',
      fieldLabel: _('Documents'),
      name: 'sub_documents'
    });

    this.sub_unsorted = this.sub_dir_fieldset.add({
      xtype: 'textfield',
      fieldLabel: _('Other'),
      name: 'sub_unsorted'
    });
  },

  onRender: function(ct, position) {
    Deluge.ux.preferences.CategorisePage.superclass.onRender.call(this, ct, position);
    this.form.layout = new Ext.layout.FormLayout();
    this.form.layout.setContainer(this);
    this.form.doLayout();
  },

  onApply: function() {
    var config = {}

    config['download_path'] = this.download_path.getValue();
    config['sub_audio']     = this.sub_audio.getValue();
    config['sub_video']     = this.sub_video.getValue();
    config['sub_tv']        = this.sub_tv.getValue();
    config['sub_documents'] = this.sub_documents.getValue();
    config['sub_unsorted']  = this.sub_unsorted.getValue();

    deluge.client.categorise.set_config(config);
  },

  afterRender: function() {
    Deluge.ux.preferences.CategorisePage.superclass.afterRender.call(this);
    this.updateConfig();
  },

  updateConfig: function() {
    deluge.client.categorise.get_config({
      success: function(config) {
        this.download_path.setValue(config['download_path']);
        this.sub_audio.setValue(config['sub_audio']);
        this.sub_video.setValue(config['sub_video']);
        this.sub_tv.setValue(config['sub_tv']);
        this.sub_documents.setValue(config['sub_documents']);
        this.sub_unsorted.setValue(config['sub_unsorted'] );
      },
      scope: this
    });
  }
});

Deluge.plugins.CategorisePlugin = Ext.extend(Deluge.Plugin, {

  name: 'Categorise',

  onDisable: function() {
    deluge.preferences.removePage(this.prefsPage);
  },

  onEnable: function() {
    this.prefsPage = deluge.preferences.addPage(new Deluge.ux.preferences.CategorisePage());
  }
});

Deluge.registerPlugin('Categorise', Deluge.plugins.CategorisePlugin);
