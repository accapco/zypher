// fetch the modal content (login/register)
async function fetchModalContent(route) {
    try {
        const response = await fetch(route, { method: 'GET' });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data.html;
    } catch (error) {
        alert(error);
        window.location.reload();
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
    }
}

// display register modal content
async function showRegisterModal(modal) {
    const register_html = await fetchModalContent("/account/register");
    if (register_html) {
        modal.innerHTML = register_html;
        attachCloseButton(modal);
        attachLoginLink(modal);
    }
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