==========
``url.py``
==========

|PyPI| |Pythons| |CI|

.. |PyPI| image:: https://img.shields.io/pypi/v/url-py.svg
  :alt: PyPI version
  :target: https://pypi.org/project/url-py/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/url-py.svg
  :alt: Supported Python versions
  :target: https://pypi.org/project/url-py/

.. |CI| image:: https://github.com/crate-py/url/workflows/CI/badge.svg
  :alt: Build status
  :target: https://github.com/crate-py/url/actions?query=workflow%3ACI


Python bindings to the `Rust url crate <https://docs.rs/url/>`_.

Installation
------------

The distribution on PyPI is named ``url.py`` (equivalently ``url-py``), and thus can be installed via e.g.:

.. code:: sh

    $ pip install url-py

Note that if you install ``url-py`` from source, you will need a Rust toolchain installed, as it is a build-time dependency.
If you believe you are on a common platform which should have wheels built (i.e. and not need to compile from source), feel free to file an issue or pull request modifying the GitHub action used here to build wheels via ``maturin``.
