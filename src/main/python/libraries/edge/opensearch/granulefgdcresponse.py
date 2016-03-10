import datetime

from edge.opensearch.fgdcresponsebysolr import FgdcResponseBySolr

class GranuleFgdcResponse(FgdcResponseBySolr):
    def __init__(self):
        super(GranuleFgdcResponse, self).__init__()

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        pass
