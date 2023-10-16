"""
Many of the tests follows the examples from the crate README.
"""

import pytest

from url import URL, InvalidIPv6Address, RelativeURLWithoutBase, URLError


def test_https_url():
    issue_url = URL.parse(
        "https://github.com/rust-lang/rust/issues?labels=E-easy&state=open",
    )
    assert issue_url.scheme == "https"
    assert issue_url.username == ""
    assert issue_url.password is None
    assert issue_url.host_str == "github.com"

    # TODO: Decide what API makes sense here in Python --
    #       get back an IP address and otherwise error, or some other API
    # assert (issue_url.host() == Some(Host::Domain("github.com")))

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
    with pytest.raises(InvalidIPv6Address):
        URL.parse("http://[:::1]")


def test_invalid_relative_url_without_base():
    with pytest.raises(RelativeURLWithoutBase):
        URL.parse("../main.css")


def test_invalid_junk():
    with pytest.raises(URLError):
        URL.parse("https:/12949a;df;;@@@")
