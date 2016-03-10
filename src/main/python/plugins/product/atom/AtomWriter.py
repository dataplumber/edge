import logging
import datetime

from edge.elasticsearch.opensearch.granuleatomresponse import GranuleAtomResponse
from edge.elasticsearch.granulewriter import GranuleWriter

class AtomWriter(GranuleWriter):
    
    def __init__(self, configFilePath):
        super(AtomWriter, self).__init__(configFilePath, [['identifier']])

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = GranuleAtomResponse(
            self._configuration.get('service', 'linkToGranule'),
            self._configuration.get('service', 'host'),
            self._configuration.get('service', 'url')
        )

        response.title = 'GIBS Product Search Results'
        #response.description = 'Search result for "'+searchText+'"'
        response.link = searchUrl
        response.authors.append('GIBS Product Search Service')
        response.updated = datetime.datetime.utcnow().isoformat()+'Z'
        response.id = 'tag:'+self._configuration.get('service', 'host')+','+datetime.datetime.utcnow().date().isoformat()
        response.parameters = searchParams

        return response.generate(solrResponse, pretty) 
