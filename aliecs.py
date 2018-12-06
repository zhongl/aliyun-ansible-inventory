#!/usr/bin/env python
# coding=utf-8

""" A customize inventory script for ansible to list aliyun ecs instances.
"""

import os
import json
import itertools
import argparse

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class Rpc:
    def __init__(self, key_id, secret, region):
        self.client = AcsClient(key_id, secret, region)

    def execute(self, request, callback):
        return callback(self.client.do_action_with_exception(request))


def describe_instances(region, page_size=1, page_num=1):
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('ecs.aliyuncs.com')
    request.set_method('POST')
    request.set_version('2014-05-26')
    request.set_action_name('DescribeInstances')

    request.add_query_param('PageSize', page_size)
    request.add_query_param('PageNumber', page_num)
    request.add_query_param('RegionId', region)
    return request


def transform(instance):
    network = instance['InstanceNetworkType']

    def private_ip():
        if network == 'vpc':
            return instance['VpcAttributes']['PrivateIpAddress']['IpAddress'][0]
        else:
            return instance['InnerIpAddress']['IpAddress'][0]

    return (
        instance['InstanceId'],
        {
            'name': instance['InstanceName'],
            'type': instance['InstanceType'],
            'zone': instance['ZoneId'],
            'network': network,
            'ansible_host': private_ip(),
            'public_ip': instance['PublicIpAddress']['IpAddress']
        }
    )


def host(rpc, region, id):
    def callback(response):
        ins = map(transform, json.loads(response)['Instances']['Instance'])
        return json.dumps({'_meta': {'hostvars': dict(iter(ins))}})

    request = describe_instances(region)
    request.add_query_param('InstanceIds', json.dumps([id]))
    return rpc.execute(request, callback)


def list_host(rpc, region, page_size):
    def group_by_meta(key, iters):
        iters.sort(key = lambda i: i[1][key])
        return [(k, map(lambda i: i[0], list(v)))
                for k, v in itertools.groupby(iters, lambda i: i[1][key])]

    def fetch(num, ins):
        def callback(response):
            obj = json.loads(response)
            ins.extend(map(transform, obj['Instances']['Instance']))
            
            if obj['TotalCount'] > len(ins) :
                return fetch(num + 1, ins)
            else:
                return ins

        return rpc.execute(describe_instances(region, page_size, num), callback)

    ins = fetch(1, [])

    tuples = [('_meta', {'hostvars': dict(iter(ins))})]

    tuples.extend(group_by_meta('type', ins))
    tuples.extend(group_by_meta('zone', ins))
    tuples.extend(group_by_meta('network', ins))

    return json.dumps(dict(iter(tuples)))
    


def main():
    key_id = os.getenv("ALIYUN_ACCESS_KEY", "UNSET").strip()
    secret = os.getenv("ALIYUN_ACCESS_SECRET", "UNSET").strip()
    region = os.getenv("ALIYUN_REGION_ID", "cn-hangzhou").strip()
    page_size = os.getenv("ALIYUN_PAGE_SIZE", "100").strip()

    parser = argparse.ArgumentParser(description='Get inventory of Aliyun.')
    parser.add_argument("--list", action='store_true', dest='list')
    parser.add_argument("--host", action='store', dest='host')
    args = parser.parse_args()

    if args.list:
        print list_host(Rpc(key_id, secret, region), region, page_size)
    elif args.host:
        print host(Rpc(key_id, secret, region), region, args.host)
    else:
        print '{}'


if __name__ == "__main__":
    main()
