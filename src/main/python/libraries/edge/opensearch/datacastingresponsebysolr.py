import json
import logging

from edge.opensearch.fgdcresponse import FgdcResponse
from edge.dateutility import DateUtility

class DatacastingResponseBySolr(FgdcResponse):
    def __init__(self, portalUrl, archivedWithin):
        super(DatacastingResponseBySolr, self).__init__()
        
        self.addNamespace("datacasting", "http://datacasting.jpl.nasa.gov/datacasting")
        self.addNamespace("georss", "http://www.georss.org/georss")
        self.addNamespace("gml", "http://www.opengis.net/gml")
        
        self.portalUrl = portalUrl
        self.archivedWithin = archivedWithin

    def generate(self, solrDatasetResponse, solrGranuleResponse = None, pretty=False):
        self._populate(solrDatasetResponse, solrGranuleResponse)
        return super(DatacastingResponseBySolr, self).generate(pretty)

    def _populate(self, solrDatasetResponse, solrGranuleResponse = None):
        if solrDatasetResponse is not None:
            solrJson = json.loads(solrDatasetResponse)

            logging.debug('dataset count: '+str(len(solrJson['response']['docs'])))

            if len(solrJson['response']['docs']) == 1:
                # ok now populate variables!
                doc = solrJson['response']['docs'][0]
                
                self.variables['doc'] = doc
                
                # Format dates
                try:
                    self.variables['DatasetCitation_ReleaseYear'] = DateUtility.convertTimeLong(doc['DatasetCitation-ReleaseDateLong'][0], '%Y')
                except:
                    pass
                
                # Link to dataset portal page
                self.variables['DatasetPortalPage'] = self.portalUrl+'/'+doc['Dataset-ShortName'][0]
                
                # Set default pub date to x hours ago because we cast all granules archived within the last x hours
                self.variables['PubDate'] = DateUtility.pastDateRFC822(self.archivedWithin)
            else:
                raise Exception('No dataset found')
                
        if solrGranuleResponse is not None:
            solrGranuleJson = json.loads(solrGranuleResponse)
            
            logging.debug('granule count: '+str(len(solrGranuleJson['response']['docs'])))
            
            pubDate = 0
            for doc in solrGranuleJson['response']['docs']:
                if (doc['Granule-ArchiveTimeLong'][0] > pubDate):
                    pubDate = doc['Granule-ArchiveTimeLong'][0]
                self._populateItem(solrGranuleResponse, doc, None)
            
            if pubDate != 0:
                # Set pub date to latest granule archive date
                self.variables['PubDate'] = DateUtility.convertTimeLongToRFC822(pubDate)
                
            self.variables['granules'] = solrGranuleJson['response']['docs']
        else:
            raise Exception('No granules found')
                
    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
