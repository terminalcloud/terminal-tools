#!/usr/bin/env python

import argparse
from terminalcloud import terminal


def link_terminals(term, src_term, ports):
    try:
        ckey = terminal.get_terminal(subdomain=term)['terminal']['container_key']
        links = [{"port": ports[port], "source": src_term} for port in range(len(ports))]
        output = terminal.add_terminal_links(ckey, links)
        return output['success']
    except Exception, e:
        return e

def unlink_terminals(term, src_term, ports):
    try:
        ckey = terminal.get_terminal(subdomain=term)['terminal']['container_key']
        links = [{"port": ports[port], "source": src_term} for port in range(len(ports))]
        output = terminal.remove_terminal_links(ckey,links)
        return output['success']
    except Exception, e:
        return e

def clean_terminal_links(term):
    try:
        ckey = terminal.get_terminal(subdomain=term)['terminal']['container_key']
        links = terminal.list_terminal_access(ckey)['links']
        flinks = map(lambda x: {'port':x.split(':')[0],'source':x.split(':')[-1]},links)
        terminal.remove_terminal_links(ckey,flinks)
        return 'success'
    except Exception, e:
        print e

def show_terminal_links(term):
    try:
       ckey = terminal.get_terminal(subdomain=term)['terminal']['container_key']
       links = terminal.list_terminal_access(ckey)['links']
       flinks = map(lambda x: {'port':x.split(':')[0],'source':x.split(':')[-1]},links)
       print '%s\t\t%s' % ('Source','Port')
       print '---------------------'
       for link in range(len(flinks)):
           print '%s\t%s' % (flinks[link]['source'],flinks[link]['port'])
    except Exception, e:
        return e

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, help="link, unlink, clean, show")
    parser.add_argument("terminal", type=str, help="Terminal to be modified")
    parser.add_argument("-s", "--source", type=str, default=None, help="Source Terminal. (subdomain)")
    parser.add_argument("-p", "--ports", type=str, default='*', help="Ports, separated by comma. By default '*' (all ports)")
    parser.add_argument('-u', '--utoken', type=str, help="Your user token (see https://www.terminal.com/settings/api)")
    parser.add_argument('-a', '--atoken', type=str, help="Your access token (see https://www.terminal.com/settings/api)")
    parser.add_argument('-c', '--creds', type=str, default='creds.json', help="Credentials Json file. By default 'creds.json'")
    args = parser.parse_args()

    try:
        terminal.setup_credentials(args.utoken, args.atoken, args.creds)
    except Exception, e:
        print "Cannot setup your credentials. Check if they're correct"
        exit(e)

    if args.action == 'link':
        print link_terminals(args.terminal, args.source, args.ports.split(','))
    else:
        if args.action == 'unlink':
            print unlink_terminals(args.terminal, args.source, args.ports.split(','))
        else:
            if args.action == 'clean':
                clean_terminal_links(args.terminal)
            else:
                if args.action == 'show':
                    show_terminal_links(args.terminal)
                else:
                    exit('Action not found. Exiting.')