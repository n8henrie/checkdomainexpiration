"""checkdomainexpiration.py :: Check expiration date for domains.

Required environment variables:
    DOMAINS: Comma separated list of domains to check
    PUSHOVER_SNS_ARN: ARN for Pushover SNS service
"""

import datetime
import os
from collections import namedtuple

import boto3
from whois import NICClient


def get_expiration_date(domain_info: str) -> datetime.date:
    """Parse whois results and return the expiration date for the domain.

    Args:
        domain_info: whois lookup results

    Returns:
        Domain expiration date as datetime
    """
    ExpiryInfo = namedtuple("ExpiryInfo", "key_str format_string")

    expiry_infos = (
            ExpiryInfo("Expiration Date: ", "%d-%b-%Y"),
            ExpiryInfo("Registry Expiry Date: ", "%Y-%m-%dT%H:%M:%SZ"),
            )

    for line in domain_info.splitlines():
        stripped = line.strip()

        for expiry_info in expiry_infos:

            if stripped.startswith(expiry_info.key_str):

                date_str = stripped.split(expiry_info.key_str)[-1]
                format_string = expiry_info.format_string

                dt = datetime.datetime.strptime(date_str, format_string)
                return dt.date()

    else:
        raise ValueError("Could not find expiration date in domain_info")


def get_domain_info(domain: str) -> str:
    """Make a whois lookup for domain.

    Args:
        domain: domain to look up

    Returns:
        whois lookup results
    """
    nicclient = NICClient()
    options = {"quick": True}
    flags = 0
    domain_info = nicclient.whois_lookup(
            query_arg=domain,
            options=options,
            flags=flags
            )
    return domain_info


def format_output(delta: datetime.timedelta, domain: str) -> str:
    """Format output string from timedelta and domain."""
    return f"{delta.days} days remaining for domain {domain}"


def lambda_handler(event: dict, context: dict) -> None:

    sns = boto3.client(service_name="sns")
    topic_arn = os.environ['PUSHOVER_SNS_ARN']

    domains = os.environ['DOMAINS'].split(",")
    for domain in domains:
        domain_info = get_domain_info(domain)
        exp_date = get_expiration_date(domain_info)

        remaining = exp_date - datetime.datetime.now().date()
        output = format_output(delta=remaining, domain=domain)

        print(output)
        if remaining > datetime.timedelta(30):
            sns.publish(TopicArn=topic_arn, Message=output)
