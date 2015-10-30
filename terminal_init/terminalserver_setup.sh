#!/usr/bin/env bash
#The MIT License (MIT)
#
#Copyright (c) 2015 Cloudlabs, INC

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


#TOOLS_PATH='/CL/readonly/cloudlabs/latest'
TOOLS_PATH='/TEST/readonly/cloudlabs/latest'
DAEMON_BIN="$TOOLS_PATH/daemon"
CHKCONFIG_BIN="$TOOLS_PATH/chkconfig"
UPSTART_CONF="$TOOLS_PATH/terminal-server.conf"
SYSV_INIT_FILE="$TOOLS_PATH/terminal-server"


get_osflavor(){
    if [[ -f "/etc/lsb-release" ]]
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

get_daemon(){
    if [[ ! -x /usr/local/bin/daemon ]]; then
        echo "Copying Daemon"
        cp "$DAEMON_BIN" /usr/local/bin/daemon
        chmod +x /usr/local/bin/daemon
    fi
}

get_chkconfig(){
    if [[ ! -x  /sbin/chkconfig ]]; then
        echo "Copying Chkconfig"
        cp "$CHKCONFIG_BIN" /sbin/chkconfig
        chmod +x /sbin/chkconfig
    fi
}

install_daemon(){
    echo "Installing Daemon from its package"
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


install_chkconfig(){
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

get_requisites(){
    flavor=$1
    if [[ "$flavor" == "debian" ]]
        then
            get_daemon
            get_chkconfig || install_chkconfig "$flavor"
        elif [[ "$flavor" == "rpm" ]]
            then
                get_daemon
                which chkconfig >/dev/null || install_chkconfig "$flavor"
        else
            get_daemon
    fi
}

install_upstart-conf(){
    if [[ ! -f /etc/init/terminal-server.conf ]]
        then
            cp "$UPSTART_CONF" /etc/init/terminal-server.conf
            chmod +x /etc/init/terminal-server.conf
    fi
}

install_sysv_init(){
    if [[ ! -x /etc/init.d/terminal-server.conf ]]
        then
            cp "$SYSV_INIT_FILE" /etc/init.d/terminal-server
            chmod +x /etc/init.d/terminal-server
            chkconfig --add terminal-server
    fi
}

comment_rc.local(){
    if [[ -f /etc/rc.local ]]
        then
            sed -i  '/^bash\ \/srv\/cloudlabs\/container_scripts\/container_startup.sh/ s/^#*/#/' /etc/rc.local
    fi
}

remove_cloudlabside(){
    if [[ -x /etc/init.d/cloudlabside ]]
        then
            rm /etc/init.d/cloudlabside
    fi
}



### Main Process ##

# Check the Linux flavor
flavor=$(get_osflavor)

# Install pre-requisites if needed
get_requisites "$flavor"

# Install init/upstart scripts
if [[ "$flavor" == "ubuntu" ]]
    then
        install_upstart-conf
    else
        install_sysv_init
fi

# Comment out the old initialization mode and remove old init scripts
[[ $? -eq 0 ]] && comment_rc.local && remove_cloudlabside