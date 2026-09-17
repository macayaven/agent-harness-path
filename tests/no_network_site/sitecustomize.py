"""Fail any network connection attempted during offline course verification."""

from __future__ import annotations

import socket


def _blocked(*_args, **_kwargs):
    raise RuntimeError(
        "network access is disabled for offline course verification "
        "(COURSE_MODE=stub); a notebook tried to open a socket"
    )


socket.create_connection = _blocked
socket.socket.connect = _blocked
socket.socket.connect_ex = _blocked
