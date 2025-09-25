globalData = {}
cfg = {}

def read_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                cfg[key.strip()] = value.strip()

    return cfg

def index(cfg: dict, key: str)->int:
    return int(cfg[key]) - 1