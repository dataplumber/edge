import logging
import os
import os.path
import urllib
import json

from edge.writer.solrtemplateresponsewriter import SolrTemplateResponseWriter
from edge.opensearch.solrtemplateresponse import SolrTemplateResponse

class Writer(SolrTemplateResponseWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = SolrTemplateResponse(self._configuration, searchUrl, searchParams)
        response.setTemplate(self.template)
        response.variables['serviceUrl'] = self._configuration.get('service', 'url')

        return response.generate(solrResponse, pretty=pretty)

    def _constructSolrQuery(self, startIndex, entriesPerPage, parameters, facets):
        sortKeys = json.loads(self._configuration.get('solr', 'sortKeys'))

        queries = []
        filterQueries = []
        sort = None
        sortDir = 'asc'
        start = '*'
        end = '*'

        for key, value in parameters.iteritems():
            if value != "":
                if key == 'keyword':
                    queries.append(urllib.quote(value))

        if len(queries) == 0:
            queries.append('*:*')

        query = 'q='+'+AND+'.join(queries)+'&version=2.2&indent=on&wt=json'

        if len(filterQueries) > 0:
            query += '&fq='+'+AND+'.join(filterQueries)
        
        if self.facet:
            query += '&rows=0&facet=true&facet.limit=-1&facet.mincount=1&'
            query += '&'.join(['facet.field=' + facet for facet in self.facetDefs.values()])
        else:
            query += '&start='+str(startIndex)+'&rows='+str(entriesPerPage)
            if sort is not None:
                query += '&sort=' + urllib.quote(sort + ' ' + sortDir + ",InternalVersion desc")
            else:
                query += '&sort=' + urllib.quote("submit_date desc")

        logging.debug('solr query: '+query)

        return query
