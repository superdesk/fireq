import argparse
import asyncore
import smtpd
import time
from email.parser import Parser
from pathlib import Path

from . import log


class Server(smtpd.SMTPServer, object):
    """Logging-enabled SMTPServer instance."""

    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        path = Path(path)
        path.mkdir(exist_ok=True)
        self._path = path

    def process_message(self, peer, mailfrom, rcpttos, data):
        msg = Parser().parsestr(data)
        subject = msg['subject']
        msgid = msg['message-id'].strip('<>')
        name = '%s:%s:%s:%s.log' % (time.time(), rcpttos[0], subject, msgid)
        email = self._path / name
        email.write_text(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run an SMTP server.')
    parser.add_argument('addr', help='addr to bind to')
    parser.add_argument('port', type=int, help='port to bind to')
    parser.add_argument('path', help='directory to store to')
    args = parser.parse_args()

    log.info('Starting SMTP server at {0}:{1}'.format(args.addr, args.port))
    server = Server(args.path, (args.addr, args.port), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        log.info('Cleaning up')
