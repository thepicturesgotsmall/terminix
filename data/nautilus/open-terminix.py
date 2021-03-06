# -*- coding: UTF-8 -*-

# This example is contributed by Martin Enlund
# Example modified for Terminix
import os
import urllib
from urlparse import urlparse

import gettext
gettext.textdomain("terminix")
_ = gettext.gettext

import gi

gi.require_version('Nautilus', '3.0')

from gi.repository import Nautilus, GObject, Gio

class OpenTerminixExtension(GObject.GObject, Nautilus.MenuProvider):

    def __init__(self):
        self.terminal = 'terminix'

    def _open_terminal(self, file):
        if file.get_uri_scheme() in ['ftp','sftp']:
            result = urlparse(file.get_uri())
            if result.username:
                value = 'ssh -t %s@%s' % (result.username, result.hostname)
            else:
                value = 'ssh -t %s' % (result.hostname)
            if result.port:
                value = value + " -p " + result.port
            if file.is_directory():
                value = value + " cd \"%s\" ; $SHELL" % (result.path)

            os.system('%s -e "%s" &' % (self.terminal, value))
        else:            
            gfile = Gio.File.new_for_uri(file.get_uri())
            filename = gfile.get_path()
            if filename is None:
                os.system('%s &' % (self.terminal))
            else:
                os.system('%s -w "%s" &' % (self.terminal, filename))
    
    def menu_activate_cb(self, menu, file):
        self._open_terminal(file)

    def menu_background_activate_cb(self, menu, file):

        self._open_terminal(file)

    def get_file_items(self, window, files):
        if len(files) != 1:
            print "Number of files is %d" % len(files) 
            return
        items = []
        file = files[0]
        print "Handling file: ", file.get_uri()
        print "file scheme: ", file.get_uri_scheme()

        if file.is_directory(): #and file.get_uri_scheme() == 'file':

            if file.get_uri_scheme() in ['ftp','sftp']:
                item = Nautilus.MenuItem(name='NautilusPython::openterminal_remote_item',
                                        label=_(u'Open Remote Terminix'),
                                        tip=_(u'Open Remote Terminix In %s') % file.get_uri())
                item.connect('activate', self.menu_activate_cb, file)
                items.append(item)

            gfile = Gio.File.new_for_uri(file.get_uri())
            info = gfile.query_info("standard::*", Gio.FileQueryInfoFlags.NONE, None)
            # Get UTF-8 version of basename
            filename = info.get_attribute_as_string("standard::name")

            item = Nautilus.MenuItem(name='NautilusPython::openterminal_file_item',
                                    label=_(u'Open In Terminix'),
                                    tip=_(u'Open Terminix In %s') % filename)
            item.connect('activate', self.menu_activate_cb, file)
            items.append(item)

        return items

    def get_background_items(self, window, file):
        items = []
        if file.get_uri_scheme() in ['ftp','sftp']:
            item = Nautilus.MenuItem(name='NautilusPython::openterminal_bg_remote_item',
                                    label=_(u'Open Remote Terminix Here'),
                                    tip=_(u'Open Remote Terminix In This Directory'))
            item.connect('activate', self.menu_activate_cb, file)
            items.append(item)

        item = Nautilus.MenuItem(name='NautilusPython::openterminal_bg_file_item',
                                 label=_(u'Open Terminix Here'),
                                 tip=_(u'Open Terminix In This Directory'))
        item.connect('activate', self.menu_background_activate_cb, file)
        items.append(item)
        return items