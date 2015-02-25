#!/usr/bin/env python
import json
import time
import urllib
import urllib2
import argparse

def get_credentials(utoken, atoken, credsfile):
    if utoken is None and atoken is None:
        try:
            creds = json.load(open(credsfile, 'r'))
            utoken = creds['user_token']
            atoken = creds['access_token']
        except:
            print "Can't open credentials file. \n ", \
                "You must provide a user token and a access token at least one time, or a valid credentials file"
            exit(127)
    elif (utoken is not None and atoken is None) or (utoken is None and atoken is not None):
        print "--utoken AND --atoken parameters must be passed together"
        exit(1)
    else:
        with open(credsfile, 'w') as cfile:
            json.dump({'user_token': utoken, 'access_token': atoken}, cfile)
    return utoken, atoken


def get_cpu_and_ram(size):
    cpu = None
    cpu_index = 0
    terminals = [{"size": "micro", "cpu": "2 (max)", "ram": "256"},
                 {"size": "mini", "cpu": "50", "ram": "800"},
                 {"size": "small", "cpu": "100", "ram": "1600"},
                 {"size": "medium", "cpu": "200", "ram": "3200"},
                 {"size": "xlarge", "cpu": "400", "ram": "6400"},
                 {"size": "2xlarge", "cpu": "800", "ram": "12800"},
                 {"size": "4xlarge", "cpu": "1600", "ram": "25600"},
                 {"size": "8xlarge", "cpu": "3200", "ram": "51200"}]
    for index in range(0, len(terminals)):
        if str(size) == str(terminals[index]['size']):
            print str(terminals[index]['size'])
            cpu = str(terminals[index]['cpu'])
            ram = str(terminals[index]['ram'])
    if cpu:
        return cpu, ram
    else:
        print "Terminal size not found"
        exit(0)


def start_snapshot(name, snapshot_id, utoken, atoken, cpu, ram, script):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/start_snapshot',
                                        urllib.urlencode({
                                            'user_token': utoken,
                                            'access_token': atoken,
                                            'snapshot_id': snapshot_id,
                                            'cpu': cpu,
                                            'ram': ram,
                                            'temporary': 'false',
                                            'name': name,
                                            'startup_script': script,
                                            'autopause': False,
                                        })).read())
    request_id = output['request_id']
    print 'request_id:', request_id

    while output.get('status') != 'success':
        output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/request_progress',
                                            urllib.urlencode({
                                                'request_id': request_id,
                                            })).read())
        print '.'
        time.sleep(1)

    container_key = output['result']['container_key']
    subdomain = output['result']['subdomain']
    container_ip = output['result']['container_ip']

    return container_key, container_ip, subdomain


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="The name of your new Terminal")
    parser.add_argument("snapshot_id", help="The ID of the snapshot that you want to start")
    parser.add_argument("script", help="A string with the commands to be executed")
    parser.add_argument('-s', '--script', type=str, help="The startup command string")
    parser.add_argument('-u', '--utoken', type=str, help="Your user token (see https://www.terminal.com/settings/api)")
    parser.add_argument('-a', '--atoken', type=str,
                        help="Your access token (see https://www.terminal.com/settings/api)")
    parser.add_argument('-f', '--creds', type=str, default='creds.json',
                        help="Your credentials file (creds.json by default)")
    parser.add_argument('-z', '--size', type=str, default='micro')
    args = parser.parse_args()

    snapshot_id = args.snapshot_id
    utoken, atoken = get_credentials(args.utoken, args.atoken, args.creds)
    cpu, ram = get_cpu_and_ram(args.size)
    c_key, c_ip, subdomain = start_snapshot(args.name, args.snapshot_id, utoken, atoken, cpu, ram, args.script)
    print 'Key: ', c_key
    print 'IP: ', c_ip
    print 'Subdomain: ', subdomain