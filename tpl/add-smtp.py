import argparse
import asyncore
import datetime as dt
import logging
import random
import smtpd
from email.parser import Parser
from pathlib import Path

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    datefmt='[%Y-%m-%d %H:%M:%S %Z]',
    format='%(asctime)s %(message)s'
)


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
        log.info('to=%r subject=%r', rcpttos, subject)
        for addr in rcpttos:
            name = (
                '{0:%Y%V/%w-%H%M%S}-{1:02d}-{2}.log'
                .format(dt.datetime.now(), random.randint(0, 99), addr)
            )
            log.info('filename=%r to=%r subject=%r', name, addr, subject)
            email = self._path / name
            email.parent.mkdir(exist_ok=True)
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
