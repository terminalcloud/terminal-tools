#!/usr/bin/env python
import os
import re
import json
import urllib2
import argparse
import subprocess

bin_filename = 'pulldocker'
dockerhub_url = 'https://registry.hub.docker.com'
defaults = {'user':'root', 'entrypoint':'/bin/sh -c', 'cmd':'', 'wdir':'/root'}


def get_pulldocker_bin(filename):
    for path in os.environ["PATH"].split(":"):
        fullpath = '%s/%s'% (path, filename)
        if os.path.exists(fullpath):
            if os.path.isfile(fullpath):
                if os.access(fullpath,os.X_OK):
                    return fullpath
                else:
                    exit('Cannot execute %s. Check file permissions.'% fullpath)
            else:
                exit('%s is not a file.'% fullpath)
        else:
            pass
    exit('%s not found in path')

def get_dockerfile_details(user, repo):
    raw_dockerfile = '%s/u/%s/%s/dockerfile/raw' % (dockerhub_url,user,repo)
    output = {}
    try:
        response = urllib2.urlopen(raw_dockerfile)
        dockerfile = response.read()
        dockerfile = dockerfile.replace('\\\n', ' ')
        f = [a[1] for a in re.findall(r'(FROM|from)\s+(.*)', dockerfile)][0]
        maintainer = [a[1] for a in re.findall(r'(MAINTAINER|maintainer)\s+(.*)', dockerfile)]
        lines = re.findall(r'\n(COPY|copy|ADD|add|RUN|run|WORKDIR|workdir|ENV|env)\s+(.*)', dockerfile)
        cmds = [a[1] for a in re.findall(r'\n(CMD|cmd)\s+(.*)', dockerfile)]
        envs = [a[1] for a in re.findall(r'\n(ENV|env)\s+(.*)', dockerfile)]
        volumes = [a[1] for a in re.findall(r'\n(volume|VOLUME)\s+(.*)', dockerfile)]
        wdir = [a[1] for a in re.findall(r'\n(workdir|WORKDIR)\s+(.*)', dockerfile)]
        ports = [a[1] for a in re.findall(r'\n(expose|EXPOSE)\s+(.*)', dockerfile)]
        duser = [a[1] for a in re.findall(r'\n(user|USER)\s+(.*)', dockerfile)]
        entrypoint = [a[1] for a in re.findall(r'\n(ENTRYPOINT|entrypoint)\s+(.*)', dockerfile)]
        output = {'FROM': f,
                 'lines': lines,
                 'ENV': envs,
                 'VOL': volumes,
                 'PORTS': ports}
        try:
            output['CMD'] = json.loads(cmds[0])
        except:
            output['CMD'] = cmds
        output['WDIR'] = wdir[0] if wdir != [] else None
        output['ENTRYPOINT'] = re.sub('["\[\]]','',entrypoint[0]) if entrypoint != [] else None
        output['MAINTAINER'] = maintainer[0] if maintainer != [] else None
        output['USER'] = duser[0] if duser != [] else 'root'
    except Exception, e:
        print '(>>>%s)'% e
        for key in ('FROM', 'CMD', 'ENV', 'VOL', 'WDIR', 'PORTS', 'ENTRYPOINT', 'MAINTAINER', 'USER'): output[key] = None
    return output

def get_customdockerfile_details(filename):
    output = {}
    try:
        with open(filename, 'r') as f:
            dockerfile = f.read()
        dockerfile = dockerfile.replace('\\\n', ' ')
        f = [a[1] for a in re.findall(r'(FROM|from)\s+(.*)', dockerfile)][0]
        maintainer = [a[1] for a in re.findall(r'(MAINTAINER|maintainer)\s+(.*)', dockerfile)]
        lines = re.findall(r'\n(COPY|copy|ADD|add|RUN|run|WORKDIR|workdir|ENV|env)\s+(.*)', dockerfile)
        cmds = [a[1] for a in re.findall(r'\n(CMD|cmd)\s+(.*)', dockerfile)]
        envs = [a[1] for a in re.findall(r'\n(ENV|env)\s+(.*)', dockerfile)]
        volumes = [a[1] for a in re.findall(r'\n(volume|VOLUME)\s+(.*)', dockerfile)]
        wdir = [a[1] for a in re.findall(r'\n(workdir|WORKDIR)\s+(.*)', dockerfile)]
        ports = [a[1] for a in re.findall(r'\n(expose|EXPOSE)\s+(.*)', dockerfile)]
        duser = [a[1] for a in re.findall(r'\n(user|USER)\s+(.*)', dockerfile)]
        entrypoint = [a[1] for a in re.findall(r'\n(ENTRYPOINT|entrypoint)\s+(.*)', dockerfile)]
        output = {'FROM': f,
                  'lines': lines,
                 'ENV': envs,
                 'VOL': volumes,
                 'PORTS': ports}
        try:
            output['CMD'] = json.loads(cmds[0])
        except:
            output['CMD'] = cmds
        output['WDIR'] = wdir[0] if wdir != [] else None
        output['ENTRYPOINT'] = re.sub('["\[\]]','',entrypoint[0]) if entrypoint != [] else None
        output['MAINTAINER'] = maintainer[0] if maintainer != [] else None
        output['USER'] = duser[0] if duser != [] else 'root'
    except Exception, e:
        print '(%s)'% e
        for key in ('FROM', 'CMD', 'ENV', 'VOL', 'WDIR', 'PORTS', 'ENTRYPOINT', 'MAINTAINER', 'USER'): output[key] = None
    return output

def get_startup_commands(parsed, customs, defaults):
    script = []

    exports = get_envs(parsed)
    if len(exports) > 0:
        script.append(get_envs(parsed))

    if customs['wdir'] is not None:
        script.append('cd %s ;'% customs['wdir'])
    else:
        if parsed['WDIR'] is not None:
            if len(parsed['WDIR']) > 0:
                script.append('cd %s \n'% parsed['WDIR'])
        else:
            script.append('cd %s ;'% defaults['wdir'])

    if customs['entrypoint'] is not None:
            script.append('%s '% customs['entrypoint'])
    else:
        if parsed['ENTRYPOINT'] is not None:
            if len(parsed['ENTRYPOINT']) > 0:
                script.append('%s '% parsed['ENTRYPOINT'])
        else:
            script.append('%s '% defaults['entrypoint'])

    if customs['cmd'] is not None:
        script.append('%s'% customs['cmd'])
    else:
        if parsed['CMD'] is not None:
            if len(parsed['CMD']) > 0:
                for cmd in range(len(parsed['CMD'])):
                    script.append('%s'% parsed['CMD'][cmd])
        else:
            script.append('%s'% defaults['cmd'])
    return script

def sanitize_image(raw_image):
    try:
        if len(raw_image.rsplit(':',-1)) == 2:
            userrepo, tag = raw_image.rsplit(':',-1)
        else:
            userrepo, tag = raw_image, None
        if len(userrepo.rstrip('/').lstrip('/').split('/')) == 2:
            user, repo = userrepo.rstrip('/').lstrip('/').split('/')
        else:
            user, repo = '_', userrepo.rstrip('/').lstrip('/')
        user, repo = re.sub('/','',user), re.sub('/','',repo)
        image = '%s/%s:%s'% (user, repo, tag) if tag is not None else  '%s/%s'% (user, repo)
        return {'user':user, 'repo':repo, 'tag':tag, 'image':image}
    except:
        exit('ERROR: Image name format not supported')

def pullimage(image, rootdir):
    pulldocker = get_pulldocker_bin(bin_filename)
    try:
        if rootdir is not None:
            return subprocess.call([pulldocker,'-o', '%s'% rootdir, '%s'% image])
        else:
            return subprocess.call([pulldocker,image['image']])
    except Exception, e:
        print '(%s)'% e
        return False

def get_rootdir(image, custom_dir):
    if custom_dir is None:
        if image['user'] == '_':
            if image['tag'] is None:
                return image['repo']
            else:
                return '%s:%s'%(image['repo'], image['tag'])
        else:
                return image['image']
    else:
        if custom_dir[0] != '/':
            custom_dir = os.path.join(os.getcwd(),custom_dir)
        if os.path.isdir(custom_dir):
            return custom_dir
        else:
            exit('ERROR: rootdir not found')

def get_user(parsed, custom_user):
    if custom_user is None:
        if parsed['USER'] is None:
            return defaults['user']
        else:
            return parsed['USER']
    else:
        return custom_user

def get_envs(parsed):
    exports = ''
    envs = parsed['ENV']
    if envs is not None:
        for env in envs:
          e, val = re.split('\s+', env, 1)
          exports += 'export %s=\"%s\"; ' % (e, val)
    return exports

def make_startup_script(runscript, comms):
    if os.path.exists(runscript):
        print 'Docker startup script ' + runscript + 'already exists - Overwriting'
    try:
        with open(runscript, 'w') as f:
            for line in comms:
                f.write(line)
            f.write('\n')
            f.close()
        os.chmod(runscript, 755)
    except Exception, e:
        exit('ERROR: Cannot write %s script (%s)'% (runscript,e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description='RUNIMAGE - Run a docker image natively, inside a chroot jail and without Docker'
    parser.add_argument('image', type=str, help='Docker image to be dumped')
    parser.add_argument('-u', '--user', type=str, default=None ,help='Run the container with a custom user [%s]'% defaults['user'])
    parser.add_argument('-e', '--entrypoint', type=str, default=None, help='Entrypoint bin/script [%s]'% defaults['entrypoint'])
    parser.add_argument('-c', '--cmd', type=str, default=None, help='Command/argument executed by the entrypoint [%s]'% defaults['cmd'])
    parser.add_argument('-D', '--rootdir', type=str, default=None, help='Custom path to run/pull the docker image')
    parser.add_argument('-d', '--wdir', type=str, default=None, help='Custom internal work dir')
    parser.add_argument('-f', '--dockerfile', type=str, default=None, help='Custom dockerfile')
    parser.add_argument('-w', '--overwrite', type=bool, default=False, help='DANGER - Overwrite image if it already exists')
    args = vars(parser.parse_args())

    image=sanitize_image(args['image'])
    parsed_dockerfile = get_customdockerfile_details(args['dockerfile']) if args['dockerfile'] is not None else get_dockerfile_details(image['user'],image['repo'])
    rootdir = get_rootdir(image, args['rootdir'])
    runscript = '/run.sh'
    user = get_user(parsed_dockerfile,args['user'])
    script_array = get_startup_commands(parsed_dockerfile, args, defaults)
    print 'Pulling %s...'% image['image']
    pullimage(image['image'],rootdir)
    os.chroot(rootdir)
    cmdchain = ['su'] + ['-l'] + [user] + ['-c'] + [runscript]
    make_startup_script(runscript, script_array)
    print cmdchain
    print 'Your application is running in ports: "%s" ' % parsed_dockerfile['PORTS']
    subprocess.call(cmdchain)