from common.podsudnost import getPodsudnostValue as g
from globals import Podsudnost

a = 'Бурлинский районный суд  Западно-Казахстанской области'
print(g(a))

# a = '0'
# print(bool(int(a)))

# a = Podsudnost().load_json()
# print(a.data)