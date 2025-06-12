if [ `_get_json_value analytics` == "true" ]; then
    if ! install-highcharts-server; then
        echo "WARNING: Failed to install highcharts-export-server."
        exit 0
    fi
    echo "Highcharts export server installed successfully."
fi