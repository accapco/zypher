// add to cart button function
const add_to_cart_btn = document.getElementById("add-to-cart");
const add_to_cart_url = "/cart/add"

add_to_cart_btn.addEventListener("click", async (event) => {
    event.preventDefault();
    const formData =  new FormData();
    formData.append("product_id", event.target.getAttribute("data-product-id"))
    formData.append("price", event.target.getAttribute("data-price"))

    const response = await fetch(add_to_cart_url, {method: 'POST', body: formData});
    const data = await response.json();
    pushNotif(data.status, data.message);
});

function changeMainImage(clickedThumbnail) {
    newImageUrl = clickedThumbnail.getAttribute("data-image-url");

    // Change the main image source
    var mainImage = document.getElementById('main-image');
    mainImage.src = newImageUrl;

    // Remove 'selected' class from all thumbnails
    var thumbnails = document.querySelectorAll('.thumbnail-image img');
    thumbnails.forEach(function(thumbnail) {
        thumbnail.classList.remove('selected');
    });

    // Add 'selected' class to the clicked thumbnail
    clickedThumbnail.classList.add('selected');
}

