import os
import requests

MOZ_API_KEY = os.getenv("MOZ_API_KEY")
MOZ_SECRET_KEY = os.getenv("MOZ_SECRET_KEY")
MOZ_API_URL = "https://api.moz.com/jsonrpc"

def moz_rpc(method, params):
    headers = {
        "x-moz-token": MOZ_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "jsonrpc": "2.0",
        "id": "vertex",
        "method": method,
        "params": {"data": params}
    }
    resp = requests.post(MOZ_API_URL, headers=headers, json=body)
    resp.raise_for_status()
    return resp.json()["result"]

def get_domain_overview(domain):
    return moz_rpc("DataSiteMetricsFetchMultipleAction", {"targets": [domain]})

def get_keyword_difficulty(term):
    return moz_rpc("DataKeywordMetricsOpportunityFetchAction", {"keyword": term})
