import datetime
import urllib

from edge.elasticsearch.opensearch.atomresponsebyelasticsearch import AtomResponseByElasticsearch
from edge.dateutility import DateUtility

class GranuleAtomResponse(AtomResponseByElasticsearch):
    def __init__(self, linkToGranule, host, url):
        super(GranuleAtomResponse, self).__init__()

        self.linkToGranule = linkToGranule.split(',')
        self.host = host
        self.url = url

    def _populateChannel(self, solrResponse):
        self.variables.append({'name': 'link', 'attribute': {'href': self.url+self.searchBasePath+'podaac-dataset-osd.xml', 'rel': 'search', 'type': 'application/opensearchdescription+xml' }})

    def _populateItem(self, solrResponse, doc, item):
        item.append({'name': 'title', 'value': doc['_source']['name']})
        #item.append({'name': 'content', 'value': doc['Granule-Name'][0]})
        
        updated = None
        startTime = None
        if 'start_time' in doc['_source'] and doc['_source']['start_time'] is not None:
            updated = DateUtility.convertTimeLongToIso(doc['_source']['start_time'])
            startTime = updated
        else:
            updated = datetime.datetime.utcnow().isoformat()+'Z'
        
        item.append({'name': 'updated', 'value': updated})
        item.append({'name': 'id', 'value': doc['_source']['identifier'] + ':' + doc['_source']['name']})
        
        parameters = {'identifier': doc['_source']['identifier'], 'name': doc['_source']['name']}
        parameters['full'] = 'true'
        item.append({'name': 'link', 'attribute': {'href': self.url+self.searchBasePath + 'granule?' + urllib.urlencode(parameters), 'rel': 'enclosure', 'type': 'application/atom+xml', 'title': 'GIBS Metadata' }})
        del parameters['full']
        '''
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
        '''
        item.append({'namespace': 'gibs', 'name': 'identifier', 'value': doc['_source']['identifier']})
        '''
        item.append({'namespace': 'podaac', 'name': 'shortName', 'value': doc['Dataset-ShortName'][0]})
        
        if 'GranuleSpatial-NorthLat' in doc and 'GranuleSpatial-EastLon' in doc and 'GranuleSpatial-SouthLat' in doc and 'GranuleSpatial-WestLon' in doc:
            item.append({'namespace': 'georss', 'name': 'where', 'value': {'namespace': 'gml', 'name': 'Envelope', 'value': [{'namespace': 'gml', 'name': 'lowerCorner', 'value': ' '.join([doc['GranuleSpatial-WestLon'][0], doc['GranuleSpatial-SouthLat'][0]])}, {'namespace': 'gml', 'name': 'upperCorner', 'value': ' '.join([doc['GranuleSpatial-EastLon'][0], doc['GranuleSpatial-NorthLat'][0]])}]}})
        '''
        if startTime is not None:
            item.append({'namespace': 'time', 'name': 'start', 'value': startTime})

        if 'stop_time' in doc['_source'] and doc['_source']['stop_time'] is not None:
            item.append({'namespace': 'time', 'name': 'end', 'value': DateUtility.convertTimeLongToIso(doc['_source']['stop_time'])})

        if 'full' in self.parameters and self.parameters['full']:
            self._populateItemWithAllMetadata(doc['_source'], item)
