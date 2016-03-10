import datetime
import json
import logging
import urllib

from edge.response.jsontemplateresponse import JsonTemplateResponse

class SolrJsonTemplateResponse(JsonTemplateResponse):
    def __init__(self):
        super(SolrJsonTemplateResponse, self).__init__()

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
