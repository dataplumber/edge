import logging
import urllib

from edge.writer.genericproxywriter import GenericProxyWriter

class Writer(GenericProxyWriter):
    def __init__(self, configFilePath):
        super(Writer, self).__init__(configFilePath)
