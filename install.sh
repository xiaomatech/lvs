#!/usr/bin/env bash
rpm -ivh https://raw.githubusercontent.com/xiaomatech/lvs/master/kernel-2.6.32-279.22.1.el6.lvs.x86_64.rpm --force
rpm -ivh https://raw.githubusercontent.com/xiaomatech/lvs/master/lvs-tools-1.0.1-dsnat.el6.x86_64.rpm

chkconfig keepalived on

#gw ip gro/lro
interfaces=`ifconfig | grep ^e | awk '{print $1}' | fgrep -v :`
for t_iface in $interfaces ; do
	ethtool -K $t_iface gro off
	ethtool -K $t_iface lro off

	ethtool -K $t_iface gso off
	ethtool -K $t_iface tso off
done

chkconfig irqbalance off

curl https://raw.githubusercontent.com/xiaomatech/lvs/master/set_affinity.sh| bash