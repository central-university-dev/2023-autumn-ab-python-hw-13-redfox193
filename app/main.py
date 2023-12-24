import json

from app.api import api


async def read_body(receive) -> dict | list:
    message = await receive()
    body = json.loads(message.get('body').decode())
    return body


async def app(scope, receive, send):
    assert scope['type'] == 'http'
    body = await read_body(receive)

    await api.process_request(scope['method'], scope['path'], body, send)
