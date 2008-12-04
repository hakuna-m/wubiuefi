# Copyright (c) 2008 Hampus Wessman
#
# Written by Hampus Wessman
#
# This file is part of Wubi the Win32 Ubuntu Installer.
#
# Wubi is free software; you can redistribute it and/or modify
# it under 5the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# Wubi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import copy
import xml.sax
import xml.sax.handler
from xml.sax.saxutils import escape, unescape

class MetalinkException(Exception):
    def __init__(self, message):
        self._message = message
    def __str__(self):
        return self._message

class Metalink:
    def __init__(self):
        self.files = []
    def get_dict(self):
        """Return all the data as a dictionary. Used by __eq__."""
        dict = copy.copy(self.__dict__)
        files = []
        for f in self.files:
            files.append(f.get_dict())
        dict['files'] = files
        return dict
    def __eq__(self, other):
        """Returns true if this object is equal to 'other'."""
        return self.get_dict() == other.get_dict()

class MetalinkFile:
    def __init__(self):
        self.name = ''
        self.identity = ''
        self.version = ''
        self.size = -1
        self.description = ''
        self.language = ''
        self.os = ''
        self.hashes = []
        self.piece_hashes = []
        self.piece_length = -1
        self.piece_type = 'sha1'
        self.urls = []
        self.maxconnections = -1
    def get_dict(self):
        dict = copy.copy(self.__dict__)
        hashes = []
        for x in self.hashes:
            hashes.append(x.get_dict())
        dict['hashes'] = hashes
        urls = []
        for x in self.urls:
            urls.append(x.get_dict())
        dict['urls'] = urls
        return dict
    def __eq__(self, other):
        return self.get_dict() == other.get_dict()

class MetalinkHash:
    def __init__(self, type='', hash=''):
        self.type = type
        self.hash = hash
    def get_dict(self):
        return copy.copy(self.__dict__)
    def __eq__(self, other):
        return self.get_dict() == other.get_dict()

class MetalinkUrl:
    def __init__(self, url='', type=''):
        self.url = url
        self.type = type
        self.location = ''
        self.preference = -1
        self.maxconnections = -1
    def get_dict(self):
        return copy.copy(self.__dict__)
    def __eq__(self, other):
        return self.get_dict() == other.get_dict()

class MetalinkHandler(xml.sax.handler.ContentHandler):
    def __init__(self, metalink):
        self._metalink = metalink

    def startDocument(self):
        self._elements = []
        self._attrs = []
        self._content = ''
        self._file = None
        self._pieces = {}

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        # Update the element list and content variable
        self._elements.append(name.lower())
        self._attrs.append(attrs)
        self._content = ''
        # Some elements are processed here (most after the end element, see below)
        if self._elements == ['metalink', 'files', 'file']:
            self._file = MetalinkFile()
            if attrs.has_key('name'):
                self._file.name = attrs['name']
        elif self._elements == ['metalink', 'files', 'file', 'resources']:
            if attrs.has_key('maxconnections'):
                try:
                    self._file.maxconnections = int(attrs['maxconnections'])
                except:
                    pass # Ignore this if it can't be parsed
        elif self._elements == ['metalink', 'files', 'file', 'verification', 'pieces']:
            if attrs.has_key('type'):
                self._file.piece_type = attrs['type']
            if attrs.has_key('length'):
                try:
                    self._file.piece_length = int(attrs['length'])
                except:
                    pass # Ignore this if it isn't a number
            self._pieces = {}

    def endElement(self, name):
        # Collect and update data
        attrs = self._attrs.pop()
        content = unescape(self._content.strip())
        self._content = ''
        # Process elements. They have to be processed here if they need the
        # element's content.
        if self._elements == ['metalink', 'files', 'file']:
            # Files must have a filename, otherwise they will be ignored.
            if self._file.name != '':
                self._metalink.files.append(self._file)
        elif self._elements == ['metalink', 'files', 'file', 'resources', 'url']:
            url = MetalinkUrl()
            url.url = content
            if attrs.has_key('type'): url.type = attrs['type']
            if attrs.has_key('location'): url.location = attrs['location']
            if attrs.has_key('maxconnections'):
                try:
                    url.maxconnections = int(attrs['maxconnections'])
                except:
                    pass # Ignore this if it's not a number
            if attrs.has_key('preference'):
                try:
                    url.preference = int(attrs['preference'])
                except:
                    pass # Ignore this if it's not a number
            self._file.urls.append(url)
        elif self._elements == ['metalink', 'files', 'file', 'identity']:
            self._file.identity = content
        elif self._elements == ['metalink', 'files', 'file', 'version']:
            self._file.version = content
        elif self._elements == ['metalink', 'files', 'file', 'size']:
            try:
                self._file.size = int(content)
            except:
                pass # Ignore this if it can't be parsed
        elif self._elements == ['metalink', 'files', 'file', 'description']:
            self._file.description = content
        elif self._elements == ['metalink', 'files', 'file', 'language']:
            self._file.language = content
        elif self._elements == ['metalink', 'files', 'file', 'os']:
            self._file.os = content
        elif self._elements == ['metalink', 'files', 'file', 'verification', 'hash']:
            # The hash must have a type, otherwise it will be ignored.
            if attrs.has_key('type'):
                hash = MetalinkHash()
                hash.type = attrs['type']
                hash.hash = content
                self._file.hashes.append(hash)
        elif self._elements == ['metalink', 'files', 'file', 'verification', 'pieces', 'hash']:
            if attrs.has_key('piece'):
                self._pieces[attrs['piece']] = content
        elif self._elements == ['metalink', 'files', 'file', 'verification', 'pieces']:
            # Add all the pieces in the right order (starting at index "0")
            for i in range(len(self._pieces)):
                # If this piece is missing, then skip all the pieces
                if not self._pieces.has_key(str(i)):
                    self._file.piece_hashes = []
                    break
                # If it does exist, then add it
                self._file.piece_hashes.append(self._pieces[str(i)])
            self._pieces = {} # Empty the temporary list
        # Remove this element from the list
        self._elements.pop()

    def characters(self, content):
        self._content += content # Save these characters for later

def parse_metalink(filename):
    try:
        metalink = Metalink()
        xml.sax.parse(filename, MetalinkHandler(metalink))
        return metalink
    except xml.sax.SAXParseException:
        raise MetalinkException('Failed to parse xml-file.')
    except IOError:
        raise MetalinkException('Failed to read file.')

def parse_string(text):
    try:
        metalink = Metalink()
        xml.sax.parseString(text, MetalinkHandler(metalink))
        return metalink
    except xml.sax.SAXParseException:
        raise MetalinkException('Failed to parse xml-data.')
