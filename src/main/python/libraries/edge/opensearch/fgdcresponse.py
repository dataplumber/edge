import logging

from jinja2 import Environment, Template
import re
import xml.etree.ElementTree

from edge.opensearch.response import Response

class FgdcResponse(Response):
    def __init__(self):
        self.namespaces = {}
        self.env = Environment()
        self.env.trim_blocks = True
        self.env.autoescape = True
        self.variables = {}

    def setTemplate(self, template):
        self.template = self.env.from_string(template.replace('>\n<', '><'))

    def addNamespace(self, name, uri):
        self.namespaces[name] = uri

    def removeNamespace(self, name):
        del self.namespaces[name]

    def generate(self, pretty=False, xmlDeclaration=""):
        logging.debug('FgdcResponse.generate is called.')
        fgdcStr = self.template.render(self.variables).encode('utf-8')
        if fgdcStr != "" and pretty:
            #xmlDeclaration ="<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n<!DOCTYPE metadata SYSTEM \"http://www.fgdc.gov/metadata/fgdc-std-001-1998.dtd\">\n"
            tree = xml.etree.ElementTree.fromstring(fgdcStr)
            self._indent(tree)
            
            for namespace in self.namespaces.keys():
                xml.etree.ElementTree.register_namespace(namespace, self.namespaces[namespace])
            
            return xmlDeclaration + xml.etree.ElementTree.tostring(tree, encoding='utf-8')
        else:
            return fgdcStr

    # Provided by http://effbot.org/zone/element-lib.htm#prettyprint
    def _indent(self, elem, level=0):
        i = "\n" + level * "   "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "   "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                
