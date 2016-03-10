import logging
import os
import os.path
import urllib

from edge.writer.solrtemplateresponsewriter import SolrTemplateResponseWriter
from edge.response.solrfacettemplateresponse import SolrFacetTemplateResponse

class Writer(SolrTemplateResponseWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)
        
        self.facet = True
        self.contentType = 'application/json'
        
        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        response = SolrFacetTemplateResponse(self.facetDefs)
        response.setTemplate(self.template)
        
        return response.generate(solrResponse, pretty=pretty)

    def _constructSolrQuery(self, startIndex, entriesPerPage, parameters, facets):
        queries = []
        filterQueries = []

        for key, value in parameters.iteritems():
            if value != "":
                if key == 'keyword':
                    queries.append(urllib.quote(value))
                elif key == 'startTime':
                    queries.append('EndingDateTime-Internal:['+value+'%20TO%20*]')
                elif key == 'endTime':
                    queries.append('BeginningDateTime:[*%20TO%20'+value+']')
                elif key == 'bbox':
                    coordinates = value.split(",")
                    filterQueries.append('Spatial-Geometry:[' + coordinates[1] + ',' + coordinates[0] + '%20TO%20' + coordinates[3] + ',' + coordinates[2] + ']')
                elif key == 'concept_id':
                    queries.append('concept-id:' + self._urlEncodeSolrQueryValue(value))

        for key, value in facets.iteritems():
            tagKey = '{!tag=' + key + '}' + key
            if type(value) is list:
                if (len(value) == 1):
                    filterQueries.append(tagKey + ':' + self._urlEncodeSolrQueryValue(value[0]))
                else:
                    filterQueries.append(tagKey + ':(' + '+OR+'.join([ self._urlEncodeSolrQueryValue(x) for x in value ]) + ")")
            else:    
                filterQueries.append(tagKey + ':' + self._urlEncodeSolrQueryValue(value))

        if len(queries) == 0:
            queries.append('*:*')

        query = 'q='+'+AND+'.join(queries)+'&version=2.2&indent=on&wt=json'

        if len(filterQueries) > 0:
            query += '&fq='+'&fq='.join(filterQueries)
        
        if self.facet:
            query += '&rows=0&facet=true&facet.limit=-1&'
            query += '&'.join(['facet.field={!ex=' + facet +'}' + facet if facet in facets else 'facet.field=' + facet for facet in self.facetDefs.values()])
        else:
            query += '&start='+str(startIndex)+'&rows='+str(entriesPerPage)

        logging.debug('solr query: '+query)

        return query
