function togglePaymentDetails(detailsId) {
    const details = document.querySelectorAll('.payment-details');
    const options = document.querySelectorAll('.payment-option');

    // Hide all details and remove selected class from all options
    details.forEach(detail => {
        detail.style.display = 'none'; // Hide all details
    });
    options.forEach(option => {
        option.classList.remove('selected'); // Remove selected class
    });

    const selectedDetail = document.getElementById(detailsId);
    if (selectedDetail) {
        selectedDetail.style.display = 'block'; // Show selected details
        selectedDetail.parentElement.classList.add('selected'); // Add selected class to parent
    }
}

function toggleBillingDetails(selected) {
    const sameDetails = document.getElementById('same-details');
    const differentDetails = document.getElementById('different-details');
    const billingOptions = document.querySelectorAll('.billing-option');

    // Remove highlight from all options
    billingOptions.forEach(option => {
    option.classList.remove('selected');
    option.querySelector('input').checked = false; // Uncheck all
    });

    if (selected === 'same') {
    sameDetails.classList.add('visible');
    differentDetails.classList.remove('visible');
    billingOptions[0].classList.add('selected'); // Highlight the "same" option
    billingOptions[0].querySelector('input').checked = true; // Check the radio button
    } else {
    sameDetails.classList.remove('visible');
    differentDetails.classList.add('visible');
    billingOptions[1].classList.add('selected'); // Highlight the "different" option
    billingOptions[1].querySelector('input').checked = true; // Check the radio button
    }
}

// handle submit
const form = document.querySelector(".checkout-form");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form_data = new FormData(form);

    const url = form.action;
    const response = await fetch(url, {'method': "POST", 'body': form_data});
    const data = await response.json();

    window.location.href = data.redirect;
});