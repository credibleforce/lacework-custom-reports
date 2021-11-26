class DataSetHandler():
    def __init__(self,dataset):
        self.dataset = dataset
        self.data = { "name": None, "data": None }
        self.load()
        self.generate()

    def load(self):
        return None

    def generate(self):
        return self.data