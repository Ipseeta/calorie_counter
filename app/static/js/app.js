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

    const validUnits = ["units", "grams", "ml", "bowl", "cup", "tbsp", "tsp", "plate"];
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
        'vitamin_d': 'Vit D',
        'calcium': 'Calcium',
        'iron': 'Iron',
        'potassium': 'Potassium'
    };

    return formatMap[nutrient] ||
           nutrient.charAt(0).toUpperCase() +
           nutrient.slice(1).replace(/_/g, ' ');
}

// Get emoji based on health score
function getScoreEmoji(score) {
    if (score >= 8) return "🌟";
    if (score >= 6) return "👍";
    if (score >= 4) return "😐";
    return "⚠️";
}

// Generates HTML for health score display
function generateHealthScoreHTML(healthScore) {
    const emoji = getScoreEmoji(healthScore.score);
    const circumference = 2 * Math.PI * 45; // radius = 45
    const offset = circumference - (healthScore.score / 10) * circumference;

    return `
        <div class="health-score-card" style="
            background: linear-gradient(135deg, var(--card, white) 0%, var(--bg, #f8fafc) 100%);
            padding: 24px;
            border-radius: 16px;
            margin: 20px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
        ">
            <h3 style="margin: 0 0 20px 0; color: var(--text, #1e293b); font-size: 1rem; font-weight: 600;">Health Score</h3>

            <div style="position: relative; width: 120px; height: 120px; margin: 0 auto 16px;">
                <svg width="120" height="120" style="transform: rotate(-90deg);">
                    <circle cx="60" cy="60" r="45" fill="none" stroke="var(--border, #e2e8f0)" stroke-width="10"/>
                    <circle cx="60" cy="60" r="45" fill="none" stroke="${healthScore.color}" stroke-width="10"
                        stroke-linecap="round"
                        stroke-dasharray="${circumference}"
                        stroke-dashoffset="${offset}"
                        style="transition: stroke-dashoffset 1s ease-out;"/>
                </svg>
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                ">
                    <span style="font-size: 28px;">${emoji}</span>
                    <div style="
                        font-size: 1.5rem;
                        font-weight: 700;
                        color: ${healthScore.color};
                        line-height: 1;
                    ">${healthScore.score}</div>
                </div>
            </div>

            <p style="
                margin: 0;
                color: var(--text-muted, #64748b);
                font-size: 0.9rem;
                line-height: 1.5;
                max-width: 280px;
                margin: 0 auto;
            ">
                ${healthScore.message}
            </p>
        </div>
    `;
}

function generateNutritionTableHTML(data) {
    return `
        <div style="margin-top: 20px;">
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 16px;
                padding: 12px 16px;
                background: var(--primary-light, #dcfce7);
                border-radius: 10px;
            ">
                <span style="font-size: 1.25rem;">🍽️</span>
                <p style="
                    font-size: 0.9rem;
                    color: var(--text, #1e293b);
                    margin: 0;
                "><strong>${data.quantity} ${data.unit}</strong> of <strong>${data.food_item}</strong></p>
            </div>
            <table class="nutrition-table">
                <thead>
                    <tr>
                        <th>Nutrient</th>
                        <th style="text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(data.nutrition_info)
                        .filter(([nutrient]) => !['insight', 'is_recipe', 'is_valid_food', 'recipe_urls'].includes(nutrient))
                        .map(([nutrient, value], index) => {
                            if (typeof value === 'object') {
                                const isExpandable = ['carbohydrates', 'fat'].includes(nutrient);

                                const mainRow = `
                                    <tr>
                                        <td style="cursor: ${isExpandable ? 'pointer' : 'default'}"
                                            onclick="${isExpandable ? `toggleSubRows('${nutrient}-subrows')` : ''}"
                                            class="nutrient-row">
                                            ${formatNutrientName(nutrient)}
                                            ${isExpandable ? '<span style="float: right; transition: transform 0.2s;">▼</span>' : ''}
                                        </td>
                                        <td style="text-align: right; font-weight: 500;">
                                            ${value.total}
                                        </td>
                                    </tr>`;

                                const subRows = Object.entries(value)
                                    .filter(([key]) => key !== 'total')
                                    .map(([subKey, subVal]) => {
                                        const info = getNutrientInfo(subKey);
                                        return `
                                            <tr id="${nutrient}-subrows" style="display: none;">
                                                <td style="padding-left: 32px; color: var(--text-muted, #64748b); font-size: 0.9rem;">
                                                    ${subKey.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                                                    ${info ? `
                                                        <span class="info-icon" onclick="event.stopPropagation(); showTooltip(event)" style="
                                                            display: inline-flex;
                                                            align-items: center;
                                                            justify-content: center;
                                                            width: 16px;
                                                            height: 16px;
                                                            background: var(--bg, #f1f5f9);
                                                            border-radius: 50%;
                                                            font-size: 11px;
                                                            margin-left: 6px;
                                                            cursor: pointer;
                                                            color: var(--text-muted, #64748b);
                                                        ">
                                                            i
                                                            <div class="nutrient-tooltip" style="
                                                                display: none;
                                                                position: fixed;
                                                                background: rgba(0, 0, 0, 0.9);
                                                                color: white;
                                                                padding: 10px 14px;
                                                                border-radius: 8px;
                                                                font-size: 12px;
                                                                max-width: 220px;
                                                                z-index: 1000;
                                                                text-align: left;
                                                                line-height: 1.4;
                                                                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                                                            ">${info}</div>
                                                        </span>
                                                    ` : ''}
                                                </td>
                                                <td style="text-align: right; color: var(--text-muted, #64748b); font-size: 0.9rem;">
                                                    ${subVal}
                                                </td>
                                            </tr>
                                        `;
                                    }).join('');

                                return mainRow + subRows;
                            } else {
                                return `
                                    <tr>
                                        <td>${formatNutrientName(nutrient)}</td>
                                        <td style="text-align: right; font-weight: 500;">${value}</td>
                                    </tr>
                                `;
                            }
                        }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Toggle sub-rows for expandable nutrients
function toggleSubRows(id) {
    const subRows = document.querySelectorAll(`#${id}`);
    const arrow = event.currentTarget.querySelector('span');

    subRows.forEach(row => {
        if (row.style.display === 'none') {
            row.style.display = 'table-row';
            if (arrow) arrow.style.transform = 'rotate(180deg)';
        } else {
            row.style.display = 'none';
            if (arrow) arrow.style.transform = 'rotate(0deg)';
        }
    });
}

function generateRecipeVideosHTML(data) {
    if (!data.recipe_urls || data.recipe_urls.length === 0) return '';

    return `
        <div style="margin-top: 24px;">
            <h3 style="
                margin: 0 0 16px 0;
                color: var(--text, #1e293b);
                font-size: 1rem;
                font-weight: 600;
            ">Recipe Videos</h3>
            <div style="
                display: flex;
                flex-direction: column;
                gap: 16px;
            ">
                ${data.recipe_urls.slice(0, 3).map(video => `
                    <div style="
                        background: var(--card, white);
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    ">
                        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
                            <iframe
                                src="https://www.youtube.com/embed/${video.id}"
                                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowfullscreen
                                loading="lazy"
                            ></iframe>
                        </div>
                        <div style="padding: 12px 16px;">
                            <a href="${video.url}"
                               target="_blank"
                               rel="noopener noreferrer"
                               style="
                                color: var(--primary, #22c55e);
                                text-decoration: none;
                                font-size: 0.875rem;
                                font-weight: 500;
                                line-height: 1.4;
                                display: -webkit-box;
                                -webkit-line-clamp: 2;
                                -webkit-box-orient: vertical;
                                overflow: hidden;
                               "
                            >
                                ${video.title}
                            </a>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function generateErrorHTML(error) {
    return `
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 12px;
            color: #dc2626;
            padding: 16px;
            border: 1px solid #fecaca;
            border-radius: 12px;
            margin-top: 16px;
            background-color: #fef2f2;
        ">
            <span style="font-size: 1.5rem; line-height: 1;">😕</span>
            <div>
                <p style="margin: 0; font-weight: 600;">Oops! Something went wrong</p>
                <p style="margin: 6px 0 0; font-size: 0.875rem; opacity: 0.8;">${error}</p>
            </div>
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
            <div style="
                color: #dc2626;
                padding: 16px;
                border: 1px solid #fecaca;
                border-radius: 12px;
                margin-top: 16px;
                background: #fef2f2;
            ">
                ${validationErrors.map(error => `<p style="margin: 4px 0;">${error}</p>`).join('')}
            </div>
        `;
        resultsContainer.style.display = 'block';
        return;
    }

    // Show loader and hide results
    resultsContainer.style.display = 'none';
    loader.style.display = 'flex';
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
                    color: #dc2626;
                    padding: 16px;
                    border: 1px solid #fecaca;
                    border-radius: 12px;
                    margin-top: 16px;
                    background: #fef2f2;
                ">
                    <p style="margin: 0;">${data.error}</p>
                    ${data.error_type ? `<p style="margin: 8px 0 0; font-size: 0.875rem; opacity: 0.8;">Error type: ${data.error_type}</p>` : ''}
                </div>
            `;
        } else {
            result.innerHTML = `
                <div>
                    ${data.insight ? `<p style="margin: 0 0 16px 0; font-style: italic; color: var(--text-muted, #64748b); line-height: 1.6;">${data.insight}</p>` : ''}
                    ${data.is_valid_food && data.health_score ? generateHealthScoreHTML(data.health_score) : ''}
                    ${data.is_valid_food ? generateNutritionTableHTML(data) : ''}
                    ${data.recipe_urls ? generateRecipeVideosHTML(data) : ''}
                </div>`;
        }
        resetForm();
    } catch (error) {
        result.innerHTML = generateErrorHTML(error);
    } finally {
        loader.style.display = 'none';
        resultsContainer.style.display = 'block';
        // Smooth scroll to results
        setTimeout(() => {
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

// Store selected file globally for the modal
let selectedImageFile = null;

// Image upload handling
document.addEventListener('DOMContentLoaded', function() {
    const imageSearchBtn = document.getElementById('imageSearchBtn');
    const imageModal = document.getElementById('imageModal');
    const closeBtn = document.querySelector('.close');
    const cameraInput = document.getElementById('cameraInput');
    const galleryInput = document.getElementById('galleryInput');
    const cameraBtn = document.getElementById('cameraBtn');
    const galleryBtn = document.getElementById('galleryBtn');
    const dropZone = document.getElementById('dropZone');
    const previewImage = document.getElementById('previewImage');
    const analyzeImageBtn = document.getElementById('analyzeImageBtn');

    // Track which input was used
    let activeInput = null;

    // Open modal
    function openModal() {
        imageModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    // Close modal
    function closeModal() {
        imageModal.style.display = 'none';
        document.body.style.overflow = '';
        // Don't reset if we have an image and are about to analyze
        if (!selectedImageFile) {
            resetUpload();
        }
    }

    // Open modal on image button click
    imageSearchBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        openModal();
    });

    // Close modal handlers
    closeBtn.addEventListener('click', function() {
        selectedImageFile = null;
        resetUpload();
        imageModal.style.display = 'none';
        document.body.style.overflow = '';
    });

    // Close on outside click
    imageModal.addEventListener('click', function(e) {
        if (e.target === imageModal) {
            selectedImageFile = null;
            resetUpload();
            imageModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    });

    // Prevent modal close on modal content click
    document.querySelector('.modal-content').addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && imageModal.style.display === 'block') {
            selectedImageFile = null;
            resetUpload();
            imageModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    });

    // Camera button - opens camera on mobile
    cameraBtn.addEventListener('click', function(e) {
        e.preventDefault();
        activeInput = cameraInput;
        cameraInput.click();
    });

    // Gallery button - opens file picker
    galleryBtn.addEventListener('click', function(e) {
        e.preventDefault();
        activeInput = galleryInput;
        galleryInput.click();
    });

    // Handle file selection from input element
    function handleFileInput(inputElement) {
        const files = inputElement.files;
        if (!files || files.length === 0) {
            console.log('No files selected');
            return;
        }

        const file = files[0];
        console.log('File selected:', file.name, file.type, file.size);

        // More lenient type check for camera captures
        if (!file.type.startsWith('image/') && !file.type === '') {
            alert('Please select an image file');
            return;
        }

        // Size validation (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            alert('Please select an image smaller than 10MB');
            return;
        }

        // Store the file globally
        selectedImageFile = file;
        console.log('selectedImageFile set:', selectedImageFile);

        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            dropZone.classList.add('has-image');
            analyzeImageBtn.disabled = false;
        };
        reader.onerror = function(e) {
            console.error('FileReader error:', e);
            alert('Error reading the image file');
        };
        reader.readAsDataURL(file);
    }

    // Camera input change handler
    cameraInput.addEventListener('change', function(e) {
        console.log('Camera input changed');
        handleFileInput(this);
    });

    // Gallery input change handler
    galleryInput.addEventListener('change', function(e) {
        console.log('Gallery input changed');
        handleFileInput(this);
    });

    // Drop zone click handler - opens gallery
    dropZone.addEventListener('click', function(e) {
        e.preventDefault();
        if (!dropZone.classList.contains('has-image')) {
            activeInput = galleryInput;
            galleryInput.click();
        }
    });

    // Drag and drop handlers
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            const file = files[0];
            if (!file.type.startsWith('image/')) {
                alert('Please drop an image file');
                return;
            }
            if (file.size > 10 * 1024 * 1024) {
                alert('Please drop an image smaller than 10MB');
                return;
            }
            selectedImageFile = file;
            const reader = new FileReader();
            reader.onload = function(evt) {
                previewImage.src = evt.target.result;
                dropZone.classList.add('has-image');
                analyzeImageBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });

    // Analyze image button click handler
    analyzeImageBtn.addEventListener('click', async function() {
        console.log('Analyze button clicked, selectedImageFile:', selectedImageFile);

        if (!selectedImageFile) {
            alert('No image selected. Please take a photo or choose from gallery.');
            return;
        }

        const loader = document.getElementById('loader');
        const result = document.getElementById('result');
        const resultsContainer = document.getElementById('results-container');

        // Store the file before closing modal (which might reset it)
        const fileToUpload = selectedImageFile;

        // Show loader and close modal
        loader.style.display = 'flex';
        imageModal.style.display = 'none';
        document.body.style.overflow = '';
        resultsContainer.style.display = 'none';
        result.innerHTML = '';

        try {
            const formData = new FormData();
            formData.append('image', fileToUpload, fileToUpload.name || 'photo.jpg');

            console.log('Sending image:', fileToUpload.name, fileToUpload.size, fileToUpload.type);

            const response = await fetch('/analyze_image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            console.log('Response:', data);

            if (data.error) {
                result.innerHTML = `
                    <div style="
                        color: #dc2626;
                        padding: 16px;
                        border: 1px solid #fecaca;
                        border-radius: 12px;
                        margin-top: 16px;
                        background: #fef2f2;
                    ">
                        <p style="margin: 0;">${data.error.message || data.error}</p>
                    </div>
                `;
            } else {
                result.innerHTML = `
                    <div>
                        ${data.insight ? `<p style="margin: 0 0 16px 0; font-style: italic; color: var(--text-muted, #64748b); line-height: 1.6;">${data.insight}</p>` : ''}
                        ${data.is_valid_food && data.health_score ? generateHealthScoreHTML(data.health_score) : ''}
                        ${data.is_valid_food ? generateNutritionTableHTML(data) : ''}
                        ${data.recipe_urls ? generateRecipeVideosHTML(data) : ''}
                    </div>`;
            }
        } catch (error) {
            console.error('Upload error:', error);
            result.innerHTML = generateErrorHTML(error);
        } finally {
            loader.style.display = 'none';
            resultsContainer.style.display = 'block';
            // Smooth scroll to results
            setTimeout(() => {
                resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
            // Reset after upload completes
            resetUpload();
        }
    });

    // Reset upload state
    function resetUpload() {
        selectedImageFile = null;
        activeInput = null;
        cameraInput.value = '';
        galleryInput.value = '';
        previewImage.src = '';
        dropZone.classList.remove('has-image', 'dragover');
        analyzeImageBtn.disabled = true;
    }

    // Fetch food suggestions when page loads
    fetchFoodSuggestions();
});

// Get nutrient information for tooltips
function getNutrientInfo(nutrient) {
    const nutrientInfo = {
        monounsaturated: "Helps reduce bad cholesterol levels and supports heart health",
        polyunsaturated: "Essential fats that support brain function and cell growth",
        saturated: "Should be limited as part of a healthy diet",
        trans: "Artificial fats that should be avoided",
        fiber: "Aids digestion and helps maintain healthy blood sugar levels",
        added_sugar: "Added sugars should be limited in your diet",
        sugar: "Natural and added sugars combined"
    };
    return nutrientInfo[nutrient] || "";
}

// Handle tooltip positioning and display
function showTooltip(event) {
    // Hide all other tooltips first
    document.querySelectorAll('.nutrient-tooltip').forEach(tooltip => {
        tooltip.style.display = 'none';
    });

    const tooltip = event.currentTarget.querySelector('.nutrient-tooltip');
    const currentDisplay = tooltip.style.display;

    if (currentDisplay === 'none') {
        const rect = event.currentTarget.getBoundingClientRect();
        tooltip.style.display = 'block';

        // Position tooltip above the icon
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';

        // Ensure tooltip stays within viewport
        const tooltipRect = tooltip.getBoundingClientRect();
        if (tooltipRect.left < 0) {
            tooltip.style.left = '10px';
        }
        if (tooltipRect.right > window.innerWidth) {
            tooltip.style.left = (window.innerWidth - tooltipRect.width - 10) + 'px';
        }
        if (tooltipRect.top < 0) {
            // If not enough space above, show below
            tooltip.style.top = (rect.bottom + 10) + 'px';
        }
    } else {
        tooltip.style.display = 'none';
    }
}

// Close tooltips when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.nutrient-tooltip') && !event.target.closest('.info-icon')) {
        document.querySelectorAll('.nutrient-tooltip').forEach(tooltip => {
            tooltip.style.display = 'none';
        });
    }
});
