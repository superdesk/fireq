#!/usr/bin/env python3
import asyncio
import base64
import json
import os

from aiofiles import open
from aiohttp import web, ClientSession

auth = os.environ.get('GITHUB_AUTH')
assert auth, 'Set GITHUB_AUTH in environment as "username:token"'


def pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True)


async def http_middleware(app, handler):
    async def inner(request):
        global auth
        b64auth = base64.b64encode(auth.encode()).decode()
        headers = {'Authorization': 'Basic %s' % b64auth}
        with ClientSession(headers=headers) as session:
            request.http = session
            return await handler(request)
    return inner


async def test(request):
    body = await request.json()
    headers = dict(request.headers.items())
    print(headers)
    print(pretty_json(body))
    event = request.headers.get('X-GitHub-Event')
    if event == 'push':
        sha = body['after']
        repo = body['repository']
        url = repo['statuses_url'].format(sha=sha)
        data = {
            'state': 'pending',
            'target_url': 'http://test.superdesk.org:8080',
            'description': 'Superdesk Deploy in progress',
            'context': 'naspeh-sf/deploy/push'
        }
        async with request.http.post(url, data=json.dumps(data)) as resp:
            print(resp.status)
            print(pretty_json(await resp.json()))
            if resp.status != 201:
                return web.json_response('Can\'t create status')

        path = './push/%s' % sha
        os.makedirs(path, exist_ok=True)
        req = {
            'headers': headers,
            'json': body
        }
        async with open(path + '/request.json', mode='w') as f:
            await f.write(pretty_json(req))
        proc = await asyncio.create_subprocess_shell(
            'cd {root}; ./fire gh-push {path}'
            .format(root='.', path=path)
        )
        code = await proc.wait()
        print(code)

        update = {
            'state': 'success',
            'description': 'Superdesk Deploy passed'
        }
        data = dict(data, **update)
        async with request.http.post(url, data=json.dumps(data)) as resp:
            print(resp.status)
            print(pretty_json(await resp.json()))
    return web.json_response('OK')

app = web.Application(middlewares=[http_middleware])
app.router.add_post('/', test)
web.run_app(app)
