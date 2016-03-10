import datetime
import urllib

from edge.opensearch.atomresponsebysolr import AtomResponseBySolr
from edge.dateutility import DateUtility

class GranuleAtomResponse(AtomResponseBySolr):
    def __init__(self, linkToGranule, host, url):
        super(GranuleAtomResponse, self).__init__()

        self.linkToGranule = linkToGranule.split(',')
        self.host = host
        self.url = url

    def _populateChannel(self, solrResponse):
        self.variables.append({'name': 'link', 'attribute': {'href': self.url+self.searchBasePath+'podaac-dataset-osd.xml', 'rel': 'search', 'type': 'application/opensearchdescription+xml' }})

    def _populateItem(self, solrResponse, doc, item):
        item.append({'name': 'title', 'value': doc['Granule-Name'][0]})
        #item.append({'name': 'content', 'value': doc['Granule-Name'][0]})
        
        updated = None
        startTime = None
        if 'Granule-StartTimeLong' in doc and doc['Granule-StartTimeLong'][0] != '':
            updated = DateUtility.convertTimeLongToIso(doc['Granule-StartTimeLong'][0])
            startTime = updated
        else:
            updated = datetime.datetime.utcnow().isoformat()+'Z'
        
        item.append({'name': 'updated', 'value': updated})
        item.append({'name': 'id', 'value': doc['Dataset-PersistentId'][0] + ':' + doc['Granule-Name'][0]})
        
        parameters = {'datasetId': doc['Dataset-PersistentId'][0], 'granuleName': doc['Granule-Name'][0]}
        parameters['full'] = 'true'
        item.append({'name': 'link', 'attribute': {'href': self.url+self.searchBasePath + 'granule?' + urllib.urlencode(parameters), 'rel': 'enclosure', 'type': 'application/atom+xml', 'title': 'PO.DAAC Metadata' }})
        del parameters['full']
        parameters['format'] = 'iso'
        item.append({'name': 'link', 'attribute': {'href': self.url+self.metadataBasePath + 'granule?' +  urllib.urlencode(parameters), 'rel': 'enclosure', 'type': 'text/xml', 'title': 'ISO-19115 Metadata' }})
        parameters['format'] = 'fgdc'
        item.append({'name': 'link', 'attribute': {'href': self.url+self.metadataBasePath + 'granule?' +  urllib.urlencode(parameters), 'rel': 'enclosure', 'type': 'text/xml', 'title': 'FGDC Metadata' }})
        
        #item.append({'name': 'description', 'value': doc['Dataset-Description'][0]})
        #item.append({'name': 'link', 'value': self.portalUrl+'/'+doc['Dataset-ShortName'][0]})
        #link = self._getLinkToGranule(doc)
        #if link['href'] is not None:
        #    item.append({'name': 'link', 'attribute': link})
        if 'GranuleReference-Type' in doc:
            if 'Granule-DataFormat' in doc:
                type = 'application/x-' + doc['Granule-DataFormat'][0].lower()
            else:
                type = 'text/plain'
            #Look for ONLINE reference only
            granuleRefDict = dict([(doc['GranuleReference-Type'][i], doc['GranuleReference-Path'][i]) for i,x in enumerate(doc['GranuleReference-Status']) if x=="ONLINE"])
            if 'LOCAL-OPENDAP' in granuleRefDict:
                item.append({'name': 'link', 'attribute': {'href': granuleRefDict['LOCAL-OPENDAP'], 'rel': 'enclosure', 'type': 'text/html', 'title': 'OPeNDAP URL' }})
            elif 'REMOTE-OPENDAP' in granuleRefDict:
                item.append({'name': 'link', 'attribute': {'href': granuleRefDict['REMOTE-OPENDAP'], 'rel': 'enclosure', 'type': 'text/html', 'title': 'OPeNDAP URL' }})
            if 'LOCAL-FTP' in granuleRefDict:
                item.append({'name': 'link', 'attribute': {'href': granuleRefDict['LOCAL-FTP'], 'rel': 'enclosure', 'type': type, 'title': 'FTP URL' }})
            elif 'REMOTE-FTP' in granuleRefDict:
                item.append({'name': 'link', 'attribute': {'href': granuleRefDict['REMOTE-FTP'], 'rel': 'enclosure', 'type': type, 'title': 'FTP URL' }})

        item.append({'namespace': 'podaac', 'name': 'datasetId', 'value': doc['Dataset-PersistentId'][0]})
        item.append({'namespace': 'podaac', 'name': 'shortName', 'value': doc['Dataset-ShortName'][0]})
        
        if 'GranuleSpatial-NorthLat' in doc and 'GranuleSpatial-EastLon' in doc and 'GranuleSpatial-SouthLat' in doc and 'GranuleSpatial-WestLon' in doc:
            item.append({'namespace': 'georss', 'name': 'where', 'value': {'namespace': 'gml', 'name': 'Envelope', 'value': [{'namespace': 'gml', 'name': 'lowerCorner', 'value': ' '.join([doc['GranuleSpatial-WestLon'][0], doc['GranuleSpatial-SouthLat'][0]])}, {'namespace': 'gml', 'name': 'upperCorner', 'value': ' '.join([doc['GranuleSpatial-EastLon'][0], doc['GranuleSpatial-NorthLat'][0]])}]}})
        
        if startTime is not None:
            item.append({'namespace': 'time', 'name': 'start', 'value': startTime})

        if 'Granule-StopTimeLong' in doc and doc['Granule-StopTimeLong'][0] != '':
            item.append({'namespace': 'time', 'name': 'end', 'value': DateUtility.convertTimeLongToIso(doc['Granule-StopTimeLong'][0])})

        if 'full' in self.parameters and self.parameters['full']:
            multiValuedElementsKeys = ('GranuleArchive-', 'GranuleReference-')
            self._populateItemWithPodaacMetadata(doc, item, multiValuedElementsKeys)

    '''
    def _getLinkToGranule(self, doc):
        attr = {}
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
            if link is not None:
                attr['rel'] = 'http://esipfed.org/ns/discovery/1.1/data#'
                attr['title'] = 'Granule File'
                
                if 'GranuleArchive-Name' in doc and 'GranuleArchive-Type' in doc and 'GranuleArchive-FileSize':
                    granuleArchiveDict  = dict(zip(doc['GranuleArchive-Type'], zip(doc['GranuleArchive-Name'], doc['GranuleArchive-FileSize']))) 
                    if link.endswith(granuleArchiveDict['DATA'][0]):
                        attr['size'] = granuleArchiveDict['DATA'][1]
                
                if 'Granule-DataFormat' in doc:
                    attr['type'] = 'application/x-' + doc['Granule-DataFormat'][0].lower()
        else:
            #No link to granule download provided so create link back to opensearch to retrieve granule metadata
            link = "http://" + self.host + "/granule/opensearch.atom?granule=" + doc['Granule-Name'][0]
        attr['href'] = link
        return attr
    '''
