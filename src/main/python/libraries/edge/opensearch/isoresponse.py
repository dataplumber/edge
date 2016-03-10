import logging

from xml.dom.minidom import *
import xml.sax.saxutils
from jinja2 import Environment, Template

from edge.opensearch.response import Response

class IsoResponse(Response):
    def __init__(self):
        self.env = Environment()
        self.env.trim_blocks = True
        self.env.autoescape = True
        self.variables = {}

    def setTemplate(self, template):
        self.template = self.env.from_string(template)

    def addNamespace(self, name, uri):
        self.namespaces[name] = uri

    def removeNamespace(self, name):
        del self.namespaces[name]

    def generate(self, pretty=False):
        logging.debug('IsoResponse.generate is called.')
        
        if pretty:
            try :
                isoStr = self.template.render(self.variables).encode('utf-8').replace('\n', '')
            except Exception as e:
                logging.debug("Problem generating ISO " + str(e))
                del self.variables['doc']
                isoStr = self.template.render(self.variables).encode('utf-8').replace('\n', '')
            document = xml.dom.minidom.parseString(isoStr)
            return document.toprettyxml()
        else:
            return self.template.render(self.variables).replace('\n', '')
