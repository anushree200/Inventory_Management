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
