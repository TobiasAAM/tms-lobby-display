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
    print device_info
    
    scheduling_url = config[u'coreAPI'] + u'scheduling/schedule'
    scheduling_payload = {'username':config[u'username'], 'password':config[u'password'], u'start_time': u'2013-08-01 11:00:00', u'end_time': u'2013-08-01 13:59:59'}
    
    scheduling_response = requests.post(scheduling_url, data=json.dumps(scheduling_payload), headers=headers)
    schedule = json.loads(scheduling_response.text)
    
    for item in schedule['data']:
        start_time = schedule['data'][item]['start_time']
        start_date = schedule['data'][item]['start_date']
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
                            content_url = config[u'coreAPI'] + u'content/content'
                            content_payload = {'username':config[u'username'], 'password':config[u'password'], u'device_ids': [device_uuid], u'content_ids': [event['cpl_id']]}
                        
                            content_response = requests.post(content_url, data=json.dumps(content_payload), headers=headers)
                            content = json.loads(content_response.text)
                            for ct in content['data']:
                                print json.dumps(content['data'][ct], indent=4)
                            print 'Start', start_time, start_date
                            print 'Duration', duration
                            print '3D Movie', playlist_is3d
                            print 'Name', item['name']
if __name__ == u'__main__':
    read_tms()