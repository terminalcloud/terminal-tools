#!/usr/bin/env python
import sys
import json
import time
import urllib
import hashlib
import urllib2

username = 'qmaxquique'


def list_terminals(user_token, access_token):
    print 'Asking for information...'
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/list_terminals',
                                        urllib.urlencode({
                                            'user_token': user_token,
                                            'access_token': access_token,
                                        })).read())
    return output


def list_snapshots(user_token, access_token, username):
    print 'Asking for information...'
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/list_snapshots',
                                        urllib.urlencode({
                                            'user_token': user_token,
                                            'access_token': access_token,
                                            'username': username,
                                            'order': 'date',
                                        })).read())
    return output


def snapshot_terminal(container_key, title, body, readme, tags, public):
    print 'Snapshotting...'
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/snapshot_terminal',
                                        urllib.urlencode({
                                            'container_key': container_key,
                                            'user_token': user_token,
                                            'access_token': access_token,
                                            'title': title,
                                            'body': body,
                                            'readme': readme,
                                            'tags': tags,
                                        })).read())
    request_id = output['request_id']
    print 'request_id', request_id

    while output.get('status') != 'success':
        output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/request_progress',
                                            urllib.urlencode({'request_id': request_id, })).read())
        time.sleep(1)
    return output


def rm_snapshot(user_token, access_token, snap_id):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/delete_snapshot',
                                        urllib.urlencode({
                                            'user_token': user_token,
                                            'access_token': access_token,
                                            'snapshot_id': snap_id,
                                        })).read())
    return output


def get_usage(user_token, access_token):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/terminal_usage_history',
                                        urllib.urlencode({
                                            'user_token': user_token,
                                            'access_token': access_token,
                                        })).read())
    return output


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
    elif (utoken != None and atoken == None) or (utoken == None and atoken != None):
        print "--utoken AND --atoken parameters must be passed together"
        exit(1)
    else:
        with open(credsfile, 'w') as file:
            json.dump({'user_token': utoken, 'access_token': atoken}, file)
    return utoken, atoken


if __name__ == '__main__':
    user_token, access_token = get_credentials(None, None, 'creds.json')
    action = sys.argv[1]
    if action == 'list':
        list_of_terminals = list_terminals(user_token, access_token)
        for i in range(len(list_of_terminals['terminals'])):
            terminal_name = list_of_terminals['terminals'][i]['name']
            terminal_key = list_of_terminals['terminals'][i]['container_key']
            terminal_status = list_of_terminals['terminals'][i]['status']
            print terminal_name, ' - ', terminal_key, '-', terminal_status
    elif action == 'snap':
        container_key = sys.argv[2]
        title = sys.argv[3]
        output = snapshot_terminal(container_key, title, "automatic snapshot", "automatic snapshot", "auto", "false")
        print 'Snap URL: https://www.terminal.com/snapshot/%s' % output['result']
    elif action == 'list-snaps':
        output = list_snapshots(user_token, access_token, username)
        for i in range(len(output['snapshots'])):
            print output['snapshots'][i]['title'], '|', output['snapshots'][i]['id']
    elif action == 'rm-snap':
        snap_id = sys.argv[2]
        output = rm_snapshot(user_token, access_token, snap_id)
        print output['status']
    elif action == 'raw_list':
        output = list_terminals(user_token, access_token)
        print output
    elif action == 'get_usage':
        output = get_usage(user_token, access_token)
        print output
