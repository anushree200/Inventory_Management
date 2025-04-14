function toggleMenu() {
    const menu = document.getElementById('dropdownMenu');
    if (menu) {
        console.log('Toggling menu, current display:', menu.style.display);
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    } else {
        console.log('Error: dropdownMenu element not found');
    }
}

window.addEventListener('click', function(e) {
    const menu = document.getElementById('dropdownMenu');
    if (menu && !e.target.closest('.topbar')) {
        console.log('Click outside topbar, hiding menu');
        menu.style.display = 'none';
    }
});

// Basic form validation for vendor forms (unchanged unless needed)
document.querySelectorAll('.vendor-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                alert(`${field.name} is required!`);
            }
        });
        if (!isValid) e.preventDefault();
    });
});