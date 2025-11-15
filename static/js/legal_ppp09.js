/**
 * Legal Team - PPP09 (ภ.พ.09) Management JavaScript
 * Handles ภ.พ.09 CRUD operations, PDF upload/download, and expiry alerts
 */

let currentPage = 1;
let currentFilters = {
    search: '',
    province: '',
    payment_status: '',
    expiring_soon: false,
    sort: 'created_at',
    order: 'desc'
};
let currentPPP09Id = null;
let isEditMode = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadPPP09List();
    initializeEventListeners();
});

// Event Listeners
function initializeEventListeners() {
    // Add PPP09 button
    document.getElementById('btn-add-ppp09').addEventListener('click', () => {
        openPPP09Modal();
    });

    // Close modal buttons
    document.getElementById('btn-close-modal').addEventListener('click', closePPP09Modal);
    document.getElementById('btn-cancel').addEventListener('click', closePPP09Modal);

    // Form submission
    document.getElementById('ppp09-form').addEventListener('submit', handleFormSubmit);

    // Search input (debounced)
    let searchTimeout;
    document.getElementById('search').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentFilters.search = e.target.value;
            currentPage = 1;
            loadPPP09List();
        }, 300);
    });

    // Filter changes
    document.getElementById('filter-province').addEventListener('change', (e) => {
        currentFilters.province = e.target.value;
        currentPage = 1;
        loadPPP09List();
    });

    document.getElementById('filter-payment').addEventListener('change', (e) => {
        currentFilters.payment_status = e.target.value;
        currentPage = 1;
        loadPPP09List();
    });

    // Expiring soon filter
    document.getElementById('btn-filter-expiring').addEventListener('click', () => {
        currentFilters.expiring_soon = !currentFilters.expiring_soon;
        document.getElementById('btn-filter-expiring').classList.toggle('bg-orange-100');
        document.getElementById('btn-filter-expiring').classList.toggle('border-orange-300');
        currentPage = 1;
        loadPPP09List();
    });

    // Clear filters
    document.getElementById('btn-clear-filters').addEventListener('click', () => {
        document.getElementById('search').value = '';
        document.getElementById('filter-province').value = '';
        document.getElementById('filter-payment').value = '';
        currentFilters = { search: '', province: '', payment_status: '', expiring_soon: false, sort: 'created_at', order: 'desc' };
        document.getElementById('btn-filter-expiring').classList.remove('bg-orange-100', 'border-orange-300');
        currentPage = 1;
        loadPPP09List();
    });

    // PDF Modal
    document.getElementById('btn-close-pdf-modal').addEventListener('click', closePDFModal);
    document.getElementById('btn-cancel-pdf').addEventListener('click', closePDFModal);
    document.getElementById('pdf-form').addEventListener('submit', handlePDFUpload);

    // Close modals on outside click
    document.getElementById('ppp09-modal').addEventListener('click', (e) => {
        if (e.target.id === 'ppp09-modal') {
            closePPP09Modal();
        }
    });

    document.getElementById('pdf-modal').addEventListener('click', (e) => {
        if (e.target.id === 'pdf-modal') {
            closePDFModal();
        }
    });
}

// Load PPP09 list
async function loadPPP09List() {
    showLoading(true);

    try {
        const params = new URLSearchParams({
            page: currentPage,
            limit: 20,
            ...currentFilters
        });

        const response = await fetch(`/api/legal/ppp09?${params}`);
        if (!response.ok) throw new Error('Failed to load ภ.พ.09 list');

        const data = await response.json();

        renderPPP09Table(data.data);
        renderPagination(data);
        checkExpiryAlerts(data.data);

    } catch (error) {
        console.error('Error loading ภ.พ.09:', error);
        showNotification('Failed to load ภ.พ.09 list', 'error');
    } finally {
        showLoading(false);
    }
}

// Render PPP09 table
function renderPPP09Table(ppp09List) {
    const tbody = document.getElementById('ppp09-tbody');

    if (!ppp09List || ppp09List.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="px-6 py-8 text-center text-gray-500">
                    No ภ.พ.09 records found
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = ppp09List.map(ppp09 => {
        const isExpiringSoon = ppp09.expiry_date && isWithinDays(ppp09.expiry_date, 90);
        const isExpired = ppp09.expiry_date && isPastDate(ppp09.expiry_date);

        return `
        <tr class="hover:bg-gray-50 ${isExpired ? 'bg-red-50' : isExpiringSoon ? 'bg-orange-50' : ''}">
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="font-medium text-blue-600">${escapeHtml(ppp09.branch_id)}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${escapeHtml(ppp09.ppp09_number || '-')}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${escapeHtml(ppp09.owner_name || '-')}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                ${escapeHtml(ppp09.address_province || '-')}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                ${ppp09.expiry_date ? formatDate(ppp09.expiry_date) : '-'}
                ${isExpired ? '<span class="ml-2 text-xs text-red-600 font-medium">EXPIRED</span>' : ''}
                ${isExpiringSoon && !isExpired ? '<span class="ml-2 text-xs text-orange-600 font-medium">SOON</span>' : ''}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${ppp09.annual_tax_amount ? formatCurrency(ppp09.annual_tax_amount) : '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getPaymentStatusBadge(ppp09.payment_status)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-center">
                ${ppp09.pdf_file_path ?
                    `<button onclick="downloadPDF('${ppp09.ppp09_id}')" class="text-blue-600 hover:text-blue-800">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                    </button>`
                    : '-'
                }
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button onclick="editPPP09('${ppp09.ppp09_id}')" class="text-green-600 hover:text-green-800 mr-2">Edit</button>
                <button onclick="openPDFUploadModal('${ppp09.ppp09_id}')" class="text-purple-600 hover:text-purple-800 mr-2">PDF</button>
                <button onclick="deletePPP09('${ppp09.ppp09_id}', '${escapeHtml(ppp09.ppp09_number || ppp09.branch_id)}')" class="text-red-600 hover:text-red-800">Delete</button>
            </td>
        </tr>
    `}).join('');
}

// Check expiry alerts
function checkExpiryAlerts(ppp09List) {
    const alertsContainer = document.getElementById('expiry-alerts');
    const expiringSoon = ppp09List.filter(p => p.expiry_date && isWithinDays(p.expiry_date, 90) && !isPastDate(p.expiry_date));
    const expired = ppp09List.filter(p => p.expiry_date && isPastDate(p.expiry_date));

    let alerts = [];

    if (expired.length > 0) {
        alerts.push(`
            <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded">
                <p class="font-bold">⚠️ ${expired.length} ภ.พ.09 Expired</p>
                <p class="text-sm">There are ${expired.length} ภ.พ.09 documents that have already expired. Please renew them immediately.</p>
            </div>
        `);
    }

    if (expiringSoon.length > 0) {
        alerts.push(`
            <div class="bg-orange-100 border-l-4 border-orange-500 text-orange-700 p-4 rounded">
                <p class="font-bold">🔔 ${expiringSoon.length} ภ.พ.09 Expiring Soon</p>
                <p class="text-sm">There are ${expiringSoon.length} ภ.พ.09 documents expiring within 90 days. Consider renewing them soon.</p>
            </div>
        `);
    }

    alertsContainer.innerHTML = alerts.join('');
}

// Render pagination (same as branch)
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

    // Previous
    const prevBtn = createPaginationButton('Previous', page > 1, () => { currentPage = page - 1; loadPPP09List(); });
    buttonsContainer.appendChild(prevBtn);

    // Pages
    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(total_pages, page + 2);

    for (let i = startPage; i <= endPage; i++) {
        const btn = createPaginationButton(i.toString(), true, () => { currentPage = i; loadPPP09List(); }, i === page);
        buttonsContainer.appendChild(btn);
    }

    // Next
    const nextBtn = createPaginationButton('Next', page < total_pages, () => { currentPage = page + 1; loadPPP09List(); });
    buttonsContainer.appendChild(nextBtn);
}

function createPaginationButton(text, enabled, onClick, isActive = false) {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = `px-4 py-2 text-sm font-medium rounded-lg ${
        isActive ? 'bg-purple-600 text-white' : enabled ? 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50' : 'bg-gray-100 text-gray-400 cursor-not-allowed'
    }`;
    btn.disabled = !enabled;
    if (enabled && onClick) btn.addEventListener('click', onClick);
    return btn;
}

// Open PPP09 modal
function openPPP09Modal(ppp09 = null) {
    const modal = document.getElementById('ppp09-modal');
    const form = document.getElementById('ppp09-form');
    const title = document.getElementById('modal-title');

    isEditMode = ppp09 !== null;
    currentPPP09Id = ppp09 ? ppp09.ppp09_id : null;

    if (isEditMode) {
        title.textContent = 'Edit ภ.พ.09';
        document.getElementById('ppp09-id').value = ppp09.ppp09_id;
        document.getElementById('branch-id').value = ppp09.branch_id || '';
        document.getElementById('ppp09-number').value = ppp09.ppp09_number || '';
        document.getElementById('owner-name').value = ppp09.owner_name || '';
        document.getElementById('issue-date').value = ppp09.issue_date || '';
        document.getElementById('expiry-date').value = ppp09.expiry_date || '';
        document.getElementById('address-number').value = ppp09.address_number || '';
        document.getElementById('address-moo').value = ppp09.address_moo || '';
        document.getElementById('address-trok').value = ppp09.address_trok || '';
        document.getElementById('address-soi').value = ppp09.address_soi || '';
        document.getElementById('address-road').value = ppp09.address_road || '';
        document.getElementById('address-tambon').value = ppp09.address_tambon || '';
        document.getElementById('address-amphoe').value = ppp09.address_amphoe || '';
        document.getElementById('address-province').value = ppp09.address_province || '';
        document.getElementById('address-postal').value = ppp09.address_postal_code || '';
        document.getElementById('land-rai').value = ppp09.land_area_rai || '';
        document.getElementById('land-ngan').value = ppp09.land_area_ngan || '';
        document.getElementById('land-wa').value = ppp09.land_area_wa || '';
        document.getElementById('building-area').value = ppp09.building_area_sqm || '';
        document.getElementById('annual-tax').value = ppp09.annual_tax_amount || '';
        document.getElementById('payment-status').value = ppp09.payment_status || '';
        document.getElementById('remarks').value = ppp09.remarks || '';
    } else {
        title.textContent = 'Add New ภ.พ.09';
        form.reset();
    }

    modal.classList.remove('hidden');
}

// Close PPP09 modal
function closePPP09Modal() {
    document.getElementById('ppp09-modal').classList.add('hidden');
    isEditMode = false;
    currentPPP09Id = null;
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    showLoading(true);

    try {
        const formData = {
            branch_id: document.getElementById('branch-id').value.trim(),
            ppp09_number: document.getElementById('ppp09-number').value.trim() || null,
            issue_date: document.getElementById('issue-date').value || null,
            expiry_date: document.getElementById('expiry-date').value || null,
            owner_name: document.getElementById('owner-name').value.trim() || null,
            address_number: document.getElementById('address-number').value.trim() || null,
            address_moo: document.getElementById('address-moo').value.trim() || null,
            address_trok: document.getElementById('address-trok').value.trim() || null,
            address_soi: document.getElementById('address-soi').value.trim() || null,
            address_road: document.getElementById('address-road').value.trim() || null,
            address_tambon: document.getElementById('address-tambon').value.trim() || null,
            address_amphoe: document.getElementById('address-amphoe').value.trim() || null,
            address_province: document.getElementById('address-province').value.trim() || null,
            address_postal_code: document.getElementById('address-postal').value.trim() || null,
            land_area_rai: parseFloatOrNull(document.getElementById('land-rai').value),
            land_area_ngan: parseFloatOrNull(document.getElementById('land-ngan').value),
            land_area_wa: parseFloatOrNull(document.getElementById('land-wa').value),
            building_area_sqm: parseFloatOrNull(document.getElementById('building-area').value),
            annual_tax_amount: parseFloatOrNull(document.getElementById('annual-tax').value),
            payment_status: document.getElementById('payment-status').value || null,
            remarks: document.getElementById('remarks').value.trim() || null
        };

        const url = isEditMode ? `/api/legal/ppp09/${currentPPP09Id}` : '/api/legal/ppp09';
        const method = isEditMode ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save ภ.พ.09');
        }

        showNotification(isEditMode ? 'ภ.พ.09 updated successfully' : 'ภ.พ.09 created successfully', 'success');
        closePPP09Modal();
        loadPPP09List();

    } catch (error) {
        console.error('Error saving ภ.พ.09:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Edit PPP09
async function editPPP09(ppp09Id) {
    showLoading(true);

    try {
        const response = await fetch(`/api/legal/ppp09/${ppp09Id}`);
        if (!response.ok) throw new Error('Failed to load ภ.พ.09');

        const ppp09 = await response.json();
        openPPP09Modal(ppp09);

    } catch (error) {
        console.error('Error loading ภ.พ.09:', error);
        showNotification('Failed to load ภ.พ.09 for editing', 'error');
    } finally {
        showLoading(false);
    }
}

// Delete PPP09
async function deletePPP09(ppp09Id, identifier) {
    if (!confirm(`Are you sure you want to delete ภ.พ.09 "${identifier}"?\n\nThis will also delete any associated PDF file.\nThis action cannot be undone.`)) {
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`/api/legal/ppp09/${ppp09Id}`, { method: 'DELETE' });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete ภ.พ.09');
        }

        showNotification('ภ.พ.09 deleted successfully', 'success');
        loadPPP09List();

    } catch (error) {
        console.error('Error deleting ภ.พ.09:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// PDF Upload Modal
function openPDFUploadModal(ppp09Id) {
    document.getElementById('pdf-ppp09-id').value = ppp09Id;
    document.getElementById('pdf-file').value = '';
    document.getElementById('pdf-modal').classList.remove('hidden');
}

function closePDFModal() {
    document.getElementById('pdf-modal').classList.add('hidden');
}

// Handle PDF Upload
async function handlePDFUpload(e) {
    e.preventDefault();
    showLoading(true);

    try {
        const ppp09Id = document.getElementById('pdf-ppp09-id').value;
        const fileInput = document.getElementById('pdf-file');
        const file = fileInput.files[0];

        if (!file) throw new Error('Please select a PDF file');

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            throw new Error('PDF file size exceeds 10MB limit');
        }

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`/api/legal/ppp09/${ppp09Id}/upload-pdf`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to upload PDF');
        }

        showNotification('PDF uploaded successfully', 'success');
        closePDFModal();
        loadPPP09List();

    } catch (error) {
        console.error('Error uploading PDF:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Download PDF
async function downloadPDF(ppp09Id) {
    try {
        window.location.href = `/api/legal/ppp09/${ppp09Id}/download-pdf`;
    } catch (error) {
        console.error('Error downloading PDF:', error);
        showNotification('Failed to download PDF', 'error');
    }
}

// Utility Functions

function getPaymentStatusBadge(status) {
    const badges = {
        'paid': '<span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">Paid</span>',
        'unpaid': '<span class="px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800">Unpaid</span>',
        'overdue': '<span class="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">Overdue</span>'
    };
    return badges[status] || '-';
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('th-TH', { style: 'currency', currency: 'THB' }).format(amount);
}

function parseFloatOrNull(value) {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? null : parsed;
}

function isWithinDays(dateString, days) {
    const targetDate = new Date(dateString);
    const today = new Date();
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= days;
}

function isPastDate(dateString) {
    const targetDate = new Date(dateString);
    const today = new Date();
    return targetDate < today;
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
    const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';

    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
