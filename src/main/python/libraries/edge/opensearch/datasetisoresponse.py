from edge.opensearch.isoresponsebysolr import IsoResponseBySolr

class DatasetIsoResponse(IsoResponseBySolr):
    def __init__(self):
        super(DatasetIsoResponse, self).__init__()

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
