#!/usr/bin/env bash
# Script to install `daemon` and create init scripts for daemon usage with standard programs
# Cloudlabs, INC. Copyright (C) 2015
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Cloudlabs, INC. - 653 Harrison St, San Francisco, CA 94107.
# http://www.terminal.com - help@terminal.com


get_full_path(){
   echo $(cd $(dirname "$1") && pwd -P)/$(basename "$1")
}


get_osflavor(){
    if [[ -f "/etc/lsb_release" ]]
        then
            echo "ubuntu"
        elif [[ -f "/etc/redhat-release" ]]
        then
            echo "rpm"
        elif [[ -f "/etc/debian_version" ]]
        then
            echo "debian"
        else
            echo "ERROR: Cannot get the system type. Exiting."
            exit 1
    fi
}

install_daemon(){
    echo 'Attempting Daemon Installation'
    cd /tmp
    if [[ $1 == "debian" ]] || [[ "$1" == "ubuntu" ]]
        then
        wget -q https://github.com/terminalcloud/terminal-tools/raw/master/daemon_0.6.4-2_amd64.deb || exit -1
        dpkg -i daemon_0.6.4-2_amd64.deb
    else
        wget -q http://libslack.org/daemon/download/daemon-0.6.4-1.x86_64.rpm || exit -1
        rpm -i daemon-0.6.4-1.x86_64.rpm
    fi
}


install_upstart_init() {
    cat > /tmp/"$name" << END
description "Daemonized Test service -  Upstart script"

start on runlevel [2345]
stop on runlevel [!2345]
respawn

env name="$name"
env command="$command"
env command_args="$command_args"
env daemon="$daemon"
env daemon_start_args="--respawn"
env pidfiles="/var/run"
env user=""
env chroot=""
env chdir=""
env umask=""
env stdout="daemon.info"
env stderr="daemon.err"


pre-start script
[ -x "\$daemon" ] || exit 0
end script

exec "\$daemon"  "\$daemon_start_args" --name "\$name" --pidfiles "\$pidfiles" \
                \${user:+--user \$user} \${chroot:+--chroot \$chroot} \
                \${chdir:+--chdir \$chdir} \${umask:+--umask \$umask} \
                \${stdout:+--stdout \$stdout} \${stderr:+--stderr \$stderr} \
                -- "\$command" \$command_args

pre-stop script
"\$daemon" --stop --name "\$name" --pidfiles "\$pidfiles"
end script
END

    # We only replace the init script if the file does not already exists, and finally we enable it.
    if [[ -f /etc/init/"$name".conf ]]
        then
            echo "The file /etc/init/$name.conf already exist."
            echo "If you want to overwrite it execute \`cp /tmp/$name /etc/init/$name.conf \`"
        else
            cp /tmp/"$name" /etc/init/"$name".conf
            chmod +x /etc/init/"$name".conf
    fi
}


install_sysv_init(){
    cat > /tmp/"$name" << EOF
#!/bin/sh
#
### BEGIN INIT INFO
# Provides:          $name
# Required-Start:
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Should-Start:
# Should-Stop:
# Short-Description: Daemonized $name service.
### END INIT INFO
# chkconfig: 2345 90 60
name="$name"
command="$command"
command_args="$command_args"
daemon="$daemon"

[ -x "\$daemon" ] || exit 0

# This can be customized as needed
daemon_start_args="--respawn"
pidfiles="/var/run"
user=""
chroot=""
chdir=""
umask=""
stdout="daemon.info"
stderr="daemon.err"

case "\$1" in
    start)
        if "\$daemon" --running --name "\$name" --pidfiles "\$pidfiles"
        then
            echo "\$name is already running."
        else
            echo -n "Starting \$name..."
            "\$daemon" \$daemon_start_args --name "\$name" --pidfiles "\$pidfiles" \${user:+--user \$user} \${chroot:+--chroot \$chroot} \
                \${chdir:+--chdir \$chdir} \${umask:+--umask \$umask} \${stdout:+--stdout \$stdout} \${stderr:+--stderr \$stderr} -- "\$command" \$command_args
            echo done.
        fi
        ;;

    stop)
        if "\$daemon" --running --name "\$name" --pidfiles "\$pidfiles"
        then
            echo -n "Stopping \$name..."
            "\$daemon" --stop --name "\$name" --pidfiles "\$pidfiles"
            echo done.
        else
            echo "\$name is not running."
        fi
        ;;

    restart|reload)
        if "\$daemon" --running --name "\$name" --pidfiles "\$pidfiles"
        then
            echo -n "Restarting \$name..."
            "\$daemon" --restart --name "\$name" --pidfiles "\$pidfiles"
            echo done.
        else
            echo "\$name is not running."
            exit 1
        fi
        ;;

    status)
        "\$daemon" --running --name "\$name" --pidfiles "\$pidfiles" --verbose
        ;;

    *)
        echo "usage: \$0 <start|stop|restart|reload|status>" >&2
        exit 1
esac

exit 0
EOF

    # We only replace the init script if the file does not already exists, and finally we enable it.
    if [[ -f /etc/init.d/"$name" ]]
        then
            echo "The file /etc/init.d/$name already exist."
            echo "If you want to overwrite it execute \`cp /tmp/$name /etc/init.d/ \`"
        else
            cp /tmp/"$name" /etc/init.d/
            chmod +x /etc/init.d/"$name"

            chkconfig --add "$name"
    fi
}

chkconfig_install(){
    if [[ "$1" == "debian" ]]
        then
            echo "Installing chkconfig, please wait"
            apt-get update >> /dev/null
            apt-get -y install chkconfig >> /dev/null
        elif [[ "$1" == "rpm" ]]
            then
                echo "Installing chkconfig, please wait"
                yum -y install chkconfig >> /dev/null
        else
            echo "Cannot install chkconfig utility"
    fi
}

##### Main #####

[[ "$#" -gt 2 ]] || { echo "Usage: $0 service_name command 'command_parameters'"; exit 0 ; }

name=$1
command=$(get_full_path $2)
command_args=$3

# Install 'Daemon' if needed
which daemon > /dev/null && echo "Daemon already installed" || install_daemon $(get_osflavor)

# Install SysV init script or Upstart according with the Linux Flavour
daemon=$(which daemon)
if [[ $(get_osflavor) == "ubuntu" ]]
    then
        echo "Installing Upstart Script"
        install_upstart_init
    elif [[ $(get_osflavor) == "debian" ]] || [[ $(get_osflavor) == "rpm" ]]
    then
        echo 'Checking if chkconfig is available'
        which chkconfig > /dev/null && echo "chkconfig installed" || chkconfig_install $(get_osflavor)
        echo "Installing SysV Init script"
        install_sysv_init
    else
        echo "Cannot get the OS Flavor. Exiting."
        exit 1
fi

# Starting the Daemonized service
service "$name" start