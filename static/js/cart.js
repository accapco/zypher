// Change the quantity of the item
function changeQuantity(button, change) {
    var quantityElement = button.parentElement.querySelector('.quantity');
    var quantity = parseInt(quantityElement.textContent) + change;
    if (quantity < 1) return;  // Prevent quantity from going below 1

    quantityElement.textContent = quantity;

    // Update the item price based on new quantity
    var row = button.closest('.table-row');
    var unitPrice = parseFloat(row.querySelector('.item-price').getAttribute('data-unit-price'));
    var newPrice = unitPrice * quantity;
    row.querySelector('.item-price').textContent = '₱' + newPrice.toFixed(2);

    updateTotal();
}

// Update total price based on selected items
function updateTotal() {
    var checkboxes = document.querySelectorAll('.item-checkbox:checked');
    var total = 0;
    var selectedItems = [];
    
    checkboxes.forEach(function(checkbox) {
        var row = checkbox.closest('.table-row');
        var itemPrice = parseFloat(row.querySelector('.item-price').textContent.replace('₱', ''));
        total += itemPrice;

        selectedItems.push({
            product_id: checkbox.getAttribute('data-product-id'),
            image_url: checkbox.getAttribute('data-image-url'),
            price: checkbox.getAttribute('data-price'),
            quantity: checkbox.getAttribute('data-quantity'),
            size: checkbox.getAttribute('data-size'),
            color: checkbox.getAttribute('data-color')
        });
    });
    
    document.getElementById('total').textContent = '₱ ' + total.toFixed(2);
    document.getElementById('selected-items').value = JSON.stringify(selectedItems);
}

// Select or deselect all items
function selectAll(selectAllCheckbox) {
    var checkboxes = document.querySelectorAll('.item-checkbox');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = selectAllCheckbox.checked;
    });
    updateTotal();
}

// remove from cart button function
const remove_btns = document.querySelectorAll("#remove");

remove_btns.forEach((button) => {
    button.addEventListener("click", async (event) => {
        event.preventDefault();
        const cart_item_id = button.getAttribute("data-cart-item-id");
        const remove_cart_item_url = `${cart_item_id}/remove`
        response = await fetch(remove_cart_item_url, {method: 'POST'});
        data = await response.json();
        alert(data.message);
        window.location.replace(data.redirect);
    });
})