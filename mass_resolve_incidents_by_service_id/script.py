#!/usr/bin/env python3
# REST API Guide: https://api-reference.pagerduty.com
# Just needs the API Token from the Account Owner to run
# TODO: exception handling when no/invalid api_token is passed
#       minor tweaks :)
# curl -X GET --header 'Accept: application/vnd.pagerduty+json;version=2' --header 'Authorization: Token token=_Z-qucZGi_JtwtZem7Ws' 'https://api.pagerduty.com/incidents?service_ids%5B%5D=POVE6WX&time_zone=UTC'

import requests
import json

# account definitions
api_token = 'xxx'
service_id = 'xxx'
from_email = 'xxx'
url = 'https://api.pagerduty.com/incidents'
header =    {
                'Accept':'application/vnd.pagerduty+json;version=2',
                'Content-Type': 'application/json', 
                'Authorization':'Token token=' + api_token,
                'From': from_email
            }

## added pagination support
# switch to max result limit (as specified on PD documentation website)
limit = 100
offset = 0
reset_offset = 0

# maintain a count
total_updates = 0

while True:
    params = {'service_ids[]': service_id, 'statuses[]': 'triggered', 'limit': limit, 'offset': offset}

    # Get the list of incidents from PD based on the supplied service ID and convert it to JSON
    incidents_list = json.loads(requests.get(url, params=params, headers=header).text)

    
    for incident in incidents_list['incidents']:
        # update count
        total_updates+=1

        incident_id = incident['id']
        # form the new payload for the api request to change the incident status to resolved
        payload = {
            'incident': {
                'type': 'incident_reference',
                'status': 'resolved'
            }
        }

        # form the new url for the api request
        update_url = url + '/{}'.format(incident_id)

        # fire the request. for some reason had to convert payload to str
        response = requests.put(update_url, headers=header, data=str(payload))

        if response.status_code == 200:
            print(incident_id + ' - SUCCESS')
        else:   
            print(incident_id + ' - FAILED - ' + response.text)

    # we need to monitor the offset variable to stop making it go out of bounds
    if reset_offset == 1: 
        offset = 0
        reset_offset =0

    # condition to break out of infinite while loop
    if offset < 9900:
        offset+=limit
    elif incidents_list['more'] == True and offset == 9900:
        # add a flag condition to bypass the offset limit of 100
        reset_offset = 1
    else:
        break

# print some fancy stats on the cli
print('Total incidents resolved: {}\nTotal pages fetched: {}'.format(str(total_updates),str((offset//limit)+1)))