"""Offline tests have no model credentials and cannot resolve external hosts."""

import socket

import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def offline(monkeypatch, request):
    if request.node.get_closest_marker("live"):
        return
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    original = socket.getaddrinfo
    connect = socket.socket.connect

    def resolve(host, *args, **kwargs):
        if host not in {None, "localhost", "127.0.0.1", "::1", b"localhost"}:
            raise AssertionError("External network is forbidden in offline tests.")
        return original(host, *args, **kwargs)

    def local_connect(sock, address):
        if isinstance(address, tuple) and address[0] not in {"127.0.0.1", "::1", "localhost"}:
            raise AssertionError("External network is forbidden in offline tests.")
        return connect(sock, address)

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    monkeypatch.setattr(socket.socket, "connect", local_connect)
