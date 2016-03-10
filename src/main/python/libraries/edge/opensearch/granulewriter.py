from types import *
import logging
import urllib
import json

from edge.opensearch.responsewriter import ResponseWriter
from edge.dateutility import DateUtility
from edge.httputility import HttpUtility
from edge.spatialsearch import SpatialSearch
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

        #entriesPerPage = self._configuration.getint('solr', 'entriesPerPage')
        try:
            self.entriesPerPage = requestHandler.get_argument('itemsPerPage')
            #cap entries per age at 400
            if (int(self.entriesPerPage) > 400):
                self.entriesPerPage = 400
            self.searchParameters['itemsPerPage'] = self.entriesPerPage
        except:
            pass

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

        parameters = ['startTime', 'endTime', 'keyword', 'granuleName', 'datasetId', 'shortName', 'bbox', 'sortBy']
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

        #Fetch dataset metadata from Solr
        datasetVariables = {}
        if 'datasetId' in self.variables:
            datasetVariables['datasetId'] = self.variables['datasetId']
        if 'shortName' in self.variables:
            datasetVariables['shortName'] = self.variables['shortName']
        self._getSingleSolrDatasetResponse(datasetVariables, self._onSolrDetermineProcessLevelResponse)

    def _getSolrResponse(self, startIndex, entriesPerPage, variables):
        query = self._constructSolrQuery(startIndex, entriesPerPage, variables)
        url = self._configuration.get('solr', 'granuleUrl')

        httpUtility = HttpUtility()
        httpUtility.getResponse(url+'/select/?'+query, self._onSolrResponse)

    def _constructSolrQuery(self, startIndex, entriesPerPage, variables):
        #set default sort order
        sort='Granule-StartTimeLong+desc'
        filterQuery = None
        queries = []
        for key, value in variables.iteritems():
            #query = ''
            if key == 'startTime':
                startTime = DateUtility.convertISOToUTCTimestamp(value)
                if startTime is not None:
                    query = 'Granule-StopTimeLong:'
                    query += '['+str(startTime)+'%20TO%20*]'
                    queries.append(query)
            elif key == 'endTime':
                stopTime = DateUtility.convertISOToUTCTimestamp(value)
                if stopTime is not None:
                    query = 'Granule-StartTimeLong:'
                    query += '[*%20TO%20'+str(stopTime)+']'
                    queries.append(query)
            elif key == 'keyword':
                newValue = urllib.quote(value)

                query = 'SearchableText-LowerCased:('+newValue+')'
                queries.append(query)
            elif key == 'datasetId':
                query = 'Dataset-PersistentId:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'shortName':
                query = 'Dataset-ShortName-Full:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'granuleName':
                query = 'Granule-Name-Full:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'granuleIds':
                granuleIds = []
                for granuleId in value:
                    granuleIds.append(str(granuleId))
                query = 'Granule-Id:('+'+OR+'.join(granuleIds)+')'
                queries.append(query)

                startIndex = 0
            elif key == 'sortBy':
                sortByMapping = {'timeAsc': 'Granule-StartTimeLong+asc'}
                if value in sortByMapping.keys():
                    sort = sortByMapping[value]
            elif key == 'bbox':
                filterQuery = self._constructBoundingBoxQuery(value)
            #if query != '':
            #    queries.append('%2B'+query)

        if len(queries) == 0:
            queries.append('*')

        query = 'q='+'+AND+'.join(queries)+'&fq=Granule-AccessType:(OPEN+OR+PREVIEW+OR+SIMULATED+OR+REMOTE)+AND+Granule-Status:ONLINE&version=2.2&start='+str(startIndex)+'&rows='+str(entriesPerPage)+'&indent=on&wt=json&sort='+sort
        if filterQuery is not None:
            query += '&' + filterQuery
        logging.debug('solr query: '+query)
        
        return query
    
    def _onSolrDetermineProcessLevelResponse(self, response):
        try:
            #Determine dataset processing level
            processingLevel = None
            solrJson = json.loads(response.body)
            if len(solrJson['response']['docs']) >= 1:
                if 'bbox' in self.variables:
                    processingLevel = solrJson['response']['docs'][0]['Dataset-ProcessingLevel-Full'][0]
                
                    if processingLevel is not None and processingLevel.find('2') != -1:
                        if self._configuration.get('service', 'bbox') == 'l2':
                            #Call Matt's L2 Search Service
                            #raise Exception(self._configuration.get('service', 'l2')+'?'+requestHandler.request.query)
                            httpUtility = HttpUtility()
                            url = self._configuration.get('service', 'l2') + '?'
                            if 'format' not in self.requestHandler.request.arguments:
                                url += 'format=atom&'
                            url += self.requestHandler.request.query
                            logging.debug("Calling L2 Service: " + url)
                            result = httpUtility.getResponse(url, self._onL2Response)
                        else:
                            points = self.variables['bbox'].split(',')
                            if len(points) == 4:
                                spatialSearch = SpatialSearch(
                                    self._configuration.get('service', 'database')
                                )
                                spatialResult = spatialSearch.searchGranules(
                                    int(self.startIndex),
                                    int(self.entriesPerPage),
                                    float(points[0]),
                                    float(points[1]),
                                    float(points[2]),
                                    float(points[3])
                                )
                                logging.debug("Granule spatial search returned")
                                #if len(spatialResult[0]) > 0:
                                self.variables['granuleIds'] = spatialResult[0]
                                self.variables['granuleIdsFound'] = spatialResult[1]
                
                            del self.variables['bbox']
                            solrJson = {'responseHeader': {'params': {}}, 'response': {}}
                            solrJson['response']['numFound'] = int(self.variables['granuleIdsFound'])
                            solrJson['response']['start'] = int(self.startIndex)
                            solrJson['responseHeader']['params']['rows'] = int(self.entriesPerPage)
                            solrJson['response']['docs'] = []
                            for name in self.variables['granuleIds']:
                               solrJson['response']['docs'].append({'Granule-Name': [name]})
                            solrResponse = json.dumps(solrJson)
                            
                            searchText = ''
                            if 'keyword' in self.variables:
                                searchText = self.variables['keyword']
                            openSearchResponse = self._generateOpenSearchResponse(
                                solrResponse,
                                searchText,
                                self._configuration.get('service', 'url')+self.requestHandler.request.path,
                                self.searchParameters,
                                self.pretty
                            )
                            
                            self.requestHandler.set_header("Content-Type", "application/xml")
                            #requestHandler.set_header("Content-Type", "application/rss+xml")
                            #requestHandler.write(solrResponse)
                            self.requestHandler.write(openSearchResponse)
                            self.requestHandler.finish()
                    else:
                        #Dataset is not an L2 dataset so handle search via Solr
                        try:
                            self._getSolrResponse(self.startIndex, self.entriesPerPage, self.variables)
                        except:
                            logging.exception('Failed to get solr response.')
                else:
                    #Not a bounding box search so handle search via Solr
                    try:
                        self._getSolrResponse(self.startIndex, self.entriesPerPage, self.variables)
                    except:
                        logging.exception('Failed to get solr response.')
            else:
                #Dataset metadata cannot be retreived so return empty search result
                solrJson = {'responseHeader': {'params': {}}, 'response': {}}
                solrJson['response']['numFound'] = 0
                solrJson['response']['start'] = int(self.startIndex)
                solrJson['responseHeader']['params']['rows'] = int(self.entriesPerPage)
                solrJson['response']['docs'] = []
                solrResponse = json.dumps(solrJson)
                
                self._writeResponse(solrResponse)
        except BaseException as exception:
            logging.exception('Failed to determine dataset processing level for bbox search ' + str(exception))
            self._handleException(str(exception))

    def _onL2Response(self, response):
        if response.error:
            self._handleException(str(response.error))
        else:
            try:
                logging.debug('header: Content-Type '+response.headers['Content-Type'])
                self.requestHandler.set_header('Content-Type', response.headers['Content-Type'])
                logging.debug('header: Content-Length '+response.headers['Content-Length'])
                self.requestHandler.set_header('Content-Length', response.headers['Content-Length'])
            except:
                pass
            self.requestHandler.write(response.body)
            self.requestHandler.finish()
    
