import urllib
from edge.opensearch.rssresponsebysolr import RssResponseBySolr
from edge.dateutility import DateUtility

class DatasetRssResponse(RssResponseBySolr):
    def __init__(self, portalUrl, url, datasets):
        super(DatasetRssResponse, self).__init__()
        self.portalUrl = portalUrl
        self.url = url
        self.datasets = datasets

    def _populateChannel(self, solrResponse):
        self.variables.append({'namespace': 'atom', 'name': 'link', 'attribute': {'href': self.url+self.searchBasePath+'podaac-granule-osd.xml', 'rel': 'search', 'type': 'application/opensearchdescription+xml' }})

    def _populateItem(self, solrResponse, doc, item):
        persistentId = doc['Dataset-PersistentId'][0]
        idTuple = ('datasetId', persistentId)
        if persistentId == '':
            idTuple = ('shortName', doc['Dataset-ShortName'][0])
        portalUrl = ""
        if doc['DatasetPolicy-ViewOnline'][0] == 'Y' and doc['DatasetPolicy-AccessType-Full'][0] in ['OPEN', 'PREVIEW', 'SIMULATED', 'REMOTE']:
            portalUrl = self.portalUrl+'/'+doc['Dataset-ShortName'][0]
            item.append({'name': 'enclosure', 'attribute': {'url': portalUrl, 'type': 'text/html', 'length': '0'}})
        item.append({'name': 'title', 'value': doc['Dataset-LongName'][0]})
        item.append({'name': 'description', 'value': doc['Dataset-Description'][0]})
        item.append({'name': 'link', 'value': portalUrl})
        
        item.append({'name': 'enclosure', 'attribute': {'url': self.url + self.searchBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('full', 'true'), ('format', 'rss')])), 'type': 'application/rss+xml', 'length': '0'}})
        item.append({'name': 'enclosure', 'attribute': {'url': self.url + self.metadataBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('format', 'iso')])), 'type': 'text/xml', 'length': '0'}})
        item.append({'name': 'enclosure', 'attribute': {'url': self.url + self.metadataBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('format', 'gcmd')])), 'type': 'text/xml', 'length': '0'}})
        
        #Only generate granule search link if dataset has granules
        if (doc['Dataset-ShortName'][0] in self.datasets):
            supportedGranuleParams = dict([(key,value) for key,value in self.parameters.iteritems() if key in ['bbox', 'startTime', 'endTime', 'format']])
            if persistentId == '':
                supportedGranuleParams['shortName'] = doc['Dataset-ShortName'][0]
            else:
                supportedGranuleParams['datasetId'] = persistentId
            item.append({'name': 'enclosure', 'attribute': {'url': self.url + self.searchBasePath + 'granule?' + urllib.urlencode(supportedGranuleParams), 'type': 'application/rss+xml', 'length': '0'}})
        
        if 'Dataset-ImageUrl' in doc and doc['Dataset-ImageUrl'][0] != '':
            item.append({'name': 'enclosure', 'attribute': {'url': doc['Dataset-ImageUrl'][0], 'type': 'image/jpg', 'length': '0'}})
        
        if 'DatasetLocationPolicy-Type' in doc and 'DatasetLocationPolicy-BasePath' in doc:
            url = dict(zip(doc['DatasetLocationPolicy-Type'], doc['DatasetLocationPolicy-BasePath']))
            if 'LOCAL-OPENDAP' in url:
                item.append({'name': 'enclosure', 'attribute': {'url': url['LOCAL-OPENDAP'], 'type': 'text/html', 'length': '0'}})
            elif 'REMOTE-OPENDAP' in url:
                item.append({'name': 'enclosure', 'attribute': {'url': url['REMOTE-OPENDAP'], 'type': 'text/html', 'length': '0'}})
            if 'LOCAL-FTP' in url:
                item.append({'name': 'enclosure', 'attribute': {'url': url['LOCAL-FTP'], 'type': 'text/plain', 'length': '0'}})
            elif 'REMOTE-FTP' in url:
                item.append({'name': 'enclosure', 'attribute': {'url': url['REMOTE-FTP'], 'type': 'text/plain', 'length': '0'}})
                
        updated = None
        if 'DatasetMetaHistory-LastRevisionDateLong' in doc and doc['DatasetMetaHistory-LastRevisionDateLong'][0] != '':
            updated = DateUtility.convertTimeLongToIso(doc['DatasetMetaHistory-LastRevisionDateLong'][0])
        else:
            updated = datetime.datetime.utcnow().isoformat()+'Z'
        
        item.append({'name': 'pubDate', 'value': updated})
        item.append({'name': 'guid', 'value': persistentId})
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
