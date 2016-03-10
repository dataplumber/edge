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
        response = SolrJsonTemplateResponse()
        response.setTemplate(self.template)

        return response.generate(solrResponse, pretty=pretty)

    def _constructSolrQuery(self, startIndex, entriesPerPage, parameters, facets):
        queries = []
        filterQueries = []
        filterQueries.append('status:1')
        sort = None

        for key, value in parameters.iteritems():
            if value != "":
                if key == 'keyword':
                    #Special case keyword search on glossary_items only match title
                    if 'table' in parameters and parameters['table'] == 'glossary_items':
                        queries.append('title_t:('+urllib.quote(value) + ')')
                    else:
                        queries.append(urllib.quote(value))
                elif key == 'year':
                    start = value + "-01-01T00:00:00.000Z"
                    end = value + "-12-31T23:59:59.999Z"
                    filterQueries.append('created_at:['+start+'%20TO%20'+end+']')
                elif key == 'table':
                    filterQueries.append('type:' + value)
                elif key == 'glossary_title':
                    range = value.lower().split('-')
                    filterQueries.append('{!frange%20l=' + range[0] + '%20u=' + range[1] + 'z}' + 'title_lc')
                elif key == 'sort':
                    sort = urllib.quote(value)
                else:
                    if type(value) is list:
                        if 'table' in parameters and parameters['table'] == 'news_items':
                            filterQueries.append(key + ':(' + '+OR+'.join([self._urlEncodeSolrQueryValue(v) for v in value]) + ')')
                        else:
                            for v in value:
                                filterQueries.append(key + ':' + self._urlEncodeSolrQueryValue(v))
                    else:
                        filterQueries.append(key + ':' + self._urlEncodeSolrQueryValue(value))
        if len(queries) == 0:
            queries.append('*:*')

        query = 'q='+'+AND+'.join(queries)+'&version=2.2&indent=on&wt=json&start='+str(startIndex)+'&rows='+str(entriesPerPage)

        if len(filterQueries) > 0:
            query += '&fq='+'+AND+'.join(filterQueries)

        if sort is not None:
            query += '&sort=' + sort

        logging.debug('solr query: '+query)

        return query
