import requests
import json
import os
import datetime

class TMSConnector:
    def __init__(self, coreAPI, user, password):
        self.coreAPI = coreAPI
        self.user = user
        self.password = password
        self.headers = {u'content-type': u'application/json'}
        
    def get_device_info(self, device_id):
        info_url = self.coreAPI + u'monitoring/info'
    
        info_payload = {u'username':self.user, u'password':self.password, u'device_ids':[device_id]}    
        info_response = requests.post(info_url, data=json.dumps(info_payload), headers=self.headers)
        device_info = info_response.json()
        return device_info[u'data'][device_id]
    
    def get_scheduling(self, start_time, end_time):
        scheduling_url = self.coreAPI + u'scheduling/schedule'
        scheduling_payload = {u'username':self.user, u'password':self.password, u'start_time': start_time, u'end_time': end_time}
        
        scheduling_response = requests.post(scheduling_url, data=json.dumps(scheduling_payload), headers=self.headers)
        schedule = scheduling_response.json()
        return schedule[u'data']
    
    def get_playlist(self, playlist_id, device_id):
        playlist_url = self.coreAPI + u'playlist/playlist'
        playlist_payload = {u'username':self.user, u'password':self.password, u'playlist_ids': [playlist_id], u'device_ids': [device_id]}
    
        playlist_response = requests.post(playlist_url, data=json.dumps(playlist_payload), headers=self.headers)
        playlist = playlist_response.json()
        if device_id in playlist[u'data'] and playlist_id in playlist[u'data'][device_id] and u'playlist' in playlist[u'data'][device_id][playlist_id]:
            return playlist[u'data'][device_id][playlist_id][u'playlist']
    
    def get_content(self, content_id, device_id):
        content_url = self.coreAPI + u'content/content'
        content_payload = {u'username':self.user, u'password':self.password, u'device_ids': [device_id], u'content_ids': [content_id]}
    
        content_response = requests.post(content_url, data=json.dumps(content_payload), headers=self.headers)
        content = content_response.json()
        return content[u'data']
    
    def get_title(self, content_id):
        title_url = self.coreAPI + u'title/get_title_with_cpl'
        title_payload = {u'username':self.user, u'password':self.password, u'cpl_uuid': content_id}
    
        title_response = requests.post(title_url, data=json.dumps(title_payload), headers=self.headers)
        title = title_response.json()
        for item in title[u'data']:
            if u'name' in item:
                return item[u'name']
        return u'No title'

def read_tms():
    #read config file
    try:
        config = json.load(open(os.path.join(os.path.dirname(__file__), u'settings.json'), u'r'))
    except IOError:
        raise IOError(u'The settings.json file does not exist') 
    
    tms_connection = TMSConnector(config[u'coreAPI'], config[u'username'], config[u'password'])
    now = datetime.datetime.now()
    endofday = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=2)
    
    timeline = []

    schedule = tms_connection.get_scheduling(now.strftime(u'%Y-%m-%d %H:%M:%S'), endofday.strftime(u'%Y-%m-%d %H:%M:%S'))
    for schedule_item in schedule.itervalues():
        timeline_entry={}
        start_time = schedule_item[u'start_time']
        start_date = schedule_item[u'start_date']
        duration = schedule_item[u'duration']
        device_uuid = schedule_item[u'device_information'][u'device_uuid']
        playlist_uuid = schedule_item[u'device_information'][u'device_playlist_uuid']
        
        #device_info = tms_connection.get_device_info(device_uuid)
        #for key, val in device_info.iteritems():
        #    print key, ':', val
        
        duration_m, duration_s = divmod(duration, 60)
        duration_h, duration_m = divmod(duration_m, 60)
        
        timeline_entry.update({u'start_date':start_date, u'start_time':start_time})
        timeline_entry.update({u'duration_h': int(duration_h), u'duration_m': int(duration_m)})
        
        if playlist_uuid == None or device_uuid == None:
            continue
        
        playlist = tms_connection.get_playlist(playlist_uuid, device_uuid)
        
        if playlist == None:
            continue
        
        playlist_is3d = playlist[u'is_3d']
        for event in playlist[u'events']:
            if u'cpl_id' in event:
                title = tms_connection.get_title(event[u'cpl_id'])
                timeline_entry.update({u'title':title})
                
                content = tms_connection.get_content(event[u'cpl_id'], device_uuid)
                for ct in content.itervalues():
                    if(u'content_kind' not in ct):
                        continue
                    if(ct[u'content_kind'] == u'feature'):      
                        timeline_entry.update({u'audio_language': ct[u'audio_language']})
                        if(playlist_is3d):
                            timeline_entry.update({u'is_3D': True})
                        if(ct[u'subtitled'] and u'subtitle_language' in ct):
                            timeline_entry.update({u'subtitle_Language':ct[u'subtitle_language']})
                        if(ct[u'rating'] != None):
                            timeline_entry.update({u'rating':ct[u'rating']})
                            
                        timeline.append(timeline_entry)
        
    return json.dumps(timeline, indent=4)
                            
if __name__ == u'__main__':
    print read_tms()