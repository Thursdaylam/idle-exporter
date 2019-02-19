from prometheus_client import start_http_server, Gauge
import time
import os
import subprocess
from stat import *
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re

log_list = []

idle_guage = Gauge('user_input_idle_time', 'Time since last user input, based on /dev/pts mod time')
avg_idle_guage =Gauge('avg_user_input_idle_time', 'Time since last user input, 1 minute average based on 1 second polls to improve reliability regardless of prometheus poll rate, based on /dev/pts mod time')
idle_guage_w =Gauge('user_w_idle_time', 'Time since last user input based on w, process label shows the WHAT Field of w',['process'])

def get_last_use():

    mypath = '/dev/pts'
    onlyfiles = [f for f in listdir(mypath)]

    now = datetime.now()

    min_usage = float('Inf')
    process = 999
    for file in onlyfiles:
        unix_timestamp = float(os.stat(mypath + '/' + file)[ST_MTIME])
        last_modified = datetime.fromtimestamp(unix_timestamp)
        
        elapsed = now - last_modified
        if elapsed.total_seconds()<min_usage:
            min_usage = elapsed.total_seconds()
            process = mypath + '/' + file
    

    return min_usage


def running_mean(interval = 60):
    global log_list
    min_usage = get_last_use()
    log_list.append(min_usage)

    if len(log_list)>interval:
        log_list.pop(0)
    
    average = sum(log_list)/float(len(log_list))
    return average


def update_idle():

    try:
        average_idle_time = running_mean(interval = 60)
        avg_idle_guage.set(average_idle_time)  

        idle_time = get_last_use()
        idle_guage.set(idle_time)

    except Exception as e:
        print(str(e))

        
def parse_time(input):
    digits = [int(x) for x in re.findall(r'\d+', input)]
    units = re.findall(r'[a-zA-Z]+', input)



    # W The standard format is DDdays, HH:MMm, MM:SS or SS.CC 
    # if the times are greater than 2 days, 1hour, or 1 minute respectively.
    if len(units) == 0:
        time = digits[0] * 60 + digits[1]
    
    elif units[0] == 's':
        time = digits[0] + digits[1]/100
    
    elif units[0] == 'm':
        time = digits[0] * 60 * 60 + digits[1] * 60

    elif units[0] == 'days':
        time = digits[0] * 60 * 60 *24
    
    return time

def update_idle_w():

    output = subprocess.check_output(['w'])
    output = output.splitlines()
    output = [x.decode("utf-8")  for x in output]

    metadata = output.pop(0)
    headers = output.pop(0)


    idle_index = headers.split().index('IDLE')
    what_index = headers.split().index('WHAT')
    min_time = float('Inf')
    whatString = ''
    if len(output) == 0:
        min_time = float('NAN')
    else:
        first = False
        for line in output:
            stringline = line
            idle_time = stringline.split()[idle_index]
            whatString = stringline.split()[what_index]
            if first:
                min_time = parse_time(idle_time)
            else:
                min_time = min(min_time, parse_time(idle_time))

    idle_guage_w.labels(process=whatString).set(min_time)


if __name__ == '__main__':
    print('server starting')
    start_http_server(3003)
    print('server started')
    while True:
        time.sleep(1)
        try:
            update_idle()
        except Exception as e:
            print(str(e))
        
        try:
            update_idle_w()
        except Exception as e:
            print(str(e))
        
