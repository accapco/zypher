const main_div = document.querySelector(".account-main");

const account_details_link = document.getElementById("details");
const orders_link = document.getElementById("orders");
const password_change_link = document.getElementById("password-change");

const account_menu_btns = document.querySelectorAll(".page-link");
var active_btn = null;

function processAjaxData(data, page, url_path){
    main_div.innerHTML = data.html;
    window.history.pushState({"html": data.html}, page, url_path);
}

window.addEventListener("popstate", (event) => {
    if(event.state){
        main_div.innerHTML = event.state.html;
    }
});

// set active menu button
account_menu_btns.forEach((btn) => {
    btn.addEventListener("click", (event) => {
        if (active_btn) {
            active_btn.classList.remove("active")
        }
        event.target.classList.add("active");
        active_btn = event.target;
    });
})

document.addEventListener("DOMContentLoaded", () => {
    if (window.location.search.includes('?page=details')) {
        account_details_link.click();
    } else if (window.location.search.includes('?page=orders')) {
        orders_link.click();
    } else if (window.location.search.includes('?page=password-change')) {
        password_change_link = document.getElementById("password-change");
    } else {
        account_details_link.click();
    }
});

// account details
account_details_link.addEventListener("click", async (event) => {
    event.preventDefault();
    const url = "/account/details";
    const response = await fetch (url, {method: 'GET'});
    const data = await response.json();
    processAjaxData(data, "Account Details", "/details");
    attachEditButton(main_div);
    handleAccountSubmit(main_div);
});

function attachEditButton(html) {
    const edit_btn = html.querySelector("#edit-btn");
    const form_fields = html.querySelectorAll("input[type=text], input[type=email]");

    edit_btn.addEventListener("click", () => {
        if (edit_btn.innerText == "Enable Editing") {
            form_fields.forEach(field => {
                field.removeAttribute('disabled');
            });
            edit_btn.innerText = "Disable Editing";
        } else {
            form_fields.forEach(field => {
                field.setAttribute('disabled', true);
            });
            edit_btn.innerText = "Enable Editing";
        }
    });
}

function handleAccountSubmit(html) {
    const form = html.querySelector("form");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: form.method,
            body: formData
        });
        const data = await response.json();
        alert(data.message);
        account_details_link.click();
    })
} 

// orders
orders_link.addEventListener("click", async (event) => {
    event.preventDefault();
    const url = "/account/orders";
    const response = await fetch (url, {method: 'GET'});
    const data = await response.json();
    processAjaxData(data, "Orders", "/orders")
    attachOrderTabs(main_div);
});

function attachOrderTabs(html) {
    const tabs = html.querySelectorAll(".nav .tab");

    tabs.forEach((tab) => {
        tab.addEventListener("click", (event) => {
            event.preventDefault();
            const status = tab.getAttribute("data-status");
            filterOrdersTable(status, html);
            setActiveOrderButton(status, tabs)
        });
    });
}

function filterOrdersTable(status, html) {
    const orders_table = html.querySelector(".orders-table");
    const rows = orders_table.querySelectorAll(".order");

    rows.forEach((row) => {
        const order_status = row.querySelector(".status h3");
        console.log(status);
        console.log(order_status.innerText);
        if (status === "all" || status === order_status.innerText.toLowerCase()) {
            row.style.display = "grid";
        } else  {
            row.style.display = "none";
        }
    });
}

function setActiveOrderButton(set_active_status, tabs) {
    tabs.forEach((tab) => {
        tab_status = tab.getAttribute("data-status");
        if (tab_status === set_active_status) {
            tab.classList.add("active");
        } else {
            tab.classList.remove("active");
        }
    });
}