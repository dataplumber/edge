import datetime
import json
import logging
import urllib

from edge.opensearch.templateresponse import TemplateResponse

class ESTemplateResponse(TemplateResponse):
    def __init__(self, link = "", parameters = {}, defaultItemsPerPage = 0):
        super(ESTemplateResponse, self).__init__()
        self.link = link
        self.parameters = parameters
        self.defaultItemsPerPage = defaultItemsPerPage

    def generate(self, solrResponse, pretty=False):
        self._populate(solrResponse)
        return super(ESTemplateResponse, self).generate(pretty)

    def _populate(self, response):
        start = 0
        rows = 0
        numFound = 0

        self.variables['parameters'] = self.parameters

        if response is not None:
            solrJson = json.loads(response, strict = False)
            self.variables['docs'] = solrJson['hits']['hits']
            self.variables['numFound'] = int(solrJson['hits']['total'])
            self.variables['itemsPerPage'] = int(self.parameters['itemsPerPage']) if 'itemsPerPage' in self.parameters else self.defaultItemsPerPage
            self.variables['startIndex'] = int(self.parameters['startIndex']) if 'startIndex' in self.parameters else 0

            start = self.variables['startIndex']
            rows = self.variables['itemsPerPage']
            numFound = self.variables['numFound']


        self.parameters['startIndex'] = start
        self.variables['myself'] = self.link + '?' + urllib.urlencode(self.parameters, True)

        if rows != 0:
            self.parameters['startIndex'] = numFound - (numFound % rows)
        self.variables['last'] = self.link + '?' + urllib.urlencode(self.parameters, True)

        self.parameters['startIndex'] = 0
        self.variables['first'] = self.link + '?' + urllib.urlencode(self.parameters, True)
        if start > 0:
            if (start - rows > 0):
                self.parameters['startIndex'] = start - rows
            self.variables['prev'] = self.link + '?' + urllib.urlencode(self.parameters, True)

        if start + rows < numFound:
            self.parameters['startIndex'] = start + rows
            self.variables['next'] = self.link + '?' + urllib.urlencode(self.parameters, True)
