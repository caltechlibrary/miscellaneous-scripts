#!/usr/bin/env python3

import json
import sys
import csv
from   commonpy.network_utils import net
from   decouple import config

base_url = config('FOLIO_OKAPI_URL', default = None)

headers = {
    "x-okapi-token":  config('FOLIO_OKAPI_TOKEN', default = None),
    "x-okapi-tenant": config('FOLIO_OKAPI_TENANT_ID', default = None),
    "content-type":   "application/json",
}

request_url = base_url + '/users?limit=10000'

(response, error) = net('get', request_url, headers = headers)
if error:
    raise error

response_dict = json.loads(response.text)
num_records = response_dict['totalRecords']
if num_records != len(response_dict['users']):
    raise 'Failed to get all records'

with open('users.json', 'w') as f:
    json.dump(response_dict['users'], f)

print('Wrote ' + str(num_records) + ' to users.json')

def field_value(user_dict, field, subfield = None):
    if subfield:
        if field in user_dict and subfield in user_dict[field]:
            return user_dict[field][subfield]
        else:
            return 'MISSING'
    else:
        return user_dict[field] if field in user_dict else 'MISSING'

with open('users.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Username', 'Barcode', 'UUID', 'Email'])
    for user in response_dict['users']:
        username = field_value(user, 'username')
        barcode  = field_value(user, 'barcode')
        uuid     = field_value(user, 'id')
        email    = field_value(user, 'personal', 'email')
        writer.writerow([username, barcode, uuid, email])

print('Wrote ' + str(num_records) + ' to users.csv')
