import logging
import json

from xml.dom.minidom import *
from jinja2 import Environment, Template

from edge.dateutility import DateUtility
from edge.opensearch.response import Response

class JsonTemplateResponse(Response):
    def __init__(self):
        super(JsonTemplateResponse, self).__init__()
        self.env = Environment()
        self.env.trim_blocks = True
        self.env.autoescape = False
        self.variables = {}
        self.env.filters['convertISOTime'] = DateUtility.convertISOTime
        self.env.filters['jsonify'] = self.jsonify

    def setTemplate(self, template):
        self.template = self.env.from_string(template)

    def generate(self, pretty=False):
        if pretty:
            return json.dumps(json.loads(self.template.render(self.variables), strict=False), indent=3)
        else:
            return self.template.render(self.variables)

    def jsonify(self, value):
        if value or value == 0:
            return json.dumps(value)
        else:
            return "null"
