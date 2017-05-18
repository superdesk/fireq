#!/usr/bin/env python
from superdesk.factory import get_app

application = get_app(config_object='settings')
celery = application.celery


def main():
    import sys

    from flask_script import Manager
    from superdesk import COMMANDS
    from superdesk.ws import create_server

    if len(sys.argv) == 2 and sys.argv[1] == 'ws':
        create_server(application.config)
    else:
        manager = Manager(application)
        manager.run(COMMANDS)


if __name__ == '__main__':
    main()
