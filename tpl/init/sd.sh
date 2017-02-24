cat <<"EOF" >> {{config}}
{{>init/.superdesk.sh}}
EOF

if [[ "$(hostname)" =~ ^sd-naspeh ]]; then
    _activate
    pip install -e git+https://github.com/superdesk/superdesk-core.git@1.6#egg=Superdesk-Core
fi
