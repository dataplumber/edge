from edge.opensearch.responsebysolr import ResponseBySolr

class DatasetResponseBySolr(ResponseBySolr):
    def __init__(self, portalUrl):
        super(DatasetResponseBySolr, self).__init__()
        self.portalUrl = portalUrl

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        item.append({'name': 'title', 'value': doc['Dataset-LongName'][0]})
        item.append({'name': 'description', 'value': doc['Dataset-Description'][0]})
        item.append({'name': 'link', 'value': self.portalUrl+'/'+doc['Dataset-ShortName'][0]})
