import logging

from xml.dom.minidom import Document
import xml.sax.saxutils

from edge.opensearch.response import Response

class AtomResponse(Response):
    def __init__(self):
        super(AtomResponse, self).__init__()
        self.namespaces = {
            '': 'http://www.w3.org/2005/Atom',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
            'podaac': 'http://podaac.jpl.nasa.gov/opensearch/',
            'georss': 'http://www.georss.org/georss',
            'gml': 'http://www.opengis.net/gml',
            'time': 'http://a9.com/-/opensearch/extensions/time/1.0/'
        }

        self.title = None
        self.link = None
        self.update = None
        self.authors = []
        self.variables = []
        self.items = []
        self.id = None
        self.updated = None
        self.parameters = {}

    def addNamespace(self, name, uri):
        self.namespaces[name] = uri

    def removeNamespace(self, name):
        del self.namespaces[name]

    def generate(self, pretty=False):
        logging.debug('AtomResponse.generate is called.')

        document = Document()
        feed = document.createElement('feed')
        for namespace in self.namespaces.keys():
            namespaceAttr = 'xmlns'
            if namespace != '':
                namespaceAttr += ':'+namespace
            feed.setAttribute(namespaceAttr, self.namespaces[namespace])
        document.appendChild(feed)

        title = document.createElement('title')
        feed.appendChild(title)
        title.appendChild(document.createTextNode(xml.sax.saxutils.escape(self.title)))
        '''
        link = document.createElement('link')
        feed.appendChild(link)
        link.appendChild(document.createTextNode(xml.sax.saxutils.escape(self.link)))
        '''

        updated = document.createElement('updated')
        feed.appendChild(updated)
        updated.appendChild(document.createTextNode(xml.sax.saxutils.escape(self.updated)))

        id = document.createElement('id')
        feed.appendChild(id)
        id.appendChild(document.createTextNode(xml.sax.saxutils.escape(self.id)))

        author = document.createElement('author')
        feed.appendChild(author)
        for authorName in self.authors:
            authorElement = document.createElement('name')
            author.appendChild(authorElement)
            authorElement.appendChild(document.createTextNode(xml.sax.saxutils.escape(authorName)))

        for variable in self.variables:
            '''
            elementName = variable['name']
            if 'namespace' in variable:
                elementName = variable['namespace']+':'+elementName

            variableElement = document.createElement(elementName)
            feed.appendChild(variableElement)
            variableElement.appendChild(document.createTextNode(xml.sax.saxutils.escape(str(variable['value']))))
            '''
            self._createNode(document, variable, feed)

        for item in self.items:
            itemElement = document.createElement('entry')
            feed.appendChild(itemElement)

            for itemEntry in item:
                self._createNode(document, itemEntry, itemElement);
                '''
                elementName = itemEntry['name']
                if 'namespace' in itemEntry:
                    elementName = itemEntry['namespace']+':'+elementName

                variableElement = document.createElement(elementName)
                itemElement.appendChild(variableElement)

                if 'value' in itemEntry:
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
                else:
                    if 'attribute' in itemEntry:
                        for attr in itemEntry['attribute'].keys():
                            variableElement.setAttribute(attr, itemEntry['attribute'][attr])
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
