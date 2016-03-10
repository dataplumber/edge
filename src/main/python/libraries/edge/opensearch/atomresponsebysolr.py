import json
import urllib

from edge.opensearch.atomresponse import AtomResponse
from collections import defaultdict

class AtomResponseBySolr(AtomResponse):
    def __init__(self):
        super(AtomResponseBySolr, self).__init__()

    def generate(self, solrResponse, pretty=False):
        self._populate(solrResponse)
        return super(AtomResponseBySolr, self).generate(pretty)

    def _populate(self, solrResponse):
        #response.title = 'OCSI Dataset Search: '+searchText
        #response.description = 'Search result for "'+searchText+'"'
        #response.link = searchUrl
        self._populateChannel(solrResponse)

        if solrResponse is None:
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'totalResults', 'value': 1}
            )
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'startIndex', 'value': 1}
            )
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'itemsPerPage', 'value': 1}
            )
            self.parameters['startIndex'] = 0
            url = self.link + '?' + urllib.urlencode(self.parameters)
            self.variables.append({'name': 'link', 'attribute': {'href': url, 'rel': 'self', 'type': 'application/atom+xml'}})
            self.variables.append({'name': 'link', 'attribute': {'href': url, 'rel': 'first', 'type': 'application/atom+xml'}})
            item = [
                {'name': 'title', 'value': 'Error'},
                {'name': 'content', 'value': 'error'}
            ]
            self.items.append(item)
        else:
            #logging.debug(solrResponse)
            solrJson = json.loads(solrResponse)
            numFound = int(solrJson['response']['numFound'])
            start = int(solrJson['response']['start'])
            rows = int(solrJson['responseHeader']['params']['rows'])

            self.parameters['startIndex'] = start
            self.variables.append({'name': 'link', 'attribute': {'href': self.link + '?' + urllib.urlencode(self.parameters), 'rel': 'self', 'type': 'application/atom+xml'}})
            self.parameters['startIndex'] = 0
            self.variables.append({'name': 'link', 'attribute': {'href': self.link + '?' + urllib.urlencode(self.parameters), 'rel': 'first', 'type': 'application/atom+xml'}})
            if start > 0:
                if (start - rows > 0):
                    self.parameters['startIndex'] = start - rows
                self.variables.append({'name': 'link', 'attribute': {'href': self.link + '?' + urllib.urlencode(self.parameters), 'rel': 'previous', 'type': 'application/atom+xml'}})
            if start + rows < numFound:
                self.parameters['startIndex'] = start + rows
                self.variables.append({'name': 'link', 'attribute': {'href': self.link + '?' + urllib.urlencode(self.parameters), 'rel': 'next', 'type': 'application/atom+xml'}})
            
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'totalResults', 'value': solrJson['response']['numFound']}
            )
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'startIndex', 'value': solrJson['response']['start']}
            )
            self.variables.append(
                {'namespace': 'opensearch', 'name': 'itemsPerPage', 'value': solrJson['responseHeader']['params']['rows']}
            )

            for doc in solrJson['response']['docs']:
                """
                item = [
                    {'name': 'title', 'value': doc['Dataset-LongName'][0]},
                    {'name': 'description', 'value': doc['Dataset-Description'][0]},
                    {'name': 'link', 'value': self._configuration.get('portal', 'datasetUrl')+'/'+doc['Dataset-ShortName'][0]}
                ]
                """
                item = []
                '''
                #Handle dataset_location_policy values differently
                if 'DatasetLocationPolicy-Type' in doc and 'DatasetLocationPolicy-BasePath' in doc:
                    for i, x in enumerate(doc['DatasetLocationPolicy-Type']):
                        item.append({'namespace': 'podaac', 'name': self._camelCaseStripHyphen(x.title()), 'value': doc['DatasetLocationPolicy-BasePath'][i]})
                    del doc['DatasetLocationPolicy-Type']
                    del doc['DatasetLocationPolicy-BasePath']
                
                multiValuedElementsKeys = ('DatasetRegion-', 'DatasetCharacter-', 'DatasetCitation-', 'DatasetContact-Contact-', 'DatasetDatetime-', 
                                           'DatasetInteger-', 'DatasetParameter-', 'DatasetProject-', 'DatasetReal-', 'DatasetResource-', 
                                           'DatasetSoftware-', 'DatasetSource-', 'DatasetVersion-', 'Collection-',
                                           'GranuleArchive-', 'GranuleReference-', 'GranuleReal-')
                multiValuedElements = defaultdict(list)
                for docKey in doc.keys():
                    if docKey.startswith(multiValuedElementsKeys):
                        multiValuedElements[docKey.split('-', 1)[0]].append(docKey)
                    else:
                        item.append({'namespace': 'podaac', 'name': self._camelCaseStripHyphen(docKey), 'value': doc[docKey]})
                for multiValuedKey in multiValuedElements:
                    for i, x in enumerate(doc[multiValuedElements[multiValuedKey][0]]):
                        values = {}
                        for key in multiValuedElements[multiValuedKey]:
                            values[self._camelCaseStripHyphen(key.split('-', 1)[1])] = doc[key][i]
                        item.append({'namespace': 'podaac', 'name': self._camelCaseStripHyphen(multiValuedKey), 'value': values})
                '''
                self._populateItem(solrResponse, doc, item)
                self.items.append(item)

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
    
    def _populateItemWithPodaacMetadata(self, doc, item, multiValuedElementsKeys):
        ignoreElementsEndingWith = ('-Full', '-Long')
        multiValuedElements = defaultdict(list)
        for docKey in doc.keys():
            if docKey.startswith(multiValuedElementsKeys):
                multiValuedElements[docKey.split('-', 1)[0]].append(docKey)
            elif not docKey.endswith(ignoreElementsEndingWith):
                if len(doc[docKey]) > 1:
                    item.append({'namespace': 'podaac', 'name': self._camelCaseStripHyphen(docKey), 'value': [{'namespace': 'podaac', 'name': 'value', 'value': x} for x in doc[docKey]]})
                else:
                    item.append({'namespace': 'podaac', 'name': self._camelCaseStripHyphen(docKey), 'value': doc[docKey][0]})
        for multiValuedKey in multiValuedElements:
            for i, x in enumerate(doc[multiValuedElements[multiValuedKey][0]]):
                values = []
                for key in multiValuedElements[multiValuedKey]:
                    if not key.endswith(ignoreElementsEndingWith):
                        values.append({'namespace': 'podaac', 'name': self._camelCaseStripHyphen(key.split('-', 1)[1]), 'value': doc[key][i]})
                item.append({'namespace': 'podaac', 'name': self._camelCaseStripHyphen(multiValuedKey), 'value': values})

    def _camelCaseStripHyphen(self, key):
        #special case to remove duplicate element, contact from element tag
        key = key.replace('-Element-', '', 1).replace('Contact-', '', 1)
        return key[0].lower() + key[1:].replace('-', '')
