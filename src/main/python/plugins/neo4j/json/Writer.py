import logging
import os
import os.path
import urllib

from edge.writer.neo4jtemplateresponsewriter import Neo4jTemplateResponseWriter
from edge.response.neo4jjsontemplateresponse import Neo4jJsonTemplateResponse

class Writer(Neo4jTemplateResponseWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)
        
        self.contentType = 'application/json'

        templatePath = os.path.dirname(configFilePath) + os.sep
        templatePath += self._configuration.get('service', 'template')
        self.template = self._readTemplate(templatePath)

    def _generateOpenSearchResponse(self, Neo4jResponse, searchText, searchUrl, searchParams, pretty):
        response = Neo4jJsonTemplateResponse(searchUrl, searchParams)
        response.setTemplate(self.template)

        return response.generate(Neo4jResponse, pretty=pretty)

    def _constructNeo4jQuery(self, startIndex, entriesPerPage, parameters, facets):
        queries = []
        filterQueries = []
        sort = None
        ## temporarily return static string for debugging purposes
        ## This method will be modified to construct a cypher query for neo4j
        q = { 'query' : 'MATCH (r) RETURN count(r);' }
        return q

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

        logging.debug('solr query: '+query)

        return query

