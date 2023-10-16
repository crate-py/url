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

#[pymethods]
impl UrlPy {
    #[classmethod]
    fn parse(_cls: &PyType, value: &str) -> PyResult<UrlPy> {
        match Url::parse(value) {
            Ok(inner) => Ok(UrlPy { inner }),
            Err(ParseError::EmptyHost) => Err(EmptyHost::new_err(value.to_string())),
            Err(ParseError::IdnaError) => Err(IdnaError::new_err(value.to_string())),
            Err(ParseError::InvalidPort) => Err(InvalidPort::new_err(value.to_string())),
            Err(ParseError::InvalidIpv4Address) => {
                Err(InvalidIPv4Address::new_err(value.to_string()))
            }
            Err(ParseError::InvalidIpv6Address) => {
                Err(InvalidIPv6Address::new_err(value.to_string()))
            }
            Err(ParseError::InvalidDomainCharacter) => {
                Err(InvalidDomainCharacter::new_err(value.to_string()))
            }
            Err(ParseError::RelativeUrlWithoutBase) => {
                Err(RelativeURLWithoutBase::new_err(value.to_string()))
            }
            Err(ParseError::RelativeUrlWithCannotBeABaseBase) => {
                Err(RelativeURLWithCannotBeABaseBase::new_err(value.to_string()))
            }
            Err(ParseError::SetHostOnCannotBeABaseUrl) => {
                Err(SetHostOnCannotBeABaseURL::new_err(value.to_string()))
            }
            Err(e) => Err(URLError::new_err(e.to_string())),
        }
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
