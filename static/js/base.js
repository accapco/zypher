// fetch the modal content (login/register)
async function fetchModalContent(route) {
    try {
        const response = await fetch(route, {method: 'GET'});
        if (!response.ok) {
            pushNotif("error", "Network error");
        }
        const data = await response.json();
        return data.html;
    } catch (error) {
        pushNotif("error", error);
    }
}

// handle the close button inside the modal
function attachCloseButton(modal) {
    const close_btns = modal.querySelectorAll("#close, #close-btn, #cancel-btn");
    close_btns.forEach(btn => {
        btn.addEventListener('click', (event) => {
            event.preventDefault();
            modal.style.display = "none";
        });
    })
}

// display login modal content
async function showLoginModal(modal) {
    const loginHtml = await fetchModalContent("/account/login");
    if (loginHtml) {
        modal.innerHTML = loginHtml;
        modal.style.display = "block";
        attachCloseButton(modal);
        attachRegisterLink(modal);
        handleFormSubmit(modal);
    }
}

// display register modal content
async function showRegisterModal(modal) {
    const register_html = await fetchModalContent("/account/register");
    if (register_html) {
        modal.innerHTML = register_html;
        attachCloseButton(modal);
        attachLoginLink(modal);
        handleFormSubmit(modal);
    }
}

// submit handler
function handleFormSubmit(modal) {
    const form = modal.querySelector("form");
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const route = form.getAttribute("action");
        const form_data = new FormData(form);
        let response = await fetch(route, {"method": 'POST', "body": form_data});
        const data = await response.json();
        let message = data.message
        if (!response.ok) {
            pushNotif("warning", message);
        } else {
            window.location = data.redirect;
        }
    });
}

// handle register link inside the login modal
function attachRegisterLink(modal) {
    const register_link = modal.querySelector("#register a");
    register_link.addEventListener('click', async (event) => {
        event.preventDefault();
        await showRegisterModal(modal);
    });
}

// handle login link inside the register modal
function attachLoginLink(modal) {
    const login_link = modal.querySelector("#login a");
    login_link.addEventListener('click', async (event) => {
        event.preventDefault();
        await showLoginModal(modal);
    });
}

// open login form
const login_btn = document.getElementById("login-btn");
if (login_btn) {
    login_btn.addEventListener('click', async (event) => {
        event.preventDefault();
        const modal = document.getElementById("login-modal");
        await showLoginModal(modal);
    });
}

// notifs
const notifs = document.querySelector("#notifications");

function pushNotif(type, message) {
    const notif = document.createElement("div");
    notif.classList.add("notif",  type);
    notif.innerHTML = `
            <div class="icon ${type}"></div>
            <p>${message}</p>`;
    notifs.appendChild(notif);
    setTimeout(popNotif, 10000, notif);
}

function popNotif(notif) {
    setTimeout(() => {notif.classList.add("fade")}, 400);
    notifs.removeChild(notif);
}