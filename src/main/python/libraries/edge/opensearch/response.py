import logging

from xml.dom.minidom import Document
import xml.sax.saxutils

class Response(object):
    def __init__(self):
        self.searchBasePath = '/ws/search/'
        self.metadataBasePath = '/ws/metadata/'

    def generate(self, pretty=False):
        pass
