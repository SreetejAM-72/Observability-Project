import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger()

NEW_RELIC_GRAPHQL_ENDPOINT = "https://api.newrelic.com/graphql"


def _build_session(api_key: str) -> requests.Session:
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    session.headers.update({
        "API-Key": api_key,
        "Content-Type": "application/json",
    })

    return session


class NewRelicClient:
    def __init__(self, api_key: str) -> None:
        self.session = _build_session(api_key)

    def _execute_graphql(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = self.session.post(
            NEW_RELIC_GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables},
            timeout=10,
        )

        if response.status_code != 200:
            logger.error(
                "newrelic_request_failed status=%s response=%s",
                response.status_code,
                response.text,
            )
            response.raise_for_status()

        return response.json()

    def policy_exists_by_name(self, account_id: int, policy_name: str) -> bool:
        query = """
        query($accountId: Int!, $name: String!) {
          actor {
            account(id: $accountId) {
              alerts {
                policiesSearch(searchCriteria: {name: $name}) {
                  policies { id }
                }
              }
            }
          }
        }
        """

        data = self._execute_graphql(
            query,
            {"accountId": account_id, "name": policy_name},
        )

        policies = (
            data.get("data", {})
            .get("actor", {})
            .get("account", {})
            .get("alerts", {})
            .get("policiesSearch", {})
            .get("policies", [])
        )

        return len(policies) > 0

    def create_alert_policy(self, account_id: int, policy_name: str) -> None:
        mutation = """
        mutation CreateAlertPolicy($accountId: Int!, $name: String!) {
          alertsPolicyCreate(accountId: $accountId, policy: {name: $name}) {
            id
          }
        }
        """

        self._execute_graphql(
            mutation,
            {"accountId": account_id, "name": policy_name},
        )