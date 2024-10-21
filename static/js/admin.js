const page_buttons = document.querySelectorAll(".admin-side button");

async function fetchInnerHTML(route) {
    try {
        const response = await fetch(route);
        const data = await response.json();
        if (data.html) {
            return data.html;
        } else {
            return null;
        };
    } catch (error) {
        alert(error);
    }
};

function setActiveButton(route) {
    page_buttons.forEach((btn) => {
        if (btn.getAttribute("data-route") != route) {
            btn.classList.remove("active");
        } else {
            btn.classList.add("active");
            const parent_button = btn.parentElement.querySelector(".parent-btn");
            parent_button.classList.add("active");
        }
    });
}

function attachActionButtons(html) {
    const action_btns = html.querySelectorAll(".action");
    action_btns.forEach(btn => {
        btn.addEventListener("click", async () => {
            try {
                var route = btn.getAttribute("data-route");
                const response = await fetch(route);
                const data = await response.json();
                openModal(data.html, route);
            } catch (error) {
                alert(error);
            };
        });
    });
}

function openModal(html, route) {
    const modal = document.querySelector(".modal");
    modal.innerHTML = html;
    modal.style.display = "block";
    attachCloseButton(modal);
    handleSubmitAction(modal);

    if (route.includes('product') && route.includes('edit')) {
        attachDraggableUploadArea(main_div);
        attachImageDelete(main_div);
    } else if (route.includes('product') && route.includes('add')) {
        attachDraggableUploadArea(main_div, prepare=true);
    }
}

function handleSubmitAction(modal) {
    const form = modal.querySelector("form");
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const action = form.getAttribute("action");
        const response = await fetch(action, {
            method: 'POST',
            body: new FormData(form)
        });
        const data = await response.json();
        pushNotif(data.status, data.message);
        setMainDivContent(data.redirect)
        modal.style.display = "none";
    });
}

function attachExpandIcons(html) {
    const expand_icons = html.querySelectorAll('.expand-icon');
    if (expand_icons) {
        expand_icons.forEach(icon => {
            icon.addEventListener('click', (event) => {
                const children_div = icon.parentElement.parentElement.parentElement.querySelector('.children');
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
    };
}

const main_div = document.querySelector(".admin-main");

async function setMainDivContent(route) {
    html = await fetchInnerHTML(route);
    if (html) {
        main_div.innerHTML = html;
        attachActionButtons(main_div);
        if (route === "/categories/") {
            attachExpandIcons(main_div);
        }
        if (route === "/orders/") {
            attachFilters(main_div);
        }
    } else {
        window.location.reload()
    }
}

async function handlePageButtonClick(btn) {
    var route = btn.getAttribute("data-route");
    await setMainDivContent(route);
    setActiveButton(route);
}

// main
page_buttons.forEach((btn) => {
    btn.addEventListener("click", async (event) => {
        event.preventDefault();
        if (btn.classList.contains("parent-btn")) {
            const child_btns = btn.parentElement.querySelectorAll(".child-btn");
            if (child_btns.length > 0) {
                child_btns.forEach((child_btn) => {
                    child_btn.classList.toggle("collapsed");
                });
            } else {
                handlePageButtonClick(btn);
            }
        } else {
            handlePageButtonClick(btn);
        }
    });
});

// order filters
var active_order_status = "all";
var active_payment_method = "all";

function attachFilters(html) {
    const status_filters = html.querySelectorAll("#status-buttons button");
    const payment_method_filters = html.querySelectorAll("#payment-method-buttons button");

    status_filters.forEach((filter) => {
        filter.addEventListener("click", (event) => {
            event.preventDefault();
            active_order_status = filter.getAttribute("data-status");
            filterOrdersTable();
            setActiveOrderButton(filter, status_filters)
        });
    });

    payment_method_filters.forEach((filter) => {
        filter.addEventListener("click", (event) => {
            event.preventDefault();
            active_payment_method = filter.getAttribute("data-method");
            filterOrdersTable();
            setActiveOrderButton(filter, payment_method_filters)
        });
    });
}

function filterOrdersTable() {
    const orders_table = main_div.querySelectorAll(".orders-list .order");

    orders_table.forEach((row) => {
        const order_status = row.querySelector(".status h3");
        const payment_method = row.querySelector(".payment-method p");
        if ((active_order_status === "all" || order_status.innerText.toLowerCase().includes(active_order_status.toLowerCase())) &&
            (active_payment_method === "all" || payment_method.innerText.toLowerCase().includes(active_payment_method.toLowerCase())
        )) {
            row.style.display = "grid";
        } else  {
            row.style.display = "none";
        }
    });
}

function setActiveOrderButton(set_active_filter, filters) {
    filters.forEach((filter) => {
        if (filter === set_active_filter) {
            filter.classList.add("active");
        } else {
            filter.classList.remove("active");
        }
    });
}

let files_array = [];
let temp_image_id = 0;

// attach draggable upload area
function attachDraggableUploadArea(html, prepare=false) {
    const drop_zone = html.querySelector('#drop-zone');
    const product_id = html.querySelector("form").getAttribute("data-product-id");
    const file_upload_btn = html.querySelector('.input-action');
    const file_input = html.querySelector('#images');

    files_array = [];
    temp_image_id = 0;

    // handle drag over and leave events
    drop_zone.addEventListener('dragover', (event) => {
        event.preventDefault();
        drop_zone.classList.add('dragover');
    });

    drop_zone.addEventListener('dragleave', () => {
        drop_zone.classList.remove('dragover');
    });

    // handle drop event
    drop_zone.addEventListener('drop', async (event) => {
        event.preventDefault();
        drop_zone.classList.remove('dragover');
        
        const files = event.dataTransfer.files;

        if (prepare) {
            prepareUpload(files);
        } else {
            uploadImage(files, product_id);
        }
    });

    // handle image upload click
    file_upload_btn.addEventListener("click", (event) => {
        event.preventDefault();
        file_input.click();
    });

    file_input.addEventListener("change", async (event) => {
        if (prepare) {
            prepareUpload(event.target.files);
        } else {
            uploadImage(event.target.files, product_id);
        }
    });
}

function prepareUpload(files) {
    Array.from(files).forEach((file) => {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (event) => createTempPreview(event, file);
            reader.readAsDataURL(file);
        } else {
            pushNotif("warning", "Please drop a valid image file.");
        }
    });
}

function setFileInput() {
    const file_input = document.querySelector('#images');
    const data_transfer = new DataTransfer()
    files_array.forEach((item) => {
        data_transfer.items.add(item.file);
    });
    file_input.files = data_transfer.files;
    console.log(file_input.files);
}

function createTempPreview(event, file) {
    const col_div = document.createElement("div")
    col_div.classList.add("column");
    col_div.id = `image-${temp_image_id}`;

    col_div.innerHTML = `
        <div class="image-container">
            <img src="${event.target.result}">
        </div>
        <div class="controls">
            <div data-image-id="${temp_image_id}" class="delete"></div>
        </div>
    `;

    const images_preview = document.querySelector(".images-preview");
    images_preview.appendChild(col_div);

    files_array.push({
        'id': temp_image_id,
        'file': file
    });
    setFileInput();
    temp_image_id += 1;

    const delete_btn = col_div.querySelector(".controls .delete");

    delete_btn.addEventListener("click", (event) => {
        event.preventDefault();
        const image_id = delete_btn.getAttribute("data-image-id");

        files_array.forEach((item, index) => {
            if (item.id === Number(image_id)) {
                files_array.splice(index, 1);
            } 
        });

        setFileInput();
        removePreview(image_id);
    });
}

async function uploadImage(files, product_id) {
    const form_data = new FormData();
    Array.from(files).forEach((file) => {
        if (file && file.type.startsWith('image/')) {
            form_data.append('image', file);
        } else {
            pushNotif("warning", "Please drop a valid image file.");
        }
    });

    const upload_url = `/products/${product_id}/images/upload`;
    const response = await fetch(upload_url, {
        method: 'POST', 
        body: form_data
    });
    const data = await response.json();
    pushNotif(data.status, data.message);
    if (data.status === "success") {
        data.files.forEach((file) => {
            createPreview(file['filename'], file['image_id']);
        });
    }
}

function attachImageDelete(html) {
    const delete_btns = html.querySelectorAll(".controls .delete");
    const product_id = document.querySelector("form").getAttribute("data-product-id");

    delete_btns.forEach((btn) => {
        btn.addEventListener("click", async (event) => {
            event.preventDefault();

            const image_id = btn.getAttribute("data-image-id");
            const delete_url = `/products/${product_id}/images/${image_id}/delete`;

            const response = await fetch(delete_url, {method: 'POST'});
            const data = await response.json();
            
            pushNotif(data.status, data.message);

            if (data.status === "success") {
                removePreview(image_id);
            }
        });
    });
}

function removePreview(image_id) {
    const col = document.getElementById(`image-${image_id}`);
    col.remove();
}

function createPreview(filename, image_id) {
    const images_preview = document.querySelector(".images-preview");

    const col_div = document.createElement("div");
    col_div.classList.add("column");

    col_div.id = `image-${image_id}`;
    col_div.innerHTML = `
        <div class="image-container">
            <img src="static/uploads/${filename}">
        </div>
        <div class=controls>
            <div data-image-id="${image_id}" class="delete"></div>
        </div>
    `
    images_preview.appendChild(col_div);
    attachImageDelete(col_div);
}

page_buttons[0].click();