from types import *
import logging
import urllib
import json
from collections import OrderedDict

from edge.httputility import HttpUtility
from edge.writer.templateresponsewriter import TemplateResponseWriter

class Neo4jTemplateResponseWriter(TemplateResponseWriter):
    def __init__(self, configFilePath, requiredParams = None):
        super(Neo4jTemplateResponseWriter, self).__init__(configFilePath, requiredParams)
        self.searchParameters = {}
        self.variables = {}
        self.facet = False
        self.facetDefs = {}
        self.contentType = 'application/json; charset=UTF-8'

    def get(self, requestHandler):
        super(Neo4jTemplateResponseWriter, self).get(requestHandler)

        startIndex = 0
        try:
            startIndex = requestHandler.get_argument('startIndex')
        except:
            pass

        entriesPerPage = self._configuration.getint('neo4j', 'entriesPerPage')
        try:
            entriesPerPage = requestHandler.get_argument('itemsPerPage')
            maxEntriesPerPage = self._configuration.getint('neo4j', 'maxEntriesPerPage')
            if (int(entriesPerPage) > maxEntriesPerPage):
                entriesPerPage = maxEntriesPerPage
            self.searchParameters['itemsPerPage'] = entriesPerPage
        except:
            pass

        try:
            if requestHandler.get_argument('pretty').lower() == 'true':
                self.pretty = True
                self.searchParameters['pretty'] = 'true'
        except:
            pass

        parameters = {}
        for parameter in self._configuration.get('neo4j', 'parameters').split(','):
            try:
                value = requestHandler.get_arguments(parameter)
                if len(value) == 1:
                    parameters[parameter] = value[0]
                    self.searchParameters[parameter] = value[0]
                elif len(value) > 0:
                    parameters[parameter] = value
                    self.searchParameters[parameter] = value
            except:
                pass

        facets = {}
        if self._configuration.has_option('neo4j', 'facets'):
            self.facetDefs = json.loads(self._configuration.get('neo4j', 'facets'), object_pairs_hook=OrderedDict)
            for facet in self.facetDefs.keys():
                try:
                    value = requestHandler.get_arguments(facet)
                    if len(value) > 0:
                        facets[self.facetDefs[facet]] = value
                        self.searchParameters[facet] = value
                except:
                    pass

        try:
            self._getNeo4jResponse(startIndex, entriesPerPage, parameters, facets)
        except:
            logging.exception('Failed to get solr response.')

    def _urlEncodeNeo4jQueryValue(self, value):
        return urllib.quote('"'+value+'"')

    def _onNeo4jResponse(self, response):
        logging.debug(response)
        if response.error:
            self._handleException(str(response.error))
        else:
            self._writeResponse(response.body)

    def _writeResponse(self, responseText):
        searchText = ''
        if 'keyword' in self.variables:
            searchText = self.variables['keyword']
        try:
            openSearchResponse = self._generateOpenSearchResponse(
                responseText,
                searchText,
                self._configuration.get('service', 'url') + self.requestHandler.request.path,
                self.searchParameters,
                self.pretty
            )
            self.requestHandler.set_header("Content-Type", self.contentType)
            self.requestHandler.set_header('Access-Control-Allow-Origin', '*')
            self.requestHandler.write(openSearchResponse)
            self.requestHandler.finish()
        except BaseException as exception:
            self._handleException(str(exception))

    def _getNeo4jResponse(self, startIndex, entriesPerPage, parameters, facets):
        query = self._constructNeo4jQuery(startIndex, entriesPerPage, parameters, facets)
        url = self._configuration.get('neo4j', 'datasetUrl')

        print 'Request is being constructed for :', url + '/cypher'
        print 'Body being sent:\n\t', json.dumps({"query" : "MATCH (r) RETURN count(r);"})

        httpUtility = HttpUtility()
        httpUtility.getResponse(url+'/cypher', self._onNeo4jResponse, body=json.dumps({"query" : "MATCH (r) RETURN count(r);"}), json=True)

    def _generateOpenSearchResponse(self, neo4jResponse, searchText, searchUrl, searchParams, pretty):
        pass

    def _constructNeo4jQuery(self, startIndex, entriesPerPage, parameters, facets):
        pass

