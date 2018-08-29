#!/usr/bin/env python

import os
import sys
import csv
from splunk.clilib import cli_common as cli

appdir = os.path.dirname(os.path.dirname(__file__))

# Use local modules
sys.path.insert(0, os.path.join(appdir, "bin/lib/chardet"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/idna"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/python-certifi"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/requests"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/urllib3"))

import act

def fact_search(client, object_value):

    result = []
    for fact in client.fact_search(object_value=object_value):
        heading = fact.type.name

        for obj in fact.objects:
            value = obj.value
            if fact.value and fact.value != "-":
                # Append fact value if it is set
                value += " ({})".format(fact.value)
            if obj.value != object_value:
                result.append({"act.{}".format(heading): value})

    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python act_search.py object_value_field")
        sys.exit(2)

    cfg = cli.getConfStanza('act', 'config')

    api_url = cfg.get("api_url")
    user_id = cfg.get("act_userid")
    api_proxy = cfg.get("api_proxy")
    api_http_user = cfg.get("api_http_user")
    api_http_password = cfg.get("api_http_auth")

    requests_opt = {}
    if api_http_user or api_http_password:
        requests_opt["auth"] = (api_http_user, api_http_password)

    if api_proxy:
        requests_opt["proxies"] = {
            "http": api_proxy,
            "https": api_proxy,
        }

    client = act.Act(
        api_url,
        user_id=user_id,
        log_level="warning",
        requests_common_kwargs=requests_opt
    )

    object_value_field = sys.argv[1]

    facts = []
    headers = {}

    for row in csv.DictReader(sys.stdin):
        object_value = row.get(object_value_field, None)

        if not object_value:
            continue

        for fact in fact_search(client, object_value):
            fact[object_value_field] = object_value
            facts.append(fact)

            for key, value in row.iteritems():
                if value and not fact.get(key, None):
                    fact[key] = value

            for key in fact.keys():
                if key not in headers:
                    headers[key] = True

    w = csv.DictWriter(sys.stdout, fieldnames=headers.keys())
    w.writeheader()
    for fact in facts:
        w.writerow(fact)


main()
