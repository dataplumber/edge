import logging
import os
import os.path
import codecs

from edge.opensearch.datasetgcmdresponse import DatasetGcmdResponse
from edge.opensearch.datasetwriter import DatasetWriter

class DifWriter(DatasetWriter):
    def __init__(self, configFilePath):
        super(DifWriter, self).__init__(configFilePath)
        
        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = DatasetGcmdResponse(self._configuration)
        response.setTemplate(self.template)
        
        allowNone = False
        if 'allowNone' in searchParams and searchParams['allowNone'].lower() == 'true':
            allowNone = True
        
        return response.generate(solrResponse, pretty=pretty, allowNone=allowNone)

    def _readTemplate(self, path):
        file = codecs.open(path, encoding='utf-8')
        data = file.read()
        file.close()

        return data
