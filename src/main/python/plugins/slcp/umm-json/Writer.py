import logging
import os
import os.path

from edge.writer.solrtemplateresponsewriter import SolrTemplateResponseWriter
from edge.response.solrjsontemplateresponse import SolrJsonTemplateResponse

class Writer(SolrTemplateResponseWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

        self.contentType = 'application/json'

        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = SolrJsonTemplateResponse()
        response.setTemplate(self.template)

        return response.generate(solrResponse, pretty=pretty)

    def _constructSolrQuery(self, startIndex, entriesPerPage, parameters, facets):
        queries = []

        for key, value in parameters.iteritems():
            if key == 'id':
                queries.append('id:' + self._urlEncodeSolrQueryValue(value))
            elif key == 'slcpShortName':
                queries.append('SlcpShortName:' + self._urlEncodeSolrQueryValue(value))
            elif key == 'shortName':
                queries.append('ShortName:' + self._urlEncodeSolrQueryValue(value))

        query = 'q='+'+AND+'.join(queries)+'&version=2.2&indent=on&wt=json'+'&rows='+str(entriesPerPage)

        logging.debug('solr query: '+query)

        return query
