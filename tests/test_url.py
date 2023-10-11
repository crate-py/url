import pytest

from url import URL, URLError


def test_valid():
    """
    Follows the example from the crate README.
    """
    issue_url = URL.parse(
        "https://github.com/rust-lang/rust/issues?labels=E-easy&state=open",
    )
    assert issue_url


def test_invalid():
    with pytest.raises(URLError, match="empty host"):
        URL.parse("https:/12949a;df;;@@@")
