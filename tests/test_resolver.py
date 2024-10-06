import re
import uuid

import pytest

from reactpy_router import route
from reactpy_router.resolvers import StarletteResolver


def test_resolve_any():
    resolver = StarletteResolver(route("{404:any}", "Hello World"))
    assert resolver.parse_path("{404:any}") == re.compile("^(?P<_numeric_404>.*)$")
    assert resolver.converter_mapping == {"_numeric_404": str}
    assert resolver.resolve("/hello/world") == ("Hello World", {"404": "/hello/world"})


def test_parse_path():
    resolver = StarletteResolver(route("/", None))
    assert resolver.parse_path("/a/b/c") == re.compile("^/a/b/c$")
    assert resolver.converter_mapping == {}

    assert resolver.parse_path("/a/{b}/c") == re.compile(r"^/a/(?P<b>[^/]+)/c$")
    assert resolver.converter_mapping == {"b": str}

    assert resolver.parse_path("/a/{b:int}/c") == re.compile(r"^/a/(?P<b>\d+)/c$")
    assert resolver.converter_mapping == {"b": int}

    assert resolver.parse_path("/a/{b:int}/{c:float}/c") == re.compile(r"^/a/(?P<b>\d+)/(?P<c>\d+(\.\d+)?)/c$")
    assert resolver.converter_mapping == {"b": int, "c": float}

    assert resolver.parse_path("/a/{b:int}/{c:float}/{d:uuid}/c") == re.compile(
        r"^/a/(?P<b>\d+)/(?P<c>\d+(\.\d+)?)/(?P<d>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/c$"
    )
    assert resolver.converter_mapping == {"b": int, "c": float, "d": uuid.UUID}

    assert resolver.parse_path("/a/{b:int}/{c:float}/{d:uuid}/{e:path}/c") == re.compile(
        r"^/a/(?P<b>\d+)/(?P<c>\d+(\.\d+)?)/(?P<d>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<e>.+)/c$"
    )
    assert resolver.converter_mapping == {
        "b": int,
        "c": float,
        "d": uuid.UUID,
        "e": str,
    }


def test_parse_path_unkown_conversion():
    resolver = StarletteResolver(route("/", None))
    with pytest.raises(ValueError):
        resolver.parse_path("/a/{b:unknown}/c")


def test_parse_path_re_escape():
    """Check that we escape regex characters in the path"""
    resolver = StarletteResolver(route("/", None))
    assert resolver.parse_path("/a/{b:int}/c.d") == re.compile(r"^/a/(?P<b>\d+)/c\.d$")
    assert resolver.converter_mapping == {"b": int}
