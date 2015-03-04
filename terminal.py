#!/usr/bin/env python
import json
import urllib
import urllib2

# Authentication
def setup_credentials(utoken, atoken, credsfile):
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
    global user_token
    global access_token
    user_token, access_token = str(utoken), str(atoken)
    return user_token, access_token


# Manage Request
def make_request(call, params=None, url=None, headers=None, raw=False):
    try:
        if url is None:
            url = 'https://api.terminal.com/v0.2/%s' % call
        if headers is None:
            headers={'user-token': user_token,'access-token':access_token, 'Content-Type':'application/json'}
        if params is None:
            data = json.dumps({})
        else:
            parsed_params={}
            for key in params.keys():
                if params[key] is not None:
                    parsed_params.update({key:params[key]})
            if raw:
                data = urllib.urlencode(parsed_params)
                headers.pop('Content-Type')
            else:
                data = json.dumps(parsed_params)
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        results = json.loads(response.read())
        results.update({u'success':True})
        map(str,results)
        return results
    except urllib2.HTTPError as e:
        return json.loads(e.read())

# Browse Snapshots and Users
def get_snapshot(snapshot_id):
    call = 'get_snapshot'
    params = {"snapshot_id":snapshot_id}
    response = make_request(call, params)
    return response

def get_profile(username):
    call = 'get_profile'
    params = {"username":username}
    response = make_request(call, params)
    return response

def list_public_snapshots(username, tag=None, featured=None, title=None, page=0, perPage=1000 ,sortby='popularity'):
    call = 'list_public_snapshots'
    params = {'username':username, 'tag':tag, 'featured':featured, 'title':title,\
              'page':page, 'perPage':perPage, 'sortby':sortby}
    response = make_request(call, params)
    return response

def count_public_snapshots(username=None, tag=None, featured=None, title=None):
    call = 'count_public_snapshots'
    params = {'username':username, 'tag':tag, 'featured':featured, 'title':title}
    response = make_request(call, params)
    return response


# Create and Manage Terminals
def list_terminals():
    call = 'list_terminals'
    params = None
    response = make_request(call, params)
    return response

def get_terminal(container_key=None, subdomain=None):
    if (container_key is None and subdomain is None):
        return {'error':'container_key OR subdomain must be passed'}
    call = 'get_terminal'
    params = {'container_key':container_key, 'subdomain':subdomain}
    response = make_request(call, params)
    return response


def start_snapshot(snapshot_id, instance_type=None, temporary=None, name=None, autopause=None, startup_script=None):
    call = 'start_snapshot'
    params = {'snapshot_id': snapshot_id, 'instance_type': instance_type, 'temporary': temporary, 'name': name,
              'autopause': autopause, 'startup_script': startup_script}
    response = make_request(call, params)
    return response

def delete_terminal(container_key):
    call = 'delete_terminal'
    params = {'container_key':container_key}
    response = make_request(call, params)
    return  response

def restart_terminal(container_key):
    call = 'restart_terminal'
    params = {'container_key':container_key}
    response = make_request(call, params)
    return  response

def pause_terminal(container_key):
    call = 'pause_terminal'
    params = {'container_key':container_key}
    response = make_request(call, params)
    return  response

def resume_terminal(container_key):
    call = 'resume_terminal'
    params = {'container_key':container_key}
    response = make_request(call, params)
    return  response

def edit_terminal(container_key, instance_type=None, diskspace=None, name=None, custom_data=None):
    call = 'edit_terminal'
    params = {'container_key':container_key, 'instance_type':instance_type, 'diskspace':diskspace, \
              'name':name, 'custom_data':custom_data}
    response = make_request(call, params)
    return response


# Create and Manage Snapshots
def list_snapshots(tag=None, featured=None, title=None, page=0, perPage=1000 ,sortby='popularity'):
    call = 'list_snapshots'
    params = {'tag':tag, 'featured':featured, 'title':title,'page':page, 'perPage':perPage, 'sortby':sortby}
    response = make_request(call, params)
    return response

def count_snapshots(tag=None, featured=None, title=None):
    call = 'count_snapshots'
    params = {'tag':tag, 'featured':featured, 'title':title}
    response = make_request(call, params)
    return response

def delete_snapshot(snapshot_id):
    call = 'delete_snapshot'
    params = {'snapshot_id':snapshot_id}
    response = make_request(call, params)
    return  response

def edit_snapshot(snapshot_id, body=None, title=None, readme=None, tags=None):
    call = 'edit_snapshot'
    params = {'snapshot_id':snapshot_id, 'body':body, 'title':title, 'readme':readme, 'tags':tags}
    response = make_request(call, params)
    return response

def snapshot_terminal(container_key, body=None, title=None, readme=None, tags=None, public=None):
    call = 'snapshot_terminal'
    params = {'container_key':container_key, 'body':body, 'title':title, 'readme':readme, \
              'tags':tags, 'public':public}
    response = make_request(call, params)
    return response


# Manage Terminal Access
def add_terminal_links(container_key, links):
    call = 'add_terminal_links'
    params= {'container_key':container_key, 'links':links}
    response = make_request(call, params)
    return response

def remove_terminal_links(container_key, links):
    call = 'remove_terminal_links'
    params= {'container_key':container_key, 'links':links}
    response = make_request(call, params)
    return response

def list_terminal_access(container_key):
    call = 'list_terminal_access'
    params = {'container_key':container_key}
    response = make_request(call, params)
    return  response

def edit_terminal_access(container_key, is_public_list, access_rules):
    call = 'edit_terminal_access'
    params = {'container_key':container_key, 'is_public_list':is_public_list, 'access_rules':access_rules}
    response = make_request(call, params)
    return response


# Manage Terminal DNS & Domains
def get_cname_records():
    call = 'get_cname_records'
    params = {}
    response = make_request(call, params)
    return response

def add_domain_to_pool(domain):
    call = 'add_domain_to_pool'
    params = {'domain':domain}
    response = make_request(call, params)
    return response

def remove_domain_from_pool(domain):
    call = 'remove_domain_from_pool'
    params = {'domain':domain}
    response = make_request(call, params)
    return response

def add_cname_record(domain, subdomain, port):
    call = add_cname_record
    params = {'domain':domain, 'subdomain':subdomain, 'port':port}
    response = make_request(call, params)
    return response

def remove_cname_record(domain):
    call = 'remove_cname_record'
    params = {'domain':domain}
    response = make_request(call, params)
    return response


# Manage Terminal Idle Settings
def set_terminal_idle_settings(container_key, triggers=None, action=None):
    call = 'set_terminal_idle_settings'
    params = {'container_key':container_key}
    response = make_request(call, params)
    return response

def get_terminal_idle_setting(container_key):
    call = 'get_terminal_idle_setting'
    params = {'container_key':container_key}
    response = make_request(call, params)
    return response


# Manage Usage and Credits
def instance_types():
    call = 'instance_types'
    params = None
    response = make_request(call, params)
    return response

def instance_price(instance_type):
    call = 'instance_price'
    params = {'instance_type':instance_type}
    response = make_request(call, params)
    return response

def balance():
    call = 'balance'
    params = None
    response = make_request(call, params)
    return response

def balance_added():
    call = 'balance_added'
    params = None
    response = make_request(call, params)
    return response

def gift(email, cents):
    call = 'gift'
    params = {'email':email, 'cents':cents}
    response = make_request(call, params)
    return response

def burn_history():
    call = 'burn_history'
    params = None
    response = make_request(call, params)
    return response

def terminal_usage_history():
    call = 'terminal_usage_history'
    params = None
    response = make_request(call, params)
    return response

def burn_state():
    call = 'burn_state'
    params = None
    response = make_request(call, params)
    return response

def burn_estimates():
    call = 'burn_estimates'
    params = None
    response = make_request(call, params)
    return response


# Manage SSH Public Keys
def add_authorized_key_to_terminal(container_key, publicKey):
    call = 'add_authorized_key_to_terminal'
    params = {'container_key':container_key, 'publicKey':publicKey}
    response = make_request(call, params)
    return response

def add_authorized_key_to_ssh_proxy(name, publicKey):
    call = 'add_authorized_key_to_ssh_proxy'
    params = {'name':name, 'publicKey':publicKey}
    try:
        response = make_request(call, params)
    except Exception, e:
        return {'status':e}
    return response

def del_authorized_key_from_ssh_proxy(name, fingerprint):
    call = 'del_authorized_key_from_ssh_proxy'
    params = {'name':name, 'fingerprint':fingerprint}
    response = make_request(call, params)
    return response

def get_authorized_keys_from_ssh_proxy():
    call = 'get_authorized_keys_from_ssh_proxy'
    params = None
    response = make_request(call, params)
    return response


# Other
def request_progress(request_id):
    call = 'request_progress'
    params = {'request_id':request_id}
    response = make_request(call, params)
    return response

def who_am_i():
    call = 'who_am_i'
    response =  make_request(call)
    return response