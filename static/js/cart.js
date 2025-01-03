// Change the quantity of the item
function changeQuantity(button, change) {
    var quantityElement = button.parentElement.querySelector('.quantity');
    var quantity = parseInt(quantityElement.textContent) + change;
    if (quantity < 1) return;  // Prevent quantity from going below 1

    quantityElement.textContent = quantity;
    const checkbox = button.parentElement.parentElement.querySelector("input[type=checkbox]");
    checkbox.setAttribute("data-quantity", quantity);

    // Update the item price based on new quantity
    var row = button.closest('.table-row');
    var unitPrice = parseFloat(row.querySelector('.item-price').getAttribute('data-unit-price'));
    var newPrice = unitPrice * quantity;
    row.querySelector('.item-price').textContent = '₱' + newPrice.toFixed(2);

    updateTotal();
}

// Update total price based on selected items
var selectedItems = [];
function updateTotal() {
    selectedItems = [];
    var checkboxes = document.querySelectorAll('.item-checkbox:checked');
    var total = 0;
    
    checkboxes.forEach(function(checkbox) {
        var row = checkbox.closest('.table-row');
        var itemPrice = parseFloat(row.querySelector('.item-price').textContent.replace('₱', ''));
        total += itemPrice;

        selectedItems.push({
            product_id: checkbox.getAttribute('data-product-id'),
            name: checkbox.getAttribute('data-name'),
            image_url: checkbox.getAttribute('data-image-url'),
            price: checkbox.getAttribute('data-price'),
            quantity: checkbox.getAttribute('data-quantity'),
            size: checkbox.getAttribute('data-size'),
            color: checkbox.getAttribute('data-color')
        });

        console.log(selectedItems);
    });
    document.getElementById('order-total').textContent = '₱ ' + total.toFixed(2);
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
        const response = await fetch(remove_cart_item_url, {method: 'POST'});
        const data = await response.json();
        pushNotif(data.status, data.message);
        if (data.status === "info") {
            const table = button.parentElement.parentElement.parentElement;
            const row = button.parentElement.parentElement;
            table.removeChild(row);
        }
    });
})

// checkout button
const checkout_btn = document.querySelector("#checkout-btn");

checkout_btn.addEventListener("click", async (event) => {
    event.preventDefault();
    updateTotal();
    checkout_url = "/prepare_checkout";
    const form = new FormData();
    form.append("selected_items", JSON.stringify(selectedItems));
    fetch(checkout_url, {method: 'POST', body: form})
        .then(response => response.json())
        .then(data => {
            window.location.replace(data.redirect);
        })
        .catch(error => {
            alert(error);
        })
});