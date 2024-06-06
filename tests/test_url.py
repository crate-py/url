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
