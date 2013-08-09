import requests
import json
import os
import datetime
import warnings

class TMSConnector:
    warnings.warn('This class is deprecated, please use the JavaScript functions',DeprecationWarning )
    '''
    A connector which provides an API wrapper for the TMS API.
    
    :param coreAPI: URL to the API (ending with /core/)
    :param user: Username to login
    :param password: Password to login
    '''
    def __init__(self, coreAPI, user, password):
        self.coreAPI = coreAPI
        self.user = user
        self.password = password
        self.headers = {u'content-type': u'application/json'}

    def get_screen_name(self, device_id):
        '''
        Returns the screen name which a device belongs to
        
        :param device_id: UUID of the device
        '''
        complex_url = self.coreAPI + u'configuration/screen'

        complex_payload = {u'username':self.user, u'password':self.password}
        complex_response = requests.post(complex_url, data=json.dumps(complex_payload), headers=self.headers)
        complex_info = complex_response.json()
        for screen in complex_info[u'data'].itervalues():
            for device in screen[u'devices']:
                if device == device_id:
                    return screen[u'title']
        return None

    def get_device_info(self, device_id):
        '''
        Returns the monitoring information of a device
        
        :param device_id: UUID of the device
        '''
        info_url = self.coreAPI + u'monitoring/info'

        info_payload = {u'username':self.user, u'password':self.password, u'device_ids':[device_id]}
        info_response = requests.post(info_url, data=json.dumps(info_payload), headers=self.headers)
        device_info = info_response.json()
        return device_info[u'data'][device_id]

    def get_scheduling(self, start_time, end_time):
        '''
        Returns the upcoming schedule between two given times
        
        :param start_time: Start time for the schedule lookup
        :param end_time: End time for the schedule lookup
        '''
        scheduling_url = self.coreAPI + u'scheduling/schedule'
        scheduling_payload = {u'username':self.user, u'password':self.password, u'start_time': start_time, u'end_time': end_time}

        scheduling_response = requests.post(scheduling_url, data=json.dumps(scheduling_payload), headers=self.headers)
        schedule = scheduling_response.json()
        return schedule[u'data']

    def get_playlist(self, playlist_id, device_id):
        '''
        Returns a playlist for a given device
        
        :param playlist_id: UUID of the playlist to get
        :param device_id: UUID of the device
        '''
        playlist_url = self.coreAPI + u'playlist/playlist'
        playlist_payload = {u'username':self.user, u'password':self.password, u'playlist_ids': [playlist_id], u'device_ids': [device_id]}

        playlist_response = requests.post(playlist_url, data=json.dumps(playlist_payload), headers=self.headers)
        playlist = playlist_response.json()
        if device_id in playlist[u'data'] and playlist_id in playlist[u'data'][device_id] and u'playlist' in playlist[u'data'][device_id][playlist_id]:
            return playlist[u'data'][device_id][playlist_id][u'playlist']

    def get_content(self, content_id, device_id):
        '''
        Returns content for a given content ID on a device
        
        :param content_id: UUID of the content to get (CPL)
        :param device_id: UUID of the device
        '''
        content_url = self.coreAPI + u'content/content'
        content_payload = {u'username':self.user, u'password':self.password, u'device_ids': [device_id], u'content_ids': [content_id]}

        content_response = requests.post(content_url, data=json.dumps(content_payload), headers=self.headers)
        content = content_response.json()
        return content[u'data']

    def get_title(self, content_id):
        '''
        Returns the title according to a CPL
        
        :param content_id: UUID of the content to get (CPL)
        '''
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

    #instantiate class
    tms_connection = TMSConnector(config[u'coreAPI'], config[u'username'], config[u'password'])
    
    #times to get schedule for
    now = datetime.datetime.now()
    endofday = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=2)

    schedule = tms_connection.get_scheduling(now.strftime(u'%Y-%m-%d %H:%M:%S'), endofday.strftime(u'%Y-%m-%d %H:%M:%S'))
    
    timeline = []
    
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

        #from seconds to hours, minutes, seconds
        duration_m, duration_s = divmod(duration, 60)
        duration_h, duration_m = divmod(duration_m, 60)
        
        duration_m_str = "%02d" % duration_m
        duration_h_str = "%d" % duration_h

        start_time_format = datetime.datetime.strptime(start_time, u'%H:%M:%S')

        timeline_entry.update({u'start_date':start_date, u'start_time':start_time_format.strftime(u'%I:%M %p').lstrip(u'0')})
        timeline_entry.update({u'duration_h': duration_h_str, u'duration_m': duration_m_str})

        #skip if there is no valid playlist / device id
        if playlist_uuid == None or device_uuid == None:
            continue

        playlist = tms_connection.get_playlist(playlist_uuid, device_uuid)

        #should not happen - nevertheless check for empty playlist
        if playlist == None:
            continue

        playlist_is3d = playlist[u'is_3d']
        for event in playlist[u'events']:
            #only take events into account which have a CPL, otherwise title cannot be obtained later
            if u'cpl_id' in event:
                title = tms_connection.get_title(event[u'cpl_id'])
                timeline_entry.update({u'title':title})

                content = tms_connection.get_content(event[u'cpl_id'], device_uuid)
                for ct in content.itervalues():
                    #check if content kind is existing - if not, skip
                    if(u'content_kind' not in ct):
                        continue
                    #ads etc are not of interest
                    if(ct[u'content_kind'] == u'feature'):
                        if('audio_language' in ct):
                            timeline_entry.update({u'audio_language': ct[u'audio_language']})
                        if(playlist_is3d):
                            timeline_entry.update({u'is_3D': True})
                        if(ct[u'subtitled'] and u'subtitle_language' in ct):
                            timeline_entry.update({u'subtitle_language':ct[u'subtitle_language']})
                        if(ct[u'rating'] != None):
                            timeline_entry.update({u'rating':ct[u'rating']})

                        screen_name = tms_connection.get_screen_name(device_uuid)
                        if(screen_name != None):
                            timeline_entry.update({u'screen_name':screen_name})

                        if(timeline_entry not in timeline):
                            #only if all necessary information could be obtained add to timeline
                            timeline.append(timeline_entry)

    #sort timeline according the start_time of the schedule and dump it into json
    return json.dumps(sorted(timeline, key=lambda movie: movie['start_time']))

#can be run from console as well
if __name__ == u'__main__':
    print read_tms()