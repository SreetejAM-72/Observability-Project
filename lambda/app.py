import json
import logging
import os
from typing import Any, Dict

from ec2_client import (
    get_instance_application_tag,
    list_all_application_tags,
)
from newrelic_client import NewRelicClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

NEW_RELIC_API_KEY = os.environ["NEW_RELIC_API_KEY"]
NEW_RELIC_ACCOUNT_ID = int(os.environ["NEW_RELIC_ACCOUNT_ID"])


def handle_event_driven(event: Dict[str, Any]) -> None:
    instance_id = event["detail"]["instance-id"]

    application = get_instance_application_tag(instance_id)

    if not application:
        logger.info("instance_missing_application_tag instance_id=%s", instance_id)
        return

    nr = NewRelicClient(NEW_RELIC_API_KEY)

    if nr.policy_exists_by_name(NEW_RELIC_ACCOUNT_ID, application):
        logger.info("policy_exists application=%s", application)
        return

    nr.create_alert_policy(NEW_RELIC_ACCOUNT_ID, application)

    logger.info("policy_created application=%s", application)


def handle_scheduled_sync() -> None:
    nr = NewRelicClient(NEW_RELIC_API_KEY)

    applications = list_all_application_tags()

    for app in applications:
        if not nr.policy_exists_by_name(NEW_RELIC_ACCOUNT_ID, app):
            nr.create_alert_policy(NEW_RELIC_ACCOUNT_ID, app)
            logger.info("policy_created application=%s", app)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("event=%s", json.dumps(event))

    # Scheduled invocation
    if "source" not in event:
        handle_scheduled_sync()
        return {"status": "sync_complete"}

    # EventBridge EC2 trigger
    handle_event_driven(event)

    return {"status": "processed"}