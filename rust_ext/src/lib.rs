use pyo3::prelude::*;
use hmac::{Hmac, Mac};
use sha2::Sha256;
use similar::TextDiff;

/// Compute HMAC-SHA256 and return base64-encoded digest.
#[pyfunction]
fn hmac_sha256_base64(key: &str, data: &str) -> PyResult<String> {
    type HmacSha256 = Hmac<Sha256>;
    let mut mac = HmacSha256::new_from_slice(key.as_bytes())
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    mac.update(data.as_bytes());
    let result = mac.finalize().into_bytes();
    Ok(base64::encode(result))
}

/// Generate a unified diff between two strings.
#[pyfunction]
fn unified_diff(original: &str, updated: &str, filename: Option<&str>) -> PyResult<String> {
    let name = filename.unwrap_or("file");
    let diff = TextDiff::from_lines(original, updated);
    Ok(
        diff
            .unified_diff()
            .header(&format!("{}.orig", name), &format!("{}.new", name))
            .to_string(),
    )
}

#[pymodule]
fn rust_ext(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hmac_sha256_base64, m)?)?;
    m.add_function(wrap_pyfunction!(unified_diff, m)?)?;
    Ok(())
}
