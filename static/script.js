// static/script.js

function submitForm() {
    const foodItem = document.getElementById("food_item").value;
    const quantity = document.getElementById("quantity").value;
    const quantityUnit = document.getElementById("quantity_unit").value;

    fetch("/calculate_calories", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
            food_item: foodItem, 
            quantity: quantity,
            unit: quantityUnit 
        })
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = "";  // Clear previous results

        if (data.error) {
            resultDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
        } else {
            resultDiv.innerHTML = `<p>${data.calories_info}</p>`;
        }
    })
    .catch(error => {
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    });
}
