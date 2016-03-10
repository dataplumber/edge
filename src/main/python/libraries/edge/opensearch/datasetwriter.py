from types import *
import json
import logging
import urllib

import requestresponder
from edge.dateutility import DateUtility
from edge.httputility import HttpUtility
from edge.opensearch.responsewriter import ResponseWriter
import re

class DatasetWriter(ResponseWriter):
    def __init__(self, configFilePath):
        super(DatasetWriter, self).__init__(configFilePath)
        self.datasets = []

    def get(self, requestHandler):
        super(DatasetWriter, self).get(requestHandler)
        #searchParameters = {}
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
            self.searchParameters['itemsPerPage'] = entriesPerPage
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

        parameters = ['startTime', 'endTime', 'keyword', 'datasetId', 'shortName', 'instrument', 'satellite', 'fileFormat', 'status', 'processLevel', 'sortBy', 'bbox', 'allowNone']
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
        """
        else:
            variables['keyword'] = '""'
        """
        #If generating OpenSearch response, need to make additional call to solr
        #to determine which datasets have granules 
        try:
            if 'search' in requestHandler.request.path:
                callback = self._getSolrHasGranuleResponseCallback(startIndex, entriesPerPage)
                self._getSolrHasGranuleResponse(callback)
            else:
               self._getSolrResponse(startIndex, entriesPerPage, self.variables)
        except:
            logging.exception('Failed to get solr response.')
        """
        searchText = ''
        if 'keyword' in variables:
            searchText = variables['keyword']
        openSearchResponse = self._generateOpenSearchResponse(
            solrResponse,
            searchText,
            self._configuration.get('service', 'url') + requestHandler.request.path,
            searchParameters,
            pretty
        )

        requestHandler.set_header("Content-Type", "application/xml")
        #requestHandler.set_header("Content-Type", "application/rss+xml")
        #requestHandler.write(solrResponse)
        requestHandler.write(openSearchResponse)
        """

    def _getSolrResponse(self, startIndex, entriesPerPage, variables):
        query = self._constructSolrQuery(startIndex, entriesPerPage, variables)
        url = self._configuration.get('solr', 'datasetUrl')

        httpUtility = HttpUtility()
        httpUtility.getResponse(url+'/select/?'+query, self._onSolrResponse)

    def _constructSolrQuery(self, startIndex, entriesPerPage, variables):
        queries = []
        sort = None
        filterQuery = None
        for key, value in variables.iteritems():
            #query = ''
            if key == 'startTime':
                startTime = DateUtility.convertISOToUTCTimestamp(value)
                if startTime is not None:
                    query = 'DatasetCoverage-StopTimeLong-Long:'
                    query += '['+str(startTime)+'%20TO%20*]'
                    queries.append(query)
            elif key == 'endTime':
                stopTime = DateUtility.convertISOToUTCTimestamp(value)
                if stopTime is not None:
                    query = 'DatasetCoverage-StartTimeLong-Long:'
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
            elif key == 'satellite':
                query = 'DatasetSource-Source-ShortName-Full:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'instrument':
                query = 'DatasetSource-Sensor-ShortName-Full:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'fileFormat':
                query = 'DatasetPolicy-DataFormat-LowerCased:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'status':
                query = 'DatasetPolicy-AccessType-LowerCased:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'processLevel':
                query = 'Dataset-ProcessingLevel-LowerCased:'+value
                queries.append(query)
            elif key == 'sortBy':
                sortByMapping = {'timeDesc': 'DatasetCoverage-StartTimeLong-Long+desc', 'timeAsc': 'DatasetCoverage-StartTimeLong-Long+asc', 
                                 'popularityDesc': 'Dataset-AllTimePopularity+desc', 'popularityAsc': 'Dataset-AllTimePopularity+asc'}
                if value in sortByMapping.keys():
                    sort = sortByMapping[value]
            elif key == 'bbox':
                filterQuery = self._constructBoundingBoxQuery(value)

            #if query != '':
            #    queries.append('%2B'+query)

        if len(queries) == 0:
            queries.append('*')

        query = 'q='+'+AND+'.join(queries)+'&fq=DatasetPolicy-AccessType-Full:(OPEN+OR+PREVIEW+OR+SIMULATED+OR+REMOTE)+AND+DatasetPolicy-ViewOnline:Y&version=2.2&start='+str(startIndex)+'&rows='+str(entriesPerPage)+'&indent=on&wt=json'
        if sort is not None:
            query += '&sort=' + sort
        if filterQuery is not None:
            query += '&' + filterQuery
        logging.debug('solr query: '+query)
        
        return query
    
    def _getSolrHasGranuleResponse(self, callback):
        url = self._configuration.get('solr', 'granuleUrl')

        httpUtility = HttpUtility()
        return httpUtility.getResponse(url+'/select?q=*:*&facet=true&facet.field=Dataset-ShortName-Full&facet.limit=-1&rows=0&indent=on&wt=json&version=2.2', callback)
    
    def _getSolrHasGranuleResponseCallback(self, startIndex, entriesPerPage):   
        def onSolrHasGranuleResponse(response):
            try:
                solrJson = json.loads(response.body)
                logging.debug("Got response for dataset facet")
                datasetCounter = solrJson['facet_counts']['facet_fields']['Dataset-ShortName-Full']
                self.datasets = [datasetCounter[i] for i in range(len(datasetCounter)) if i % 2 == 0]
                self._getSolrResponse(startIndex, entriesPerPage, self.variables)
            except:
                logging.exception('Failed to get solr response.')
        return onSolrHasGranuleResponse
