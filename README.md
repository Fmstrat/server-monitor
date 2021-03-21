# server-monitor
Checks if ips:ports are up and running.

## Usage
```
# wget https://raw.githubusercontent.com/Fmstrat/server-monitor/master/server-monitor.py
# ./server-monitor.py --help
usage: server-monitor.py [-h] [-u SMTPUSER] [-p SMTPPASS] [-l SMTPSUBJECT] [-o INTERVAL] [-r RETRY] [-d DELAY] [-t TIMEOUT] -s SMTPSERVER -f SMTPFROM
                         -k SMTPTO -m MONITOR [MONITOR ...]

Check if hosts are up.

optional arguments:
  -h, --help                                                 show this help message and exit
  -s SMTPSERVER, --smtpserver SMTPSERVER                     The SMTP server:port
  -f SMTPFROM, --smtpfrom SMTPFROM                           The FROM email address
  -k SMTPTO, --smtpto SMTPTO                                 The TO email address
  -u SMTPUSER, --smtpuser SMTPUSER                           The SMTP username
  -p SMTPPASS, --smtppass SMTPPASS                           The SMTP password
  -l SMTPSUBJECT, --smtpsubject SMTPSUBJECT                  The SMTP subject line
  -o INTERVAL, --interval INTERVAL                           The interval in minutes between checks (default 60)
  -r RETRY, --retry RETRY                                    The retry count when a connection fails (default 5)
  -d DELAY, --delay DELAY                                    The retry delay in seconds when a connection fails (default 10)
  -t TIMEOUT, --timeout TIMEOUT                              The connection timeout in seconds (default 3)
  -y PUSHOVERAPI, --pushoverapi PUSHOVERAPI                  The pushover.net API key
  -z PUSHOVERUSER, --pushoveruser PUSHOVERUSER               The pushover.net user key


required arguments:
  -m MONITOR [MONITOR ...], --monitor MONITOR [MONITOR ...]  The servers to monitor. Format: "<server>:<port> <server>:<port>"
```

## Docker
The following example is for docker-compose.
```
  server-monitor:
    image: nowsci/server-monitor
    container_name: server-monitor
    volumes:
      - /etc/localtime:/etc/localtime:ro
    environment:
      - OPTIONS=--smtpserver mail:25 --smtpfrom user@domain.tld --smtpto user@domain.tld --monitor google.com:443 microsoft.com:443
    restart: "no"
```
