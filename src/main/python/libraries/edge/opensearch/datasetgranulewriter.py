from types import *
import logging
import urllib
import urlparse
import httplib
from xml.dom.minidom import Document
import json
import xml.sax.saxutils
import datetime
import codecs

from edge.opensearch.responsewriter import ResponseWriter
from edge.dateutility import DateUtility
from edge.httputility import HttpUtility
from edge.spatialsearch import SpatialSearch
import re

class DatasetGranuleWriter(ResponseWriter):
    def __init__(self, configFilePath, requiredParams = None):
        super(DatasetGranuleWriter, self).__init__(configFilePath, requiredParams)
        self.solrGranuleResponse = None

    def get(self, requestHandler):
        super(DatasetGranuleWriter, self).get(requestHandler)
        #logging.debug('uri: '+str(requestHandler.request.headers))

        startIndex = 0
        try:
            startIndex = requestHandler.get_argument('startIndex')
        except:
            pass

        entriesPerPage = self._configuration.getint('solr', 'entriesPerPage')
        try:
            entriesPerPage = requestHandler.get_argument('itemsPerPage')
            #cap entries per age at 400
            if (int(entriesPerPage) > 400):
                entriesPerPage = 400
        except:
            pass
        
        #pretty = True
        try:
            if requestHandler.get_argument('pretty').lower() == 'false':
                self.pretty = False
        except:
            pass
        
        parameters = ['startTime', 'endTime', 'keyword', 'granuleName', 'datasetId', 'shortName', 'bbox', 'sortBy']
        #variables = {}
        for parameter in parameters:
            try:
                value = requestHandler.get_argument(parameter)
                self.variables[parameter] = value
            except:
                pass

        if 'keyword' in self.variables:
            self.variables['keyword'] = self.variables['keyword'].replace('*', '')
            self.variables['keyword'] = self.variables['keyword'].lower()
        """
        if 'bbox' in variables:
            points = variables['bbox'].split(',')
            if len(points) == 4:
                spatialSearch = SpatialSearch(
                    self._configuration.get('service', 'database')
                )
                spatialResult = spatialSearch.searchGranules(
                    int(startIndex),
                    int(entriesPerPage),
                    float(points[0]),
                    float(points[1]),
                    float(points[2]),
                    float(points[3])
                )
                if len(spatialResult[0]) > 0:
                    variables['granuleIds'] = spatialResult[0]
                    variables['granuleIdsFound'] = spatialResult[1]

            del variables['bbox']
        """
        try:
            self._getSolrResponse(startIndex, entriesPerPage, self.variables)
            """
            solrJson = json.loads(solrResponse)
            if len(solrJson['response']['docs']) >= 1:
                dataset = solrJson['response']['docs'][0]['Dataset-ShortName'][0];
                logging.debug('Getting solr response for dataset ' + dataset)
                solrDatasetResponse = self._getSingleSolrDatasetResponse({'shortName' : dataset})
            """
        except:
            logging.exception('Failed to get solr response.')
        """
        if 'granuleIdsFound' in variables:
            #solrJson = json.loads(solrResponse)
            numFound = solrJson['response']['numFound']
            solrJson['response']['numFound'] = int(variables['granuleIdsFound'])
            solrJson['response']['start'] = int(startIndex)
            solrJson['responseHeader']['params']['rows'] = numFound
            solrResponse = json.dumps(solrJson)

        searchText = ''
        if 'keyword' in variables:
            searchText = variables['keyword']
        try:
            openSearchResponse = self._generateOpenSearchResponse(
                solrResponse,
                solrDatasetResponse,
                searchText,
                self._configuration.get('service', 'url')+requestHandler.request.uri,
                pretty
            )
            requestHandler.set_header("Content-Type", "application/xml")
            requestHandler.write(openSearchResponse)
        except Exception as exception:
            logging.exception(exception)
            requestHandler.set_status(404)
            requestHandler.write('ERROR - ' + str(exception))
        """

    def _getSolrResponse(self, startIndex, entriesPerPage, variables):
        query = self._constructSolrQuery(startIndex, entriesPerPage, variables)
        url = self._configuration.get('solr', 'granuleUrl')

        httpUtility = HttpUtility()
        httpUtility.getResponse(url+'/select/?'+query, self._onSolrGranuleResponse)

    def _constructSolrQuery(self, startIndex, entriesPerPage, variables):
        #set default sort order
        sort='Granule-StartTimeLong+desc'
        queries = []
        for key, value in variables.iteritems():
            #query = ''
            if key == 'startTime':
                startTime = DateUtility.convertISOToUTCTimestamp(value)
                if startTime is not None:
                    query = 'Granule-StartTimeLong:'
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
                sortByMapping = {'timeAsc': 'Granule-StartTimeLong+asc', 'archiveTimeDesc': 'Granule-ArchiveTimeLong+desc'}
                if value in sortByMapping.keys():
                    sort = sortByMapping[value]
            elif key == 'archiveTime':
                query = 'Granule-ArchiveTimeLong:['+str(value)+'%20TO%20*]'
                queries.append(query)
            #if query != '':
            #    queries.append('%2B'+query)

        if len(queries) == 0:
            queries.append('*')

        query = 'q='+'+AND+'.join(queries)+'&fq=Granule-AccessType:(OPEN+OR+PREVIEW+OR+SIMULATED+OR+REMOTE)+AND+Granule-Status:ONLINE&version=2.2&start='+str(startIndex)+'&rows='+str(entriesPerPage)+'&indent=on&wt=json&sort='+sort
        logging.debug('solr query: '+query)
        
        return query

    def _readTemplate(self, path):
        file = codecs.open(path, encoding='utf-8')
        data = file.read()
        file.close()

        return data
    
    def _generateOpenSearchResponse(self, solrGranuleResponse, solrDatasetResponse, pretty):
        pass
    
    def _onSolrGranuleResponse(self, response):
        if response.error:
            self._handleException(str(response.error))
        else:
            self.solrGranuleResponse = response.body
            solrJson = json.loads(response.body)
            if len(solrJson['response']['docs']) >= 1:
                dataset = solrJson['response']['docs'][0]['Dataset-ShortName'][0];
                logging.debug('Getting solr response for dataset ' + dataset)
                self._getSingleSolrDatasetResponse({'shortName' : dataset}, self._onSolrDatasetResponse)
            else:
                try:
                    openSearchResponse = self._generateOpenSearchResponse(
                        None,
                        None,
                        self.pretty
                    )
                    self.requestHandler.set_header("Content-Type", "application/xml")
                    self.requestHandler.write(openSearchResponse)
                    self.requestHandler.finish()
                except BaseException as exception:
                    self._handleException(str(exception))

    def _onSolrDatasetResponse(self, response):
        if response.error:
            self._handleException(str(response.error))
        else:
            try:
                openSearchResponse = self._generateOpenSearchResponse(
                    self.solrGranuleResponse,
                    response.body,
                    self.pretty
                )
                self.requestHandler.set_header("Content-Type", "application/xml")
                self.requestHandler.write(openSearchResponse)
                self.requestHandler.finish()
            except BaseException as exception:
                self._handleException(str(exception))
