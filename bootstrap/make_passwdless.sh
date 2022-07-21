### This file is autogenerated by make_passwdless.py ###

#!/bin/sh

set -o errexit
set -o nounset

mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -q -N '' -t rsa -f ~/.ssh/id_rsa
fi

sshpass -p asxz ssh-copy-id -o StrictHostKeyChecking=no ubuntu@10.139.212.128
sshpass -p asxz ssh-copy-id -o StrictHostKeyChecking=no ubuntu@10.139.212.207
