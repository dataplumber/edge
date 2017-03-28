import logging

from xml.dom.minidom import *
from jinja2 import Environment, Template

from edge.dateutility import DateUtility
from edge.opensearch.response import Response

class TemplateResponse(Response):
    def __init__(self):
        super(TemplateResponse, self).__init__()
        self.env = Environment()
        self.env.trim_blocks = True
        self.env.autoescape = True
        self.variables = {}
        self.env.filters['convertISOTime'] = DateUtility.convertISOTime

    def setTemplate(self, template):
        self.template = self.env.from_string(template)

    def generate(self, pretty=False):
        logging.debug('TemplateResponse.generate is called.')
        
        if pretty:
            try :
                xmlStr = self.template.render(self.variables).encode('utf-8').replace('\n', '')
            except Exception as e:
                logging.debug("Problem generating template " + str(e))
                xmlStr = self.template.render({}).encode('utf-8').replace('\n', '')
            document = xml.dom.minidom.parseString(xmlStr)
            return document.toprettyxml()
        else:
            return self.template.render(self.variables).replace('\n', '')
