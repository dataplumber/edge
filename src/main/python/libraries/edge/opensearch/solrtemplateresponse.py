import datetime
import json
import logging
import urllib

from edge.opensearch.templateresponse import TemplateResponse

class SolrTemplateResponse(TemplateResponse):
    def __init__(self, configuration, link, parameters):
        super(SolrTemplateResponse, self).__init__()
        self._configuration = configuration
        self.link = link
        self.parameters = parameters

    def generate(self, solrResponse, pretty=False):
        self._populate(solrResponse)
        return super(SolrTemplateResponse, self).generate(pretty)

    def _populate(self, solrResponse):
        self.variables['link'] = self.link

        start = 0
        rows = 0
        numFound = 0
        
        if solrResponse is not None:
            solrJson = json.loads(solrResponse)
            
            logging.debug('doc count: '+str(len(solrJson['response']['docs'])))
            
            self.variables['docs'] = solrJson['response']['docs']
            self.variables['numFound'] = solrJson['response']['numFound']
            self.variables['itemsPerPage'] = solrJson['responseHeader']['params']['rows']
            self.variables['startIndex'] = solrJson['response']['start']
            
            self.variables['updated'] = datetime.datetime.utcnow().isoformat() + 'Z'
            
            start = int(solrJson['response']['start'])
            rows = int(solrJson['responseHeader']['params']['rows'])
            numFound = int(solrJson['response']['numFound'])

            logging.debug(self.variables['numFound'])
            logging.debug(self.variables['itemsPerPage'])
        
            if 'facet_counts' in solrJson:
                self.variables['facets'] = solrJson['facet_counts']

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
