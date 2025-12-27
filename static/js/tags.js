// Tag Input and Management JavaScript
(function() {
    'use strict';

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeTagInputs();
        initializeTagManagement();
    });

    function initializeTagInputs() {
        const tagInputs = document.querySelectorAll('input[data-role="tagsinput"]');
        
        tagInputs.forEach(input => {
            createTagInput(input);
        });
    }

    function createTagInput(input) {
        // Hide original input
        input.style.display = 'none';
        
        // Create tag container
        const container = document.createElement('div');
        container.className = 'tag-input-container form-control';
        container.style.minHeight = '38px';
        container.style.cursor = 'text';
        
        // Create hidden input field for typing
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'text';
        hiddenInput.className = 'tag-hidden-input';
        hiddenInput.style.border = 'none';
        hiddenInput.style.outline = 'none';
        hiddenInput.style.background = 'transparent';
        hiddenInput.style.width = 'auto';
        hiddenInput.style.minWidth = '100px';
        
        container.appendChild(hiddenInput);
        input.parentNode.insertBefore(container, input.nextSibling);
        
        // Initialize with existing tags
        if (input.value) {
            const existingTags = input.value.split(',').map(tag => tag.trim()).filter(tag => tag);
            existingTags.forEach(tag => addTag(tag, container, input));
        }
        
        // Event handlers
        hiddenInput.addEventListener('keydown', function(event) {
            handleTagInput(event, container, input);
        });
        
        hiddenInput.addEventListener('blur', function() {
            if (this.value.trim()) {
                addTag(this.value.trim(), container, input);
                this.value = '';
            }
        });
        
        container.addEventListener('click', function() {
            hiddenInput.focus();
        });
        
        // Tag suggestions
        createTagSuggestions(hiddenInput, container, input);
    }

    function handleTagInput(event, container, input) {
        const hiddenInput = event.target;
        const value = hiddenInput.value.trim();
        
        switch (event.key) {
            case 'Enter':
            case ',':
                event.preventDefault();
                if (value) {
                    addTag(value, container, input);
                    hiddenInput.value = '';
                }
                break;
                
            case 'Backspace':
                if (!value) {
                    const tags = container.querySelectorAll('.tag-item');
                    if (tags.length > 0) {
                        removeTag(tags[tags.length - 1], container, input);
                    }
                }
                break;
                
            case 'ArrowUp':
            case 'ArrowDown':
                handleSuggestionNavigation(event, container);
                break;
        }
    }

    function addTag(tagText, container, input) {
        // Validate tag
        if (!isValidTag(tagText)) {
            showTagError('Invalid tag. Use only letters, numbers, and spaces.');
            return;
        }
        
        // Check for duplicates
        const existingTags = getTagsFromContainer(container);
        if (existingTags.includes(tagText.toLowerCase())) {
            showTagError('Tag already exists.');
            return;
        }
        
        // Check maximum tags limit
        if (existingTags.length >= 10) {
            showTagError('Maximum 10 tags allowed.');
            return;
        }
        
        // Create tag element
        const tag = document.createElement('span');
        tag.className = 'tag-item badge bg-primary me-1 mb-1';
        tag.innerHTML = `
            ${escapeHtml(tagText)}
            <button type="button" class="btn-close btn-close-white ms-1" aria-label="Remove tag"></button>
        `;
        
        // Add remove functionality
        const removeButton = tag.querySelector('.btn-close');
        removeButton.addEventListener('click', function(event) {
            event.stopPropagation();
            removeTag(tag, container, input);
        });
        
        // Insert before hidden input
        const hiddenInput = container.querySelector('.tag-hidden-input');
        container.insertBefore(tag, hiddenInput);
        
        // Update original input value
        updateInputValue(container, input);
        
        // Hide suggestions
        hideSuggestions(container);
    }

    function removeTag(tagElement, container, input) {
        tagElement.remove();
        updateInputValue(container, input);
    }

    function getTagsFromContainer(container) {
        const tagElements = container.querySelectorAll('.tag-item');
        return Array.from(tagElements).map(tag => 
            tag.textContent.trim().toLowerCase()
        );
    }

    function updateInputValue(container, input) {
        const tags = getTagsFromContainer(container);
        input.value = tags.join(', ');
        
        // Trigger change event
        const event = new Event('change');
        input.dispatchEvent(event);
    }

    function isValidTag(tag) {
        // Tag validation rules
        if (tag.length < 2 || tag.length > 25) return false;
        if (!/^[a-zA-Z0-9\s]+$/.test(tag)) return false;
        return true;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showTagError(message) {
        // Create or update error message
        let errorElement = document.querySelector('.tag-error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'tag-error-message text-danger small mt-1';
            
            // Find the first tag container and add error after it
            const tagContainer = document.querySelector('.tag-input-container');
            if (tagContainer) {
                tagContainer.parentNode.insertBefore(errorElement, tagContainer.nextSibling);
            }
        }
        
        errorElement.textContent = message;
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.parentNode.removeChild(errorElement);
            }
        }, 3000);
    }

    function createTagSuggestions(hiddenInput, container, input) {
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'tag-suggestions position-fixed bg-white border rounded shadow-lg';
        suggestionsContainer.style.display = 'none';
        suggestionsContainer.style.zIndex = '9999';
        suggestionsContainer.style.maxHeight = '200px';
        suggestionsContainer.style.overflowY = 'auto';
        suggestionsContainer.style.width = 'auto';
        suggestionsContainer.style.minWidth = '200px';
        suggestionsContainer.style.maxWidth = '300px';
        
        document.body.appendChild(suggestionsContainer);
        
        // Load available tags from server
        let availableTags = [
            'technology', 'programming', 'web development', 'javascript', 'python', 
            'coding', 'software', 'mobile', 'android', 'ios', 'react', 'nodejs',
            'gaming', 'entertainment', 'music', 'movies', 'sports', 'news',
            'business', 'marketing', 'startups', 'education', 'learning',
            'design', 'ui/ux', 'graphics', 'photography', 'art',
            'travel', 'food', 'health', 'fitness', 'lifestyle'
        ];
        
        // Fetch existing tags from server
        fetch('/api/tags')
            .then(response => response.json())
            .then(data => {
                if (data.tags && data.tags.length > 0) {
                    availableTags = [...new Set([...data.tags, ...availableTags])];
                }
            })
            .catch(error => {
                console.log('Using fallback tags');
            });
        
        hiddenInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            
            if (query.length >= 2) {
                const suggestions = availableTags.filter(tag => 
                    tag.toLowerCase().includes(query) && !getTagsFromContainer(container).includes(tag)
                ).slice(0, 8);
                
                showSuggestions(suggestions, suggestionsContainer, container, input);
            } else {
                hideSuggestions(container);
            }
        });
        
        hiddenInput.addEventListener('blur', function() {
            // Delay hiding to allow clicking on suggestions
            setTimeout(() => hideSuggestions(container), 300);
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(event) {
            if (!container.contains(event.target) && !suggestionsContainer.contains(event.target)) {
                hideSuggestions(container);
            }
        });
    }

    function showSuggestions(suggestions, suggestionsContainer, container, input) {
        suggestionsContainer.innerHTML = '';
        
        if (suggestions.length === 0) {
            hideSuggestions(container);
            return;
        }
        
        suggestions.forEach((suggestion, index) => {
            const suggestionElement = document.createElement('div');
            suggestionElement.className = 'tag-suggestion px-3 py-2';
            suggestionElement.textContent = suggestion;
            suggestionElement.style.cursor = 'pointer';
            suggestionElement.style.borderBottom = '1px solid #f0f0f0';
            suggestionElement.style.transition = 'all 0.2s ease';
            
            suggestionElement.addEventListener('mouseenter', function() {
                // Remove active class from others
                suggestionsContainer.querySelectorAll('.tag-suggestion').forEach(el => {
                    el.classList.remove('active');
                    el.style.backgroundColor = '';
                });
                this.classList.add('active');
                this.style.backgroundColor = '#f8f9fa';
            });
            
            suggestionElement.addEventListener('mouseleave', function() {
                if (!this.classList.contains('active')) {
                    this.style.backgroundColor = '';
                }
            });
            
            suggestionElement.addEventListener('mousedown', function(e) {
                // Prevent blur event from firing before click
                e.preventDefault();
            });
            
            suggestionElement.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                addTag(suggestion, container, input);
                const hiddenInput = container.querySelector('.tag-hidden-input');
                hiddenInput.value = '';
                hideSuggestions(container);
                hiddenInput.focus();
            });
            
            // Remove border from last item
            if (index === suggestions.length - 1) {
                suggestionElement.style.borderBottom = 'none';
            }
            
            suggestionsContainer.appendChild(suggestionElement);
        });
        
        // Position suggestions
        const containerRect = container.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        suggestionsContainer.style.top = (containerRect.bottom + scrollTop + 2) + 'px';
        suggestionsContainer.style.left = (containerRect.left + scrollLeft) + 'px';
        suggestionsContainer.style.minWidth = Math.max(200, containerRect.width) + 'px';
        suggestionsContainer.style.display = 'block';
    }

    function hideSuggestions(container) {
        const suggestionsContainer = document.querySelector('.tag-suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
    }

    function handleSuggestionNavigation(event, container) {
        const suggestionsContainer = container.parentNode.querySelector('.tag-suggestions');
        if (!suggestionsContainer || suggestionsContainer.style.display === 'none') return;
        
        event.preventDefault();
        
        const suggestions = suggestionsContainer.querySelectorAll('.tag-suggestion');
        let activeIndex = -1;
        
        suggestions.forEach((suggestion, index) => {
            if (suggestion.classList.contains('active')) {
                activeIndex = index;
            }
        });
        
        // Remove current active class
        suggestions.forEach(suggestion => suggestion.classList.remove('active'));
        
        if (event.key === 'ArrowDown') {
            activeIndex = (activeIndex + 1) % suggestions.length;
        } else if (event.key === 'ArrowUp') {
            activeIndex = activeIndex <= 0 ? suggestions.length - 1 : activeIndex - 1;
        }
        
        if (suggestions[activeIndex]) {
            suggestions[activeIndex].classList.add('active');
        }
    }

    // Tag management functions
    function initializeTagManagement() {
        // Tag cloud interactions
        const tagCloudItems = document.querySelectorAll('.tag-cloud-item');
        tagCloudItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.1)';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
        
        // Tag filtering
        const tagFilter = document.getElementById('tagFilter');
        if (tagFilter) {
            tagFilter.addEventListener('input', function() {
                const query = this.value.toLowerCase();
                filterTags(query);
            });
        }
    }

    function filterTags(query) {
        const tagItems = document.querySelectorAll('.tag-item, .tag-card');
        
        tagItems.forEach(item => {
            const tagName = item.textContent.toLowerCase();
            const matches = tagName.includes(query);
            item.style.display = matches ? '' : 'none';
        });
        
        // Update count
        const visibleTags = Array.from(tagItems).filter(item => item.style.display !== 'none');
        const countElement = document.querySelector('.tag-count');
        if (countElement) {
            countElement.textContent = `${visibleTags.length} tags found`;
        }
    }

    // CSS for tag styling
    const style = document.createElement('style');
    style.textContent = `
        .tag-input-container {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 4px;
            padding: 6px 12px;
            min-height: 38px;
        }
        
        .tag-input-container:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .tag-hidden-input {
            flex: 1;
            min-width: 100px;
        }
        
        .tag-item {
            display: inline-flex;
            align-items: center;
            font-size: 0.875rem;
            font-weight: 500;
            padding: 4px 8px;
            border-radius: 16px;
            animation: fadeIn 0.3s ease;
        }
        
        .tag-item .btn-close {
            width: 12px;
            height: 12px;
            font-size: 10px;
            margin-left: 4px;
        }
        
        .tag-suggestion {
            transition: background-color 0.2s ease;
        }
        
        .tag-suggestion:hover,
        .tag-suggestion.active {
            background-color: #f8f9fa;
        }
        
        .tag-error-message {
            animation: shake 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .tag-cloud-item {
            transition: all 0.3s ease;
        }
        
        .tag-card {
            transition: all 0.3s ease;
            border: 1px solid #e9ecef;
        }
        
        .tag-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
    `;
    document.head.appendChild(style);

    // Expose tag functions globally
    window.TagInput = {
        addTag,
        removeTag,
        getTagsFromContainer,
        isValidTag,
        showTagError
    };

})();
