import logging
import os
import os.path
import urllib

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
        response = SolrJsonTemplateResponse(parameters=searchParams)
        response.setTemplate(self.template)

        return response.generate(solrResponse, pretty=pretty)

    def _constructSolrQuery(self, startIndex, entriesPerPage, parameters, facets):
        queries = []
        filterQueries = []
        start = '*'
        end = '*'

        for key, value in parameters.iteritems():
            if value != "":
                if key == 'keyword':
                    queries.append(urllib.quote(value))
                elif key == 'ds':
                    filterQueries.append('datasetShortName:%s' % value)
                elif key == 'startTime':
                    start = value
                elif key == 'endTime':
                    end = value
                elif key == 'basinId':
                    filterQueries.append('basinId_i:%s' % value)
                elif key == 'basinName':
                    filterQueries.append('basinName:%s' % value)
        filterQueries.append('(time:[' + start + '%20TO%20' + end + '])')

        if len(queries) == 0:
            queries.append('*:*')

        query = 'q='+'+AND+'.join(queries)+'&version=2.2&indent=on&wt=json&start='+str(startIndex)+'&rows='+str(entriesPerPage)

        if len(filterQueries) > 0:
            query += '&fq='+'+AND+'.join(filterQueries)

        logging.debug('solr query: '+query)

        return query
