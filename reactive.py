#!/usr/bin/env python
import os
import json
import urllib
import urllib2
import argparse


def get_load_average():  # :rtype : dict
    raw_average = os.getloadavg()
    load_average = {'1min': raw_average[0], '5min': raw_average[1], '15min': raw_average[2]}
    return load_average


def get_terminal_details(user_token, access_token, subdomain):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/get_terminal',
                                        urllib.urlencode({
                                            'user_token': user_token,
                                            'access_token': access_token,
                                            'subdomain': subdomain,
                                        })).read())
    return output


def set_terminal_size(user_token, access_token, container_key, cpu, ram, diskspace):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/edit_terminal',
                                        urllib.urlencode({
                                            'user_token': user_token,
                                            'access_token': access_token,
                                            'container_key': container_key,
                                            'cpu': cpu,
                                            'ram': ram,
                                            'diskspace': diskspace,
                                        })).read())
    return output


def  get_new_size(cpu_size, action): # :rtype : dict
    cpu_index = 0
    terminals = [ {"cpu" : 25, "ram" : 256},
        {"cpu" : 50, "ram" : 800},
        {"cpu" : 100, "ram" : 1600},
        {"cpu" : 200, "ram" : 3200},
        {"cpu" : 400, "ram" : 6400},
        {"cpu" : 800, "ram" : 12800},
        {"cpu" : 1600, "ram" : 25600},
        {"cpu" : 3200, "ram" : 51200}]
    for index in range(0, len(terminals)):
        if str(int(cpu_size)) == str(terminals[index]['cpu']):
            cpu_index = index
    if action == 'increase':
        return  terminals[(cpu_index + 1)]['cpu'],terminals[(cpu_index + 1)]['ram']
    elif action == 'decrease':
        return  terminals[(cpu_index - 1)]['cpu'],terminals[(cpu_index - 1)]['ram']


def decide_cpu(subdomain, cpu_size, load_average, min_size = 100, max_size = 3200, low_margin = 0.2,  up_margin = 0.7, resolution = '15m'):
    print "load average for %s resolution: %s" % (resolution, load_average[resolution])
    if cpu_size < max_size:
        if load_average[resolution] > (cpu_size / 100 * up_margin):
            print 'Load average is higher than expected: %s' % load_average['15min']
            print "Upsizing"
            cpu, ram = get_new_size(cpu_size, 'increase')
            container_key = get_terminal_details(user_token, access_token, subdomain)['terminal']['container_key']
            diskspace = get_terminal_details(user_token, access_token, subdomain)['terminal']['diskspace']
            print set_terminal_size(user_token, access_token, container_key, cpu, ram, diskspace)
        elif cpu_size > min_size:
            if load_average[resolution] <= low_margin:
                print "You're wasting computing power, downsizing"
                cpu, ram = get_new_size(cpu_size, 'decrease')
                container_key = get_terminal_details(user_token, access_token, subdomain)['terminal']['container_key']
                diskspace = get_terminal_details(user_token, access_token, subdomain)['terminal']['diskspace']
                print set_terminal_size(user_token, access_token, container_key, cpu, ram, diskspace)
            else:
                print "Optimus Prime"
        else:
            print "The size of the terminal is already the minimum. Downsize is not possible"
    else:
        print "The size of the terminal is already the maximum. Upsize is not possible"


def get_credentials(utoken, atoken, credsfile):
    if utoken == None and atoken == None:
        try:
            creds = json.load(open(credsfile, 'r'))
            utoken = creds['user_token']
            atoken = creds['access_token']
        except:
            print "Can't open credentials file. \n ", \
                  "You must provide a user token and a access token at least one time, or a valid credentials file"
            exit(127)
    elif (utoken != None and atoken ==None) or (utoken == None and atoken != None):
        print "--utoken AND --atoken parameters must be passed together"
        exit(1)
    else:
        with open(credsfile, 'w') as file:
            json.dump({'user_token':utoken, 'access_token': atoken}, file)
    return utoken, atoken


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("subdomain", help="The subdomain name of your terminal. This is your Terminal.com username plus a number")
    parser.add_argument('-m', '--minsize', type=int, default=50, help="Min size of your resultant instance (25 for micro, 50 for mini, 100 for small...)")
    parser.add_argument('-M', '--maxsize', type=int, default=800, help="Max size of your resultant instance (200 for medium, 400 for xlarge, 800 for 2xlarge...)")
    parser.add_argument('-l', '--lmargin', type=float, default=0.0, help="The lower margin of 15min load average needed to downscale your instance")
    parser.add_argument('-u', '--umargin', type=float, default=0.7, help="The upper margin of 15min load average needed to upscale your instance")
    parser.add_argument('-t', '--res', type=str, default='standard', help="Resolution (15m , 5m and 1m). Accepted values: 'standard', 'high', 'higher'")
    parser.add_argument('-U', '--utoken', type=str, default=None, help='Your Terminal.com user token.')
    parser.add_argument('-K', '--atoken', type=str, default=None, help='Your Terminal.com access token.')
    parser.add_argument('-F', '--creds', type=str, default='creds.json', help='Your json credentials file.')
    args = parser.parse_args()

    subdomain = args.subdomain
    user_token, access_token = get_credentials(args.utoken, args.atoken, args.creds)

    if get_terminal_details(user_token, access_token, subdomain)['terminal']['cpu'] == '2 (max)':
        cpu_size = float('25')
    else:
        cpu_size = float(get_terminal_details(user_token, access_token, subdomain)['terminal']['cpu'])

    if args.res == 'standard':
        resolution = '15min'
    elif args.res == 'high':
        resolution = '5min'
    elif args.res == 'higher':
        resolution = '1min'
    else:
        print "Resolution value not valid"
        exit(1)

    load_average = get_load_average()
    decide_cpu(subdomain, cpu_size, load_average, args.minsize, args.maxsize, args.lmargin, args.umargin, resolution)
