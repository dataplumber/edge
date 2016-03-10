import json
import logging

from edge.opensearch.fgdcresponse import FgdcResponse
from datetime import datetime

class FgdcResponseBySolr(FgdcResponse):
    def __init__(self):
        super(FgdcResponseBySolr, self).__init__()

    def generate(self, solrDatasetResponse, solrGranuleResponse = None, pretty=False):
        self._populate(solrDatasetResponse, solrGranuleResponse)
        return super(FgdcResponseBySolr, self).generate(pretty, "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n<!DOCTYPE metadata SYSTEM \"http://www.fgdc.gov/metadata/fgdc-std-001-1998.dtd\">\n")

    def _populate(self, solrDatasetResponse, solrGranuleResponse = None):
        if solrDatasetResponse is not None:
            solrJson = json.loads(solrDatasetResponse)

            logging.debug('dataset count: '+str(len(solrJson['response']['docs'])))

            if len(solrJson['response']['docs']) == 1:
                # ok now populate variables!
                doc = solrJson['response']['docs'][0]
                
                self.variables['doc'] = doc
                
                # Round spatial to 3 decimal places
                doc['DatasetCoverage-WestLon'][0] = '%.3f' % round(float(doc['DatasetCoverage-WestLon'][0]), 3)
                doc['DatasetCoverage-EastLon'][0] = '%.3f' % round(float(doc['DatasetCoverage-EastLon'][0]), 3)
                doc['DatasetCoverage-NorthLat'][0] = '%.3f' % round(float(doc['DatasetCoverage-NorthLat'][0]), 3)
                doc['DatasetCoverage-SouthLat'][0] = '%.3f' % round(float(doc['DatasetCoverage-SouthLat'][0]), 3)
                
                # Base on the value of Dataset-ProcessingLevel, we query the SOLR differently.
                # For 2 or 2P, we look for these 2 attributes:
                #
                #   ACROSS_TRACK_RESOLUTION           NUMBER
                #   ALONG_TRACK_RESOLUTION            NUMBER
                #
                # Because the units of 2 and 2P products are in meters, we have to convert to decimal degrees.
                #
                # The formula is:
                #
                #    1 degree = 111.16 km or 111160.0 meters 
                # 
                # Calculate latitude and longitude resolution for 2 and 2P products
                if (doc['Dataset-ProcessingLevel'][0] == '2' or doc['Dataset-ProcessingLevel'][0] == '2P'):
                    self.variables['Dataset_LatitudeResolution'] = '%.17f' % round(float(doc['Dataset-AlongTrackResolution'][0]) / 111160.0, 17)
                    self.variables['Dataset_LongitudeResolution'] = '%.17f' % round(float(doc['Dataset-AcrossTrackResolution'][0]) / 111160.0, 17)
                # For value of Dataset-ProcessingLevel of 3 or 4, we look for different attributes:
                #
                # LATIUDE_RESOLUTION
                # LONGITUDE RESOLUTION
                elif (doc['Dataset-ProcessingLevel'][0] == '3' or doc['Dataset-ProcessingLevel'][0] == '4'):
                    self.variables['Dataset_LatitudeResolution'] = doc['Dataset-LatitudeResolution'][0]
                    self.variables['Dataset_LongitudeResolution'] = doc['Dataset-LongitudeResolution'][0]

                # Format dates
                try:
                    self.variables['DatasetCitation_ReleaseDateTime'] = self._convertTimeLongToString(doc['DatasetCitation-ReleaseDateLong'][0])
                    self.variables['DatasetCitation_ReleaseDate'] = datetime.utcfromtimestamp(float(doc['DatasetCitation-ReleaseDateLong'][0]) / 1000).strftime('%Y%m%d')
                    self.variables['DatasetCitation_ReleaseTime'] = datetime.utcfromtimestamp(float(doc['DatasetCitation-ReleaseDateLong'][0]) / 1000).strftime('%H%M%S')+'Z'
                    self.variables['DatasetCoverage_StartTime'] = self._convertTimeLongToString(doc['DatasetCoverage-StartTimeLong'][0])
                except:
                    pass
                
                # Create list of unique dataset sensor
                self.variables['UniqueDatasetSensor'] = {}
                for i, x in enumerate(doc['DatasetSource-Sensor-ShortName']):
                    self.variables['UniqueDatasetSensor'][x] = i
                self.variables['UniqueDatasetSensor'] = self.variables['UniqueDatasetSensor'].values()
                
                # Create list of unique dataset source
                self.variables['UniqueDatasetSource'] = {}
                for i, x in enumerate(doc['DatasetSource-Source-ShortName']):
                    self.variables['UniqueDatasetSource'][x] = i
                self.variables['UniqueDatasetSource'] = self.variables['UniqueDatasetSource'].values()
                
                # Create dictionary for dataset_resource
                self.variables['DatasetResource'] = dict(zip(doc['DatasetResource-Type'], doc['DatasetResource-Path']))
                
                # Get index of dataset Technical Contact
                self.variables['TechnicalContactIndex'] = -1
                for i, x in enumerate(doc['DatasetContact-Contact-Role']):
                    if (x.upper() == 'TECHNICAL CONTACT'):
                        logging.debug('tech contact is ' + str(i))
                        self.variables['TechnicalContactIndex'] = i
                        break;
                
                if 'Dataset-Provider-ProviderResource-Path' not in doc:
                    doc['Dataset-Provider-ProviderResource-Path'] = ['']
            else:
                raise Exception('No dataset found')
                
        else:
            raise Exception('No dataset found')
        
        if solrGranuleResponse is not None:
            solrGranuleJson = json.loads(solrGranuleResponse)
            
            logging.debug('granule count: '+str(len(solrGranuleJson['response']['docs'])))
            if (len(solrGranuleJson['response']['docs']) == 0):
                raise Exception('No granules found')
            
            for doc in solrGranuleJson['response']['docs']:
                self._populateItem(solrGranuleResponse, doc, None)
                
                doc['Granule-StartTimeLong'][0] = self._convertTimeLongToString(doc['Granule-StartTimeLong'][0])
                doc['Granule-StopTimeLong'][0] = self._convertTimeLongToString(doc['Granule-StopTimeLong'][0])
                
                # Create dictionary for bounding box extent
                '''
                if ('GranuleReal-Value' in doc and 'GranuleReal-DatasetElement-Element-ShortName' in doc):
                    # Round real value to 3 decimal places
                    doc['GranuleReal-Value'] = ['%.3f' % round(float(value), 3) for value in doc['GranuleReal-Value']]
                    doc['GranuleBoundingBox'] = dict(zip(doc['GranuleReal-DatasetElement-Element-ShortName'], doc['GranuleReal-Value']))
                '''
                if 'GranuleSpatial-NorthLat' in doc and 'GranuleSpatial-EastLon' in doc and 'GranuleSpatial-SouthLat' in doc and 'GranuleSpatial-WestLon' in doc:
                    doc['GranuleBoundingBox'] = dict([('southernmostLatitude', '%.3f' % round(float(doc['GranuleSpatial-SouthLat'][0]), 3)), 
                                                      ('northernmostLatitude', '%.3f' % round(float(doc['GranuleSpatial-NorthLat'][0]), 3)),
                                                      ('westernmostLongitude', '%.3f' % round(float(doc['GranuleSpatial-WestLon'][0]), 3)),
                                                      ('easternmostLongitude', '%.3f' % round(float(doc['GranuleSpatial-EastLon'][0]), 3))])
                else:
                    # Encounter granule with no bounding box so raise an exception
                    raise Exception('granule ' + doc['Granule-Name'][0] + ' has no bounding box')
            self.variables['granules'] = solrGranuleJson['response']['docs']
        else:
            raise Exception('No granules found')
                
    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
    
    def _convertTimeLongToString(self, time):
        isoTime = ''
        try:
            isoTime = datetime.utcfromtimestamp(float(time) / 1000).strftime('%Y%m%dT%H%M%SZ')
        except ValueError:
            pass
        return isoTime
