import re
import uuid

import pytest
from reactpy_router import Resolver, route


def test_parse_path():
    resolver = Resolver(route("/", None))
    assert resolver.parse_path("/a/b/c") == (re.compile("^/a/b/c$"), {})
    assert resolver.parse_path("/a/{b}/c") == (
        re.compile(r"^/a/(?P<b>[^/]+)/c$"),
        {"b": str},
    )
    assert resolver.parse_path("/a/{b:int}/c") == (
        re.compile(r"^/a/(?P<b>\d+)/c$"),
        {"b": int},
    )
    assert resolver.parse_path("/a/{b:int}/{c:float}/c") == (
        re.compile(r"^/a/(?P<b>\d+)/(?P<c>\d+(\.\d+)?)/c$"),
        {"b": int, "c": float},
    )
    assert resolver.parse_path("/a/{b:int}/{c:float}/{d:uuid}/c") == (
        re.compile(
            r"^/a/(?P<b>\d+)/(?P<c>\d+(\.\d+)?)/(?P<d>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-["
            r"0-9a-f]{4}-[0-9a-f]{12})/c$"
        ),
        {"b": int, "c": float, "d": uuid.UUID},
    )
    assert resolver.parse_path("/a/{b:int}/{c:float}/{d:uuid}/{e:path}/c") == (
        re.compile(
            r"^/a/(?P<b>\d+)/(?P<c>\d+(\.\d+)?)/(?P<d>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-["
            r"0-9a-f]{4}-[0-9a-f]{12})/(?P<e>.+)/c$"
        ),
        {"b": int, "c": float, "d": uuid.UUID, "e": str},
    )


def test_parse_path_unkown_conversion():
    resolver = Resolver(route("/", None))
    with pytest.raises(ValueError):
        resolver.parse_path("/a/{b:unknown}/c")


def test_parse_path_re_escape():
    """Check that we escape regex characters in the path"""
    resolver = Resolver(route("/", None))
    assert resolver.parse_path("/a/{b:int}/c.d") == (
        #                          ^ regex character
        re.compile(r"^/a/(?P<b>\d+)/c\.d$"),
        {"b": int},
    )


def test_match_star_path():
    resolver = Resolver(route("/", None))
    assert resolver.parse_path("*") == (re.compile("^.*$"), {})
