function toggleMenu() {
    const menu = document.getElementById('dropdownMenu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

window.addEventListener('click', function(e) {
    const menu = document.getElementById('dropdownMenu');
    if (!e.target.closest('.topbar')) {
        menu.style.display = 'none';
    }
});
