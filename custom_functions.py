#!/usr/bin/python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket
from datetime import datetime
import pytz

def sendBasiceMail(emailServer, emailUser, emailPassword, emailTo, emailSubject, emailBody):

    # initialize connection to our email server, we will use Outlook here
    smtp = smtplib.SMTP(emailServer, port='587')

    smtp.ehlo()  # send the extended hello to our server
    smtp.starttls()  # tell server we want to communicate with TLS encryption

    smtp.login(emailUser, emailPassword)  # login to our email server
 
    msg = MIMEMultipart()
    msg['From'] = emailUser
    msg['To'] = emailTo
    msg['Subject'] = emailSubject
    body = emailBody
    body = MIMEText(body, 'plain', 'utf-8') # convert the body to a MIME compatible string
    msg.attach(body) # attach it to your main message

    # send our email message 'msg' to our boss
    smtp.sendmail(emailUser, emailTo, msg.as_string())

    smtp.quit()  # finally, don't forget to close the connection

def printLog(logMessage):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print(date_time + ": " + logMessage)


def emailOther(emailServer, emailUser, emailPassword, emailTo, message):
    # message = """\

    #     Subject: Certificate Expiration


    #     The TLS Certificate for your site expires in {days}"""

    email_context = ssl.create_default_context()

    with smtplib.SMTP(emailServer, '587') as server:

        server.ehlo() # BK

        server.starttls(context = email_context)

        server.login(emailUser, emailPassword)

        server.sendmail(emailUser, emailTo, message)

def hostPortStatus(hostname, port, timeout=2):
    port = int(port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((hostname, port))
    if result == 0:
        print("Port", port, "open on host", hostname)
        return(1)
    else:
        print("Port", port, "closed on host", hostname)
        return(0)

def date_time_full():
    newYorkTz = pytz.timezone("America/New_York")
    now = datetime.now(newYorkTz)
    print("now =", now)
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S\n")
    return dt_string