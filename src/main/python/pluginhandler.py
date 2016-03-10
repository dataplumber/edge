import os
import sys
import logging

class PluginHandler(object):
    def __init__(self, name, pluginPath, format=None):
        self.name = name
        self.pluginPath = pluginPath
        self.format = format

    def handleRequest(self, httpMethod, path, requestHandler):
        paths = path.split('/')
        fileName = paths.pop()
        fileNames = fileName.split('.')
        fileSuffix = fileNames.pop()
        
        # Support plugin lookup for [fgdc|gmcd|iso].xml
        if fileSuffix == 'xml':
            fileSuffix = fileNames.pop()

        if self.format is not None and len(self.format) > 0:
            try:
                fileSuffix = requestHandler.get_argument('format')
            except:
                fileSuffix = self.format[0]
                #raise Exception("Format parameter required.")
            if fileSuffix not in self.format:
                raise Exception("Format %s not supported." % fileSuffix)
        
        pluginName = self._getPluginName(self.pluginPath+'/'+self.name+'/'+fileSuffix)
        if not pluginName:
            raise Exception("Did not find plugin.")
        
        modulePath = self.pluginPath+'.'+self.name+'.'+fileSuffix+'.'+pluginName
        if modulePath in sys.modules:
            currentModuleName = ''
            for moduleName in modulePath.split('.'):
                currentModuleName += moduleName
                #print('reloading: '+currentModuleName)
                reload(sys.modules[currentModuleName])
                currentModuleName += '.'

        #print('modulePath: '+modulePath)
        module = __import__(modulePath, globals(), locals(), [pluginName])
        plugin = getattr(module, pluginName)
        pluginObject = plugin(self.pluginPath+'/'+self.name+'/'+fileSuffix+'/plugin.conf')
        method = getattr(pluginObject, httpMethod)
        method(requestHandler)

    def _getPluginName(self, path):
        name = None
        for fileName in os.listdir(path):
            if fileName != '__init__.py' and fileName.endswith('.py'):
                name = fileName.split('.')[0]
                break

        return name

