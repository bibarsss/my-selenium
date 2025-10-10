class Data:
    def __init__(self):
        self.data = {}

    def get(self, key: str):
        return self.data.get(key, None)
    
    def index(self, key:str):
        return int(self.data[key]) - 1

class Config(Data):
    def __init__(self, data: dict = {}):
        self.data = data

    def load_config(self):
        with open("config.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    self.data[key.strip()] = value.strip()
        return self
