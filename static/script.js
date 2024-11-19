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
    const datalist = document.getElementById("food-suggestions");
    
    fetch("/get_food_suggestions")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            datalist.innerHTML = "";

            if (data.suggestions && Array.isArray(data.suggestions)) {
                data.suggestions.forEach(food => {
                    const option = document.createElement("option");
                    option.value = food;
                    datalist.appendChild(option);
                });
            } else {
                console.error("Invalid food suggestions format");
            }
        })
        .catch(error => {
            console.error("Error fetching food suggestions:", error);
            // Optionally show error to user
            const foodInput = document.getElementById("food_item");
            foodInput.placeholder = "Error loading suggestions. Please try typing...";
        });
}

// Add input validation
function validateInput(foodItem, quantity, unit) {
    const errors = [];
    
    if (!foodItem.trim()) {
        errors.push("Please enter a food item");
    }
    
    if (!quantity || quantity <= 0) {
        errors.push("Please enter a valid quantity");
    }
    
    const validUnits = ["units", "grams", "ml", "bowl", "cup", "tbsp", "tsp"];
    if (!validUnits.includes(unit)) {
        errors.push("Please select a valid unit");
    }
    
    return errors;
}

// Add this function to format nutrient names
function formatNutrientName(nutrient) {
    const formatMap = {
        'vitamin_a': 'Vit A',
        'vitamin_c': 'Vit C',
        // Add any other formatting rules here
    };
    
    // Return formatted name if it exists in the map, otherwise capitalize first letter
    return formatMap[nutrient] || 
           nutrient.charAt(0).toUpperCase() + 
           nutrient.slice(1).replace(/_/g, ' ');
}

// Update submitForm with better error handling
async function submitForm() {
    const loader = document.getElementById('loader');
    const result = document.getElementById('result');
    
    const foodItem = document.getElementById("food_item").value;
    const quantity = document.getElementById("quantity").value;
    const quantityUnit = document.getElementById("quantity_unit").value;

    // Validate input
    const validationErrors = validateInput(foodItem, quantity, quantityUnit);
    if (validationErrors.length > 0) {
        result.innerHTML = `
            <div style="color: red; padding: 10px; border: 1px solid red; border-radius: 4px; margin-top: 10px;">
                ${validationErrors.map(error => `<p style="margin: 5px 0;">${error}</p>`).join('')}
            </div>
        `;
        return;
    }

    loader.style.display = 'block';
    result.innerHTML = '';

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

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            result.innerHTML = `
                <div style="
                    color: red;
                    padding: 15px;
                    border: 1px solid red;
                    border-radius: 4px;
                    margin-top: 10px;
                    background-color: rgba(255,0,0,0.1);
                ">
                    <p style="margin: 0;">${data.error}</p>
                    ${data.error_type ? `<p style="margin: 5px 0 0; font-size: 0.9em; opacity: 0.8;">Error type: ${data.error_type}</p>` : ''}
                </div>
            `;
        } else {
            result.innerHTML = `
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 300px;">
                        <p style="margin-top: 15px; font-style: italic; color: #666;">${data.insight}</p>
                        <table class="nutrition-table" style="
                            width: 100%;
                            margin: 20px 0;
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
                            ${Object.entries(data.nutrition_info)
                                .filter(([nutrient]) => !['insight', 'is_recipe', 'recipe_urls'].includes(nutrient))
                                .map(([nutrient, value], index) => `
                                    <tr style="
                                        background-color: ${index % 2 === 0 ? '#f8f9fa' : 'white'};
                                        border-bottom: 1px solid #ddd;
                                    ">
                                        <td style="padding: 12px 15px; text-align: left;">${formatNutrientName(nutrient)}</td>
                                        <td style="padding: 12px 15px; text-align: right;">${value}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    ${data.is_recipe && data.recipe_urls ? `
                        <div style="flex: 0 0 300px;">
                            <div style="
                                background: white;
                                padding: 15px;
                                border-radius: 8px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                margin-top: 20px;
                            ">
                                <h3 style="margin-top: 0; color: #2c3e50;">Recipe Videos</h3>
                                <div class="recipe-videos" style="
                                    max-height: 500px;
                                    overflow-y: auto;
                                    padding-right: 10px;
                                ">
                                    ${data.recipe_urls.map((video, index) => `
                                        <div style="margin-bottom: 20px;">
                                            <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
                                                <iframe 
                                                    src="https://www.youtube.com/embed/${video.id}"
                                                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; border-radius: 4px;"
                                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                                    allowfullscreen
                                                ></iframe>
                                            </div>
                                            <div style="margin-top: 8px;">
                                                <a href="${video.url}" 
                                                   target="_blank" 
                                                   rel="noopener noreferrer"
                                                   style="
                                                    display: block;
                                                    color: #3498db;
                                                    text-decoration: none;
                                                    font-size: 14px;
                                                    line-height: 1.4;
                                                   "
                                                >
                                                    ${video.title}
                                                </a>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>`;
        }
    } catch (error) {
        result.innerHTML = `
            <div style="
                color: red;
                padding: 15px;
                border: 1px solid red;
                border-radius: 4px;
                margin-top: 10px;
                background-color: rgba(255,0,0,0.1);
            ">
                <p style="margin: 0;">An error occurred while processing your request.</p>
                <p style="margin: 5px 0 0; font-size: 0.9em; opacity: 0.8;">${error.message}</p>
            </div>
        `;
    } finally {
        loader.style.display = 'none';
    }
}

