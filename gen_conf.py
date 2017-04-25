#-*- coding: utf-8 -*-
"""
    生成 lvs 配置文件.

"""

import os

from jinja2 import Environment, FileSystemLoader


def template(template_dir, template_dest_dir, device, vipnets, vip2ws,
             lb_infos):
    """ 生成 lvs 配置文件.

    """
    if not os.path.exists(template_dest_dir):
        os.mkdir(template_dest_dir)

    # 模板名称.
    keepalived_template = "keepalived.conf"
    sub_keepalived_template = "sub_keepalived.conf"
    zebra_template = "zebra.conf"
    ospfd_template = "ospfd.conf"

    # 拿到 vip 列表.
    vips = [i["vip"] for i in vip2ws]
    wstypes = [i["wstype"] for i in vip2ws]

    for lb_info in lb_infos:
        # 拿到 lb 信息.
        lb = lb_info["hostname"]
        internalip = lb_info["internalip"]
        internalnetmask = lb_info["internalnetmask"]
        internalgateway = lb_info["internalgateway"]
        routerid = lb_info["routerid"]
        ospfnet = lb_info["ospfnet"]
        localips = lb_info["localips"]

        # lb 配置文件基目录.
        lb_dir = template_dest_dir + "/" + lb
        os.mkdir(lb_dir)

        # keepalived 配置文件目录.
        lb_keepalived_dir = lb_dir + "/keepalived"
        os.mkdir(lb_keepalived_dir)

        # ospfd 配置文件目录.
        lb_osfpd_dir = lb_dir + "/ospfd"
        os.mkdir(lb_osfpd_dir)

        # 模板环境.
        j2_env = Environment(
            loader=FileSystemLoader(template_dir), trim_blocks=True)

        # 生成主 keepalived 配置文件.
        ret = j2_env.get_template(keepalived_template).render(
            lips=localips, vips=vips, lb=lb.split(".")[0])
        with file(lb_keepalived_dir + "/keepalived.conf", 'w') as f:
            f.writelines(ret)

        # 生成 zebra 配置文件.
        ret = j2_env.get_template(zebra_template).render(lb=lb)
        with file(lb_osfpd_dir + "/zebra.conf", 'w') as f:
            f.writelines(ret)

        # 生成 ospfd 配置文件.
        ret = j2_env.get_template(ospfd_template).render(
            lb=lb,
            routerid=routerid,
            device=device,
            ospfnet=ospfnet,
            vipnets=vipnets)
        with file(lb_osfpd_dir + "/ospfd.conf", 'w') as f:
            f.writelines(ret)

        # 生成 keepalived 的 VIP 配置文件.
        for i in vip2ws:
            # vip 信息.
            vip = i["vip"]
            wstype = i["wstype"]
            # port 信息.
            if "ports" not in i:
                ports = [
                    {"sport": 80,
                     "dport": 80,
                     "synproxy": 1,
                     "persistence_timeout": 50}, {"sport": 443,
                                                  "dport": 443,
                                                  "synproxy": 1,
                                                  "persistence_timeout": 50}
                ]
            else:
                ports = list()
                for j in i["ports"]:
                    if "synproxy" not in j:
                        j["synproxy"] = 1
                    elif "persistence_timeout" not in j:
                        j["persistence_timeout"] = 50
                    ports.append(j)

            # 后端机器列表.
            wss_ips = i["wss"]

            ret = j2_env.get_template(sub_keepalived_template).render(
                vip=vip, ports=ports, wss=wss_ips,wstype=wstype)
            with file(lb_keepalived_dir + "/" + wstype + ".conf", 'w') as f:
                f.writelines(ret)


def main():
    template_dir = "./template"
    template_dest_dir = "/tmp/lvs/"

    device = "bond0"

    vipnets = ["10.0.12.0/24", "10.0.13.0/24", "10.0.14.0/24"]

    vip2ws = [
        {
            'wstype': 'apps',
            'vip': '10.0.12.201',
            'wss':
                ['10.3.140.121', '10.3.140.122', '10.3.140.123', '10.3.140.124'],
            'ports': [
                {'dport': 80,
                 'synproxy': 1,
                 'sport': 80,
                 'persistence_timeout': 50}, {'dport': 443,
                                              'synproxy': 1,
                                              'sport': 443,
                                              'persistence_timeout': 50}
            ]
        }, {
            'wstype': 'search',
            'vip': '10.0.12.202',
            'wss':
                ['10.3.141.131', '10.3.141.132', '10.3.141.133', '10.3.141.134'],
            'ports': [
                {'dport': 80,
                 'synproxy': 1,
                 'sport': 80,
                 'persistence_timeout': 50}, {'dport': 443,
                                              'synproxy': 1,
                                              'sport': 443,
                                              'persistence_timeout': 50}
            ]
        }
    ]

    lb_infos = [
        {
            "internalgateway": "10.0.18.1",
            "internalnetmask": "255.255.255.224",
            "hostname": "internal",
            "routerid": "10.0.18.2",
            "internalip": "10.0.18.2",
            "ospfnet": "10.0.18.0/27",
            "localips": [
                '10.0.18.20-151'
            ]
        }, {
            "internalgateway": "10.0.18.33",
            "internalnetmask": "255.255.255.224",
            "hostname": "bgp",
            "routerid": "10.0.18.34",
            "internalip": "10.0.18.34",
            "ospfnet": "10.0.18.32/27",
            "localips": [
                '10.0.18.152-232'
            ]
        }
    ]

    print template(template_dir, template_dest_dir, device, vipnets, vip2ws, lb_infos)


def dsnat():
    template_dir = "./template"
    template_dest_dir = "/tmp/lvs/dsnat"
    dsnat_template = "dsnat.conf"
    if not os.path.exists(template_dest_dir):
        os.mkdir(template_dest_dir)
    #默认出口ip池
    default_pool = ['1.1.1.1','2.2.2.2','3.3.3.3']
    #特殊网段出口ip池
    spec_pools = [
            {
                'pool':'s1',
                'dest_ip':['6.6.6.6','8.8.8.8'],
                'src_ip_range':'10.3.143.0/24'
            },
            {
                'pool':'s2',
                'dest_ip':['9.9.9.9','10.10.10.10'],
                'src_ip_range':'10.4.12.0/24'
            }
    ]
    j2_env = Environment(
        loader=FileSystemLoader(template_dir), trim_blocks=True)
    ret = j2_env.get_template(dsnat_template).render(default_pool=default_pool,spec_pools=spec_pools)
    with file(template_dest_dir + "/keepalived.conf", 'w') as f:
        f.writelines(ret)

if __name__ == '__main__':
    main()
    dsnat()
