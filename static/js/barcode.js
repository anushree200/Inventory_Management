const scanInput = document.getElementById('scanInput');
const resultEl = document.getElementById('scan-result');
const infoEl = document.getElementById('productInfo');

scanInput.addEventListener('keydown', async (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();

    const code = scanInput.value.trim();
    if (!code) return;

    document.getElementById('scannedCode').textContent = code;
    document.getElementById('barcodeValue').value = code;
    infoEl.textContent = 'Looking up product...';
    resultEl.style.display = 'block';
    resultEl.classList.remove('warning');

    try {
        const res = await fetch(`/api/product-lookup?barcode=${encodeURIComponent(code)}`);
        const data = await res.json();
        if (res.ok) {
            infoEl.textContent = `${data.pname} — current quantity: ${data.qty}`;
        } else {
            infoEl.textContent = data.error || 'This code does not match any product.';
            resultEl.classList.add('warning');
        }
    } catch (err) {
        infoEl.textContent = 'Could not look up this code (network error). You can still submit it.';
    }
});

function rescan() {
    resultEl.style.display = 'none';
    scanInput.value = '';
    scanInput.focus();
}

// A scanner only "types" into whatever field has focus — keep this input
// focused by default so a scan always lands in the right place, but don't
// steal focus while the confirm form is actively being used.
document.addEventListener('click', (e) => {
    const withinResult = resultEl.contains(e.target);
    if (!withinResult) {
        scanInput.focus();
    }
});

scanInput.focus();