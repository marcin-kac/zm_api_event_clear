#!/usr/bin/env python3.9
import requests
from datetime import datetime, timedelta
import time
import argparse
import getpass
import json
import sys
import telnetlib
import os.path
from pprint import pprint
#loggin function
def api_login(username, password):
	data = {"user":username,"pass":password,"html5": "-1","stateful":1}
	url = 'http://pioncheviot.ddns.net/zm/api/host/login.json'
	login = requests.post(url=url, data=(data))
	if login.status_code == 200:
		cookies = login.cookies
		with open('/tmp/zm_cookie.txt','w') as f:
			json.dump(requests.utils.dict_from_cookiejar(login.cookies), f)
			print("\nLogin Successful.\n")
	else:
		print(login.status_code, "Login Failure.",)
		exit(0)
	return cookies
def query_api(url,time_stamp,cookie):
    full_url =  'http://pioncheviot.ddns.net/zm/api/' + url
    events = requests.get(url=full_url,  cookies=cookie)
    json_events = json.loads(events.text)
    if events.status_code == 200:
        return json_events
    else:
        print("Record dose not exist")
        exit()
def del_api(ID,time_stamp,cookie):
    full_url =  'http://pioncheviot.ddns.net/zm/api/events/{}.json'.format(ID)
    events = requests.delete(url=full_url,  cookies=cookie)
    if events.status_code == 200:
        print("Record {} deleted".format(ID))
    else:
        print("Record dose not exist")
        exit()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a','--all',action='store_true',dest="all_events",help='List all events.')
    parser.add_argument('-d','--del',dest="del_events",action='store_true',help='Delete events')
    parser.add_argument('-n','--number',type=int,dest="older_then",help='Delete events older then "n" days')
    args = parser.parse_args()
    now = datetime.now()
    time_stamp = int(datetime.timestamp(now) * 1000)
    if os.path.isfile('/tmp/zm_cookie.txt'):
    	with open('/tmp/zm_cookie.txt', 'r') as f:
    		cookie = requests.utils.cookiejar_from_dict(json.load(f))
    else:
    	username = input("Enter ZM Username: ")
    	password = getpass.getpass(prompt="Enter ZM Password: ")
    	cookie = api_login(username,password)
    if args.del_events and args.older_then:
    	url = 'events.json'
    	response = query_api(url,time_stamp,cookie)
    	page_Count = response["pagination"]["pageCount"]
    	event_Total = response["pagination"]["count"]
    	print('Total events {}'.format(event_Total))
    	d = datetime.today() - timedelta(args.older_then)
    	if page_Count == 1:
    		events = response["events"]
    		for event in events:
    			ID = int(event['Event']["Id"])
    			time = event['Event']["StartTime"]
    			date_time_obj = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    			if date_time_obj < d:
    				request = del_api(ID,time_stamp,cookie)
    				exit()
    			else:
    				print("Record dose not exist")
    				exit()
    	elif page_Count > 1:
    		for i in range(1,page_Count):
    			url = 'events.json?page={}'.format(i)
    			response = query_api(url,time_stamp,cookie)
    			events = response["events"]
    			for event in events:
    				ID = int(event['Event']["Id"])
    				time = event['Event']["StartTime"]
    				date_time_obj = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    				if date_time_obj < d:
    					request = del_api(ID,time_stamp,cookie)
    				else:
    					print("Record dose not exist")
    					exit()
    elif args.all_events:
    	url = 'events.json'
    	response = query_api(url,time_stamp,cookie)
    	page_Count = response["pagination"]["pageCount"]
    	event_Total = response["pagination"]["count"]
    	print('Total events {}'.format(event_Total))
    	print('Total pages {}'.format(page_Count))
    	if page_Count == 1:
    		events = response["events"]
    		for event in events:
                        ID = event['Event']["Id"]
                        time = event['Event']["StartTime"]
                        frame = event['Event']["Frames"]
                        print('{} {} {}'.format(ID,time,frame))
    	elif page_Count > 1:
    		for i in range(1,page_Count):
    			url = 'events.json?page={}'.format(i)
    			response = query_api(url,time_stamp,cookie)
    			events = response["events"]
    			for event in events:
                                ID = event['Event']["Id"]
                                time = event['Event']["StartTime"]
                                frame = event['Event']['Frames']
                                print('{} {} {}'.format(ID,time,frame))
    else:
        print("No options given. Use -h for help.")
if __name__ == "__main__":
    main()
