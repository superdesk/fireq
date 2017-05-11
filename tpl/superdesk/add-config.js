window.superdeskConfig={
    defaultTimezone: "Europe/Berlin",
    server: {
        url: "{{ host_url }}/api",
        ws: "{{ host_ws }}/ws"
    },
    iframely: {
        key: "${IFRAMELY_KEY:-}"
    },
    raven: {
        dsn: "${RAVEN_DSN:-}"
    },
    publisher: {
        protocol: "https",
        tenant: "${PUBLISHER_API_DOMAIN:-}",
        domain: "${PUBLISHER_API_SUBDOMAIN:-}",
        base: "api/v1"
    }
};

