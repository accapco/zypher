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

function getActionButtons(html) {
    const action_btns = html.querySelectorAll(".action");
    action_btns.forEach(btn => {
        btn.addEventListener("click", async () => {
            try {
                var route = btn.getAttribute("data-route");
                const response = await fetch(route);
                const data = await response.json();
                openModal(data.html);
            } catch (error) {
                alert(error);
            };
        });
    });
}

function openModal(html) {
    const modal = document.querySelector(".modal");
    modal.innerHTML = html;
    modal.style.display = "block";
    attachCloseButton(modal);
    handleSubmitAction(modal);
}

function handleSubmitAction(modal) {
    const form = modal.querySelector("form");
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const action = form.getAttribute("action");
        try {
            const response = await fetch(action, {
                method: 'POST',
                body: new FormData(form)
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            alert(data.message);
            setMainDivContent(data.redirect)
            modal.style.display = "none";
        } catch (error) {
            alert('There was an error submitting the form: ' + error.message);
        }
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
                        icon.querySelector('img').src = "{{ url_for('static', filename='icons/minus.svg') }}";
                    } else {
                        children_div.style.display = 'none';
                        icon.querySelector('img').src = "{{ url_for('static', filename='icons/plus.svg') }}";
                    }
                }
            });
        });
    };
}

async function setMainDivContent(route) {
    const main_div = document.querySelector(".admin-main");
    html = await fetchInnerHTML(route);
    if (html) {
        main_div.innerHTML = html;
        getActionButtons(main_div);
        attachExpandIcons(main_div);
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

page_buttons[0].click();
page_buttons[1].click();