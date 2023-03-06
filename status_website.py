#!/usr/bin/python3

from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import os
from pathlib import Path
import re
import validators
from pushover import Client
from datetime import datetime

from custom_functions import sendBasiceMail, printLog, date_time_full
import config

# Notes
# https://stackoverflow.com/questions/1949318/checking-if-a-website + ": "-is-up-via-python

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}

websiteList = open ('../configs/website-list.txt')

websiteTimeout = 10

reg_url = websiteList.readlines()

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

def checkSiteRetry(website):
    #!/usr/bin/python3
    import urllib3
    from urllib3.util import Retry
    from urllib3.exceptions import MaxRetryError

    res = re.sub('[^a-zA-Z0-9 \n\.]', '-', website)

    file_path = "/status_website/" + res
    file = Path(file_path)

    http = urllib3.PoolManager()
    retry = Retry(3, raise_on_status=True, status_forcelist=range(500, 600))

    try:
        r = http.request('GET', website, retries=retry)
        if file.exists():
            os.remove(file)
            return (website + ": " + "back online" + "\n")
    except MaxRetryError as m_err:
        print(m_err)
        if file.exists():
            print(website + ": " + "already offline\n")
        else:
            open(file_path, 'a').close()
            print(website + ": " + "offline", end = '')
            return (website + ": " + str(m_err) + "\n")

mailBody = ""

for i in reg_url:
    website2 = i.strip()
    # print(mailBody)
    
    if validators.url(website2):
        addString = checkSiteRetry(website2)
        if addString is not None:
            mailBody = mailBody + addString
    # else:
        # print(website2 + ": " + "url invalid")

# print(mailBody)

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
