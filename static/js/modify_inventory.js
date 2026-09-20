function showForm() {
    const action = document.getElementById('action').value;
    const addForm = document.getElementById('addForm');
    const deleteForm = document.getElementById('deleteForm');
    const updateForm = document.getElementById('updateForm');

    if (addForm) addForm.classList.add('hidden');
    if (deleteForm) deleteForm.classList.add('hidden');
    if (updateForm) updateForm.classList.add('hidden');

    if (action === 'add' && addForm) {
        addForm.classList.remove('hidden');
    } else if (action === 'delete' && deleteForm) {
        deleteForm.classList.remove('hidden');
    } else if (action === 'update' && updateForm) {
        updateForm.classList.remove('hidden');
    }
}

function toggleUpdateInput() {
    const field = document.getElementById('updateField').value;
    const newValueInput = document.getElementById('newValue');
    if (newValueInput) {
        if (field) {
            newValueInput.classList.remove('hidden');
        } else {
            newValueInput.classList.add('hidden');
        }
    }
}