=============
Compatibility
=============

``url.py`` is currently in beta so long as version numbers begin with a ``0``, meaning its public interface may change if issues are uncovered, though not typically without reason.
Once it seems clear that the interfaces look correct (likely after ``url.py`` is in use for some period of time) versioning will move to `CalVer <https://calver.org/>`_ and interfaces will not change in backwards-incompatible ways without deprecation periods.

.. note::

    Backwards compatibility is always defined relative to the URL specifications implemented by our underlying library (the ``url`` crate).
    Changing a behavior which is explicitly incorrect according to the relevant specifications is not considered a backwards-incompatible change -- on the contrary, it's considered a bug fix.

In the spirit of `having some explicit detail on url.py's public interfaces <regret:before-you-deprecate:document your public api>`, here is a non-exhaustive list of things which are *not* part of the ``url.py`` public interface, and therefore which may change without warning, even once no longer in beta:

* All commonly understood indicators of privacy in Python -- in particular, (sub)packages, modules and identifiers beginning with a single underscore.
  In the case of modules or packages, this includes *all* of their contents recursively, regardless of their naming.
* All contents in the ``tests`` package unless explicitly indicated otherwise
* The precise contents and wording of exception messages raised by any callable, private *or* public.
* The precise contents of the ``__repr__`` of any type defined in the package.
* The ability to *instantiate* exceptions defined anywhere in the package, with the sole exception of those explicitly indicating they are publicly instantiable.
* The instantiation of any type with no public identifier, even if instances of it are returned by other public API.
* The concrete types within the signature of a callable whenever they differ from their documented types.
  In other words, if a function documents that it returns an argument of type ``Mapping[int, Sequence[str]]``, this is the promised return type, not whatever concrete type is returned which may be richer or have additional attributes and methods.
  Changes to the signature will continue to guarantee this return type (or a broader one) but indeed are free to change the concrete type.
* Subclassing of any class defined throughout the package.
  Doing so is not supported for any object.

If any API usage may be questionable, feel free to open a discussion (or issue if appropriate) to clarify.
