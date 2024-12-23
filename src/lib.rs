use std::{
    collections::hash_map::DefaultHasher,
    hash::{Hash, Hasher},
};

use pyo3::{
    create_exception, exceptions::PyException, prelude::*, pybacked::PyBackedStr, types::PyType,
};
use url::{ParseError, Url};

create_exception!(url, URLError, PyException);

create_exception!(url, EmptyHost, URLError);
create_exception!(url, IdnaError, URLError);
create_exception!(url, InvalidPort, URLError);
create_exception!(url, InvalidIPv4Address, URLError);
create_exception!(url, InvalidIPv6Address, URLError);
create_exception!(url, InvalidDomainCharacter, URLError);
create_exception!(url, RelativeURLWithoutBase, URLError);
create_exception!(url, RelativeURLWithCannotBeABaseBase, URLError);
create_exception!(url, SetHostOnCannotBeABaseURL, URLError);

#[repr(transparent)]
#[pyclass(name = "URL", module = "url", frozen)]
struct UrlPy {
    inner: Url,
}

fn from_result(input: Result<url::Url, ParseError>) -> PyResult<UrlPy> {
    match input {
        Ok(inner) => Ok(UrlPy { inner }),
        Err(e) => Err(match e {
            ParseError::EmptyHost => EmptyHost::new_err(e.to_string()),
            ParseError::IdnaError => IdnaError::new_err(e.to_string()),
            ParseError::InvalidPort => InvalidPort::new_err(e.to_string()),
            ParseError::InvalidIpv4Address => InvalidIPv4Address::new_err(e.to_string()),
            ParseError::InvalidIpv6Address => InvalidIPv6Address::new_err(e.to_string()),
            ParseError::InvalidDomainCharacter => InvalidDomainCharacter::new_err(e.to_string()),
            ParseError::RelativeUrlWithoutBase => RelativeURLWithoutBase::new_err(e.to_string()),
            ParseError::RelativeUrlWithCannotBeABaseBase => {
                RelativeURLWithCannotBeABaseBase::new_err(e.to_string())
            }
            ParseError::SetHostOnCannotBeABaseUrl => {
                SetHostOnCannotBeABaseURL::new_err(e.to_string())
            }
            _ => URLError::new_err(e.to_string()),
        }),
    }
}

#[pymethods]
impl UrlPy {
    fn __repr__(&self) -> String {
        format!("<URL {}>", self.inner.as_str())
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.inner == other.inner
    }

    fn __ne__(&self, other: &Self) -> bool {
        self.inner != other.inner
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    fn __str__(&self) -> &str {
        self.inner.as_str()
    }

    fn __truediv__(&self, other: &str) -> PyResult<Self> {
        // .join()'s behavior depends on whether the URL has a trailing slash or not --
        // which is good! But here for division we follow the convention of e.g. yarl that someone
        // using / always wants to simply add one, so the behavior here deviates from a simple join
        if let Some(segments) = self.inner.path_segments() {
            if let Some(last) = segments.last() {
                if !last.is_empty() {
                    return self.join(format!("{}/{}", last, other).as_str());
                }
            }
        }
        self.join(other)
    }

    #[classmethod]
    fn parse(_cls: &Bound<'_, PyType>, input: &str) -> PyResult<Self> {
        from_result(Url::parse(input))
    }

    #[classmethod]
    fn parse_with_params(
        _cls: &Bound<'_, PyType>,
        input: &str,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        // FIXME: Partially reimplemented until we know how to pass PyIterators to Rust Iterators
        let mut url = from_result(Url::parse(input))?;
        for each in value.try_iter()? {
            let (k, v): (PyBackedStr, PyBackedStr) = each?.extract()?;
            url.inner
                .query_pairs_mut()
                .append_pair(k.as_ref(), v.as_ref());
        }
        Ok(url)
    }

    fn join(&self, input: &str) -> PyResult<Self> {
        from_result(self.inner.join(input))
    }

    fn make_relative(&self, url: &UrlPy) -> Option<String> {
        self.inner.make_relative(&url.inner)
    }

    #[getter]
    fn scheme(&self) -> &str {
        self.inner.scheme()
    }

    #[getter]
    fn host(&self) -> Option<HostPy> {
        let host = self.inner.host()?;
        Some(HostPy {
            inner: host.to_owned(),
        })
    }

    #[getter]
    fn username(&self) -> &str {
        self.inner.username()
    }

    #[getter]
    fn password(&self) -> Option<&str> {
        self.inner.password()
    }

    #[getter]
    fn host_str(&self) -> Option<&str> {
        self.inner.host_str()
    }

    #[getter]
    fn port(&self) -> Option<u16> {
        self.inner.port()
    }

    #[getter]
    fn path(&self) -> &str {
        self.inner.path()
    }

    #[getter]
    fn path_segments(&self) -> Option<Vec<&str>> {
        // FIXME: Figure out how to preserve this being an iterator.
        Some(self.inner.path_segments()?.collect())
    }

    #[getter]
    fn query(&self) -> Option<&str> {
        self.inner.query()
    }

    #[getter]
    fn fragment(&self) -> Option<&str> {
        self.inner.fragment()
    }

    #[getter]
    fn cannot_be_a_base(&self) -> bool {
        self.inner.cannot_be_a_base()
    }

    #[pyo3(signature = (fragment=None))]
    fn with_fragment(&self, fragment: Option<&str>) -> Self {
        let mut cloned = self.inner.clone();
        cloned.set_fragment(fragment);
        UrlPy { inner: cloned }
    }
}

#[repr(transparent)]
#[pyclass(name = "Domain", module = "url", frozen)]
struct HostPy {
    inner: url::Host,
}

#[pymethods]
impl HostPy {
    #[new]
    fn new(input: String) -> Self {
        Self {
            inner: url::Host::Domain(input),
        }
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.inner == other.inner
    }

    fn __ne__(&self, other: &Self) -> bool {
        self.inner != other.inner
    }
}

#[pymodule]
#[pyo3(name = "url")]
fn url_py(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<UrlPy>()?;
    m.add_class::<HostPy>()?;

    m.add("URLError", py.get_type::<URLError>())?;
    m.add("EmptyHost", py.get_type::<EmptyHost>())?;
    m.add("IdnaError", py.get_type::<IdnaError>())?;
    m.add("InvalidPort", py.get_type::<InvalidPort>())?;
    m.add("InvalidIPv4Address", py.get_type::<InvalidIPv4Address>())?;
    m.add("InvalidIPv6Address", py.get_type::<InvalidIPv6Address>())?;
    m.add(
        "InvalidDomainCharacter",
        py.get_type::<InvalidDomainCharacter>(),
    )?;
    m.add(
        "RelativeURLWithoutBase",
        py.get_type::<RelativeURLWithoutBase>(),
    )?;
    m.add(
        "RelativeURLWithCannotBeABaseBase",
        py.get_type::<RelativeURLWithCannotBeABaseBase>(),
    )?;
    m.add(
        "SetHostOnCannotBeABaseURL",
        py.get_type::<SetHostOnCannotBeABaseURL>(),
    )?;

    Ok(())
}
