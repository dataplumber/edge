import datetime

from edge.opensearch.isoresponsebysolr import IsoResponseBySolr

class GranuleIsoResponse(IsoResponseBySolr):
    def __init__(self, linkToGranule):
        super(GranuleIsoResponse, self).__init__()

        self.linkToGranule = linkToGranule.split(',')

    def _populateChannel(self, solrResponse):
        pass

    def _populateItem(self, solrResponse, doc, item):
        link = self._getLinkToGranule(doc)
        if link is not None:
            doc['link'] = link

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

        return link
