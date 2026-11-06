# Imports
import asyncio

import httpx2
from fakes import USER

from lonzo.clients.ichiro import IchiroClient, add_user
from lonzo.core.user import current_user


# Code
# A call to ichiro carries the user of the chat request
def test_call_carries_the_user() -> None:

    request = httpx2.Request("GET", "http://ichiro/notes")
    token = current_user.set(USER)
    asyncio.run(add_user(request=request))
    current_user.reset(token)

    assert request.headers["X-User-Id"] == str(USER)


# Outside a request (no user), no header goes
def test_call_without_user_has_no_header() -> None:

    request = httpx2.Request("GET", "http://ichiro/notes")
    asyncio.run(add_user(request=request))

    assert "X-User-Id" not in request.headers


# The client of the app runs add_user before every request
def test_client_adds_the_user() -> None:

    assert add_user in IchiroClient().http.event_hooks["request"]
