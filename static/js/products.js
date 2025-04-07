function searchProducts() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#productRows tr');
    rows.forEach(row => {
        const name = row.querySelector('.pname').textContent.toLowerCase();
        row.style.display = name.includes(input) ? '' : 'none';
    });
}

function filterProducts() {
    const value = document.getElementById('filter').value;
    let rows = Array.from(document.querySelectorAll('#productRows tr'));

    if (value.includes('qty')) {
        rows.sort((a, b) => {
            const aQty = +a.querySelector('[data-qty]').dataset.qty;
            const bQty = +b.querySelector('[data-qty]').dataset.qty;
            return value === 'qty-asc' ? aQty - bQty : bQty - aQty;
        });
    } else if (value.includes('price')) {
        rows.sort((a, b) => {
            const aPrice = +a.querySelector('[data-price]').dataset.price;
            const bPrice = +b.querySelector('[data-price]').dataset.price;
            return value === 'price-asc' ? aPrice - bPrice : bPrice - aPrice;
        });
    }
    const tbody = document.getElementById('productRows');
    rows.forEach(row => tbody.appendChild(row));
}