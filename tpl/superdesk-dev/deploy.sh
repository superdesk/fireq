[ -z "${testing:-}" ] || (
{{>testing.sh}}
)

{{>superdesk/deploy.sh}}
