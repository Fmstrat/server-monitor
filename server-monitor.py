#!/usr/bin/python

import socket
import smtplib
import sys
import argparse
import time
import datetime
import re


def printD(string, indent):
    strindent = ""
    for x in range(0, indent):
        strindent = strindent + " "
    print("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]" + strindent + " " + string)

parser = argparse.ArgumentParser(
    description='Check if hosts are up.',
    formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=150, width=150))
parser.add_argument('-u', '--smtpuser', help='The SMTP username', default='')
parser.add_argument('-p', '--smtppass', help='The SMTP password', default='')
parser.add_argument('-l', '--smtpsubject', help='The SMTP subject line', default='A service is down!')
parser.add_argument('-o', '--interval', help='The interval in minutes between checks (default 60)', default=60, type=int)
parser.add_argument('-r', '--retry', help='The retry count when a connection fails (default 5)', default=5, type=int)
parser.add_argument('-d', '--delay', help='The retry delay in seconds when a connection fails (default 10)', default=10, type=int)
parser.add_argument('-t', '--timeout', help='The connection timeout in seconds (default 3)', default=3, type=int)
requiredArguments = parser.add_argument_group('required arguments')
requiredArguments.add_argument('-s', '--smtpserver', help='The SMTP server:port', required=True)
requiredArguments.add_argument('-f', '--smtpfrom', help='The FROM email address', required=True)
requiredArguments.add_argument('-k', '--smtpto', help='The TO email address', required=True)
requiredArguments.add_argument('-m', '--monitor', nargs='+', help='The servers to monitor. Format: "<server>:<port> <server>:<port>"', required=True)
args = parser.parse_args()


def isOpen(ip, port):
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

def checkHost(ip, port):
	ipup = False
	for i in range(retry):
		if isOpen(ip, port):
			ipup = True
			break
		else:
                        printD("Not responding, retrying in " + str(delay) + "s...",2)
			time.sleep(delay)
	return ipup

retry = args.retry
delay = args.delay
timeout = args.timeout
while True:
	for host in args.monitor:
		ipport = re.split('[:]', host)
		ip = ipport[0]
		port = int(ipport[1])
		printD("Checking " + ip + ":" + str(port), 0)
		if checkHost(ip, port):
			printD("Up", 2)
		else:
			printD("Down", 2)
			message = "Subject: " + args.smtpsubject + "\n\n"
			message = message + ip + ":" + str(port) + " is down."
			server = smtplib.SMTP(args.smtpserver)
			server.starttls()
			if args.smtpuser != '' and args.smtppass != '':
				server.login(args.smtpuser, args.smtppass)
			server.sendmail(args.smtpfrom, args.smtpto, message)
			server.quit()
	printD("Waiting " + str(args.interval) + " minutes for next check.", 0)
	time.sleep(args.interval * 60)
