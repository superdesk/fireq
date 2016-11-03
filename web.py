#!/usr/bin/env python3
import asyncio
import base64
import json
import os

from aiofiles import open
from aiohttp import web

secret = os.environ.get('SECRET')
assert secret, 'Set SECRET environment variable'


def pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True)


async def test(request):
    body = await request.json()
    headers = dict(request.headers.items())
    print(headers)
    print(pretty_json(body))
    event = request.headers.get('X-GitHub-Event')
    if event == 'push':
        sha = body['after']
        repo = body['repository']

        path = './push/%s' % sha
        os.makedirs(path, exist_ok=True)
        req = {
            'headers': headers,
            'json': body
        }
        async with open(path + '/request.json', mode='w') as f:
            await f.write(pretty_json(req))
        proc = await asyncio.create_subprocess_shell(
            'cd {root}; ./fire gh-push {path} --clean --capture'
            .format(root='.', path=path)
        )
    return web.json_response('OK')

app = web.Application()
app.router.add_post('/%s/' % secret, test)
web.run_app(app)
