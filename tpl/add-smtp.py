import argparse
import asyncio
import datetime as dt
import logging
import random
from email.parser import Parser
from pathlib import Path

from aiosmtpd.controller import Controller

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    datefmt='[%Y-%m-%d %H:%M:%S %Z]',
    format='%(asctime)s %(message)s'
)


class Handler:
    """Logging-enabled SMTP handler."""

    def __init__(self, path):
        path = Path(path)
        path.mkdir(exist_ok=True, parents=True)
        self._path = path

    async def handle_DATA(self, server, session, envelope):
        data = envelope.content.decode('utf-8', errors='replace')
        msg = Parser().parsestr(data)
        subject = msg['subject']
        rcpttos = envelope.rcpt_tos
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
        return '250 Message accepted for delivery'


if __name__ == '__main__':
    controller = None
    try:
        parser = argparse.ArgumentParser(description='Run an SMTP server.')
        parser.add_argument('addr', help='addr to bind to')
        parser.add_argument('port', type=int, help='port to bind to')
        parser.add_argument('path', help='directory to store to')
        args = parser.parse_args()

        log.info('Starting SMTP server at {0}:{1}'.format(args.addr, args.port))
        handler = Handler(args.path)
        controller = Controller(handler, hostname=args.addr, port=args.port)
        controller.start()
        log.info('SMTP server running, press Ctrl+C to stop')
        asyncio.run(asyncio.sleep(float('inf')))
    except KeyboardInterrupt:
        log.info('Cleaning up')
    except Exception as e:
        log.exception(e)
    finally:
        if controller is not None:
            controller.stop()
        log.info('SMTP server stopped')
