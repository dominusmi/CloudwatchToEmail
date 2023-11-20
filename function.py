import dataclasses
import datetime
import os
from typing import Dict

import boto3

@dataclasses.dataclass
class LogGroupHookEvent:
    event_type: str
    message: str


def send_hook2email(uuid: str, data: Any):
    # use hook2email to send the json data.
    requests.post(
        url=f"https://api.hook2email.com/hook/{uuid}/send",
        json=data
    )


def get_env():
  return os.environ["ENV"]
  

def get_groups_to_follow(logs):
  # Customise this function in order to only fetch the groups for which you want to check the logs. In this case, it looks for 
  # groups that have -{env} as part of their name, e.g. my-endpoint-prod for the prod monitor
  return [
        elm["logGroupName"] for elm in logs.describe_log_groups(logGroupNamePattern=f"-{get_env()}")['logGroups']
        if "LogMonitor" not in elm["logGroupName"]
    ]


def handler(event: Dict, context):
    end = datetime.datetime.utcnow()
    print(f"Starting - {end}")
    session = boto3.Session()
    logs = session.client("logs")
    group_names = get_groups_to_follow(logs)

    # The template for the alert sent by email
    event_message_template = "{group}/{stream}<br>{message}"
    messages = []
    error_count = 0
    critical_count = 0

    for gn in group_names:
        # We check for the pattern ERROR or CRITICAL, which are the two highest level when using the python logging library
        # The timedelta is based on how often the lambda is triggered. In this case, it's triggered every 5 minutes and, for safety, 
        # we add an extra minute to the interval. In practice, there's pretty much always less than 5 seconds
        filter_response = logs.filter_log_events(
            logGroupName=gn,
            startTime=int(
                round((end - datetime.timedelta(seconds=60 * 6)).timestamp() * 1000)),
            endTime=int(round(end.timestamp() * 1000)),
            filterPattern="?ERROR ?CRITICAL"
        )
        for event in filter_response["events"]:
            error_count += 1
            if "CRITICAL" in event["message"]:
                critical_count += 1

            # format the events to the email format
            messages.append(
                event_message_template.format(group=gn, stream=event["logStreamName"], message=event["message"])
            )

    
    if len(messages) > 0:
        event =f'Found {error_count} errors, {critical_count} critical'
        print(event)
        # HOOK_UUID is the id of the hook2email endpoint to use.
        send_hook2email(
            os.environ["HOOK_UUID"],
            LogGroupHookEvent(
                event_type=event,
                message="<br><br>".join(messages)
            ).__dict__
        )
