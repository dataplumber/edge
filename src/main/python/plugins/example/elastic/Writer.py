import logging
import os
import os.path
import urllib

from edge.writer.estemplateresponsewriter import ESTemplateResponseWriter
from edge.response.estemplateresponse import ESTemplateResponse

class Writer(ESTemplateResponseWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = ESTemplateResponse(searchUrl, searchParams, self._configuration.getint('solr', 'entriesPerPage'))
        response.setTemplate(self.template)

        return response.generate(solrResponse, pretty=pretty)

    def _constructQuery(self, startIndex, entriesPerPage, parameters, facets):
        queries = []
        filterQueries = []
        sort = None

        for key, value in parameters.iteritems():
            if value != "":
                if key == 'keyword':
                    queries.append(urllib.quote(value))
        if len(queries) == 0:
            queries.append('*')

        query = 'q='+'+AND+'.join(queries)+'&from='+str(startIndex)+'&size='+str(entriesPerPage)

        if len(filterQueries) > 0:
            query += '&fq='+'+AND+'.join(filterQueries)

        if sort is not None:
            query += '&sort=' + sort

        logging.debug('elasticsearch query: '+query)

        return query
