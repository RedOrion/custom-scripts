#!/usr/bin/python3

from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import os
from pathlib import Path
import re
import validators
from pushover import Client
from datetime import datetime
import sys, getopt

from custom_functions import sendBasiceMail, printLog, date_time_full
import config

# Notes
# https://stackoverflow.com/questions/1949318/checking-if-a-website + ": "-is-up-via-python

def checkSite(website):
    req = Request(url=website, headers=headers)

    # Gets url of site
    #res = re.split("/", website, 2)[-1]
    
    # Get full url with special characters replaced with -
    res = re.sub('[^a-zA-Z0-9 \n\.]', '-', website)

    # Gets http or https
    #siteType = website.split(":")[0]

    file_path = "/status_website/" + res
    file = Path(file_path)
    try:
        response = urlopen(req, timeout=websiteTimeout)
        # print(response)
    except HTTPError as e:
        # print(website + ": " + 'couldn\'t fulfill the request.')
        print(website + ": " + 'Error code: ' + str(e.code) + '\n')

        if file.exists():
            print(website + ": " + "already offline\n")
        else:
            open(file_path, 'a').close()
            print(website + ": " + "offline", end = '')
            return (website + ": " + str(e.code) + "\n")
    except URLError as e:
        # print(website + ": " + 'We failed to reach a server.')
        print(website + ": " + str(e.reason))

        if file.exists():
            print(website + ": " + "already offline", end = '')
        else:
            open(file_path, 'a').close()
            print(website + ": " + "offline")
            return (website + ": " + str(e.reason) + "\n")
    else:
        print(website + ": " + 'online', end = '')
        if file.exists():
            os.remove(file)
            return (website + ": " + "back online" + "\n")

def main(argv):
    websiteList = ''
    websiteTimeout = 10

    try:
        opts, args = getopt.getopt(argv,"hl:",["list="])
    except getopt.GetoptError:
        print ("status_website.py -l <websiteList>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print ("status_website.py -l <websiteList>")
        elif opt in ("-l", "--list"):
            websiteList = open (arg)

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}

    reg_url = websiteList.readlines()

    mailBody = ""

    for i in reg_url:
        website2 = i.strip()
        print(mailBody)
        
        if validators.url(website2):
            addString = checkSite(website2)
            if addString is not None:
                mailBody = mailBody + addString
        else:
            print(website2 + ": " + "url invalid")

    print(mailBody)

    mailSubject = "ALERT: Website Status"

    if mailBody != "":
        mailBody = date_time_full() + "\n" + mailBody

        sendBasiceMail(config.mailSvr, config.mailUser, config.mailPass, config.mailTo, mailSubject, mailBody)
        print("Email Sent")
        client = Client(config.PushoverUserKey, api_token=config.PushoverAPIToken)
        client.send_message(mailBody, title="Website Status")
        print("Pushover Sent\n")
    else:
        print("No changes to watched sites status")

if __name__ == "__main__":
    main(sys.argv[1:])