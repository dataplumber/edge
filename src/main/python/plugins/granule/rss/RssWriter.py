import logging

from edge.opensearch.granulerssresponse import GranuleRssResponse
from edge.opensearch.granulewriter import GranuleWriter

class RssWriter(GranuleWriter):
    
    def __init__(self, configFilePath):
        super(RssWriter, self).__init__(configFilePath, [['datasetId', 'shortName']])

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = GranuleRssResponse(self._configuration.get('service', 'linkToGranule'), 
                                      self._configuration.get('service', 'host'),
                                      self._configuration.get('service', 'url'))

        response.title = 'PO.DAAC Granule Search Results'
        response.description = 'Search result for "'+searchText+'"'
        response.link = searchUrl
        response.parameters = searchParams

        return response.generate(solrResponse, pretty) 
