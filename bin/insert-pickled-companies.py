import requests
import pickle
import json


for k in range(22):
    with open('sf.{}.0.pickle'.format(k), 'rb') as fin:
        batch = []
        for i, c in enumerate(pickle.load(fin)):
            try:
                print("{:10} processing {}".format(1+i, c.get('name')))
                batch.append({
                    'name': c['name'],
                    'url': c['website'],
                    'account_id': c['account_id'],
                })
            except:
                continue
            if len(batch) == 1024:
                requests.post('http://0.0.0.0:6543/companies', data=json.dumps({
                    'companies': batch
                }))
                batch = []
        requests.post('http://0.0.0.0:6543/companies', data=json.dumps({
            'companies': batch
        }))
