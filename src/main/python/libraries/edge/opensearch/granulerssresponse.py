import urllib
from edge.opensearch.rssresponsebysolr import RssResponseBySolr
from edge.dateutility import DateUtility

class GranuleRssResponse(RssResponseBySolr):
    def __init__(self, linkToGranule, host, url):
        super(GranuleRssResponse, self).__init__()

        self.linkToGranule = linkToGranule.split(',')
        self.host = host
        self.url = url

    def _populateChannel(self, solrResponse):
        self.variables.append({'namespace':'atom', 'name': 'link', 'attribute': {'href': self.url+self.searchBasePath+'podaac-dataset-osd.xml', 'rel': 'search', 'type': 'application/opensearchdescription+xml' }})

    def _populateItem(self, solrResponse, doc, item):
        item.append({'name': 'title', 'value': doc['Granule-Name'][0]})
        item.append({'name': 'description', 'value': doc['Granule-Name'][0]})
        #item.append({'name': 'description', 'value': doc['Dataset-Description'][0]})
        #item.append({'name': 'link', 'value': self.portalUrl+'/'+doc['Dataset-ShortName'][0]})
        
        updated = None
        startTime = None
        if 'Granule-StartTimeLong' in doc and doc['Granule-StartTimeLong'][0] != '':
            updated = DateUtility.convertTimeLongToIso(doc['Granule-StartTimeLong'][0])
            startTime = updated
        else:
            updated = datetime.datetime.utcnow().isoformat()+'Z'
        
        item.append({'name': 'pubDate', 'value': updated})
        item.append({'name': 'guid', 'value': doc['Dataset-PersistentId'][0] + ':' + doc['Granule-Name'][0]})
        
        link = self._getLinkToGranule(doc)
        if link is not None:
            item.append({'name': 'link', 'value': link})
        
        parameters = {'datasetId': doc['Dataset-PersistentId'][0], 'granuleName': doc['Granule-Name'][0]}
        parameters['full'] = 'true'
        parameters['format'] = 'rss'
        item.append({'name': 'enclosure', 'attribute': {'url': self.url+self.searchBasePath + 'granule?' + urllib.urlencode(parameters), 'type': 'application/rss+xml', 'length': '0'}})
        del parameters['full']
        parameters['format'] = 'iso'
        item.append({'name': 'enclosure', 'attribute': {'url': self.url+self.metadataBasePath + 'granule?' +  urllib.urlencode(parameters), 'type': 'text/xml', 'length': '0'}})
        parameters['format'] = 'fgdc'
        item.append({'name': 'enclosure', 'attribute': {'url': self.url+self.metadataBasePath + 'granule?' +  urllib.urlencode(parameters), 'type': 'text/xml', 'length': '0'}})
        
        if 'GranuleReference-Type' in doc:
            if 'Granule-DataFormat' in doc:
                type = 'application/x-' + doc['Granule-DataFormat'][0].lower()
            else:
                type = 'text/plain'
            #Look for ONLINE reference only
            granuleRefDict = dict([(doc['GranuleReference-Type'][i], doc['GranuleReference-Path'][i]) for i,x in enumerate(doc['GranuleReference-Status']) if x=="ONLINE"])
            if 'LOCAL-OPENDAP' in granuleRefDict:
                item.append({'name': 'enclosure', 'attribute': {'url': granuleRefDict['LOCAL-OPENDAP'], 'type': 'text/html', 'length': '0'}})
            elif 'REMOTE-OPENDAP' in granuleRefDict:
                item.append({'name': 'enclosure', 'attribute': {'url': granuleRefDict['REMOTE-OPENDAP'], 'type': 'text/html', 'length': '0'}})
            if 'LOCAL-FTP' in granuleRefDict:
                item.append({'name': 'enclosure', 'attribute': {'url': granuleRefDict['LOCAL-FTP'], 'type': type, 'length': '0'}})
            elif 'REMOTE-FTP' in granuleRefDict:
                item.append({'name': 'enclosure', 'attribute': {'url': granuleRefDict['REMOTE-FTP'], 'type': type, 'length': '0'}})

        item.append({'namespace': 'podaac', 'name': 'datasetId', 'value': doc['Dataset-PersistentId'][0]})
        item.append({'namespace': 'podaac', 'name': 'shortName', 'value': doc['Dataset-ShortName'][0]})
        
        if 'GranuleSpatial-NorthLat' in doc and 'GranuleSpatial-EastLon' in doc and 'GranuleSpatial-SouthLat' in doc and 'GranuleSpatial-WestLon' in doc:
            item.append({'namespace': 'georss', 'name': 'where', 'value': {'namespace': 'gml', 'name': 'Envelope', 'value': [{'namespace': 'gml', 'name': 'lowerCorner', 'value': ' '.join([doc['GranuleSpatial-WestLon'][0], doc['GranuleSpatial-SouthLat'][0]])}, {'namespace': 'gml', 'name': 'upperCorner', 'value': ' '.join([doc['GranuleSpatial-EastLon'][0], doc['GranuleSpatial-NorthLat'][0]])}]}})
        
        if 'Granule-StartTimeLong' in doc and doc['Granule-StartTimeLong'][0] != '':
            item.append({'namespace': 'time', 'name': 'start', 'value': DateUtility.convertTimeLongToIso(doc['Granule-StartTimeLong'][0])})

        if 'Granule-StopTimeLong' in doc and doc['Granule-StopTimeLong'][0] != '':
            item.append({'namespace': 'time', 'name': 'end', 'value': DateUtility.convertTimeLongToIso(doc['Granule-StopTimeLong'][0])})

        if 'full' in self.parameters and self.parameters['full']:
            multiValuedElementsKeys = ('GranuleArchive-', 'GranuleReference-')
            self._populateItemWithPodaacMetadata(doc, item, multiValuedElementsKeys)

    def _getLinkToGranule(self, doc):
        link = None

        if 'GranuleReference-Type' in doc and len(self.linkToGranule) > 0:
            granuleRefDict = dict(zip(doc['GranuleReference-Type'], zip(doc['GranuleReference-Path'], doc['GranuleReference-Status'])))

            for type in self.linkToGranule:
                # check if reference type exists
                if type in granuleRefDict:
                    # check if reference is online
                    if granuleRefDict[type][1] == 'ONLINE':
                        link = granuleRefDict[type][0]
                        break
        else:
            #No link to granule download provided so create link back to opensearch to retrieve granule metadata
            link = "http://" + self.host + "/granule/opensearch.rss?granule=" + doc['Granule-Name'][0]

        return link
