const edit_btn = document.getElementById("edit-btn");
const form_fields = document.querySelectorAll("input[type=text], input[type=email]");

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