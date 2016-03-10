import logging
import os
import os.path
import urllib

from edge.writer.solrtemplateresponsewriter import SolrTemplateResponseWriter
from edge.opensearch.solrcmrtemplateresponse import SolrCmrTemplateResponse

class Writer(SolrTemplateResponseWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)

        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):

        response = SolrCmrTemplateResponse(self._configuration, searchUrl, searchParams)
        response.setTemplate(self.template)
        response.variables['serviceUrl'] = self._configuration.get('service', 'url')

        return response.generate(solrResponse, pretty=pretty)

    def _constructSolrQuery(self, startIndex, entriesPerPage, parameters, facets):
        queries = []
        filterQueries = []

        for key, value in parameters.iteritems():
            if key == 'keyword':
                logging.debug('product/atom/Writer.py: keyword='+value)
                queries.append(urllib.quote(value))
            elif key == 'product_pt_id':
                filterQueries.append(key + ':' + self._urlEncodeSolrQueryValue(value))
            elif key == 'startTime':
                queries.append('EndingDateTime:['+value+'%20TO%20*]')
            elif key == 'endTime':
                queries.append('BeginningDateTime:[*%20TO%20'+value+']')
            elif key == 'bbox':
                coordinates = value.split(",")
                filterQueries.append('Spatial-Geometry:[' + coordinates[1] + ',' + coordinates[0] + '%20TO%20' + coordinates[3] + ',' + coordinates[2] + ']')
            elif key == 'id':
                queries.append('id:' + self._urlEncodeSolrQueryValue(value))

        for key, value in facets.iteritems():
            if type(value) is list:
                if (len(value) == 1):
                    filterQueries.append(key + ':' + self._urlEncodeSolrQueryValue(value[0]))
                else:
                    filterQueries.append(key + ':(' + '+OR+'.join([ self._urlEncodeSolrQueryValue(x) for x in value ]) + ")")
            else:    
                filterQueries.append(key + ':' + self._urlEncodeSolrQueryValue(value))

        if len(queries) == 0:
            queries.append('*:*')

        query = 'q='+'+AND+'.join(queries)+'&version=2.2&indent=on&wt=json'

        if len(filterQueries) > 0:
            query += '&fq='+'+AND+'.join(filterQueries)
        
        if self.facet:
            query += '&rows=0&facet=true&facet.limit=-1&facet.mincount=1&'
            query += '&'.join(['facet.field=' + facet for facet in self._configuration.get('solr', 'facets').split(',')])
        else:
            query += '&start='+str(startIndex)+'&rows='+str(entriesPerPage)
            query += '&sort=' + self._configuration.get('solr', 'sort')

        logging.debug('solr query: '+query)

        return query
