import json


b = []
a = {'message': 'Нет записей'}

json_text = json.dumps(a, ensure_ascii=False)

print(json_text)
print('message' in b)
print('message' in a)
