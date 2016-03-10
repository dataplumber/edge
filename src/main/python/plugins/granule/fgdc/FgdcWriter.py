import logging
import os
import os.path
import codecs

from edge.opensearch.granulefgdcresponse import GranuleFgdcResponse
from edge.opensearch.datasetgranulewriter import DatasetGranuleWriter

class FgdcWriter(DatasetGranuleWriter):
    def __init__(self, configFilePath):
        super(FgdcWriter, self).__init__(configFilePath)
        
        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrGranuleResponse, solrDatasetResponse, pretty):
        response = GranuleFgdcResponse()
        response.setTemplate(self.template)

        return response.generate(solrDatasetResponse, solrGranuleResponse, pretty)
