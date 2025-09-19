import os

directory = "arch/Байзакский районный суд Жамбылской области/Иск 1"

files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

print(files)