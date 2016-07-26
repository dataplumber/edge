import datetime
import json
import logging
import urllib

from edge.response.jsontemplateresponse import JsonTemplateResponse

class Neo4jJsonTemplateResponse(JsonTemplateResponse):
    def __init__(self, link = "", parameters = {}):
        super(Neo4jJsonTemplateResponse, self).__init__()
        self.link = link
        self.parameters = parameters

    def generate(self, neo4jResponse, pretty=False):
        self._populate(neo4jResponse)
        return super(Neo4jJsonTemplateResponse, self).generate(pretty)

    def _populate(self, neo4jResponse):
        start = 0
        rows = 0
        numFound = 0
        
        print 'GOT RESPONSE:', neo4jResponse, '\n\n'
                
        ### temporariliy short circuiting this if block (1 == 0) for debugging
        if neo4jResponse is not None and (1 == 0):
            neo4jJson = json.loads(neo4jResponse, strict = False)

            self.variables['docs'] = neo4jJson['response']['docs']
            self.variables['numFound'] = int(neo4jJson['response']['numFound'])
            self.variables['itemsPerPage'] = int(neo4jJson['responseHeader']['params']['rows'])
            self.variables['startIndex'] = int(neo4jJson['response']['start'])
            self.variables['parameters'] = self.parameters

            if 'stats' in neo4jJson:
                self.variables['stats'] = neo4jJson['stats']

            start = int(neo4jJson['response']['start'])
            rows = int(neo4jJson['responseHeader']['params']['rows'])
            numFound = int(neo4jJson['response']['numFound'])
        
        #DEBUGGING
        if neo4jResponse is not None:
            neo4jJson = json.loads(neo4jResponse, strict = False)
            self.variables['docs'] = []
            self.variables['numFound'] = 0
            self.variables['itemsPerPage'] = 0
            self.variables['startIndex'] = 0
            self.variables['parameters'] = self.parameters
            
            start = 0
            rows = 0
            numFound = 0

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

