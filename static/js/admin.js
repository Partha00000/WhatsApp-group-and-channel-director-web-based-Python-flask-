// Admin Panel JavaScript
(function() {
    'use strict';

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeAdminPanel();
    });

    function initializeAdminPanel() {
        initializeSidebar();
        initializeCharts();
        initializeTables();
        initializeForms();
        initializeBulkActions();
        initializeNotifications();
        initializeFileUploads();
        initializeRealTimeUpdates();
    }

    // Sidebar functionality
    function initializeSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');

        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('sidebar-collapsed');
                
                // Save state to localStorage
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
            });
        }

        // Restore sidebar state
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            sidebar?.classList.add('collapsed');
            mainContent?.classList.add('sidebar-collapsed');
        }

        // Submenu toggles
        const submenuToggles = document.querySelectorAll('.has-submenu');
        submenuToggles.forEach(toggle => {
            toggle.addEventListener('click', function(event) {
                if (event.target.tagName === 'A') {
                    event.preventDefault();
                }
                
                const submenu = this.nextElementSibling;
                const isOpen = submenu?.classList.contains('show');
                
                // Close all other submenus
                document.querySelectorAll('.collapse.show').forEach(menu => {
                    if (menu !== submenu) {
                        menu.classList.remove('show');
                    }
                });
                
                // Toggle current submenu
                if (submenu) {
                    submenu.classList.toggle('show');
                }
            });
        });

        // Auto-expand active submenu
        const activeSubmenuItem = document.querySelector('.submenu .nav-link.active');
        if (activeSubmenuItem) {
            const parentSubmenu = activeSubmenuItem.closest('.collapse');
            parentSubmenu?.classList.add('show');
        }
    }

    // Charts initialization
    function initializeCharts() {
        // Dashboard statistics chart
        const chartContainer = document.getElementById('statisticsChart');
        if (chartContainer && typeof Chart !== 'undefined') {
            const ctx = chartContainer.getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Groups Submitted',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    // Table enhancements
    function initializeTables() {
        // DataTables initialization
        const adminTables = document.querySelectorAll('.admin-table');
        adminTables.forEach(table => {
            if (typeof $.fn.DataTable !== 'undefined') {
                $(table).DataTable({
                    responsive: true,
                    pageLength: 25,
                    order: [[0, 'desc']],
                    columnDefs: [
                        { orderable: false, targets: -1 } // Disable sorting on actions column
                    ]
                });
            }
        });

        // Select all functionality
        const selectAllCheckbox = document.getElementById('selectAll');
        const itemCheckboxes = document.querySelectorAll('.item-checkbox');

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                itemCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
                updateBulkActionButton();
            });
        }

        itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateSelectAllState();
                updateBulkActionButton();
            });
        });

        function updateSelectAllState() {
            const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = checkedBoxes.length === itemCheckboxes.length;
                selectAllCheckbox.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < itemCheckboxes.length;
            }
        }

        function updateBulkActionButton() {
            const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
            const bulkActionButton = document.querySelector('.bulk-action-btn');
            
            if (bulkActionButton) {
                bulkActionButton.disabled = checkedBoxes.length === 0;
                bulkActionButton.textContent = `Bulk Actions (${checkedBoxes.length})`;
            }
        }

        // Row click to select
        const tableRows = document.querySelectorAll('tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('click', function(event) {
                if (event.target.type !== 'checkbox' && event.target.tagName !== 'A' && event.target.tagName !== 'BUTTON') {
                    const checkbox = this.querySelector('.item-checkbox');
                    if (checkbox) {
                        checkbox.checked = !checkbox.checked;
                        checkbox.dispatchEvent(new Event('change'));
                    }
                }
            });
        });
    }

    // Form enhancements
    function initializeForms() {
        // Auto-save functionality
        const autoSaveForms = document.querySelectorAll('[data-autosave]');
        autoSaveForms.forEach(form => {
            const formId = form.getAttribute('id') || 'form';
            let saveTimeout;

            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    clearTimeout(saveTimeout);
                    saveTimeout = setTimeout(() => {
                        saveFormData(formId, form);
                    }, 2000);
                });
            });

            // Load saved data on page load
            loadFormData(formId, form);
        });

        // Form validation
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    showToast('Please fix the errors in the form', 'error');
                }
                form.classList.add('was-validated');
            });
        });

        // Character counters
        const textareas = document.querySelectorAll('textarea[maxlength]');
        textareas.forEach(textarea => {
            const maxLength = textarea.getAttribute('maxlength');
            const counter = document.createElement('div');
            counter.className = 'form-text text-end';
            textarea.parentNode.appendChild(counter);

            function updateCounter() {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${textarea.value.length}/${maxLength} characters`;
                counter.className = remaining < 20 ? 'form-text text-end text-warning' : 'form-text text-end';
            }

            textarea.addEventListener('input', updateCounter);
            updateCounter();
        });

        // Rich text editor initialization
        const ckEditorTextareas = document.querySelectorAll('.ckeditor');
        ckEditorTextareas.forEach(textarea => {
            if (typeof ClassicEditor !== 'undefined') {
                ClassicEditor
                    .create(textarea)
                    .then(editor => {
                        console.log('CKEditor initialized');
                    })
                    .catch(error => {
                        console.error('CKEditor error:', error);
                    });
            }
        });
    }

    // Bulk actions functionality
    function initializeBulkActions() {
        const bulkActionForm = document.getElementById('bulkActionForm');
        const bulkActionButtons = document.querySelectorAll('[data-bulk-action]');

        bulkActionButtons.forEach(button => {
            button.addEventListener('click', function() {
                const action = this.getAttribute('data-bulk-action');
                const selectedItems = document.querySelectorAll('.item-checkbox:checked');

                if (selectedItems.length === 0) {
                    showToast('Please select at least one item', 'warning');
                    return;
                }

                if (action === 'delete') {
                    if (!confirm(`Are you sure you want to delete ${selectedItems.length} selected items?`)) {
                        return;
                    }
                }

                submitBulkAction(action, selectedItems);
            });
        });
    }

    function submitBulkAction(action, selectedItems) {
        const form = document.getElementById('bulkActionForm');
        if (!form) return;

        // Create hidden input for action
        let actionInput = form.querySelector('input[name="action"]');
        if (!actionInput) {
            actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            form.appendChild(actionInput);
        }
        actionInput.value = action;

        // Submit form
        form.submit();
    }

    // Notification system
    function initializeNotifications() {
        // Auto-hide notifications
        const notifications = document.querySelectorAll('.alert-dismissible');
        notifications.forEach(notification => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(notification);
                bsAlert.close();
            }, 5000);
        });

        // Real-time notifications (WebSocket simulation)
        checkForNewNotifications();
        setInterval(checkForNewNotifications, 30000); // Check every 30 seconds
    }

    function checkForNewNotifications() {
        // This would typically make an AJAX call to check for new notifications
        // For now, we'll just simulate it
        if (Math.random() < 0.1) { // 10% chance
            showToast('New group submission received!', 'info');
        }
    }

    // File upload enhancements
    function initializeFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            const dropZone = createDropZone(input);
            input.parentNode.insertBefore(dropZone, input);
            input.style.display = 'none';

            // File selection
            input.addEventListener('change', function() {
                handleFileSelection(this.files, dropZone);
            });

            // Drag and drop
            dropZone.addEventListener('dragover', function(event) {
                event.preventDefault();
                this.classList.add('dragover');
            });

            dropZone.addEventListener('dragleave', function() {
                this.classList.remove('dragover');
            });

            dropZone.addEventListener('drop', function(event) {
                event.preventDefault();
                this.classList.remove('dragover');
                handleFileSelection(event.dataTransfer.files, dropZone);
            });
        });
    }

    function createDropZone(input) {
        const dropZone = document.createElement('div');
        dropZone.className = 'file-drop-zone border-2 border-dashed rounded p-4 text-center';
        dropZone.innerHTML = `
            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
            <p class="mb-2">Drag and drop files here or <button type="button" class="btn btn-link p-0">click to select</button></p>
            <small class="text-muted">Maximum file size: 10MB</small>
        `;

        const clickButton = dropZone.querySelector('button');
        clickButton.addEventListener('click', () => input.click());

        return dropZone;
    }

    function handleFileSelection(files, dropZone) {
        const fileList = Array.from(files);
        
        fileList.forEach(file => {
            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                showToast(`File ${file.name} is too large (max 10MB)`, 'error');
                return;
            }

            // Create file preview
            const preview = document.createElement('div');
            preview.className = 'file-preview d-flex align-items-center p-2 border rounded mb-2';
            preview.innerHTML = `
                <i class="fas fa-file me-2"></i>
                <span class="flex-grow-1">${file.name}</span>
                <small class="text-muted">${formatFileSize(file.size)}</small>
                <button type="button" class="btn btn-sm btn-outline-danger ms-2">
                    <i class="fas fa-times"></i>
                </button>
            `;

            const removeButton = preview.querySelector('button');
            removeButton.addEventListener('click', () => preview.remove());

            dropZone.appendChild(preview);
        });
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Real-time updates
    function initializeRealTimeUpdates() {
        // Check for updates every minute
        setInterval(checkForUpdates, 60000);
    }

    function checkForUpdates() {
        // This would typically make an AJAX call to check for updates
        const pendingCountElement = document.querySelector('.pending-count');
        if (pendingCountElement) {
            // Simulate update check
            fetch('/admin/api/pending-count')
                .then(response => response.json())
                .then(data => {
                    pendingCountElement.textContent = data.count;
                    if (data.count > 0) {
                        pendingCountElement.classList.add('badge-warning');
                    }
                })
                .catch(error => console.error('Error checking for updates:', error));
        }
    }

    // Utility functions
    function saveFormData(formId, form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        localStorage.setItem(`admin_form_${formId}`, JSON.stringify({
            data: data,
            timestamp: new Date().toISOString()
        }));

        showToast('Draft saved', 'info', 2000);
    }

    function loadFormData(formId, form) {
        const savedData = localStorage.getItem(`admin_form_${formId}`);
        if (!savedData) return;

        try {
            const parsed = JSON.parse(savedData);
            const data = parsed.data;

            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = data[key] === 'on';
                    } else {
                        input.value = data[key];
                    }
                }
            });

            showToast('Draft restored', 'info', 2000);
        } catch (error) {
            console.error('Error loading form data:', error);
        }
    }

    function showToast(message, type = 'info', duration = 5000) {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            delay: duration
        });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', function() {
            toastContainer.removeChild(toast);
        });
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    // Search and filter functions
    function initializeSearch() {
        const searchInputs = document.querySelectorAll('.admin-search');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const query = this.value.trim();
                
                searchTimeout = setTimeout(() => {
                    if (query.length >= 2 || query.length === 0) {
                        performSearch(query);
                    }
                }, 300);
            });
        });
    }

    function performSearch(query) {
        const tableRows = document.querySelectorAll('tbody tr');
        
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    // Initialize additional features
    initializeSearch();

    // Expose admin functions globally
    window.AdminPanel = {
        showToast,
        saveFormData,
        loadFormData,
        submitBulkAction
    };

})();
