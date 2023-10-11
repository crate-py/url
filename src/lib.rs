use pyo3::{create_exception, prelude::*, types::PyType};
use url::Url;

create_exception!(url, URLError, pyo3::exceptions::PyException);

#[repr(transparent)]
#[pyclass(name = "URL", module = "url", frozen)]
struct UrlPy {
    #[allow(dead_code)]
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
}

#[pymodule]
#[pyo3(name = "url")]
fn url_py(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<UrlPy>()?;
    m.add("URLError", py.get_type::<URLError>())?;
    Ok(())
}
