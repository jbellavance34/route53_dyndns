#!/usr/bin/env python
import boto3
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOSTED_ZONE_ID = 'Z35A0XL5N1M870'
RECORD_NAME = 'home.mayoche.info'

def get_public_ip():
    headers = {"Accept": "application/json"}
    url = "https://ifconfig.co/"
    data = None
    try:
        logger.info(f"Getting pubic ip from {url}")
        data = json.loads(requests.get(url=url, headers=headers).content)["ip"]
    except Exception as error:
        logger.error(f"get_public_ip(), {error}")
    return data


def get_route53_public_ip():
    ip = None
    try:
        logger.info("Getting public ip from aws route53")
        client = boto3.client("route53")
        record = client.list_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            StartRecordName=RECORD_NAME,
            MaxItems="1",
        )
        ip = record["ResourceRecordSets"][0]["ResourceRecords"][0]["Value"]
    except Exception as error:
        logger.error(f"get_route53_public_ip(), {error}")
    return ip

def update_route53_public_ip(ip):
    logger.info("Updating public ip to aws route53")
    client = boto3.client('route53')
    response = client.change_resource_record_sets(
    HostedZoneId=HOSTED_ZONE_ID,
    ChangeBatch={
        'Comment': 'Update by route53_dyndns',
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': RECORD_NAME,
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [
                        {
                            'Value': ip
                        },
                    ],
                }
            },
        ]
    }
)

def main():
    public_ip = get_public_ip()
    route53_ip = get_route53_public_ip()
    logger.info(f"public_ip  : {public_ip}")
    logger.info(f"route53_ip : {route53_ip}")
    if public_ip == route53_ip:
        logger.info("public ip and route53 ip are the same.. nothing to do")
    else:
        update_route53_public_ip(public_ip)

if __name__ == "__main__":
    main()
