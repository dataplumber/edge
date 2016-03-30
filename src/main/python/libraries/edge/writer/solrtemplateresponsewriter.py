from types import *
import logging
import urllib
import json
from collections import OrderedDict

from edge.httputility import HttpUtility
from edge.writer.templateresponsewriter import TemplateResponseWriter

class SolrTemplateResponseWriter(TemplateResponseWriter):
    def __init__(self, configFilePath, requiredParams = None):
        super(SolrTemplateResponseWriter, self).__init__(configFilePath, requiredParams)
        self.searchParameters = {}
        self.variables = {}
        self.facet = False
        self.facetDefs = {}
        self.contentType = 'application/xml'

    def get(self, requestHandler):
        super(SolrTemplateResponseWriter, self).get(requestHandler)

        startIndex = 0
        try:
            startIndex = requestHandler.get_argument('startIndex')
        except:
            pass

        entriesPerPage = self._configuration.getint('solr', 'entriesPerPage')
        try:
            entriesPerPage = requestHandler.get_argument('itemsPerPage')
            maxEntriesPerPage = self._configuration.getint('solr', 'maxEntriesPerPage')
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
        for parameter in self._configuration.get('solr', 'parameters').split(','):
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
        if self._configuration.has_option('solr', 'facets'):
            self.facetDefs = json.loads(self._configuration.get('solr', 'facets'), object_pairs_hook=OrderedDict)
            for facet in self.facetDefs.keys():
                try:
                    value = requestHandler.get_arguments(facet)
                    if len(value) > 0:
                        facets[self.facetDefs[facet]] = value
                        self.searchParameters[facet] = value
                except:
                    pass

        try:
            self._getSolrResponse(startIndex, entriesPerPage, parameters, facets)
        except:
            logging.exception('Failed to get solr response.')

    def _urlEncodeSolrQueryValue(self, value):
        return urllib.quote('"'+value+'"')

    def _onSolrResponse(self, response):
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

    def _getSolrResponse(self, startIndex, entriesPerPage, parameters, facets):
        query = self._constructSolrQuery(startIndex, entriesPerPage, parameters, facets)
        url = self._configuration.get('solr', 'datasetUrl')

        httpUtility = HttpUtility()
        httpUtility.getResponse(url+'/select/?'+query, self._onSolrResponse)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        pass

    def _constructSolrQuery(self, startIndex, entriesPerPage, parameters, facets):
        pass
