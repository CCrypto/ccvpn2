#!/bin/sh

bind="10.99.0.20"

dev=$1
dev_mtu=$2
link_mtu=$3
local_ip=$4
remote_ip=$5

ip addr add dev $dev local $bind peer $remote_ip

if [ -n "$ifconfig_ipv6_remote" ]; then
    ip -6 neigh add proxy $ifconfig_ipv6_remote dev eth0
fi

