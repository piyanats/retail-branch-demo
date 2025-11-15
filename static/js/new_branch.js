/**
 * New Branch Team - Branch Management JavaScript
 * Handles branch CRUD operations and UI interactions
 */

let currentPage = 1;
let currentFilters = {
    search: '',
    province: '',
    status: '',
    sort: 'created_at',
    order: 'desc'
};
let currentBranchId = null;
let isEditMode = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadBranchStats();
    loadBranches();
    initializeEventListeners();
});

// Event Listeners
function initializeEventListeners() {
    // Add Branch button
    document.getElementById('btn-add-branch').addEventListener('click', () => {
        openBranchModal();
    });

    // Close modal buttons
    document.getElementById('btn-close-modal').addEventListener('click', closeBranchModal);
    document.getElementById('btn-cancel').addEventListener('click', closeBranchModal);

    // Form submission
    document.getElementById('branch-form').addEventListener('submit', handleFormSubmit);

    // Search input (debounced)
    let searchTimeout;
    document.getElementById('search').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentFilters.search = e.target.value;
            currentPage = 1;
            loadBranches();
        }, 300);
    });

    // Filter changes
    document.getElementById('filter-province').addEventListener('change', (e) => {
        currentFilters.province = e.target.value;
        currentPage = 1;
        loadBranches();
    });

    document.getElementById('filter-status').addEventListener('change', (e) => {
        currentFilters.status = e.target.value;
        currentPage = 1;
        loadBranches();
    });

    // Clear filters
    document.getElementById('btn-clear-filters').addEventListener('click', () => {
        document.getElementById('search').value = '';
        document.getElementById('filter-province').value = '';
        document.getElementById('filter-status').value = '';
        currentFilters = { search: '', province: '', status: '', sort: 'created_at', order: 'desc' };
        currentPage = 1;
        loadBranches();
    });

    // Close modal on outside click
    document.getElementById('branch-modal').addEventListener('click', (e) => {
        if (e.target.id === 'branch-modal') {
            closeBranchModal();
        }
    });
}

// Load branch statistics
async function loadBranchStats() {
    try {
        const response = await fetch('/api/branches/stats');
        if (!response.ok) throw new Error('Failed to load statistics');

        const stats = await response.json();

        document.getElementById('stat-total').textContent = stats.total_branches || 0;
        document.getElementById('stat-active').textContent = stats.active_branches || 0;
        document.getElementById('stat-opening').textContent = stats.opening_branches || 0;
        document.getElementById('stat-closed').textContent = stats.closed_branches || 0;

        // Populate province filter
        if (stats.branches_by_province && stats.branches_by_province.length > 0) {
            const provinceSelect = document.getElementById('filter-province');
            const currentValue = provinceSelect.value;

            // Keep "All Provinces" option
            provinceSelect.innerHTML = '<option value="">All Provinces</option>';

            stats.branches_by_province.forEach(item => {
                const option = document.createElement('option');
                option.value = item.province;
                option.textContent = `${item.province} (${item.count})`;
                provinceSelect.appendChild(option);
            });

            // Restore previous selection
            provinceSelect.value = currentValue;
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        showNotification('Failed to load statistics', 'error');
    }
}

// Load branches list
async function loadBranches() {
    showLoading(true);

    try {
        const params = new URLSearchParams({
            page: currentPage,
            limit: 20,
            ...currentFilters
        });

        const response = await fetch(`/api/branches?${params}`);
        if (!response.ok) throw new Error('Failed to load branches');

        const data = await response.json();

        renderBranchesTable(data.data);
        renderPagination(data);

    } catch (error) {
        console.error('Error loading branches:', error);
        showNotification('Failed to load branches', 'error');
    } finally {
        showLoading(false);
    }
}

// Render branches table
function renderBranchesTable(branches) {
    const tbody = document.getElementById('branches-tbody');

    if (!branches || branches.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                    No branches found
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = branches.map(branch => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="font-medium text-blue-600">${escapeHtml(branch.branch_id)}</span>
            </td>
            <td class="px-6 py-4">
                <span class="font-medium text-gray-900">${escapeHtml(branch.branch_name)}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                ${escapeHtml(branch.province || '-')}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                ${escapeHtml(branch.dc_code || '-')}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getStatusBadge(branch.status)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                ${branch.opening_date ? formatDate(branch.opening_date) : '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button onclick="viewBranch('${branch.branch_id}')" class="text-blue-600 hover:text-blue-800 mr-3">View</button>
                <button onclick="editBranch('${branch.branch_id}')" class="text-green-600 hover:text-green-800 mr-3">Edit</button>
                <button onclick="deleteBranch('${branch.branch_id}', '${escapeHtml(branch.branch_name)}')" class="text-red-600 hover:text-red-800">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Render pagination
function renderPagination(data) {
    const { page, total, limit, total_pages } = data;

    const start = (page - 1) * limit + 1;
    const end = Math.min(page * limit, total);

    document.getElementById('page-info-start').textContent = start;
    document.getElementById('page-info-end').textContent = end;
    document.getElementById('page-info-total').textContent = total;

    const buttonsContainer = document.getElementById('pagination-buttons');
    buttonsContainer.innerHTML = '';

    if (total_pages <= 1) return;

    // Previous button
    const prevBtn = createPaginationButton('Previous', page > 1, () => {
        currentPage = page - 1;
        loadBranches();
    });
    buttonsContainer.appendChild(prevBtn);

    // Page numbers (show max 5 pages)
    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(total_pages, page + 2);

    if (startPage > 1) {
        buttonsContainer.appendChild(createPaginationButton('1', true, () => {
            currentPage = 1;
            loadBranches();
        }));
        if (startPage > 2) {
            buttonsContainer.appendChild(createPaginationEllipsis());
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        const btn = createPaginationButton(i.toString(), true, () => {
            currentPage = i;
            loadBranches();
        }, i === page);
        buttonsContainer.appendChild(btn);
    }

    if (endPage < total_pages) {
        if (endPage < total_pages - 1) {
            buttonsContainer.appendChild(createPaginationEllipsis());
        }
        buttonsContainer.appendChild(createPaginationButton(total_pages.toString(), true, () => {
            currentPage = total_pages;
            loadBranches();
        }));
    }

    // Next button
    const nextBtn = createPaginationButton('Next', page < total_pages, () => {
        currentPage = page + 1;
        loadBranches();
    });
    buttonsContainer.appendChild(nextBtn);
}

// Create pagination button
function createPaginationButton(text, enabled, onClick, isActive = false) {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = `px-4 py-2 text-sm font-medium rounded-lg ${
        isActive
            ? 'bg-blue-600 text-white'
            : enabled
                ? 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
    }`;
    btn.disabled = !enabled;
    if (enabled && onClick) {
        btn.addEventListener('click', onClick);
    }
    return btn;
}

// Create pagination ellipsis
function createPaginationEllipsis() {
    const span = document.createElement('span');
    span.textContent = '...';
    span.className = 'px-2 text-gray-500';
    return span;
}

// Open branch modal (add or edit)
function openBranchModal(branch = null) {
    const modal = document.getElementById('branch-modal');
    const form = document.getElementById('branch-form');
    const title = document.getElementById('modal-title');

    isEditMode = branch !== null;
    currentBranchId = branch ? branch.branch_id : null;

    if (isEditMode) {
        title.textContent = 'Edit Branch';
        document.getElementById('branch-id').value = branch.branch_id;
        document.getElementById('branch-id-input').value = branch.branch_id;
        document.getElementById('branch-id-input').disabled = true;
        document.getElementById('branch-name').value = branch.branch_name || '';
        document.getElementById('address').value = branch.address || '';
        document.getElementById('province').value = branch.province || '';
        document.getElementById('district').value = branch.district || '';
        document.getElementById('postal-code').value = branch.postal_code || '';
        document.getElementById('phone').value = branch.phone || '';
        document.getElementById('dc-code').value = branch.dc_code || '';
        document.getElementById('status').value = branch.status || 'active';
        document.getElementById('opening-date').value = branch.opening_date || '';
    } else {
        title.textContent = 'Add New Branch';
        form.reset();
        document.getElementById('branch-id-input').disabled = false;
    }

    modal.classList.remove('hidden');
}

// Close branch modal
function closeBranchModal() {
    const modal = document.getElementById('branch-modal');
    modal.classList.add('hidden');
    isEditMode = false;
    currentBranchId = null;
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    showLoading(true);

    try {
        const formData = {
            branch_id: document.getElementById('branch-id-input').value.trim(),
            branch_name: document.getElementById('branch-name').value.trim(),
            address: document.getElementById('address').value.trim() || null,
            province: document.getElementById('province').value.trim() || null,
            district: document.getElementById('district').value.trim() || null,
            postal_code: document.getElementById('postal-code').value.trim() || null,
            phone: document.getElementById('phone').value.trim() || null,
            dc_code: document.getElementById('dc-code').value.trim() || null,
            status: document.getElementById('status').value,
            opening_date: document.getElementById('opening-date').value || null
        };

        const url = isEditMode ? `/api/branches/${currentBranchId}` : '/api/branches';
        const method = isEditMode ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save branch');
        }

        showNotification(isEditMode ? 'Branch updated successfully' : 'Branch created successfully', 'success');
        closeBranchModal();
        loadBranchStats();
        loadBranches();

    } catch (error) {
        console.error('Error saving branch:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// View branch details
async function viewBranch(branchId) {
    showLoading(true);

    try {
        const response = await fetch(`/api/branches/${branchId}`);
        if (!response.ok) throw new Error('Failed to load branch details');

        const branch = await response.json();

        // For now, just show in alert (later can create a detail modal)
        alert(`Branch Details:\n\nID: ${branch.branch_id}\nName: ${branch.branch_name}\nProvince: ${branch.province || '-'}\nStatus: ${branch.status}\nDocuments: ${branch.document_count || 0}\nPPP09: ${branch.has_ppp09 ? 'Yes' : 'No'}`);

    } catch (error) {
        console.error('Error loading branch:', error);
        showNotification('Failed to load branch details', 'error');
    } finally {
        showLoading(false);
    }
}

// Edit branch
async function editBranch(branchId) {
    showLoading(true);

    try {
        const response = await fetch(`/api/branches/${branchId}`);
        if (!response.ok) throw new Error('Failed to load branch');

        const branch = await response.json();
        openBranchModal(branch);

    } catch (error) {
        console.error('Error loading branch:', error);
        showNotification('Failed to load branch for editing', 'error');
    } finally {
        showLoading(false);
    }
}

// Delete branch
async function deleteBranch(branchId, branchName) {
    if (!confirm(`Are you sure you want to delete branch "${branchName}"?\n\nThis action cannot be undone.`)) {
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`/api/branches/${branchId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete branch');
        }

        showNotification('Branch deleted successfully', 'success');
        loadBranchStats();
        loadBranches();

    } catch (error) {
        console.error('Error deleting branch:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Utility Functions

function getStatusBadge(status) {
    const badges = {
        'active': '<span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">Active</span>',
        'opening': '<span class="px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800">Opening</span>',
        'closed': '<span class="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">Closed</span>'
    };
    return badges[status] || status;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading(show) {
    const loadingState = document.getElementById('loading-state');
    if (show) {
        loadingState.classList.remove('hidden');
    } else {
        loadingState.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    // Simple notification (can be enhanced with toast library)
    const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';

    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
