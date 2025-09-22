from pathlib import Path

old_name = "arch/Байзакский районный суд Жамбылской области/Иск 6/asd.pdf"
new_name = "arch/Байзакский районный суд Жамбылской области/Иск 6/111111.pdf"
o = Path(old_name)
n = Path(new_name)
o.rename(n)
print(o.exists())
print(n.exists())
print(f"Renamed {old_name} -> {new_name}")
