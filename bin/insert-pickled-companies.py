import traceback
import requests
import pickle
import json


with open('sf.pickle', 'rb') as fin:
    batch = []
    for i, c in enumerate(pickle.load(fin)):
        try:
            print("{:10} processing {}".format(i, c['name']))
            batch.append({
                'name': c['name'],
                'url': c['website'],
                'account_id': c['account_id'],
                'company_id': c['company_id'],
            })
        except:
            traceback.print_exc()
            continue
        if len(batch) == 100:
            requests.post('http://0.0.0.0:6543/companies', data=json.dumps({
                'companies': batch
            }))
            batch = []
