import requests
import json
import os

def read_tms():
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
    
    scheduling_url = config[u'coreAPI'] + u'scheduling/schedule'
    scheduling_payload = {'username':config[u'username'], 'password':config[u'password'], u'start_time': u'2013-08-01 11:00:00', u'end_time': u'2013-08-01 13:59:59'}
    
    scheduling_response = requests.post(scheduling_url, data=json.dumps(scheduling_payload), headers=headers)
    schedule = json.loads(scheduling_response.text)
    print json.dumps(schedule, indent=4)
    
    for item in schedule['data']:
        start = schedule['data'][item]['start_timestamp']
        duration = schedule['data'][item]['duration']
        device_uuid = schedule['data'][item]['device_information']['device_uuid']
        playlist_uuid = schedule['data'][item]['device_information']['device_playlist_uuid']
        
        playlist_url = config[u'coreAPI'] + u'playlist/playlist'
        playlist_payload = {'username':config[u'username'], 'password':config[u'password'], u'playlist_ids': [playlist_uuid], u'device_ids': [device_uuid]}
    
        playlist_response = requests.post(playlist_url, data=json.dumps(playlist_payload), headers=headers)
        playlist = json.loads(playlist_response.text)
        for item in playlist['data']:
            #print json.dumps(playlist['data'][item][playlist_uuid]['playlist'], indent=4)
            playlist_is3d = playlist['data'][item][playlist_uuid]['playlist']['is_3d']
            for event in playlist['data'][item][playlist_uuid]['playlist']['events']:
                if u'cpl_id' in event:
                    title_url = config[u'coreAPI'] + u'title/get_title_with_cpl'
                    title_payload = {'username':config[u'username'], 'password':config[u'password'], u'cpl_uuid': event['cpl_id']}
                
                    title_response = requests.post(title_url, data=json.dumps(title_payload), headers=headers)
                    title = json.loads(title_response.text)
                    for item in title['data']:
                        if u'name' in item:
                            print item['name']

if __name__ == u'__main__':
    read_tms()