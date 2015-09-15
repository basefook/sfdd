import requests
import pickle
import json


with open('sf.pickle', 'rb') as fin:
    batch = []
    for i, c in enumerate(pickle.load(fin)):
        try:
            print("{:10} processing {}".format(1+i, c.get('name')))
            batch.append({
                'name': c['name'],
                'url': c['website'],
                'company_id': c['company_id'],
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
