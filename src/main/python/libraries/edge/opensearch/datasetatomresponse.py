import datetime
import urllib

from edge.opensearch.atomresponsebysolr import AtomResponseBySolr
from edge.dateutility import DateUtility

class DatasetAtomResponse(AtomResponseBySolr):
    def __init__(self, portalUrl, host, url, datasets):
        super(DatasetAtomResponse, self).__init__()
        self.portalUrl = portalUrl
        self.host = host
        self.url = url
        self.datasets = datasets

    def _populateChannel(self, solrResponse):
        self.variables.append({'name': 'link', 'attribute': {'href': self.url+self.searchBasePath+'podaac-granule-osd.xml', 'rel': 'search', 'type': 'application/opensearchdescription+xml' }})

    def _populateItem(self, solrResponse, doc, item):
        persistentId = doc['Dataset-PersistentId'][0]
        idTuple = ('datasetId', persistentId)
        if persistentId == '':
            idTuple = ('shortName', doc['Dataset-ShortName'][0])
        item.append({'name': 'title', 'value': doc['Dataset-LongName'][0]})
        item.append({'name': 'content', 'value': doc['Dataset-Description'][0]})
        
        item.append({'name': 'link', 'attribute': {'href': self.url + self.searchBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('full', 'true')])), 'rel': 'enclosure', 'type': 'application/atom+xml', 'title': 'PO.DAAC Metadata' }})
        item.append({'name': 'link', 'attribute': {'href': self.url + self.metadataBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('format', 'iso')])), 'rel': 'enclosure', 'type': 'text/xml', 'title': 'ISO-19115 Metadata' }})
        item.append({'name': 'link', 'attribute': {'href': self.url + self.metadataBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('format', 'gcmd')])), 'rel': 'enclosure', 'type': 'text/xml', 'title': 'GCMD Metadata' }})
        
        #Only generate granule search link if dataset has granules
        if (doc['Dataset-ShortName'][0] in self.datasets):
            supportedGranuleParams = dict([(key,value) for key,value in self.parameters.iteritems() if key in ['bbox', 'startTime', 'endTime']])
            if persistentId == '':
                supportedGranuleParams['shortName'] = doc['Dataset-ShortName'][0]
            else:
                supportedGranuleParams['datasetId'] = persistentId
            item.append({'name': 'link', 'attribute': {'href': self.url + self.searchBasePath + 'granule?' + urllib.urlencode(supportedGranuleParams), 'rel': 'search', 'type': 'application/atom+xml', 'title': 'Granule Search' }})
        
        if 'Dataset-ImageUrl' in doc and doc['Dataset-ImageUrl'][0] != '':
            item.append({'name': 'link', 'attribute': {'href': doc['Dataset-ImageUrl'][0], 'rel': 'enclosure', 'type': 'image/jpg', 'title': 'Thumbnail' }})
        
        if 'DatasetLocationPolicy-Type' in doc and 'DatasetLocationPolicy-BasePath' in doc:
            url = dict(zip(doc['DatasetLocationPolicy-Type'], doc['DatasetLocationPolicy-BasePath']))
            if 'LOCAL-OPENDAP' in url:
                item.append({'name': 'link', 'attribute': {'href': url['LOCAL-OPENDAP'], 'rel': 'enclosure', 'type': 'text/html', 'title': 'OPeNDAP URL' }})
            elif 'REMOTE-OPENDAP' in url:
                item.append({'name': 'link', 'attribute': {'href': url['REMOTE-OPENDAP'], 'rel': 'enclosure', 'type': 'text/html', 'title': 'OPeNDAP URL' }})
            if 'LOCAL-FTP' in url:
                item.append({'name': 'link', 'attribute': {'href': url['LOCAL-FTP'], 'rel': 'enclosure', 'type': 'text/plain', 'title': 'FTP URL' }})
            elif 'REMOTE-FTP' in url:
                item.append({'name': 'link', 'attribute': {'href': url['REMOTE-FTP'], 'rel': 'enclosure', 'type': 'text/plain', 'title': 'FTP URL' }})
        if doc['DatasetPolicy-ViewOnline'][0] == 'Y' and doc['DatasetPolicy-AccessType-Full'][0] in ['OPEN', 'PREVIEW', 'SIMULATED', 'REMOTE']:
            portalUrl = self.portalUrl+'/'+doc['Dataset-ShortName'][0]
            item.append({'name': 'link', 'attribute': {'href': portalUrl, 'rel': 'enclosure', 'type': 'text/html', 'title': 'Dataset Information' }})
        updated = None
        if 'DatasetMetaHistory-LastRevisionDateLong' in doc and doc['DatasetMetaHistory-LastRevisionDateLong'][0] != '':
            updated = DateUtility.convertTimeLongToIso(doc['DatasetMetaHistory-LastRevisionDateLong'][0])
        else:
            updated = datetime.datetime.utcnow().isoformat()+'Z'
        
        item.append({'name': 'updated', 'value': updated})
        item.append({'name': 'id', 'value': persistentId})
        item.append({'namespace': 'podaac', 'name': 'datasetId', 'value': doc['Dataset-PersistentId'][0]})
        item.append({'namespace': 'podaac', 'name': 'shortName', 'value': doc['Dataset-ShortName'][0]})
        
        if doc['DatasetCoverage-WestLon'][0] != '' and doc['DatasetCoverage-SouthLat'][0] != '' and  doc['DatasetCoverage-EastLon'][0] != '' and  doc['DatasetCoverage-NorthLat'][0] != '':
            item.append({'namespace': 'georss', 'name': 'where', 'value': {'namespace': 'gml', 'name': 'Envelope', 'value': [{'namespace': 'gml', 'name': 'lowerCorner', 'value': ' '.join([doc['DatasetCoverage-WestLon'][0], doc['DatasetCoverage-SouthLat'][0]]) }, {'namespace': 'gml', 'name': 'upperCorner', 'value': ' '.join([doc['DatasetCoverage-EastLon'][0], doc['DatasetCoverage-NorthLat'][0]])}]}})
        
        if 'DatasetCoverage-StartTimeLong' in doc and doc['DatasetCoverage-StartTimeLong'][0] != '':
            item.append({'namespace': 'time', 'name': 'start', 'value': DateUtility.convertTimeLongToIso(doc['DatasetCoverage-StartTimeLong'][0])})
        
        if 'DatasetCoverage-StopTimeLong' in doc and doc['DatasetCoverage-StopTimeLong'][0] != '':
            item.append({'namespace': 'time', 'name': 'end', 'value': DateUtility.convertTimeLongToIso(doc['DatasetCoverage-StopTimeLong'][0])})
        
        if 'full' in self.parameters and self.parameters['full']:
            if 'DatasetLocationPolicy-Type' in doc and 'DatasetLocationPolicy-BasePath' in doc:
                for i, x in enumerate(doc['DatasetLocationPolicy-Type']):
                    item.append({'namespace': 'podaac', 'name': self._camelCaseStripHyphen(x.title()), 'value': doc['DatasetLocationPolicy-BasePath'][i]})
                del doc['DatasetLocationPolicy-Type']
                del doc['DatasetLocationPolicy-BasePath']
            
            multiValuedElementsKeys = ('DatasetRegion-', 'DatasetCharacter-', 'DatasetCitation-', 'DatasetContact-Contact-', 'DatasetDatetime-', 
                                       'DatasetInteger-', 'DatasetParameter-', 'DatasetProject-', 'DatasetReal-', 'DatasetResource-', 
                                       'DatasetSoftware-', 'DatasetSource-', 'DatasetVersion-', 'Collection-')
            self._populateItemWithPodaacMetadata(doc, item, multiValuedElementsKeys)
