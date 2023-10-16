use pyo3::{create_exception, exceptions::PyException, prelude::*, types::PyType};
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

fn from_result(value: Result<url::Url, ParseError>) -> PyResult<UrlPy> {
    match value {
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
    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    #[classmethod]
    fn parse(_cls: &PyType, value: &str) -> PyResult<UrlPy> {
        from_result(Url::parse(value))
    }

    fn join(&self, input: &str) -> PyResult<UrlPy> {
        from_result(self.inner.join(input))
    }

    #[getter]
    fn scheme(&self) -> &str {
        self.inner.scheme()
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
}

#[pymodule]
#[pyo3(name = "url")]
fn url_py(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<UrlPy>()?;

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
