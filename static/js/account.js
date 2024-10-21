const main_div = document.querySelector(".account-main");

const account_details_link = document.getElementById("details");
const orders_link = document.getElementById("orders");
const password_change_link = document.getElementById("password-change");

const account_menu_btns = document.querySelectorAll(".page-link");
var active_btn = null;


document.addEventListener("DOMContentLoaded", (event) => {
    if (window.location.pathname.includes("/details")) {
        attachHandlers('/details');
        window.history.pushState(
            {
                "html": main_div.innerHTML,
                "route": '/details'
            }, 
            page, "/account/details"
        );
    } else if (window.location.pathname.includes("/orders")) {
        attachHandlers('/orders');
        window.history.pushState(
            {
                "html": main_div.innerHTML,
                "route": '/orders'
            }, 
            page, "/account/orders"
        );
    }
});

// run functions based on route
function attachHandlers(url_path) {
    if (url_path === '/details') {
        attachEditButton(main_div);
        handleAccountSubmit(main_div);
        setActiveButton('/details');
    }

    if (url_path === '/orders') {
        attachOrderTabs(main_div);
        attachOrderItemLinks(main_div);
        setActiveButton('/orders');
    }
}

function setActiveButton(url_path) {
    if (url_path === '/details') {
        account_details_link.classList.add("active");
        if (active_btn !== null && active_btn !== account_details_link) {
            active_btn.classList.remove("active");
        }
        active_btn = account_details_link;
    }

    if (url_path === '/orders') {
        orders_link.classList.add("active");
        if (active_btn !== null  && active_btn !== orders_link) {
            active_btn.classList.remove("active");
        }
        active_btn = orders_link;
    }
}

// events for pressing menu buttons
function processAjaxData(data, page, url_path){
    main_div.innerHTML = data.html;
    attachHandlers(url_path);
    document.title = page;
    window.history.pushState(
        {
            "html": data.html,
            "route": url_path
        }, 
        page, "/account"+url_path
    );
}

window.addEventListener("popstate", (event) => {
    if(event.state){
        main_div.innerHTML = event.state.html;
        attachHandlers(event.state.route);
        document.title = event.page;
    }
});

// account details
account_details_link.addEventListener("click", async (event) => {
    event.preventDefault();
    const url = "/account/details?partial=true";
    const response = await fetch (url, {method: 'GET'});
    const data = await response.json();
    processAjaxData(data, "Account", "/details");
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
        const form_data = new FormData(form);
        const response = await fetch('/account/details', {
            method: 'POST',
            body: form_data 
        });
        const data = await response.json();
        pushNotif(data.status, data.message);
        account_details_link.click();
    })
} 

// orders
orders_link.addEventListener("click", async (event) => {
    event.preventDefault();
    const url = "/account/orders?partial=true";
    const response = await fetch (url, {method: 'GET'});
    const data = await response.json();
    processAjaxData(data, "Orders", "/orders")
});

function attachOrderItemLinks(html) {
    const view_btns =  html.querySelectorAll("button.view");

    view_btns.forEach((btn) => {
        btn.addEventListener("click", async (event) => {
            event.preventDefault();
            const order_id = btn.getAttribute("data-order-id");
            const url = `/account/orders/${order_id}?partial=true`;
            const response = await fetch (url, {method: 'GET'});
            const data = await response.json();
            processAjaxData(data, "Orders", `/orders/${order_id}`);
        });
    });
}

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
        const order_status = row.querySelector(".order-status");
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