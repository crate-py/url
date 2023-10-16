use pyo3::{create_exception, prelude::*, types::PyType};
use url::Url;

create_exception!(url, URLError, pyo3::exceptions::PyException);

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
    Ok(())
}
