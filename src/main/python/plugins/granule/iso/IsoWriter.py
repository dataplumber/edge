import logging
import os
import os.path
import codecs

from edge.opensearch.granuleisoresponse import GranuleIsoResponse
from edge.opensearch.datasetgranulewriter import DatasetGranuleWriter

class IsoWriter(DatasetGranuleWriter):
    def __init__(self, configFilePath):
        super(IsoWriter, self).__init__(configFilePath)
        
        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrGranuleResponse, solrDatasetResponse, pretty):
        response = GranuleIsoResponse(
            self._configuration.get('service', 'linkToGranule')
        )
        response.setTemplate(self.template)

        return response.generate(solrDatasetResponse, solrGranuleResponse, pretty)
