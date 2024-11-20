// static/script.js

// Utility function to prevent rapid-fire API calls
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

// Fetches food suggestions from the backend API
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

// Validates form input before submission
function validateInput(foodItem, quantity, unit) {
    const errors = [];
    
    if (!foodItem.trim()) {
        errors.push("Please enter a food item");
    }
    
    if (!quantity || quantity <= 0) {
        errors.push("Please enter a valid quantity");
    }
    
    const validUnits = ["units", "grams", "ml", "bowl", "cup", "tbsp", "tsp"];
    if (!unit || unit === "") {
        errors.push("Please select a unit of measurement");
    } else if (!validUnits.includes(unit)) {
        errors.push("Please select a valid unit");
    }
    
    return errors;
}

// Formats nutrient names for display
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

// Generates HTML for health score display
function generateHealthScoreHTML(healthScore) {
    return `
        <div style="
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h3 style="margin: 0 0 15px 0; color: #2c3e50;">Health Score</h3>
            <div style="
                background: #f5f5f5;
                height: 20px;
                border-radius: 10px;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    width: ${healthScore.score * 10}%;
                    height: 100%;
                    background-color: ${healthScore.color};
                    transition: width 0.5s ease-in-out;
                "></div>
            </div>
            <div style="
                display: flex;
                justify-content: space-between;
                margin-top: 5px;
                color: #666;
                font-size: 14px;
            ">
                <span>1</span>
                <span style="
                    color: ${healthScore.color};
                    font-weight: bold;
                    font-size: 16px;
                ">${healthScore.score}/10</span>
                <span>10</span>
            </div>
            <p style="
                margin: 10px 0 0 0;
                color: #666;
                font-size: 14px;
                text-align: center;
            ">
                ${healthScore.message}
            </p>
        </div>
    `;
}

function generateNutritionTableHTML(data) {
    return `
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
                .filter(([nutrient]) => !['insight', 'is_recipe', 'is_valid_food', 'recipe_urls'].includes(nutrient))
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
    `;
}

function generateRecipeVideosHTML(data) {
    if (!data.is_recipe || !data.recipe_urls) return '';
    
    return `
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
    `;
}

function generateErrorHTML(error) {
    return `
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
}

function resetForm() {
    document.getElementById('food_item').value = '';
    document.getElementById('quantity').value = '';
    document.getElementById('quantity_unit').value = '';
}

// Handles form submission and displays results
async function submitForm() {
    const loader = document.getElementById('loader');
    const result = document.getElementById('result');
    const resultsContainer = document.getElementById('results-container');
    
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

    // Show loader and hide results
    resultsContainer.style.display = 'none';
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
                        <p style="margin-top: 15px; font-style: italic; color: #666;">${data.insight || ''}</p>
                        ${data.is_valid_food && data.health_score ? generateHealthScoreHTML(data.health_score) : ''}
                        ${data.is_valid_food ? generateNutritionTableHTML(data) : ''}
                        ${data.is_recipe && data.recipe_urls ? generateRecipeVideosHTML(data) : ''}
                    </div>
                </div>`;
        }
        resetForm();
    } catch (error) {
        result.innerHTML = generateErrorHTML(error);
    } finally {
        loader.style.display = 'none';
        resultsContainer.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
// Fetch food suggestions when page loads
    fetchFoodSuggestions();
    // Add image upload functionality
    const modal = document.getElementById('imageModal');
    const imageSearchBtn = document.getElementById('imageSearchBtn');
    const closeBtn = document.querySelector('.close');
    const dropZone = document.getElementById('dropZone');
    const imageInput = document.getElementById('imageInput');
    const previewImage = document.getElementById('previewImage');
    const analyzeImageBtn = document.getElementById('analyzeImageBtn');

    // Image search button opens modal
    imageSearchBtn.onclick = function() {
        modal.style.display = "block";
    }

    // Close modal
    closeBtn.onclick = function() {
        modal.style.display = "none";
        resetUpload();
    }

    // Click outside modal to close
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            resetUpload();
        }
    }

    // Handle drag and drop
    dropZone.ondragover = function(e) {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary)';
    }

    dropZone.ondragleave = function(e) {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border)';
    }

    dropZone.ondrop = function(e) {
        e.preventDefault();
        handleFiles(e.dataTransfer.files);
    }

    // Handle click to upload
    dropZone.onclick = function() {
        imageInput.click();
    }

    imageInput.onchange = function() {
        handleFiles(this.files);
    }

    // Handle image analysis
    analyzeImageBtn.onclick = async function() {
        const file = imageInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('image', file);

        const loader = document.getElementById('loader');
        const resultsContainer = document.getElementById('results-container');
        const result = document.getElementById('result');
        const modal = document.getElementById('imageModal');
        
        modal.style.display = 'none';
        resetUpload();  // Reset the upload form
        // Show loader and hide results
        loader.style.display = 'block';
        resultsContainer.style.display = 'none';
        result.innerHTML = '';

        try {
            const response = await fetch('/analyze_image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();


            // Use your existing result container structure
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
                        <p style="margin-top: 15px; font-style: italic; color: #666;">${data.insight || ''}</p>
                        ${data.is_valid_food && data.health_score ? generateHealthScoreHTML(data.health_score) : ''}
                        ${data.is_valid_food ? generateNutritionTableHTML(data) : ''}
                        ${data.is_recipe && data.recipe_urls ? generateRecipeVideosHTML(data) : ''}
                    </div>
                </div>`;
            }

            // Close modal and show results
            modal.style.display = 'none';
            resultsContainer.style.display = 'block';

     } catch (error) {
        result.innerHTML = generateErrorHTML(error);
        } finally {
            loader.style.display = 'none';
            resultsContainer.style.display = 'block';
        }
    }

    function handleFiles(files) {
        if (files.length === 0) return;

        const file = files[0];
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            previewImage.style.display = 'block';
            document.querySelector('.drop-zone-text').style.display = 'none';
            analyzeImageBtn.disabled = false;
        }
        reader.readAsDataURL(file);
    }

    function resetUpload() {
        imageInput.value = '';
        previewImage.style.display = 'none';
        document.querySelector('.drop-zone-text').style.display = 'block';
        analyzeImageBtn.disabled = true;
        dropZone.style.borderColor = 'var(--border)';
    }
});

