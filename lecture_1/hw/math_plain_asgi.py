import json

from urllib.parse import parse_qs
from math import factorial
from typing import Any, Awaitable, Callable

Scope = dict[str, Any]
Receive = Callable[[], Awaitable[dict[str, Any]]]
Send = Callable[[dict[str, Any]], Awaitable[None]]


async def app(scope: Scope, receive: Receive, send: Send) -> None:
    assert scope["type"] == "http"

    method = scope["method"]
    path: str = scope["path"]

    if method == "GET":
        if path == "/factorial":
            await handle_factorial(scope, receive, send)
        elif path.startswith("/fibonacci/"):
            await handle_fibonacci(scope, receive, send)
        elif path == "/mean":
            await handle_mean(scope, receive, send)
        else:
            await send_response(send, 404, b'')
    else:
        await send_response(send, 404, b'')


async def handle_factorial(scope: Scope, receive: Receive, send: Send) -> None:
    query_str = scope.get('query_string', b'').decode()
    query = parse_qs(query_str)
    n = query.get('n')

    if not n:
        await send_response(send, 422, b'')
        return

    try:
        n = int(n[0])
    except ValueError:
        await send_response(send, 422, b'')
        return

    if n < 0:
        await send_response(send, 400, b'')
        return

    result = factorial(n)
    response_body = json.dumps({"result": result}).encode()
    await send_response(send, 200, response_body)


async def handle_fibonacci(scope: Scope, receive: Receive, send: Send) -> None:
    def fibonacci(num: int) -> int:
        a, b = 0, 1
        for _ in range(num):
            a, b = b, a + b
        return a

    path = scope["path"]
    n_str = path[len("/fibonacci/"):]

    if not n_str:
        await send_response(send, 422, b'')
        return

    try:
        n = int(n_str)
    except ValueError:
        await send_response(send, 422, b'')
        return

    if n < 0:
        await send_response(send, 400, b'')
        return

    result = fibonacci(n)
    response_body = json.dumps({"result": result}).encode()
    await send_response(send, 200, response_body)


async def handle_mean(scope: Scope, receive: Receive, send: Send) -> None:
    body_bytes = b''
    more_body = True

    while more_body:
        message = await receive()
        if message['type'] == 'http.request':
            body_bytes += message.get('body', b'')
            more_body = message.get('more_body', False)

    try:
        data = json.loads(body_bytes)
    except json.JSONDecodeError:
        await send_response(send, 422, b'')
        return

    if not isinstance(data, list):
        await send_response(send, 422, b'')
        return

    if not data:
        await send_response(send, 400, b'')
        return

    try:
        numbers = [float(x) for x in data]
    except (ValueError, TypeError):
        await send_response(send, 422, b'')
        return

    mean_value = sum(numbers) / len(numbers)
    response_body = json.dumps({"result": mean_value}).encode()
    await send_response(send, 200, response_body)


async def send_response(send: Send, status_code: int, body: bytes, content_type: str = 'application/json') -> None:
    match status_code:
        case 400:
            result_body = json.dumps({"error": "Bad request"}).encode()
        case 404:
            result_body = json.dumps({"error": "Not found"}).encode()
        case 422:
            result_body = json.dumps({"error": "Unprocessable Entity"}).encode()
        case 200:
            result_body = body
        case _:
            result_body = b''
    headers = [
        [b'content-type', content_type.encode()]
    ]
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': headers,
    })
    await send({
        'type': 'http.response.body',
        'body': result_body,
    })
