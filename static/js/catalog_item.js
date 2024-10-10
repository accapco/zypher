// add to cart button function
const add_to_cart_btn = document.getElementById("add-to-cart");
const add_to_cart_url = "/cart/add"

add_to_cart_btn.addEventListener("click", async (event) => {
    event.preventDefault();
    const formData =  new FormData();
    formData.append("product_id", event.target.getAttribute("data-product-id"))
    formData.append("price", event.target.getAttribute("data-price"))

    response = await fetch(add_to_cart_url, {method: 'POST', body: formData});
    data = await response.json();
    alert(data.message);
    window.location.replace(data.redirect);
});