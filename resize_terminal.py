#!/usr/bin/env python
import json
import urllib
import urllib2
import argparse


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


def get_new_size(cpu_size, action):  # :rtype : dict
    cpu_index = 0
    terminals = [{"cpu": 25, "ram": 256},
                 {"cpu": 50, "ram": 800},
                 {"cpu": 100, "ram": 1600},
                 {"cpu": 200, "ram": 3200},
                 {"cpu": 400, "ram": 6400},
                 {"cpu": 800, "ram": 12800},
                 {"cpu": 1600, "ram": 25600},
                 {"cpu": 3200, "ram": 51200}]
    for index in range(0, len(terminals)):
        if str(int(cpu_size)) == str(terminals[index]['cpu']):
            cpu_index = index
    if action == 'increase':
        return terminals[(cpu_index + 1)]['cpu'], terminals[(cpu_index + 1)]['ram']
    elif action == 'decrease':
        return terminals[(cpu_index - 1)]['cpu'], terminals[(cpu_index - 1)]['ram']


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


def upsize_terminal(cpu_size):
    print "upsizing"
    cpu, ram = get_new_size(cpu_size, 'increase')
    container_key = get_terminal_details(user_token, access_token, subdomain)['terminal']['container_key']
    diskspace = get_terminal_details(user_token, access_token, subdomain)['terminal']['diskspace']
    return set_terminal_size(user_token, access_token, container_key, cpu, ram, diskspace)


def downsize_terminal(cpu_size):
    print "downsizing"
    cpu, ram = get_new_size(cpu_size, 'decrease')
    container_key = get_terminal_details(user_token, access_token, subdomain)['terminal']['container_key']
    diskspace = get_terminal_details(user_token, access_token, subdomain)['terminal']['diskspace']
    return set_terminal_size(user_token, access_token, container_key, cpu, ram, diskspace)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="upsize or downsize")
    parser.add_argument("subdomain",
                        help="The subdomain name of your terminal. This is your Terminal.com username plus a number")
    parser.add_argument('-m', '--minsize', type=int, default=50,
                        help="Min size of your resultant instance (25 for micro, 50 for mini, 100 for small...)")
    parser.add_argument('-M', '--maxsize', type=int, default=1600,
                        help="Max size of your resultant instance (200 for medium, 400 for xlarge, 800 for 2xlarge...)")
    parser.add_argument('-U', '--utoken', type=str, default=None, help='Your Terminal.com user token.')
    parser.add_argument('-K', '--atoken', type=str, default=None, help='Your Terminal.com access token.')
    parser.add_argument('-F', '--creds', type=str, default='/etc/creds.json', help='Your json credentials file.')
    args = parser.parse_args()

    subdomain = args.subdomain
    user_token, access_token = get_credentials(args.utoken, args.atoken, args.creds)

    if get_terminal_details(user_token, access_token, subdomain)['terminal']['cpu'] == '2 (max)':
        cpu_size = float('25')
    else:
        cpu_size = float(get_terminal_details(user_token, access_token, subdomain)['terminal']['cpu'])

    if args.action == 'upsize':
        if cpu_size <= args.maxsize:
            upsize_terminal(cpu_size)
        else:
            print "Max Terminal size reached"
    elif args.action == 'downsize':
        if cpu_size >= args.minsize:
            downsize_terminal(cpu_size)
        else:
            print "Min Terminal size reached"
    else:
        print 'option not found'
        exit(1)