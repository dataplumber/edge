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
        response = SolrJsonTemplateResponse(searchUrl, searchParams)
        response.setTemplate(self.template)

        return response.generate(solrResponse, pretty=pretty)

    def _constructSolrQuery(self, startIndex, entriesPerPage, parameters, facets):
        queries = []
        filterQueries = []
        sort = None

        for key, value in parameters.iteritems():
            if value != "":
                if key == 'keyword':
                    queries.append(urllib.quote(value))
                elif key == 'startTime':
                    filterQueries.append('time:['+value+'%20TO%20*]')
                elif key == 'endTime':
                    filterQueries.append('time:[*%20TO%20'+value+']')
                elif key == 'bbox':
                    coordinates = value.split(",")
                    filterQueries.append('loc:[' + coordinates[1] + ',' + coordinates[0] + '%20TO%20' + coordinates[3] + ',' + coordinates[2] + ']')
                elif key == 'variable':
                    if value.lower() == 'sss':
                        filterQueries.append('SSS:[*%20TO%20*]')
                    elif value.lower() == 'sst':
                        filterQueries.append('SST:[*%20TO%20*]')
                    elif value.lower() == 'wind':
                        filterQueries.append('wind_speed:[*%20TO%20*]')
                elif key == "minDepth":
                    if 'variable' in parameters:
                        if parameters['variable'].lower() == 'sss':
                            filterQueries.append('SSS_depth:['+value+'%20TO%20*]')
                        elif parameters['variable'].lower() == 'sst':
                            filterQueries.append('SST_depth:['+value+'%20TO%20*]')
                        elif parameters['variable'].lower() == 'wind':
                            filterQueries.append('wind_depth:['+value+'%20TO%20*]')
                elif key == "maxDepth":
                    if 'variable' in parameters:
                        if parameters['variable'].lower() == 'sss':
                            filterQueries.append('SSS_depth:[*%20TO%20'+value+']')
                        elif parameters['variable'].lower() == 'sst':
                            filterQueries.append('SST_depth:[*%20TO%20'+value+']')
                        elif parameters['variable'].lower() == 'wind':
                            filterQueries.append('wind_depth:[*%20TO%20'+value+']')
                elif key == 'platform':
                    if type(value) is list:
                        filterQueries.append('platform:(' + '+OR+'.join(value) + ')')
                    else:
                        filterQueries.append('platform:'+value)

        if len(queries) == 0:
            queries.append('*:*')

        query = 'q='+'+AND+'.join(queries)+'&wt=json&start='+str(startIndex)+'&rows='+str(entriesPerPage)

        if len(filterQueries) > 0:
            query += '&fq='+'+AND+'.join(filterQueries)

        if sort is not None:
            query += '&sort=' + sort

        if 'stats' in parameters and parameters['stats'].lower() == 'true':
            query += '&stats=true&stats.field={!min=true%20max=true}SSS_depth&stats.field={!min=true%20max=true}SST_depth&stats.field={!min=true%20max=true}wind_depth'

        if 'facet' in parameters and parameters['facet'].lower() == 'true':
            query += '&facet=true&facet.field=platform&facet.field=device&facet.limit=-1&facet.mincount=1'

        logging.debug('solr query: '+query)

        return query
