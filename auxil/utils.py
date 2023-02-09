import random
from itertools import cycle, product
from pprint import pprint
import pandas as pd

info = dict(
    R1=dict(
        crime_rate=1,
        population=10500,
        area=80,
        wage=5000
    ),
    R2=dict(
        crime_rate=2,
        population=5600,
        area=180,
        wage=10000
    )
)
region1 = [{'corruption': 1},
           {'population', 10500},
           {'area', 80}
           ]
region2 = [{'corruption': 2},
           {'population': 5600},
           {'area', 180}
           ]

r1_replacement = {'gdp': 5000}
r2_replacement = {'gdp': 10000}
params = ['crime_rate', 'population', 'area']
params2 = ['wage', 'population', 'area']
regions = ['R1', 'R2']


def shuffler(params):
    c = params.copy()
    random.shuffle(c)
    return c


def pldata(i, o):
    res = []
    for r in o:
        regionname = r[0]
        params = r[1]
        if 'corruption' in params and info[regionname]['corruption'] == 2:
            pref = random.randint(0, 75)
        else:
            pref = random.randint(20, 100)

        t = {'region': regionname, 'player_id': i, 'pref':pref}

        for j,p in enumerate(params, start=1):
            t1 = t.copy()
            t1['info'] = p
            t1['info_position'] = j
            t1['value'] = info[regionname][p]
            res.append(t1)
    return res


n = 20
res = []

for i in range(n):
    sparams = shuffler(params)
    singleset = [(r, sparams) for r in regions]
    res.extend(pldata(i, singleset))
df1 = pd.DataFrame(res)
df1['treatment'] = 'FIC'
res = []
for i in range(n):
    sparams = shuffler(params2)
    singleset = [(r, sparams) for r in regions]
    res.extend(pldata(i, singleset))
df2 = pd.DataFrame(res)
df2['treatment'] = 'FIN'
# df.sort_values(by=['treatment','player_id','region'],inplace=True)
df = pd.concat([df1, df2])
df = df[['player_id', 'region',  'info', 'info_position', 'value','pref',  'treatment']]
print( list(df.columns.values))

df.to_csv('test.csv', index=False)
