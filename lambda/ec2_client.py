from typing import List, Optional

import boto3

ec2 = boto3.client("ec2")


def get_instance_application_tag(instance_id: str) -> Optional[str]:
    response = ec2.describe_instances(InstanceIds=[instance_id])

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            for tag in instance.get("Tags", []):
                if tag["Key"] == "application":
                    return tag["Value"]

    return None


def list_all_application_tags() -> List[str]:
    paginator = ec2.get_paginator("describe_instances")

    applications = set()

    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                for tag in instance.get("Tags", []):
                    if tag["Key"] == "application":
                        applications.add(tag["Value"])

    return list(applications)