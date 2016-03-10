from edge.opensearch.responsebysolr import ResponseBySolr

class GranuleResponseBySolr(ResponseBySolr):
    def __init__(self, linkToGranule):
        super(GranuleResponseBySolr, self).__init__()

        self.linkToGranule = linkToGranule

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        item.append({'name': 'title', 'value': doc['Granule-Name'][0]})
        item.append({'name': 'description', 'value': doc['Granule-Name'][0]})
        #item.append({'name': 'description', 'value': doc['Dataset-Description'][0]})
        #item.append({'name': 'link', 'value': self.portalUrl+'/'+doc['Dataset-ShortName'][0]})
        link = self._getLinkToGranule(doc)
        if link is not None:
            item.append({'name': 'link', 'value': link})

    def _getLinkToGranule(self, doc):
        link = None

        if 'GranuleReference-Type' in doc:
            types = doc['GranuleReference-Type']

            typeIndex = -1
            for index, type in enumerate(types):
                if type == self.linkToGranule:
                    typeIndex = index
                    break

            if typeIndex >= 0:
                if ('GranuleReference-Path' in doc) and (len(doc['GranuleReference-Path']) > typeIndex):
                    link = doc['GranuleReference-Path'][typeIndex]

        return link
