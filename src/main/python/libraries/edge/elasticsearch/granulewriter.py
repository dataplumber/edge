from types import *
import logging
import urllib
import json

from edge.opensearch.responsewriter import ResponseWriter
from edge.dateutility import DateUtility
from edge.httputility import HttpUtility
import re

class GranuleWriter(ResponseWriter):
    def __init__(self, configFilePath, requiredParams = None):
        super(GranuleWriter, self).__init__(configFilePath, requiredParams)
        self.startIndex = 0
        self.entriesPerPage = self._configuration.getint('solr', 'entriesPerPage')

    def get(self, requestHandler):
        super(GranuleWriter, self).get(requestHandler)
        #searchParameters = {}
        #logging.debug('uri: '+str(requestHandler.request.headers))
        
        #startIndex = 0
        try:
            self.startIndex = requestHandler.get_argument('startIndex')
        except:
            pass
        self.searchParameters['startIndex'] = self.startIndex

        #entriesPerPage = self._configuration.getint('solr', 'entriesPerPage')
        try:
            self.entriesPerPage = requestHandler.get_argument('itemsPerPage')
            #cap entries per age at 400
            if (int(self.entriesPerPage) > 400):
                self.entriesPerPage = 400
        except:
            pass
        self.searchParameters['itemsPerPage'] = self.entriesPerPage

        #pretty = True
        try:
            if requestHandler.get_argument('pretty').lower() == 'false':
                self.pretty = False
                self.searchParameters['pretty'] = 'false'
        except:
            pass

        try:
            if requestHandler.get_argument('full').lower() == 'true':
                self.searchParameters['full'] = 'true'
        except:
            pass
        
        try:
            self.searchParameters['format'] = requestHandler.get_argument('format')
        except:
            pass

        parameters = ['startTime', 'endTime', 'keyword', 'name', 'identifier', 'shortName', 'bbox', 'sortBy']
        #variables = {}
        for parameter in parameters:
            try:
                value = requestHandler.get_argument(parameter)
                self.variables[parameter] = value
                self.searchParameters[parameter] = value
            except:
                pass

        if 'keyword' in self.variables:
            self.variables['keyword'] = self.variables['keyword'].replace('*', '')
            self.variables['keyword'] = self.variables['keyword'].lower()

        try:
            self._getSolrResponse(self.startIndex, self.entriesPerPage, self.variables)
        except:
            logging.exception('Failed to get solr response.')

    def _getSolrResponse(self, startIndex, entriesPerPage, variables):
        query = self._constructSolrQuery(startIndex, entriesPerPage, variables)
        url = self._configuration.get('solr', 'granuleUrl')

        httpUtility = HttpUtility()
        httpUtility.getResponse(url+'/_search', self._onSolrResponse, query)

    def _constructSolrQuery(self, startIndex, entriesPerPage, variables):
        #set default sort order
        sort='desc'
        filterQuery = None
        queries = []
        for key, value in variables.iteritems():
            #query = ''
            if key == 'startTime':
                startTime = DateUtility.convertISOToUTCTimestamp(value)
                if startTime is not None:
                    query = 'stop_time:'
                    query += '['+str(startTime)+' TO *]'
                    queries.append(query)
            elif key == 'endTime':
                stopTime = DateUtility.convertISOToUTCTimestamp(value)
                if stopTime is not None:
                    query = 'start_time:'
                    query += '[* TO '+str(stopTime)+']'
                    queries.append(query)
            elif key == 'keyword':
                newValue = urllib.quote(value)

                query = 'SearchableText-LowerCased:('+newValue+')'
                queries.append(query)
            elif key == 'identifier':
                query = 'identifier:"'+value+'"'
                queries.append(query)
            elif key == 'shortName':
                query = 'Dataset-ShortName-Full:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'name':
                query = 'name:"'+value+'"'
                queries.append(query)
            elif key == 'granuleIds':
                granuleIds = []
                for granuleId in value:
                    granuleIds.append(str(granuleId))
                query = 'Granule-Id:('+'+OR+'.join(granuleIds)+')'
                queries.append(query)

                startIndex = 0
            elif key == 'sortBy':
                sortByMapping = {'timeAsc': 'asc'}
                if value in sortByMapping.keys():
                    sort = sortByMapping[value]
            elif key == 'bbox':
                filterQuery = self._constructBoundingBoxQuery(value)
            #if query != '':
            #    queries.append('%2B'+query)

        if len(queries) == 0:
            queries.append('*')

        query = 'q='+'+AND+'.join(queries)+'&from='+str(startIndex)+'&size='+str(entriesPerPage)
        if filterQuery is not None:
            query += '&' + filterQuery
        logging.debug('solr query: '+query)
        
        return json.dumps({'query' : {'filtered' : { 'query' : {'query_string' : {'query' : ' AND '.join(queries)}}, 'filter' : {'term' : {'status' : 'online'}}}}, 'from' : startIndex, 'size' : entriesPerPage, 'sort' : [{'start_time' : {'order' : sort}}]})
