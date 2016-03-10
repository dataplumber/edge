from types import *
import logging
import urllib

import requestresponder
from edge.httputility import HttpUtility
import math

class ResponseWriter(requestresponder.RequestResponder):
    def __init__(self, configFilePath, requiredParams = None):
        super(ResponseWriter, self).__init__(configFilePath)
        if requiredParams is None:
            requiredParams = []
        self.requiredParams = requiredParams
        self.searchParameters = {}
        self.pretty = True
        self.variables = {}
    
    def get(self, requestHandler):
        super(ResponseWriter, self).get(requestHandler)
        #check required parameters
        for paramList in self.requiredParams:
            countParamNotFound = 0
            for param in paramList:
                try:
                    requestHandler.get_argument(param)
                except:
                    countParamNotFound += 1
            if countParamNotFound == len(paramList):
                raise Exception("One of the following parameters is required: " + ', '.join(paramList))
    
    def _constructSingleSolrDatasetQuery(self, variables):
        queries = []
        for key, value in variables.iteritems():
            # Only key used for ISO granule record is dataset
            if key == 'datasetId':
                query = 'Dataset-PersistentId:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)
            elif key == 'shortName':
                query = 'Dataset-ShortName-Full:'+self._urlEncodeSolrQueryValue(value)
                queries.append(query)

        if len(queries) == 0:
            queries.append('*')

        query = 'q='+'+AND+'.join(queries)+'&fq=DatasetPolicy-AccessType-Full:(OPEN+OR+PREVIEW+OR+SIMULATED+OR+REMOTE)+AND+DatasetPolicy-ViewOnline:Y&version=2.2&rows=1&indent=on&wt=json'
        logging.debug('solr query: '+query)
        
        return query
    
    def _getSingleSolrDatasetResponse(self, variables, callback):
        query = self._constructSingleSolrDatasetQuery(variables)
        url = self._configuration.get('solr', 'datasetUrl')

        httpUtility = HttpUtility()
        return httpUtility.getResponse(url+'/select/?'+query, callback)
    
    def _urlEncodeSolrQueryValue(self, value):
        return urllib.quote('"'+value+'"')
    
    def _constructBoundingBoxQuery(self, value):
        coords = value.split(",")
        if len(coords) < 4:
            return None
        try:
            west = float(coords[0])
            south = float(coords[1])
            east = float(coords[2])
            north = float(coords[3])
            
            centerY = (south + north) / 2
            halfHeight = math.fabs(north - south) / 2
            
            #Check if we need to split box into two
            if (east < west):
                west1 = west
                east1 = 180.0
                
                centerX1 = (west1 + east1) / 2
                halfWidth1 = math.fabs(east1 - west1) / 2
                
                west2 = -180.0
                east2 = east
                
                centerX2 = (west2 + east2) / 2
                halfWidth2 = math.fabs(east2 - west2) / 2
                
                return "fq={!frange+l=1+u=2}map(sum(" + self._solrSeparatingXAxisFunctionQueryAggregate(centerX1, halfWidth1, centerX2, halfWidth2) + "," + self._solrSeparatingYAxisFunctionQuery(centerY, halfHeight) + "),0,0,1,0)&fq=CenterY:*"
            else:
                centerX = (west + east) / 2
                halfWidth = math.fabs(east - west) / 2

                return "fq={!frange+l=1+u=2}map(sum(" + self._solrSeparatingXAxisFunctionQuery(centerX, halfWidth) + "," + self._solrSeparatingYAxisFunctionQuery(centerY, halfHeight) + "),0,0,1,0)&fq=CenterY:*"
        except:
            return None

    def _solrSeparatingXAxisFunctionQuery(self, center, width):
        return "map(sum(" + self._solrSeparatingAxixFunction(center, "CenterX1", width, "HalfWidth1", 360) + "," + self._solrSeparatingXAxixFunctionQueryPossibleNullWidth(center, width) + "),0,1,0,1)"

    def _solrSeparatingXAxisFunctionQueryAggregate(self, center1, width1, center2, width2):
        return "map(sum(" + self._solrSeparatingAxixFunction(center1, "CenterX1", width1, "HalfWidth1", 360) + ","+ self._solrSeparatingXAxixFunctionQueryPossibleNullWidth(center1, width1) + "," +self._solrSeparatingAxixFunction(center2, "CenterX1", width2, "HalfWidth1", 360) + "," + self._solrSeparatingXAxixFunctionQueryPossibleNullWidth(center2, width2) +"),0,3,0,1)"
    
    def _solrSeparatingYAxisFunctionQuery(self, center, height):
        return self._solrSeparatingAxixFunction(center, "CenterY", height, "HalfHeight", 180)
    
    def _solrSeparatingAxixFunction(self, center, centerVar, length, lengthVar, span):
        return "map(sub(abs(sub(%.15g,%s)),sum(%.15g,%s)),0,%i,1,0)" % (center, centerVar, length, lengthVar, span)
    
    def _solrSeparatingXAxixFunctionQueryPossibleNullWidth(self, center, length):
        return "map(sum(map(HalfWidth2,0,0,1,0),map(sub(abs(sub(%.15g,CenterX2)),sum(%.15g,HalfWidth2)),0,360,1,0)),0,0,0,1)" % (center, length)

    def _generateOpenSearchResponse(self, solrResponse, searchText, searchUrl, searchParams, pretty):
        pass
    
    def _onSolrResponse(self, response):
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
            self.requestHandler.set_header("Content-Type", "application/xml")
            self.requestHandler.write(openSearchResponse)
            self.requestHandler.finish()
        except BaseException as exception:
            self._handleException(str(exception))
    
    def _handleException(self, error):
        self.requestHandler.set_status(404)
        self.requestHandler.write(error)
        self.requestHandler.finish()
