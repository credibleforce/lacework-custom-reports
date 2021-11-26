import json

class HandlerConfig():
    def __init__(self,dataHandlersPath="./types/datatypes.json",reportHandlersPath="./types/reporttypes.json"):
        self.dataHandlersPath = dataHandlersPath
        self.reportHandlersPath = reportHandlersPath    
        self.dataHandlers = {}
        self.reportHandlers = {}
        self.load()

    def load(self):
        with open(self.dataHandlersPath) as f:
            self.dataHandlers = json.load(f)

        with open(self.reportHandlersPath) as f:
            self.reportHandlers = json.load(f)

    def dataHandlers(self):
        return self.dataHandlers

    def reportHandlers(self):
        return self.reportHandlers