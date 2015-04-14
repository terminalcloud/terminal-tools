#!/usr/bin/env python
import os
import json
import time
import signal
import socket
import argparse
import subprocess
import threading
from terminalcloud import terminal

key_name = '/root/.ssh/id_rsa'

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        print self.error_message

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)

def generate_ssh_key(key_file):
    subprocess.call(['ssh-keygen','-f', key_file,'-P',''])
    os.chmod(key_file, 0600)

def get_public_key(key_file):
    with open(key_file) as f:
        content = f.readlines()[0].rstrip('\n')
    return str(content)

def start_snap(name, snapshot_id, size=None, script=None):
    output = terminal.start_snapshot(snapshot_id, size, None, name, None, script)
    time.sleep(int(int(args.quantity) * 0.04) + 1)
    request_id = output['request_id']
    output = terminal.request_progress(request_id)
    try:
        if output['status'] != 'success':
            pass
    except:
        time.sleep(int(int(args.quantity) * 0.03) + 1)
        output = terminal.request_progress(request_id)

    state = 'None'
    while output['status'] != 'success':
        try:
            time.sleep(int(args.quantity) * 0.03 + 1)
            output = terminal.request_progress(request_id)
            if output['state'] != state:
                state = output['state']
                print('%s - (%s)' % (name, state))
        except:
            print "Retrying %s" % name
            time.sleep(int(args.quantity * 0.02) + 2)
    done = False
    while done is False:
        try:
            output = terminal.request_progress(request_id)
            container_key = output['result']['container_key']
            subdomain = output['result']['subdomain']
            container_ip = output['result']['container_ip']
            done = True
        except:
            print "Retrying %s" % name
            time.sleep(int(int(args.quantity) * 0.02) + 1)
            done = False
    return container_key, container_ip, subdomain

def run_on_terminal(cip, user, pemfile, script):
    try:
        p = subprocess.Popen(
        ['ssh', '-q' ,'-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-i', pemfile,
         user + '@' + cip, script], 0, None,  None, None, None)
        p.wait()
        return p.returncode
    except Exception, e:
        return 'Error: [%s]' % e

def get_script(filename):
    try:
        with open(filename) as f:
            data = f.read()
            data.replace('\n',';')
        return data
    except Exception, e:
        print '(%s)' % e
        return None

def send_script(cip, user, pemfile, script,):
    print (cip, user, script, pemfile)
    destination='%s@%s:' % (user,cip)
    try:
        p = subprocess.Popen(
        ['scp' , '-i', pemfile, '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
         script, destination])
        p.wait()
        return p.returncode
    except Exception, e:
        return 'Error: [%s]' % e

def args_sanitizer(args):
    if args.size not in terminal.instance_types()['instance_types']:
        print "Error. Wrong instance type"
        exit(1)
    if (int(args.quantity) < 1 or int(args.quantity) > 250):
        print "Error. Terminal amount out of bounds ( should be in between 1 and 100 )"
        exit(1)
    if args.method not in ('ssh, startup, startup_key'):
        print "Error. Not a valid method. use: [ssh], startup or startup_key"
        exit(1)
    if args.ssh_key_file is None:
        key_name = args.ssh_key_file

def start_terminal_worker(name):
    container_key, container_ip, subdomain = start_snap(name, snapshot_id, args.size, script)
    terms.append({'container_key':container_key, 'container_ip':container_ip, 'subdomain':subdomain, 'name':name})
    time.sleep(2)
    terminal.add_authorized_key_to_terminal(container_key,publicKey)
    if args.method == 'ssh' and args.script is not None:
        print 'Sending Script'
        send_script(container_ip, 'root', key_name, args.script)
        print 'Running Script'
        run_on_terminal(container_ip, 'root', key_name, '/bin/bash /root/%s' % os.path.basename(args.script))

def add_terminal_links_worker(container_key,links):
    output = terminal.add_terminal_links(container_key,links)
    print output
    return output

def single_thread():
    terms = []
    for i in range(args.quantity):
        name = '%s-%s' % (args.name,i)
        print "Starting Terminal %s" % name
        container_key, container_ip, subdomain = start_snap(name, snapshot_id, args.size, script)
        terms.append({'container_key':container_key, 'container_ip':container_ip, 'subdomain':subdomain, 'name':name})
    time.sleep(1) # Prevent race-condition issues

    # Installing stuff by ssh method
    if args.method == 'ssh':
        for i in range(len(terms)):
            terminal.add_authorized_key_to_terminal(terms[i]['container_key'],publicKey)
            time.sleep(1)
            if args.script is not None:
                print "Sending Script"
                send_script(terms[i]['container_ip'], 'root', key_name ,args.script)
                print "Running Script"
                run_on_terminal(terms[i]['container_ip'], 'root', key_name ,'/bin/bash /root/%s' % os.path.basename(args.script))
    elif args.method == 'startup_key':
        for i in range(len(terms)):
            terminal.add_authorized_key_to_terminal(terms[i]['container_key'],publicKey)
            time.sleep(1)

    if args.ports is not None:
        host_subdomain=socket.gethostname()
        ports=args.ports.split(',')
        terms.append(terminal.get_terminal(None,host_subdomain)['terminal'])
        for t in range(len(terms)):
            container_key=terms[t]['container_key']
            links=[]
            for s in range(len(terms)):
                for port in range(len(ports)):
                    link={'port':(ports[port]),'source':terms[s]['subdomain']}
                    links.append(link)
            terminal.add_terminal_links(container_key,links)
    return terms

def multi_thread():
    global terms
    terms =[]
    threads=[]

    for i in range(args.quantity):
        name = '%s-%s' % (args.name,i)
        t = threading.Thread(target=start_terminal_worker, args=(name,), name=name)
        threads.append(t)
        t.setDaemon(True)
        print 'Initializying %s' % name
        if i%3 == 0:
            time.sleep(int(int(args.quantity) * 0.04) + 1)
        t.start()

    for th in range(len(threads)):
        while threads[th].is_alive():
            time.sleep(1)

    if args.ports is not None:
        threads=[]
        host_subdomain=socket.gethostname()
        ports=args.ports.split(',')
        terms.append(terminal.get_terminal(None,host_subdomain)['terminal'])
        for term in range(len(terms)):
            container_key=terms[term]['container_key']
            links=[]
            for s in range(len(terms)):
                for port in range(len(ports)):
                    link={'port':str(ports[port]),'source':terms[s]['subdomain']}
                    links.append(link)
            t = threading.Thread(target=add_terminal_links_worker, args=(container_key,links), name=terms[term]['subdomain'])
            threads.append(t)
            t.setDaemon(True)
            if (term + 1)%8 == 0:
                time.sleep(int(int(len(terms)) * 0.02) + 1)
            print '%s -  Configuring links' % t.name
            t.start()

        for th in range(len(threads)):
            while threads[th].is_alive():
                time.sleep(1)
    return terms


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("quantity", type=int, help="How many nodes will have your deploy")
    parser.add_argument('-b', "--snapshot_id", type=str, default='7067f369f7b76f0a3276beb561820a21c9b5204ab60fbd90524560db96d7cb38'\
                        , help="Base Snapshot ID. Default is Ubuntu")
    parser.add_argument("-s", "--size", type=str, default='medium', help="micro, mini, small, [medium], xlarge.. etc")
    parser.add_argument("-u", "--utoken", type=str, default=None ,help="Your user token")
    parser.add_argument("-a", "--atoken", type=str, default=None, help="Your access token")
    parser.add_argument("-c", "--creds", type=str, default='/etc/creds.json', help="A credentials json file")
    parser.add_argument("-x", "--script", type=str, default=None, help="A script file to be executed in the new Terminals. \n\
    With ssh method you can also use a binary executable. \n\
    If a script is not provided, the terminals will be created and ssh keys installed on them.")
    parser.add_argument('-m', "--method", type=str, default='ssh', help="[ssh], startup or startup_key")
    parser.add_argument('-n', "--name", type=str, default='Scripted Terminal', help="The name of your Terminal")
    parser.add_argument('-k', "--ssh_key_file", type=str, default=None, help="Use your own ssh key instead of create a new one - \
    Use your private key name")
    parser.add_argument('-p', "--ports", type=str, default=None, help="List of open ports to open between Terminals, csv.")
    parser.add_argument('-t', "--threading", type=str, default='single', help="[single] or multi - Multithreading is quick but \
    requires non-interactive scripts")
    parser.description="Utility to start and setup Terminals"
    args = parser.parse_args()

    terminal.setup_credentials(args.utoken, args.atoken, args.creds)
    args_sanitizer(args)

    # Preparing
    snapshot_id=args.snapshot_id

    if args.method == 'ssh':
        script = None
    else:
        if args.script is not None:
            script = get_script(args.script)
        else:
            script = None

    if args.method == 'ssh' or args.method == 'startup_key':
        if args.ssh_key_file is None:
            generate_ssh_key(key_name)
        else:
            key_name=args.ssh_key_file
        publicKey=get_public_key('%s.pub' % key_name)

    # Creating Terminals
    if args.threading == 'multi':
        terminals = multi_thread()
    else:
        terminals = single_thread()

    # Print results in json format
    host=terminals.pop()
    print json.dumps(terminals)