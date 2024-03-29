#!/usr/bin/python

import socket
import smtplib
import sys
import argparse
import time
import datetime
import re
import httplib
import urllib
import os
import distutils.spawn
import threading
import time

def printD(string, indent):
    strindent = ""
    for x in range(0, indent):
        strindent = strindent + " "
    print("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]" + strindent + " " + string)

parser = argparse.ArgumentParser(
    description='Check if hosts are up.',
    formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=150, width=150))
parser.add_argument('-s', '--smtpserver', help='The SMTP server:port', default='')
parser.add_argument('-f', '--smtpfrom', help='The FROM email address', default='')
parser.add_argument('-k', '--smtpto', help='The TO email address', default='')
parser.add_argument('-u', '--smtpuser', help='The SMTP username', default='')
parser.add_argument('-p', '--smtppass', help='The SMTP password', default='')
parser.add_argument('-l', '--smtpsubject', help='The SMTP subject line', default='Service status changed!')
parser.add_argument('-o', '--interval', help='The interval in minutes between checks (default 15)', default=15, type=int)
parser.add_argument('-r', '--retry', help='The retry count when a connection fails (default 5)', default=5, type=int)
parser.add_argument('-d', '--delay', help='The retry delay in seconds when a connection fails (default 10)', default=10, type=int)
parser.add_argument('-t', '--timeout', help='The connection timeout in seconds (default 3)', default=3, type=int)
parser.add_argument('-y', '--pushoverapi', help='The pushover.net API key', default='')
parser.add_argument('-z', '--pushoveruser', help='The pushover.net user key', default='')
requiredArguments = parser.add_argument_group('required arguments')
requiredArguments.add_argument('-m', '--monitor', nargs='+', help='The servers to monitor. Format: "<server>:<port> <server>:<port>:udp"', required=True)
args = parser.parse_args()

def tcpCheck(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

def udpCheck(ip, port):
    cmd = "nc -vzu -w " + str(timeout) + " " + ip + " " + str(port) + " 2>&1"
    res = os.popen('DATA=$('+cmd+');echo -n $DATA').read()
    if res != "":
        return True
    else:
        return False

def checkHost(host):
    ipup = False
    for i in range(retry):
        if host["conntype"] == "udp":
            if udpCheck(host["ip"], host["port"]):
                ipup = True
                break
            else:
                printD("No response from " + host["ip"] + ":" + str(host["port"]) + ":" + host["conntype"] + ", retrying in " + str(delay) + "s...", 0)
                time.sleep(delay)
        else:
            if tcpCheck(host["ip"], host["port"]):
                ipup = True
                break
            else:
                printD("No response from " + host["ip"] + ":" + str(host["port"]) + ":" + host["conntype"] + ", retrying in " + str(delay) + "s...", 0)
                time.sleep(delay)
    return ipup

def sendMessage():
    message = "Subject: " + args.smtpsubject + "\r\n"
    message += "From: " + args.smtpfrom + "\r\n"
    message += "To: " + args.smtpto + "\r\n"
    message += "\r\n"
    for change in changes:
        message += change + ".\r\n"
    if args.smtpserver != '' and args.smtpfrom != '' and args.smtpto != '':
        printD("Sending SMTP message",2)
        server = smtplib.SMTP(args.smtpserver)
        server.starttls()
        if args.smtpuser != '' and args.smtppass != '':
            server.login(args.smtpuser, args.smtppass)
        server.sendmail(args.smtpfrom, args.smtpto, message)
        server.quit()
    if args.pushoverapi != '' and args.pushoveruser != '':
        printD("Sending Pushover message",2)
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
            urllib.urlencode({
                "token": args.pushoverapi,
                "user": args.pushoveruser,
                "message": message,
                "sound": "falling",
            }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

def parseHost(host):
    prestatus = host["status"]
    printD("Checking " + host["ip"] + ":" + str(host["port"]) + ":" + host["conntype"] + "...", 0)
    if checkHost(host):
        host["status"] = "up"
        if prestatus == "down":
            changes.append(host["ip"] + ":" + str(host["port"]) + ":" + host["conntype"] + " is " + host["status"])
    else:
        host["status"] = "down"
        if prestatus == "up":
            changes.append(host["ip"] + ":" + str(host["port"]) + ":" + host["conntype"] + " is " + host["status"])
    printD("Status of " + host["ip"] + ":" + str(host["port"]) + ":" + host["conntype"] + ": " + host["status"], 0)

nc = distutils.spawn.find_executable("nc")
if not nc:
    printD("Missing `nc`. Exiting",0)
    sys.exit()

retry = args.retry
delay = args.delay
timeout = args.timeout
hosts = []
for host in args.monitor:
    conntype = "tcp"
    ipport = re.split('[:]', host)
    ip = ipport[0]
    port = int(ipport[1])
    if len(ipport) > 2:
        conntype = ipport[2]
    hosts.append({"ip":ip, "port":port, "conntype":conntype, "status":"unknown"})

while True:
    changes = []
    threads = []
    for host in hosts:
        t = threading.Thread(target=parseHost, args=(host,))
        threads.append(t)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if len(changes) > 0:
        sendMessage()
        del changes[:]
    del threads[:]
    printD("Waiting " + str(args.interval) + " minutes for next check.", 0)
    time.sleep(args.interval * 60)
