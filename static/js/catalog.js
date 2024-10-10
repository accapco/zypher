// for expand icons
document.querySelectorAll('.expand-icon').forEach(icon => {
    icon.addEventListener('click', (event) => {
        const children_div = icon.parentElement.querySelector('.children');
        if (children_div) {
            if (children_div.style.display === 'none') {
                children_div.style.display = 'block';
                icon.querySelector('img').src = "static/icons/minus.svg";
            } else {
                children_div.style.display = 'none';
                icon.querySelector('img').src = "static/icons/plus.svg";
            }
        }
    });
});

// link to product page
function attachProductPages(html) {
    html.querySelectorAll('.item').forEach(item => {
    item.addEventListener('click', (event) => {
        event.preventDefault();
        const url = item.getAttribute('data-url');
        window.location.href = url;
    });
});
}

// load products
async function fetchProducts() { 
    const clothing_section = document.querySelector('.clothing');
    clothing_section.innerHTML = "";

    var products_url = "/products/";

    const active_filters = document.querySelectorAll(".catalog-side input[type='radio']:checked");
    let filters = [];
    active_filters.forEach((filter) => {
        query = {
            key: filter.name,
            value: filter.value
        };
        filters.push(query);
    });

    filters.forEach((query, index) => {
        if (index === 0) {
            products_url += `?${query.key}=${query.value}`
        } else {
            products_url += `&${query.key}=${query.value}`
        }
    });

    const response = await fetch(products_url);
    const data = await response.json();
    const products = data.products;

    products.forEach((product) => {
        const item_div = document.createElement('div');
        item_div.classList.add('item');
        const uploads_folder = "/static/uploads"
        const img_url = `${uploads_folder}/${product.image_url}`;
        const product_url = `/catalog/${product.product_id}`;

        item_div.setAttribute("data-url", product_url);
        item_div.innerHTML = `
            <div class="image-container">
                <img src="${img_url}" alt="${product.product_name}" fill>
            </div>
            <div class="name">${product.product_name}</div>
            <div class="price">₱${product.price}</div>
        `;

        clothing_section.appendChild(item_div);
        attachProductPages(clothing_section);
    });
}

// add filter functionality
let last_checked_category = null;
let last_checked_color = null;
let last_checked_size = null;

function attachFilters(filter_type, active_filter) {
    const filters = document.querySelectorAll(`.catalog-side input[type='radio'][name='${filter_type}']`);
    
    filters.forEach((filter) => {
        filter.addEventListener("click", (event) => {
            if (active_filter === filter) {
                filter.checked = false;
                active_filter = null;
                fetchProducts(null);
            } else {
                active_filter = filter;
                const value = filter.value;
                fetchProducts();
            }
        });
    });
}

fetchProducts();
attachFilters('category', last_checked_category);
attachFilters('color', last_checked_color);
attachFilters('size', last_checked_size);