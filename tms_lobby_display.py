'''
Created on 1 Aug 2013

@author: Tobias Fischer
'''

import json
import requests
import os

def main():
    #read config file
    try:
        config = json.load(open(os.path.join(os.path.dirname(__file__), u'settings.json'), u'r'))
    except IOError:
        raise IOError(u'The settings.json file does not exist')
    
    url = config[u'coreAPI'] + u'monitoring/info'
    headers = {u'content-type': u'application/json'}
    
    payload = {'username':config[u'username'], 'password':config[u'password']}    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    device_info = json.loads(response.text)
    
    url = config[u'coreAPI'] + u'scheduling/schedule'
    payload = {'username':config[u'username'], 'password':config[u'password'], u'start_time': u'2013-08-01 11:00:00', u'end_time': u'2013-08-01 13:59:59'}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    schedule = json.loads(response.text)
    for item in schedule['data']:
        #print device_info['data'][schedule['data'][item]['screen_uuid']]
        print schedule['data'][item]
    
if __name__ == u'__main__':
    main()