if [ -f {{fireq_json}} ] && [ `jq ".videoserver?" {{fireq_json}}` == "true" ]; then
    apt-get -y update
    apt-get install -y --no-install-recommends ffmpeg bc python3-setuptools python3-wheel

    mkdir /opt/videoserver
    cd /opt/videoserver
    git clone https://github.com/superdesk/video-server-app.git
    python3 -m venv env
    source env/bin/activate
    pip install wheel "celery[redis]"
    pip install -r video-server-app/requirements.txt
    # deactivate
fi
