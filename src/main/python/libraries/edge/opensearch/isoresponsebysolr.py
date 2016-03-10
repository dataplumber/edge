import json
import logging

from edge.opensearch.isoresponse import IsoResponse
from datetime import date, datetime

class IsoResponseBySolr(IsoResponse):
    def __init__(self):
        super(IsoResponseBySolr, self).__init__()

    def generate(self, solrDatasetResponse, solrGranuleResponse = None, pretty=False):
        self._populate(solrDatasetResponse, solrGranuleResponse)
        return super(IsoResponseBySolr, self).generate(pretty)

    def _populate(self, solrDatasetResponse, solrGranuleResponse = None):
        if solrDatasetResponse is not None:
            solrJson = json.loads(solrDatasetResponse)

            logging.debug('dataset count: '+str(len(solrJson['response']['docs'])))

            if len(solrJson['response']['docs']) == 1:
                # ok now populate variables!
                doc = solrJson['response']['docs'][0]

                #self.variables['Dataset_ShortName'] = doc['Dataset-ShortName'][0]
                #self.variables['Dataset_ShortName'] = u'unko'
                
                self.variables['doc'] = doc
                
                # Format dates
                try:
                    self.variables['DatasetCitation_ReleaseDate'] = date.fromtimestamp(float(doc['DatasetCitation-ReleaseDateLong'][0]) / 1000).strftime('%Y%m%d')
                    self.variables['DatasetCoverage_StartTime'] = self._convertTimeLongToISO(doc['DatasetCoverage-StartTimeLong'][0])
                    self.variables['DatasetCoverage_StopTime'] = self._convertTimeLongToISO(doc['DatasetCoverage-StopTimeLong'][0])
                except:
                    pass
                
                try:
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
                    
                    # Replace all none, None values with empty string
                    doc['DatasetParameter-VariableDetail'] = [self._filterString(variableDetail) for variableDetail in doc['DatasetParameter-VariableDetail']]
                    
                    # Current date
                    self.variables['DateStamp'] = datetime.utcnow().strftime('%Y%m%d')
                    
                    # Data format version
                    self.variables['DatasetPolicy_DataFormat_Version'] = self._getDataFormatVersion(doc['DatasetPolicy-DataFormat'][0])
                except Exception as e:
                    logging.debug("Problem generating ISO " + str(e))
                    del self.variables['doc']
                
                if solrGranuleResponse is not None:
                    solrGranuleJson = json.loads(solrGranuleResponse)
                    
                    logging.debug('granule count: '+str(len(solrGranuleJson['response']['docs'])))
                    
                    for doc in solrGranuleJson['response']['docs']:
                        self._populateItem(solrGranuleResponse, doc, None)
                        
                        doc['Granule-StartTimeLong'][0] = self._convertTimeLongToISO(doc['Granule-StartTimeLong'][0])
                        doc['Granule-StopTimeLong'][0] = self._convertTimeLongToISO(doc['Granule-StopTimeLong'][0])
                        doc['Granule-ArchiveTimeLong'][0] = self._convertTimeLongToISO(doc['Granule-ArchiveTimeLong'][0])
                        doc['Granule-CreateTimeLong'][0] = self._convertTimeLongToISO(doc['Granule-CreateTimeLong'][0])
                        
                        # Create dictionary for bounding box extent
                        '''
                        if ('GranuleReal-Value' in doc and 'GranuleReal-DatasetElement-Element-ShortName' in doc):
                            self.variables['GranuleBoundingBox'] = dict(zip(doc['GranuleReal-DatasetElement-Element-ShortName'], doc['GranuleReal-Value']))
                        '''
                        if 'GranuleSpatial-NorthLat' in doc and 'GranuleSpatial-EastLon' in doc and 'GranuleSpatial-SouthLat' in doc and 'GranuleSpatial-WestLon' in doc:
                            self.variables['GranuleBoundingBox'] = dict([('southernmostLatitude', doc['GranuleSpatial-SouthLat'][0]), 
                                                              ('northernmostLatitude', doc['GranuleSpatial-NorthLat'][0]),
                                                              ('westernmostLongitude', doc['GranuleSpatial-WestLon'][0]),
                                                              ('easternmostLongitude', doc['GranuleSpatial-EastLon'][0])])
                        break
                        
                    self.variables['granules'] = solrGranuleJson['response']['docs']
                
    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
    
    def _convertTimeLongToISO(self, time):
        isoTime = ''
        try:
            isoTime = datetime.utcfromtimestamp(float(time) / 1000).isoformat() + 'Z'
        except ValueError:
            pass
        return isoTime
    
    def _filterString(self, str):
        if str.lower() == 'none':
            return ''
        else:
            return str
    
    def _getDataFormatVersion(self, dataFormat):
        version = ''
        if dataFormat == 'NETCDF':
            version = 3
        elif dataFormat == 'HDF':
            version = 4
        else:
            try:
                version = int(dataFormat[-1])
            except:
                pass
        return version
