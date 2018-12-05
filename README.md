# A inventory script of Ansible for Aliyun ECS

## Requirements

* Python 2.7
* `pip install aliyun-python-sdk-core`

## Usage

```shell
curl -LOk https://github.com/zhongl/aliyun-ansible-inventory/raw/master/aliecs.py
chmod u+x aliecs.py
ALIYUN_ACCESS_KEY=${YOUR_ACCESS_KEY} ALIYUN_ACCESS_SECRET=${YOUR_ACCESS_SECRET} ./aliecs.py --list
```

## Environments

* `ALIYUN_ACCESS_KEY`, default is `UNSET`;
* `ALIYUN_ACCESS_SECRET`, default is `UNSET`;
* `ALIYUN_REGION_ID`, default is `cn-hangzhou`;
* `ALIYUN_PAGE_SIZE`, default is `100`.

## References

* [write your own inventory script](https://docs.ansible.com/ansible/2.7/dev_guide/developing_inventory.html#developing-inventory)
* [Aliyun OpenAPI Explorer](https://api.aliyun.com/?#product=Ecs&search=DescribeIn&api=DescribeInstances&params={%22Tag%22:{%22Tag.1.value%22:%22%22,%22Tag.1.key%22:%22%22,%22Tag.1.Key%22:%22%22,%22Tag.1.Value%22:%22%22}}&tab=DEMO&lang=PYTHON)
