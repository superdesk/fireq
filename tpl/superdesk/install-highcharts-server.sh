if [ `_get_json_value analytics` == "true" ]; then
    if ! install-highcharts-server; then
        echo "WARNING: Failed to install highcharts-server."
        exit 0
    fi
    echo "Highcharts server installed successfully."
fi