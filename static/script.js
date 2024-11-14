// static/script.js

// Add this debounce function before your event listener
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

document.addEventListener("DOMContentLoaded", fetchFoodSuggestions);
function fetchFoodSuggestions() {
    fetch("/get_food_suggestions")
        .then(response => response.json())
        .then(data => {
            const datalist = document.getElementById("food-suggestions");

            // Clear any existing options
            datalist.innerHTML = "";

            if (data.suggestions) {
                data.suggestions.forEach(food => {
                    const option = document.createElement("option");
                    option.value = food;
                    datalist.appendChild(option);
                });
            } else {
                console.error("Error: No food suggestions received");
            }
        })
        .catch(error => {
            console.error("Error fetching food suggestions:", error);
        });
}

async function submitForm() {
    const loader = document.getElementById('loader');
    const result = document.getElementById('result');
    
    loader.style.display = 'block';
    result.innerHTML = '';  // Clear previous results
    
    const foodItem = document.getElementById("food_item").value;
    const quantity = document.getElementById("quantity").value;
    const quantityUnit = document.getElementById("quantity_unit").value;

    try {
        const response = await fetch("/calculate_nutrition", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                food_item: foodItem, 
                quantity: quantity,
                unit: quantityUnit 
            })
        });
        const data = await response.json();
        
        if (data.error) {
            result.innerHTML = `<p style="color: red;">${data.error}</p>`;
        } else {
            result.innerHTML = `
                <table class="nutrition-table" style="
                    width: 100%;
                    max-width: 500px;
                    margin: 20px auto;
                    border-collapse: collapse;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    overflow: hidden;
                ">
                <p>Nutrition Information for ${data.quantity} ${data.unit} of ${data.food_item}:</p>
                    <thead>
                        <tr style="
                            background-color: #4CAF50;
                            color: white;
                        ">
                            <th style="padding: 15px; text-align: left;">Nutrient</th>
                            <th style="padding: 15px; text-align: right;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(data.nutrition_info).map(([nutrient, value], index) => `
                            <tr style="
                                background-color: ${index % 2 === 0 ? '#f8f9fa' : 'white'};
                                border-bottom: 1px solid #ddd;
                            ">
                                <td style="padding: 12px 15px; text-align: left;">${nutrient}</td>
                                <td style="padding: 12px 15px; text-align: right;">${value}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>`;
        }
    } catch (error) {
        result.innerHTML = 'An error occurred while processing your request.';
    } finally {
        loader.style.display = 'none';
    }
}

async function getFoodSuggestions(query) {
    try {
        const response = await fetch(`/food_suggestions?query=${encodeURIComponent(query)}`);
        const suggestions = await response.json();
        
        const datalist = document.getElementById('food-suggestions');
        datalist.innerHTML = '';  // Clear existing suggestions
        
        suggestions.forEach(suggestion => {
            const option = document.createElement('option');
            option.value = suggestion;
            datalist.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching food suggestions:', error);
    }
}

