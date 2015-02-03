#!/usr/bin/env python
import os
import sys
import json
import time
import errno
import urllib
import urllib2
import logging
import argparse


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


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


def list_terminals(user_token, access_token):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/list_terminals',
                                        urllib.urlencode({
                                            'user_token': user_token,
                                            'access_token': access_token,
                                        })).read())
    return output


def get_terminal(user_token, access_token, subdomain):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/get_terminal',
                                        urllib.urlencode({
                                            'user_token': user_token,
                                            'access_token': access_token,
                                            'subdomain': subdomain,
                                        })).read())
    return output


def print_terminals(list_of_terminals):
    for i in range(len(list_of_terminals['terminals'])):
        terminal_name = list_of_terminals['terminals'][i]['name']
        terminal_key = list_of_terminals['terminals'][i]['container_key']
        terminal_status = list_of_terminals['terminals'][i]['status']
        print terminal_name, ' - ', terminal_key, '-', terminal_status


def delete_snapshot(snapshot_id, user_token, access_token):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/delete_snapshot',
                                        urllib.urlencode({
                                            'container_key': snapshot_id,
                                            'user_token': user_token,
                                            'snapshot_id': access_token,
                                        })).read())
    return output


def snapshot_terminal(container_key, user_token, access_token, title, body, readme, tags):
    output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/snapshot_terminal',
                                        urllib.urlencode({
                                            'container_key': container_key,
                                            'user_token': user_token,
                                            'access_token': access_token,
                                            'title': title,
                                            'body': body,
                                            'readme': readme,
                                            'tags': tags,
                                            'public': False,
                                        })).read())
    request_id = output['request_id']

    while output.get('status') != 'success':
        output = json.loads(urllib2.urlopen('https://www.terminal.com/api/v0.1/request_progress',
                                            urllib.urlencode({'request_id': request_id, })).read())
        time.sleep(1)
    time.sleep(5)
    return output


def initialize_logger(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    debug_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler(sys.stdout)
    debug_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)
    logger.addHandler(console_handler)
    return logger


def cleanup(user_token, access_token, delete_threshold, cache_file):
    line_num = sum(1 for line in open(cache_file) if line.rstrip())
    head_num = line_num - delete_threshold
    with open(cache_file) as cache:
        del_list = [next(cache) for x in xrange(head_num)]
    for snapshot_id in range(len(del_list)):
        logger.info("Deleting snapshot %s" % del_list[snapshot_id])
        delete_snapshot(user_token, access_token, snapshot_id)
    if (len(del_list) > 0):
        with open(cache_file, 'r') as cache:
            alldata = cache.read().splitlines(True)
        with open(cache_file, 'w') as cache:
            cache.writelines(alldata[(len(del_list)):])


def backup(user_token, access_token, logger, subdomain, job_name, delete_threshold, cache_file):
    logger.info('Starting %s %s backup snapshot' % (subdomain, job_name))
    container_key = get_terminal(user_token, access_token, subdomain)['terminal']['container_key']
    logger.debug('%s container key: %s' % (subdomain, container_key))
    snapshot_id = \
    snapshot_terminal(container_key, user_token, access_token, (subdomain + '-' + job_name), "backup snap",
                      "backup snap", "backup")['result']
    print snapshot_id
    logger.info('%s snapshoted in %s' % (subdomain, snapshot_id))
    with open(cache_file, "a") as cache:
        logger.debug('Writing to cache file %s, snapshot_id: %s' % (cache_file, snapshot_id))
        cache.write('%s \n' % snapshot_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="Desired action [list, backup]")
    parser.add_argument("-s", "--subdomain", help="Subdomain of the Terminal to be backed up")
    parser.add_argument("-j", "--job_name", type=str,
                        help="Unique backup job name [could be daily, weekly, monthly... etc]")
    parser.add_argument("-u", "--utoken", type=str, help="User Token")
    parser.add_argument("-a", "--atoken", type=str, help="Access Token")
    parser.add_argument("-c", "--credsfile", type=str, default="creds.json",
                        help="Credentials Json file [creds.json by default]")
    parser.add_argument("-d", "--delete", type=int, default=3,
                        help="Deletion threshold. How many terminals need to keep before delete [3 by default]")
    parser.add_argument("-l", "--log", type=str,
                        help="Where to locate the log file [default /var/log/subdomain-job_name-snapshots.log]")
    parser.add_argument("-r", "--cache_file", type=str,
                        help="Cache file [default: /var/cache/terminal_backups/subdomain-job_name-snapshots.cache]")
    args = parser.parse_args()

    user_token, access_token = get_credentials(args.utoken, args.atoken, args.credsfile)

    if args.log:
        logfile = args.log
    else:
        logfile = ('/var/log/%s-%s-snapshots.log' % (args.subdomain, args.job_name))

    if args.cache_file:
        cache_file = args.cache_file
    else:
        mkdir_p('/var/cache/terminal_backups/')
        cache_file = ('/var/cache/terminal_backups/%s-%s-snapshots.cache' % (args.subdomain, args.job_name))

    logger = initialize_logger(logfile)

    if (args.action == "list"):
        print_terminals(list_terminals(user_token, access_token))
    elif (args.action == "backup"):
        backup(user_token, access_token, logger, args.subdomain, args.job_name, args.delete, cache_file)
        cleanup(user_token, access_token, args.delete, cache_file)
    else:
        print 'Action not valid. Check syntax.'