import globals


a = globals.Config().load_config()
# print(a.data)

b = globals.IskData(a.data.copy())
# print(b.data)
b.data['1111111111111111'] = '11111111111'
print(a.data)
print(b.data)
