from itertools import product

regions = ['arkhangelsk', 'moscow', 'voronezh']
fields = [
    'live_in',
    'family',
    'press',
    'network',
    'other',
]

ls = list(product(regions, fields))
ls = [f'knowledge_{i[0]}_{i[1]}' for  i in ls]
for l in ls:
    print(f'{l} = models.BooleanField()')