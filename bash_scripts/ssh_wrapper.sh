#! /bin/bash

# Locate Configuration Path

CONF_PATH=null;

test_conf_path=/etc/dynamite_remote/config.cfg
if test -f "$test_conf_path"; then
    CONF_PATH=$test_conf_path
fi

test_conf_path=../config.cfg
if test -f "$test_conf_path"; then
    CONF_PATH=$test_conf_path
fi

test_conf_path=./config.cfg
if test -f "$test_conf_path"; then
    CONF_PATH=$test_conf_path
fi



DYNAMITE_REMOTE_ROOT=$(grep dynamite_remote_root $CONF_PATH | cut -f2 -d'=')
DYNAMITE_REMOTE_LOCKS=$DYNAMITE_REMOTE_ROOT/locks
echo $DYNAMITE_REMOTE_LOCKS

# Create the locks directory if it does not exist
mkdir -p $DYNAMITE_REMOTE_LOCKS
ssh_command=$(whereis ssh)

# Parse the commandline arguments passed in by node.py
array=( $@ )
len=${#array[@]}
hostname_or_ip=$(awk -F@ '{print $2}' <<< "${array[@]:0:1}")
node_command="${array[@]:8:$len-1}"


# Create a lock file
echo Creating lock. $DYNAMITE_REMOTE_LOCKS/$hostname_or_ip
touch "$DYNAMITE_REMOTE_LOCKS/$hostname_or_ip"
echo "$node_command" > "$DYNAMITE_REMOTE_LOCKS/$hostname_or_ip"

$ssh_command "$@"

# Remove the lock
echo Removing lock. $DYNAMITE_REMOTE_LOCKS/$hostname_or_ip
rm $DYNAMITE_REMOTE_LOCKS/$hostname_or_ip
printf '[Remote Session Exited]'


