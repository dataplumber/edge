import datetime
import json
import logging
import urllib

from edge.response.jsontemplateresponse import JsonTemplateResponse

class SolrJsonTemplateResponse(JsonTemplateResponse):
    def __init__(self, link = "", parameters = {}):
        super(SolrJsonTemplateResponse, self).__init__()
        self.link = link
        self.parameters = parameters

    def generate(self, solrResponse, pretty=False):
        self._populate(solrResponse)
        return super(SolrJsonTemplateResponse, self).generate(pretty)

    def _populate(self, solrResponse):
        start = 0
        rows = 0
        numFound = 0
        
        if solrResponse is not None:
            solrJson = json.loads(solrResponse, strict = False)

            self.variables['docs'] = solrJson['response']['docs']
            self.variables['numFound'] = int(solrJson['response']['numFound'])
            self.variables['itemsPerPage'] = int(solrJson['responseHeader']['params']['rows'])
            self.variables['startIndex'] = int(solrJson['response']['start'])
            self.variables['parameters'] = self.parameters

            if 'stats' in solrJson:
                self.variables['stats'] = solrJson['stats']

            if 'facet_counts' in solrJson:
                self.variables['facets'] = solrJson['facet_counts']

            start = int(solrJson['response']['start'])
            rows = int(solrJson['responseHeader']['params']['rows'])
            numFound = int(solrJson['response']['numFound'])


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
