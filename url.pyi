from collections.abc import Iterable
from typing import Self

class URLError(Exception): ...
class RelativeURLWithoutBase(Exception): ...
class InvalidIPv6Address(Exception): ...

class URL:
    cannot_be_a_base: bool
    host: Domain
    host_str: str
    password: str
    path: str
    path_segments: Iterable[str]
    scheme: str
    username: str

    def __truediv__(self, other: str) -> Self: ...
    @classmethod
    def parse(cls, input: str) -> Self: ...
    @classmethod
    def parse_with_params(
        cls,
        input: str,
        params: Iterable[tuple[str, str]],
    ) -> Self: ...
    def join(self, other: str) -> Self: ...
    def make_relative(self, other: Self) -> str: ...

class Domain:
    def __init__(self, value: str): ...
