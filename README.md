# CloudwatchToEmail
A simple log monitor that sends an email when it finds an error in cloudwatch logs, using [hook2email](https://hook2email.com?utm_source=github.com&utm_campaign=cloudwatch-to-email).

The monitor checks the cloudwatch logs corresponding to a given pattern (in this code, any log group that contains the pattern `-{env}`, e.g. `-prod`).
If the monitor is activated every minute, and if it finds any log message that include some pattern (in this case, `ERROR` or `CRITICAL`) it sends an request to hook2email, which then trasfers the text to an email. This creates a very simple monitoring tool, which could easily be run every minute instead of every 5 minutes.
