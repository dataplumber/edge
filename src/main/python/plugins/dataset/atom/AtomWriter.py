import logging
import datetime

from edge.opensearch.datasetatomresponse import DatasetAtomResponse
from edge.opensearch.datasetwriter import DatasetWriter

class AtomWriter(DatasetWriter):
    def __init__(self, configFilePath):
        super(AtomWriter, self).__init__(configFilePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = DatasetAtomResponse(
            self._configuration.get('portal', 'datasetUrl'),
            self._configuration.get('service', 'host'),
            self._configuration.get('service', 'url'),
            self.datasets
        )

        response.title = 'PO.DAAC Dataset Search Results'
        response.link = searchUrl
        response.authors.append('PO.DAAC Dataset Search Service')
        response.updated = datetime.datetime.utcnow().isoformat()+'Z'
        response.id = 'tag:'+self._configuration.get('service', 'host')+','+datetime.datetime.utcnow().date().isoformat()
        response.parameters = searchParams

        return response.generate(solrResponse, pretty)
