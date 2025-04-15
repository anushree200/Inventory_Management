function toggleMenu() {
    console.log('Toggle menu clicked');
    const dropdown = document.getElementById('dropdownMenu');
    dropdown.classList.toggle('active');
}

document.addEventListener('click', (event) => {
    const dropdown = document.getElementById('dropdownMenu');
    const trigger = document.querySelector('.dropdown-trigger');
    if (!dropdown.contains(event.target) && !trigger.contains(event.target)) {
        dropdown.classList.remove('active');
    }
});

function searchVendors() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.vendor-container .vendor-card');
    cards.forEach(card => {
        const name = card.querySelector('h3').textContent.toLowerCase();
        card.style.display = name.includes(input) ? '' : 'none';
    });
}

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