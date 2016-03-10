import logging

from edge.opensearch.datasetrssresponse import DatasetRssResponse
from edge.opensearch.datasetwriter import DatasetWriter

class RssWriter(DatasetWriter):
    def __init__(self, configFilePath):
        super(RssWriter, self).__init__(configFilePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = DatasetRssResponse(self._configuration.get('portal', 'datasetUrl'), self._configuration.get('service', 'url'), self.datasets)

        response.title = 'PO.DAAC Dataset Search Results'
        response.description = 'Search result for "'+searchText+'"'
        response.link = searchUrl
        response.parameters = searchParams

        return response.generate(solrResponse, pretty)
