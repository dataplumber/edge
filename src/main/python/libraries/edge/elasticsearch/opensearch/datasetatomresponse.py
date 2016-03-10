import logging
import datetime
import urllib

from edge.elasticsearch.opensearch.atomresponsebyelasticsearch import AtomResponseByElasticsearch
from edge.dateutility import DateUtility

class DatasetAtomResponse(AtomResponseByElasticsearch):
    def __init__(self, portalUrl, host, url, datasets):
        super(DatasetAtomResponse, self).__init__()
        self.portalUrl = portalUrl
        self.host = host
        self.url = url
        self.datasets = datasets

    def _populateChannel(self, solrResponse):
        self.variables.append({'name': 'link', 'attribute': {'href': self.url+self.searchBasePath+'podaac-granule-osd.xml', 'rel': 'search', 'type': 'application/opensearchdescription+xml' }})

    def _populateItem(self, solrResponse, doc, item):
        persistentId = doc['_source']['identifier']
        idTuple = ('identifier', persistentId)
        """
        if persistentId == '':
            idTuple = ('shortName', doc['Dataset-ShortName'][0])
        """
        item.append({'name': 'title', 'value': doc['_source']['title']})
        item.append({'name': 'content', 'value': doc['_source']['description']})
        
        item.append({'name': 'link', 'attribute': {'href': self.url + self.searchBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('full', 'true')])), 'rel': 'enclosure', 'type': 'application/atom+xml', 'title': 'GIBS Metadata' }})
        """
        item.append({'name': 'link', 'attribute': {'href': self.url + self.metadataBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('format', 'iso')])), 'rel': 'enclosure', 'type': 'text/xml', 'title': 'ISO-19115 Metadata' }})
        item.append({'name': 'link', 'attribute': {'href': self.url + self.metadataBasePath + 'dataset?' + urllib.urlencode(dict([idTuple, ('format', 'gcmd')])), 'rel': 'enclosure', 'type': 'text/xml', 'title': 'GCMD Metadata' }})
        """
        #Only generate granule search link if dataset has granules
        if (doc['_source']['identifier'].lower() in self.datasets):
            supportedGranuleParams = dict([(key,value) for key,value in self.parameters.iteritems() if key in ['bbox', 'startTime', 'endTime']])
            supportedGranuleParams['identifier'] = persistentId
            item.append({'name': 'link', 'attribute': {'href': self.url + self.searchBasePath + 'granule?' + urllib.urlencode(supportedGranuleParams), 'rel': 'search', 'type': 'application/atom+xml', 'title': 'Product Search' }})
        """
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
        """
        item.append({'name': 'id', 'value': doc['_source']['identifier']})
        """
        item.append({'namespace': 'podaac', 'name': 'datasetId', 'value': doc['Dataset-PersistentId'][0]})
        item.append({'namespace': 'podaac', 'name': 'shortName', 'value': doc['Dataset-ShortName'][0]})
        """
        if doc['_source']['west_longitude'] is not None and doc['_source']['south_latitude'] is not None and doc['_source']['east_longitude'] is not None and doc['_source']['north_latitude'] is not None:
            item.append({'namespace': 'georss', 'name': 'where', 'value': {'namespace': 'gml', 'name': 'Envelope', 'value': [{'namespace': 'gml', 'name': 'lowerCorner', 'value': ' '.join([str(doc['_source']['west_longitude']), str(doc['_source']['south_latitude'])]) }, {'namespace': 'gml', 'name': 'upperCorner', 'value': ' '.join([str(doc['_source']['east_longitude']), str(doc['_source']['north_latitude'])])}]}})
        
        if 'start_time' in doc['_source'] and doc['_source']['start_time'] is not None:
            item.append({'namespace': 'time', 'name': 'start', 'value': DateUtility.convertTimeLongToIso(doc['_source']['start_time'])})
        
        if 'stop_time' in doc['_source'] and doc['_source']['stop_time'] is not None:
            item.append({'namespace': 'time', 'name': 'end', 'value': DateUtility.convertTimeLongToIso(doc['_source']['stop_time'])})
        
        if 'full' in self.parameters and self.parameters['full']:
            self._populateItemWithAllMetadata(doc['_source'], item)
