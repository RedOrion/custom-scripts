#!/usr/bin/python3

from email.policy import default
from urllib.request import Request, urlopen, ssl, socket
from urllib.error import URLError, HTTPError
import json
from datetime import datetime
import socket
from pushover import Client
import sys, getopt

from custom_functions import sendBasiceMail, hostPortStatus, date_time_full
import config

# Notes
# https://www.activestate.com/blog/how-to-manage-tls-certificate-expiration-with-python/

def getCertificate(hostname,port):
    context = ssl.create_default_context()
    # ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL
    try:
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                certificate = ssock.getpeercert()
                print(certificate)
                return certificate
    except:
        return "Failure: Unable to retrieve certificate"

def main(argv):
    defaultPort = '443'

    websiteList = ''

    argv = ''

    try:
        opts, args = getopt.getopt(argv,"hl:",["list="])
    except getopt.GetoptError:
        print ("status_certificate.py -l <websiteList>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print ("status_certificate.py -l <websiteList>")
        elif opt in ("-l", "--list"):
            websiteList = open (arg)

    print(websiteList)

    reg_url = websiteList.readlines()

    mailBody = ""

    for hostname in reg_url:
        port = defaultPort
        if hostname.strip():
            hostname = hostname.strip()
            if hostname.startswith('#'):
                continue
            elif hostname.startswith('https://'):
                hostname = hostname.removeprefix("https://")
                if "/" in hostname:
                    hostname = hostname.split('/')[0]
                if ":" in hostname:
                    port = hostname.split(':')[1]
                    hostname = hostname.split(':')[0]
                hostname = hostname.strip()
                alert = f"{hostname}: https site"
                print(alert)
                if hostPortStatus(hostname,port) == 1:
                    certificate = getCertificate(hostname,defaultPort)
                    print(certificate)
                    if "Failure" not in certificate:
                        certExpires = datetime.strptime(certificate['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        print(certExpires)
                        daysToExpiration = (certExpires - datetime.now()).days
                        if daysToExpiration == 7 or daysToExpiration == 3 or daysToExpiration == 1:
                            if daysToExpiration== 1:
                                days = "1 day"
                            else:
                                days = str(daysToExpiration) + " days"
                            
                            addString = f"\n{hostname} expires in {days}"
                            mailBody = mailBody + addString
                else:
                    alert = f"{hostname}: offline"
                    print(alert)
            elif hostname.startswith('http://'):
                alert = f"{hostname}: http only"
                print(alert)
            else:
                alert = f"{hostname}: not a url/website"
                print(alert)
    
    mailSubject = "ALERT: Certificate Expiration"

    print(mailBody)

    if mailBody != "":
        mailBody = date_time_full() + "\n" + mailBody

        sendBasiceMail(config.mailSvr, config.mailUser, config.mailPass, config.mailTo, mailSubject, mailBody)
        print("Email Sent")
        client = Client(config.PushoverUserKey, api_token=config.PushoverAPIToken)
        client.send_message(mailBody, title="Certificate Expirations")
        print("Pushover Sent")
    else:
        print("No changes to watched sites status")


if __name__ == "__main__":
    main(sys.argv[1:])