import json
import logging

from edge.opensearch.isoresponse import IsoResponse
from datetime import date, datetime

class GcmdResponseBySolr(IsoResponse):
    def __init__(self, configuration):
        super(GcmdResponseBySolr, self).__init__()
        self._configuration = configuration

    def generate(self, solrResponse, pretty=False, allowNone=False):
        self._populate(solrResponse, allowNone)
        return super(GcmdResponseBySolr, self).generate(pretty)

    def _populate(self, solrResponse, allowNone):
        if solrResponse is not None:
            solrJson = json.loads(solrResponse)

            logging.debug('dataset count: '+str(len(solrJson['response']['docs'])))

            if len(solrJson['response']['docs']) == 1:
                # ok now populate variables!
                doc = solrJson['response']['docs'][0]

                #self.variables['Dataset_ShortName'] = doc['Dataset-ShortName'][0]
                #self.variables['Dataset_ShortName'] = u'unko'
                
                #Filter response from solr, if value contains none, N/A, null set to empty string
                if not allowNone:
                    for key, value in doc.iteritems():
                        if key not in ['DatasetPolicy-AccessConstraint', 'DatasetPolicy-UseConstraint'] and isinstance(value[0], basestring) and len(value[0].strip()) <= 4 and value[0].strip().lower() in ['none', 'na', 'n/a', 'null']:
                            doc[key][0] = ""
                
                self.variables['doc'] = doc
                
                # Entry_ID
                self.variables['Entry_ID'] = doc['Dataset-PersistentId'][0] if doc['Dataset-PersistentId'][0] != "" else doc['Dataset-ShortName'][0]
                
                # Entry_Title
                self.variables['Entry_Title'] = doc['Dataset-LongName'][0]
                
                # Dataset_Citation
                datasetCitationCol = ['Dataset_Creator', 'Dataset_Title', 'Dataset_Series_Name', 'Dataset_Release_Date', 'Dataset_Release_Place', 'Dataset_Publisher', 'Version', 'Other_Citation_Details', 'Online_Resource']
                if 'DatasetCitation-Creator' in doc:
                    for i, x in enumerate(doc['DatasetCitation-ReleaseDateLong']):
                        try:
                            doc['DatasetCitation-ReleaseDateLong'][i] = datetime.utcfromtimestamp(float(x) / 1000).strftime('%Y-%m-%d')
                        except:
                            pass
                    self.variables['Dataset_Citation'] = [dict(zip(datasetCitationCol,x)) for x in zip(doc['DatasetCitation-Creator'], doc['DatasetCitation-Title'], doc['DatasetCitation-SeriesName'], doc['DatasetCitation-ReleaseDateLong'], doc['DatasetCitation-ReleasePlace'], doc['DatasetCitation-Publisher'], doc['DatasetCitation-Version'], doc['DatasetCitation-CitationDetail'], doc['DatasetCitation-OnlineResource'])]
                
                # Personnel
                datasetPersonnelCol = ['Role', 'First_Name', 'Middle_Name', 'Last_Name', 'Email', 'Phone', 'Fax', 'Provider_Short_Name']
                if 'DatasetContact-Contact-Role' in doc:
                    self.variables['Personnel'] = [dict(zip(datasetPersonnelCol, x)) for x in zip(doc['DatasetContact-Contact-Role'], doc['DatasetContact-Contact-FirstName'], doc['DatasetContact-Contact-MiddleName'], doc['DatasetContact-Contact-LastName'], doc['DatasetContact-Contact-Email'], doc['DatasetContact-Contact-Phone'], doc['DatasetContact-Contact-Fax'], doc['DatasetContact-Contact-Provider-ShortName'])]
                
                # Locate dataset provider contact
                self.variables['Provider_Personnel'] = next((item for item in self.variables['Personnel'] if item["Provider_Short_Name"] == doc['Dataset-Provider-ShortName'][0]), None)
                
                # Parameter
                datasetParameterCol = ['Category', 'Topic', 'Term', 'Variable_Level_1', 'Detailed_Variable']
                if 'DatasetParameter-Category' in doc:
                    # Replace all none, None values with empty string
                    doc['DatasetParameter-VariableDetail'] = [self._filterString(variableDetail) for variableDetail in doc['DatasetParameter-VariableDetail']]
                    self.variables['Parameters'] = [dict(zip(datasetParameterCol, x)) for x in zip(doc['DatasetParameter-Category'], doc['DatasetParameter-Topic'], doc['DatasetParameter-Term'], doc['DatasetParameter-Variable'], doc['DatasetParameter-VariableDetail'])]
                
                # Format dates
                try:
                    self.variables['Start_Date'] = datetime.utcfromtimestamp(float(doc['DatasetCoverage-StartTimeLong'][0]) / 1000).strftime('%Y-%m-%d')
                    self.variables['Stop_Date'] = datetime.utcfromtimestamp(float(doc['DatasetCoverage-StopTimeLong'][0]) / 1000).strftime('%Y-%m-%d')
                except:
                    pass
                
                
                # Project
                projectCol = ['Short_Name', 'Long_Name']
                if 'DatasetProject-Project-ShortName' in doc:
                    self.variables['Project'] = [dict(zip(projectCol, x)) for x in zip(doc['DatasetProject-Project-ShortName'], doc['DatasetProject-Project-LongName'])]
                
                # Create list of unique dataset sensor
                self.variables['UniqueDatasetSensor'] = {}
                if 'DatasetSource-Sensor-ShortName' in doc:
                    for i, x in enumerate(doc['DatasetSource-Sensor-ShortName']):
                        self.variables['UniqueDatasetSensor'][x] = i
                    self.variables['UniqueDatasetSensor'] = self.variables['UniqueDatasetSensor'].values()
                
                # Create list of unique dataset source
                self.variables['UniqueDatasetSource'] = {}
                if 'DatasetSource-Source-ShortName' in doc:
                    for i, x in enumerate(doc['DatasetSource-Source-ShortName']):
                        self.variables['UniqueDatasetSource'][x] = i
                    self.variables['UniqueDatasetSource'] = self.variables['UniqueDatasetSource'].values()
                
                # Last_DIF_Revision_Date
                self.variables['Last_DIF_Revision_Date'] = datetime.utcfromtimestamp(float(doc['DatasetMetaHistory-LastRevisionDateLong'][0]) / 1000).strftime('%Y-%m-%d')
                
                # DIF_Revision_History
                self.variables['DIF_Revision_History'] = doc['DatasetMetaHistory-RevisionHistory'][0]
                
                
                
                # DIF_Creation_Date
                self.variables['DIF_Creation_Date'] = datetime.utcnow().strftime('%Y-%m-%d')
                
                # Set configurable DIF Author contact information
                self.variables['author'] = dict(self._configuration.items('author'))

                # Set configurable PO.DAAC and NODC contact information
                self.variables['podaac'] = dict(self._configuration.items('podaac'))
                self.variables['nodc'] = dict(self._configuration.items('nodc'))
                
    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
    
    def _filterString(self, str):
        if str.lower() == 'none':
            return ''
        else:
            return str
