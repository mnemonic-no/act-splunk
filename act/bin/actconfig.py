import sys
import os
from splunk.clilib import cli_common as cli

appdir = os.path.dirname(os.path.dirname(__file__))

# Use local modules
sys.path.insert(0, os.path.join(appdir, "bin/lib/chardet"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/idna"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/python-certifi"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/requests"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/urllib3"))
sys.path.insert(0, os.path.join(appdir, "bin/lib/ipaddress"))

import act.api

def setup():
    cfg = cli.getConfStanza('act', 'config')
    app = cli.getConfStanza('app', 'launcher')
    api_url = cfg.get("api_url")
    user_id = cfg.get("act_userid")
    api_proxy = cfg.get("api_proxy")
    api_http_user = cfg.get("api_http_user")
    api_http_password = cfg.get("api_http_auth")

    requests_opt = {
        "headers": { # Include version string in user agent header
            "User-Agent": "act-splunk-{}".format(app.get("version"))
        }
    }
    if api_http_user or api_http_password:
        requests_opt["auth"] = (api_http_user, api_http_password)

    if api_proxy:
        requests_opt["proxies"] = {
            "http": api_proxy,
            "https": api_proxy,
        }

    return act.api.Act(
        api_url,
        user_id=user_id,
        log_level="warning",
        requests_common_kwargs=requests_opt
    )
