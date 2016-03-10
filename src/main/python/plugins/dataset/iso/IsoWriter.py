import logging
import os
import os.path
import codecs

from edge.opensearch.datasetisoresponse import DatasetIsoResponse
from edge.opensearch.datasetwriter import DatasetWriter

class IsoWriter(DatasetWriter):
    def __init__(self, configFilePath):
        super(IsoWriter, self).__init__(configFilePath)
        
        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = DatasetIsoResponse()
        response.setTemplate(self.template)

        return response.generate(solrResponse, pretty=pretty)

    def _readTemplate(self, path):
        file = codecs.open(path, encoding='utf-8')
        data = file.read()
        file.close()

        return data
