"""
Many of the tests follows the examples from the crate README and docs.
"""

import pytest

from url import URL
import url


def test_https_url():
    issue_url = URL.parse(
        "https://github.com/rust-lang/rust/issues?labels=E-easy&state=open",
    )
    assert issue_url.scheme == "https"
    assert issue_url.username == ""
    assert issue_url.password is None
    assert issue_url.host_str == "github.com"

    assert issue_url.host == url.Domain("github.com")

    assert issue_url.port is None
    assert issue_url.path == "/rust-lang/rust/issues"
    assert list(issue_url.path_segments) == ["rust-lang", "rust", "issues"]
    assert issue_url.query == "labels=E-easy&state=open"

    # TODO: Decide what API makes sense here in Python --
    #       indexing using magic constants seems weird
    # assert (&issue_url[Position::BeforePath..] == "/rust-lang/rust/issues?labels=E-easy&state=open")  # noqa: E501

    assert issue_url.fragment is None
    assert not issue_url.cannot_be_a_base


def test_cannot_be_a_base_url():
    data_url = URL.parse("data:text/plain,Hello?World#")
    assert data_url.cannot_be_a_base
    assert data_url.scheme == "data"
    assert data_url.path == "text/plain,Hello"
    assert data_url.path_segments is None
    assert data_url.query == "World"
    assert data_url.fragment == ""


def test_join():
    this_document = URL.parse("http://servo.github.io/rust-url/url/index.html")
    css_url = this_document.join("../main.css")
    assert str(css_url) == "http://servo.github.io/rust-url/main.css"


def test_invalid_ipv6_address():
    with pytest.raises(url.InvalidIPv6Address):
        URL.parse("http://[:::1]")


def test_invalid_relative_url_without_base():
    with pytest.raises(url.RelativeURLWithoutBase):
        URL.parse("../main.css")


def test_invalid_junk():
    with pytest.raises(url.URLError):
        URL.parse("https:/12949a;df;;@@@")


def test_parse_with_params():
    url = URL.parse_with_params(
        "https://example.net?dont=clobberme",
        [("lang", "rust"), ("browser", "servo")],
    )
    assert url == URL.parse(
        "https://example.net/?dont=clobberme&lang=rust&browser=servo",
    )


def test_make_relative():
    base = URL.parse("https://example.net/a/b.html")
    url = URL.parse("https://example.net/a/c.png")
    relative = base.make_relative(url)
    assert relative == "c.png"


def test_with_fragment():
    url = URL.parse("https://example.com/data.csv")
    assert url.fragment is None

    evolved = url.with_fragment("foo")
    assert (evolved.fragment, url.fragment) == ("foo", None)


@pytest.mark.parametrize(
    "base_url",
    ["http://foo.com/bar", "http://foo.com/bar/"],
)
def test_slash(base_url: str):
    """
    Support the / operator as many Python types have decided to.

    Whether the base URL ends in a slash or not, e.g. yarl.URL adds one, so we
    follow that behavior for this (and not for .join()).
    """
    joined = URL.parse(base_url) / "baz"
    assert str(joined) == "http://foo.com/bar/baz"


def test_str():
    example = "http://example.com/"
    assert str(URL.parse(example)) == example


def test_repr():
    assert repr(URL.parse("http://example.com")) == "<URL http://example.com/>"


def test_eq():
    assert URL.parse("http://example.com") == URL.parse("http://example.com")
    assert URL.parse("http://foo.com") != URL.parse("http://bar.com")


def test_hash():
    one = URL.parse("http://example.com")
    two = URL.parse("http://example.org")
    assert {one, two, one} == {one, two}


def test_domain_hash():
    url = URL.parse("http://example.com")
    domain = url.host
    assert {domain, domain} == {domain}


@pytest.mark.parametrize(
    "input,expected",
    [
        pytest.param(
            "https://example.com?a=1&b=2&c",
            [("a", "1"), ("b", "2"), ("c", "")],
            id="trailing key without value",
        ),
        pytest.param(
            "https://example.com?a=1&b=2",
            [("a", "1"), ("b", "2")],
            id="basic query pairs",
        ),
        pytest.param(
            "https://example.com?name=John%20Doe",
            [("name", "John Doe")],
            id="URL-encoded query pairs",
        ),
        pytest.param(
            "https://example.com",
            [],
            id="no query",
        ),
        pytest.param(
            "https://example.com?",
            [],
            id="empty query",
        ),
        pytest.param(
            "https://example.com?a=1&a=2",
            [("a", "1"), ("a", "2")],
            id="duplicate keys",
        ),
    ],
)
def test_query_pairs(input: str, expected: list[tuple[str, str]]):
    url = URL.parse(input)
    assert url.query_pairs == expected


def test_with_fragment_full():
    url = URL.parse("https://example.com/path")
    assert url.fragment is None

    updated = url.with_fragment("section")
    assert updated.fragment == "section"
    assert str(updated) == "https://example.com/path#section"
    assert url.fragment is None

    cleared = updated.with_fragment(None)
    assert cleared.fragment is None
    assert str(cleared) == "https://example.com/path"

    empty = url.with_fragment("")
    assert empty.fragment == ""
    assert str(empty) == "https://example.com/path#"


def test_with_query():
    url = URL.parse("https://example.com/path")
    assert url.query is None

    updated = url.with_query("key=value")
    assert updated.query == "key=value"
    assert str(updated) == "https://example.com/path?key=value"
    assert url.query is None

    replaced = updated.with_query("new=param")
    assert replaced.query == "new=param"
    assert str(replaced) == "https://example.com/path?new=param"

    cleared = updated.with_query(None)
    assert cleared.query is None
    assert str(cleared) == "https://example.com/path"

    empty = url.with_query("")
    assert empty.query == ""
    assert str(empty) == "https://example.com/path?"


def test_without_query():
    url = URL.parse("https://example.com/path?key=value&other=param")
    assert url.query == "key=value&other=param"

    cleared = url.without_query()
    assert cleared.query == ""
    assert str(cleared) == "https://example.com/path?"
    assert url.query == "key=value&other=param"

    already_clear = URL.parse("https://example.com/path")
    still_clear = already_clear.without_query()
    assert still_clear.query == ""
    assert str(still_clear) == "https://example.com/path?"


def test_with_pair():
    url = URL.parse("https://example.com/path")

    with_one = url.with_pair("key", "value")
    assert with_one.query == "key=value"
    assert with_one.query_pairs == [("key", "value")]

    with_two = with_one.with_pair("foo", "bar")
    assert with_two.query == "key=value&foo=bar"
    assert with_two.query_pairs == [("key", "value"), ("foo", "bar")]

    with_duplicate = with_two.with_pair("key", "another")
    assert with_duplicate.query_pairs == [
        ("key", "value"),
        ("foo", "bar"),
        ("key", "another"),
    ]

    with_special = url.with_pair("name", "John Doe")
    assert with_special.query is not None
    assert (
        "name=John+Doe" in with_special.query
        or "name=John%20Doe" in with_special.query
    )
    assert with_special.query_pairs == [("name", "John Doe")]


def test_with_key_only():
    url = URL.parse("https://example.com/path")

    with_key = url.with_key_only("flag")
    assert with_key.query == "flag"
    assert with_key.query_pairs == [("flag", "")]

    with_multiple = with_key.with_key_only("another")
    assert with_multiple.query_pairs == [("flag", ""), ("another", "")]

    mixed = url.with_pair("key", "value").with_key_only("flag")
    assert mixed.query_pairs == [("key", "value"), ("flag", "")]


def test_with_pairs():
    url = URL.parse("https://example.com/path")

    extended = url.with_pairs([("a", "1"), ("b", "2"), ("c", "3")])
    assert extended.query_pairs == [("a", "1"), ("b", "2"), ("c", "3")]
    assert extended.query == "a=1&b=2&c=3"

    existing = URL.parse("https://example.com/path?existing=value")
    more = existing.with_pairs([("new", "param")])
    assert more.query_pairs == [("existing", "value"), ("new", "param")]

    empty = url.with_pairs([])
    assert empty.query == ""
    assert empty.query_pairs == []

    with_duplicates = url.with_pairs([("key", "val1"), ("key", "val2")])
    assert with_duplicates.query_pairs == [("key", "val1"), ("key", "val2")]


def test_with_keys_only():
    url = URL.parse("https://example.com/path")

    extended = url.with_keys_only(["flag1", "flag2", "flag3"])
    assert extended.query_pairs == [
        ("flag1", ""),
        ("flag2", ""),
        ("flag3", ""),
    ]

    existing = URL.parse("https://example.com/path?key=value")
    more = existing.with_keys_only(["flag"])
    assert more.query_pairs == [("key", "value"), ("flag", "")]

    empty = url.with_keys_only([])
    assert empty.query == ""
    assert empty.query_pairs == []


def test_without_pair():
    url = URL.parse("https://example.com/path?a=1&b=2&c=3&a=4")

    removed_a = url.without_pair("a")
    assert removed_a.query_pairs == [("b", "2"), ("c", "3")]
    assert removed_a.query == "b=2&c=3"

    removed_b = removed_a.without_pair("b")
    assert removed_b.query_pairs == [("c", "3")]
    assert removed_b.query == "c=3"

    removed_all = removed_b.without_pair("c")
    assert removed_all.query is None
    assert removed_all.query_pairs == []

    nonexistent = url.without_pair("nothere")
    assert nonexistent.query_pairs == url.query_pairs

    url_with_encoded = URL.parse(
        "https://example.com/path?name=John+Doe&other=value",
    )
    removed_name = url_with_encoded.without_pair("name")
    assert removed_name.query_pairs == [("other", "value")]
