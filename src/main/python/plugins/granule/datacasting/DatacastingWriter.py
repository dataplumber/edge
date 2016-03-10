import logging
import os
import os.path
import time

from edge.opensearch.granuledatacastingresponse import GranuleDatacastingResponse
from edge.opensearch.datasetgranulewriter import DatasetGranuleWriter

class DatacastingWriter(DatasetGranuleWriter):
    def __init__(self, configFilePath):
        super(DatacastingWriter, self).__init__(configFilePath, [['datasetId', 'shortName']])
        
        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)
        self.variables['sortBy'] = 'archiveTimeDesc'
        self.variables['archiveTime'] = int(round(time.time() * 1000)) - (int(self._configuration.get('solr', 'archivedWithin')) * 3600000)

    def _generateOpenSearchResponse(self, solrGranuleResponse, solrDatasetResponse, pretty):
        response = GranuleDatacastingResponse(
            self._configuration.get('portal', 'datasetUrl'), 
            self._configuration.get('service', 'linkToGranule'),
            int(self._configuration.get('solr', 'archivedWithin'))
        )
        response.setTemplate(self.template)

        return response.generate(solrDatasetResponse, solrGranuleResponse, pretty)

    def _onSolrGranuleResponse(self, response):
        if response.error:
            self._handleException(str(response.error))
        else:
            self.solrGranuleResponse = response.body
            params = {}
            if ('datasetId' in self.variables):
                params['datasetId'] = self.variables['datasetId']
            if ('shortName' in self.variables):
                params['shortName'] = self.variables['shortName']
            self._getSingleSolrDatasetResponse(params, self._onSolrDatasetResponse)
