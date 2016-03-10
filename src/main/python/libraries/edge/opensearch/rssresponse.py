import logging

from xml.dom.minidom import Document
import xml.sax.saxutils

from edge.opensearch.response import Response

class RssResponse(Response):
    def __init__(self):
        super(RssResponse, self).__init__()
        self.namespaces = {
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
            'podaac': 'http://podaac.jpl.nasa.gov/opensearch/',
            'georss': 'http://www.georss.org/georss',
            'gml': 'http://www.opengis.net/gml',
            'time': 'http://a9.com/-/opensearch/extensions/time/1.0/',
            'atom': 'http://www.w3.org/2005/Atom'
        }

        self.title = None
        self.link = None
        self.description = None
        self.variables = []
        self.items = []
        self.parameters = {}

    def addNamespace(self, name, uri):
        self.namespaces[name] = uri

    def removeNamespace(self, name):
        del self.namespaces[name]

    def generate(self, pretty=False):
        logging.debug('RssResponse.generate is called.')

        document = Document()
        rss = document.createElement('rss')
        rss.setAttribute('version', '2.0')
        for namespace in self.namespaces.keys():
            rss.setAttribute('xmlns:'+namespace, self.namespaces[namespace])
        document.appendChild(rss)

        channel = document.createElement('channel')
        rss.appendChild(channel)

        title = document.createElement('title')
        channel.appendChild(title)
        title.appendChild(document.createTextNode(xml.sax.saxutils.escape(self.title)))

        description = document.createElement('description')
        channel.appendChild(description)
        description.appendChild(document.createTextNode(xml.sax.saxutils.escape(self.description)))

        link = document.createElement('link')
        channel.appendChild(link)
        link.appendChild(document.createTextNode(xml.sax.saxutils.escape(self.link)))

        for variable in self.variables:
            '''
            elementName = variable['name']
            if 'namespace' in variable:
                elementName = variable['namespace']+':'+elementName

            variableElement = document.createElement(elementName)
            channel.appendChild(variableElement)
            variableElement.appendChild(document.createTextNode(xml.sax.saxutils.escape(str(variable['value']))))
            '''
            self._createNode(document, variable, channel)

        for item in self.items:
            itemElement = document.createElement('item')
            channel.appendChild(itemElement)

            for itemEntry in item:
                self._createNode(document, itemEntry, itemElement);
                '''
                elementName = itemEntry['name']
                if 'namespace' in itemEntry:
                    elementName = itemEntry['namespace']+':'+elementName

                variableElement = document.createElement(elementName)
                itemElement.appendChild(variableElement)

                value = itemEntry['value']
                if isinstance(value, list):
                    if len(value) > 1:
                        for valueEntry in value:
                            valueName = 'value'
                            if 'namespace' in itemEntry:
                                valueName = itemEntry['namespace']+':'+valueName
                            valueElement = document.createElement(valueName)
                            variableElement.appendChild(valueElement)
                            valueElement.appendChild(document.createTextNode(xml.sax.saxutils.escape(str(valueEntry))))
                    else:
                        variableElement.appendChild(document.createTextNode(xml.sax.saxutils.escape(str(value[0]))))
                elif isinstance(value, dict):
                    for key in value.keys():
                        valueName = key
                        if 'namespace' in itemEntry:
                            valueName = itemEntry['namespace']+':'+valueName
                        valueElement = document.createElement(valueName)
                        variableElement.appendChild(valueElement)
                        valueElement.appendChild(document.createTextNode(xml.sax.saxutils.escape(str(value[key]))))
                else:
                    variableElement.appendChild(document.createTextNode(xml.sax.saxutils.escape(str(value))))
                '''
        return document.toprettyxml() if pretty else document.toxml('utf-8') 

    def _createNode(self, document, itemEntry, itemElement):
        elementName = itemEntry['name']
        if 'namespace' in itemEntry:
            elementName = itemEntry['namespace']+':'+elementName
        variableElement = document.createElement(elementName)
        itemElement.appendChild(variableElement)
        if 'value' in itemEntry:
            value = itemEntry['value']
            if isinstance(value, list):
                for valueEntry in value:
                    self._createNode(document, valueEntry, variableElement)
            elif isinstance(value, dict):
                self._createNode(document, value, variableElement)
            else:
                variableElement.appendChild(document.createTextNode(xml.sax.saxutils.escape(str(value))))
        if 'attribute' in itemEntry:
            for attr in itemEntry['attribute'].keys():
                variableElement.setAttribute(attr, itemEntry['attribute'][attr])
