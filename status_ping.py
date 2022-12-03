#!/usr/bin/python3

import re
import os
from pathlib import Path
from pushover import Client
from datetime import datetime

from custom_functions import sendBasiceMail, date_time_full
import config

def checkPing(hostname):
    # Get full url with special characters replaced with -
    res = re.sub('[^a-zA-Z0-9 \n\.]', '-', hostname)


    file_path = "/status_ping/" + res
    file = Path(file_path)

    response = os.system("ping -c 3 -W 2 " + hostname)
    print(response)
    if response == 0:
        # print ("Host active")
        pingstatus = 1
        if file.exists():
            os.remove(file)
            return (hostname + ": " + "back online" + "\n")
    else:
        # print ("Host failed first ping check")
        response = os.system("ping -c 3 -W 2 " + hostname)
        print(response)
        if response == 0:
            # print ("Host active")
            pingstatus = 1
            if file.exists():
                os.remove(file)
                return (hostname + ": " + "back online" + "\n")
        else:
            pingstatus = 0
            # print ("Host offline")
            if file.exists():
                print(hostname + ": " + "already offline\n")
            else:
                print(hostname + ": " + "offline\n")
                open(file_path, 'a').close()
                return (hostname + ": " + "offline" + "\n")

hostList = open ('../configs/website-list.txt')

reg_host = hostList.readlines()

mailBody = ""

alreadyDone = []

for hostname in reg_host:
    hostname = hostname.strip()

    if hostname.startswith('#'):
        continue
    elif hostname.startswith('https://'):
        hostname = hostname.removeprefix("https://")
    elif hostname.startswith('http://'):
        hostname = hostname.removeprefix("http://")
    hostname = hostname.split('/')[0]
    if ":" in hostname:
        hostname = hostname.split(':')[0]

    if hostname not in alreadyDone:
        print(mailBody)
        
        addString = checkPing(hostname)
        if addString is not None:
            mailBody = mailBody + addString

        alreadyDone.append(hostname)

print(mailBody)

mailSubject = "ALERT: Ping Check"

if mailBody != "":
    mailBody = date_time_full() + "\n" + mailBody
    
    sendBasiceMail(config.mailSvr, config.mailUser, config.mailPass, config.mailTo, mailSubject, mailBody)
    print("Email Sent")
    client = Client(config.PushoverUserKey, api_token=config.PushoverAPIToken)
    client.send_message(mailBody, title="Ping Check")
    print("Pushover Sent\n")
else:
    print("No changes to watched sites status\n")


