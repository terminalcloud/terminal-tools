#!/usr/bin/env python
import os
import sys
import time
import errno
import logging
import argparse
from terminalcloud import terminal


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def snapshot_terminal(container_key, title, body, readme, tags):
    output = terminal.snapshot_terminal(container_key,body,title,readme,tags)
    request_id = output['request_id']
    time.sleep(1)
    output = terminal.request_progress(request_id)
    while output['status'] != 'success':
        time.sleep(3)
        terminal.request_progress(request_id)
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
        terminal.delete_snapshot(snapshot_id)
    if (len(del_list) > 0):
        with open(cache_file, 'r') as cache:
            alldata = cache.read().splitlines(True)
        with open(cache_file, 'w') as cache:
            cache.writelines(alldata[(len(del_list)):])


def backup(user_token, access_token, logger, subdomain, job_name, delete_threshold, cache_file):
    logger.info('Starting %s %s backup snapshot' % (subdomain, job_name))
    container_key = terminal.get_terminal(subdomain)['terminal']['container_key']
    logger.debug('%s container key: %s' % (subdomain, container_key))
    snapshot_id = \
    snapshot_terminal(container_key,(subdomain + '-' + job_name), "backup snap","backup snap", "backup")['result']
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
    parser.add_argument("-c", "--credsfile", type=str, default="~/.creds.json",
                        help="Credentials Json file [creds.json by default]")
    parser.add_argument("-d", "--delete", type=int, default=3,
                        help="Deletion threshold. How many terminals need to keep before delete [3 by default]")
    parser.add_argument("-l", "--log", type=str,
                        help="Where to locate the log file [default /var/log/subdomain-job_name-snapshots.log]")
    parser.add_argument("-r", "--cache_file", type=str,
                        help="Cache file [default: /var/cache/terminal_backups/subdomain-job_name-snapshots.cache]")
    args = parser.parse_args()

    credsfile = os.path.expanduser(args.credsfile)
    user_token, access_token = terminal.setup_credentials(args.utoken, args.atoken, credsfile)

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
        raw_list = terminal.list_terminals()['terminals']
        for term in range(len(raw_list)):
            print '%s|%s|%s' % (raw_list[term]['name'], raw_list[term]['container_key'], raw_list[term]['status'])
    elif (args.action == "backup"):
        backup(user_token, access_token, logger, args.subdomain, args.job_name, args.delete, cache_file)
        cleanup(user_token, access_token, args.delete, cache_file)
    else:
        print 'Action not valid. Check syntax.'