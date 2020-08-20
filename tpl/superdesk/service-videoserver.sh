cat <<"EOF" > /etc/systemd/system/videoserver.service
[Unit]
Description=Video editor server
Wants=network.target
After=network.target
StartLimitIntervalSec=0

[Service]
ExecStart=/bin/sh -c '. ../env/bin/activate && exec honcho start --no-colour'
WorkingDirectory=/opt/videoserver/video-server-app
Environment=CELERY_BROKER_URL=redis://localhost:6379/2
Environment=MONGO_HOST=data-sd
Environment=MONGO_DBNAME={{db_name}}_videoserver
Environment=FS_MEDIA_STORAGE_PATH=/opt/videoserver/media
Environment=FILE_STREAM_PROXY_ENABLED=True
Environment=FILE_STREAM_PROXY_URL=http{{#host_ssl}}s{{/host_ssl}}://{{host}}/video_stream
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /var/log/videoserver/

cat <<EOF >> /opt/videoserver/video-server-app/Procfile
logs: journalctl -u videoserver -f >> /var/log/videoserver/main.log
EOF

systemctl enable videoserver
systemctl restart videoserver
