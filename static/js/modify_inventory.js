function showForm() {
    document.getElementById('addForm').classList.add('hidden');
    document.getElementById('deleteForm').classList.add('hidden');
    document.getElementById('updateForm').classList.add('hidden');
    const action = document.getElementById('action').value;
    if (action) {
        document.getElementById(action + 'Form').classList.remove('hidden');
    }
}

function toggleUpdateInput() {
    const field = document.getElementById('updateField').value;
    const input = document.getElementById('newValue');
    input.classList.toggle('hidden', field === '');
}
document.getElementById('updateForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/modify-inventory', {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const data = await response.json();
    if (data.status === 'warning') {
        document.getElementById('alertMessage').textContent = data.message;
        document.getElementById('alertModal').style.display = 'block';
        window.currentVendorEmail = data.vendor_email;
        window.currentPname = data.pname;
    } else {
        // Show success/error and redirect
        alert(data.message || 'Update complete');
        window.location.href = '/products';
    }
});
function closeModal() {
    document.getElementById('alertModal').style.display = 'none';
}

async function sendEmail() {
    if (!window.currentVendorEmail) {
        alert('No vendor email available');
        return;
    }
    const response = await fetch('/send-vendor-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            pname: window.currentPname,
            email: window.currentVendorEmail
        })
    });
    const result = await response.json();
    alert(result.message);
    closeModal();
}