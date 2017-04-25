#!/usr/bin/env bash
sudo yum install -y rpm-build rpmdevtools yum-utils rng-tools
rpmdev-setuptree

rpm -ivh http://vault.centos.org/6.3/updates/Source/SPackages/kernel-2.6.32-279.22.1.el6.src.rpm
sed -i 's/CONFIG_IP_VS_TAB_BITS=12/CONFIG_IP_VS_TAB_BITS=22/g' ~/rpmbuild/SOURCES/config-generic
sed -i 's/CONFIG_IP_VS_TAB_BITS=20/CONFIG_IP_VS_TAB_BITS=22/g' ~/rpmbuild/SOURCES/kernel.config
cd ~/rpmbuild/SOURCES
tar -jxvf linux-2.6.32-279.22.1.el6.tar.bz2

wget https://raw.githubusercontent.com/xiaomatech/lvs/master/dsnat-2.6.32-279.el6.xiaomi.noconfig.patch
cd linux-2.6.32-279.22.1.el6
patch -p1 < ~/rpmbuild/SOURCES/dsnat-2.6.32-279.23.1.el6.xiaomi.noconfig.patch
cd ~/rpmbuild/SOURCES
tar -cjvf linux-2.6.32-279.22.1.el6.tar.bz2 linux-2.6.32-279.22.1.el6

sed -i 's/# % define buildid .local/%define buildid .lvs/g' ~/rpmbuild/SPECS/kernel.spec
sudo spectool -g ~/rpmbuild/SPECS/kernel.spec
sudo yum-builddep ~/rpmbuild/SPECS/kernel.spec
rpmbuild -bb --without kabichk ~/rpmbuild/SPECS/kernel.spec

ls -alt ~/rpmbuild/RPMS/x86_64/