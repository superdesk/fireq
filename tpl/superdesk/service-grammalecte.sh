cat <<"EOF" > /etc/systemd/system/grammalecte.service
[Unit]
Description=Grammalecte spellchecker server
Wants=network.target
After=network.target
StartLimitIntervalSec=0

[Service]
ExecStart=/usr/bin/python3 grammalecte-server.py --host localhost --port 9999
WorkingDirectory=/grammalecte
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl enable grammalecte
systemctl restart grammalecte
