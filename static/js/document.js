/**
 * Document Management JavaScript (Shared by SRD and SCM teams)
 * Handles document upload, download, and management operations
 */

// Get team context from window
const TEAM = window.TEAM_NAME || 'srd'; // Default to srd
const TEAM_COLOR = window.TEAM_COLOR || 'orange';

let currentPage = 1;
let currentFilters = {
    search: '',
    branch_id: '',
    document_type: '',
    team: TEAM,
    sort: 'uploaded_at',
    order: 'desc'
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDocumentStats();
    loadDocuments();
    initializeEventListeners();
});

// Event Listeners
function initializeEventListeners() {
    // Upload button
    document.getElementById('btn-upload-document').addEventListener('click', () => {
        openUploadModal();
    });

    // Close modal buttons
    document.getElementById('btn-close-modal').addEventListener('click', closeUploadModal);
    document.getElementById('btn-cancel').addEventListener('click', closeUploadModal);

    // Form submission
    document.getElementById('upload-form').addEventListener('submit', handleUpload);

    // Search input (debounced)
    let searchTimeout;
    document.getElementById('search').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentFilters.search = e.target.value;
            currentPage = 1;
            loadDocuments();
        }, 300);
    });

    // Filter changes
    document.getElementById('filter-branch').addEventListener('input', (e) => {
        currentFilters.branch_id = e.target.value;
        currentPage = 1;
        loadDocuments();
    });

    document.getElementById('filter-type').addEventListener('change', (e) => {
        currentFilters.document_type = e.target.value;
        currentPage = 1;
        loadDocuments();
    });

    // Clear filters
    document.getElementById('btn-clear-filters').addEventListener('click', () => {
        document.getElementById('search').value = '';
        document.getElementById('filter-branch').value = '';
        document.getElementById('filter-type').value = '';
        currentFilters = { search: '', branch_id: '', document_type: '', team: TEAM, sort: 'uploaded_at', order: 'desc' };
        currentPage = 1;
        loadDocuments();
    });

    // Close modal on outside click
    document.getElementById('upload-modal').addEventListener('click', (e) => {
        if (e.target.id === 'upload-modal') {
            closeUploadModal();
        }
    });
}

// Load document statistics
async function loadDocumentStats() {
    try {
        // Load all documents for this team to calculate stats
        const params = new URLSearchParams({
            team: TEAM,
            limit: 1000 // Get all for stats calculation
        });

        const response = await fetch(`/api/documents?${params}`);
        if (!response.ok) throw new Error('Failed to load statistics');

        const data = await response.json();
        const documents = data.data || [];

        // Calculate stats
        const total = documents.length;
        document.getElementById('stat-total').textContent = total;

        // Count by document type
        const typeCounts = {};
        documents.forEach(doc => {
            typeCounts[doc.document_type] = (typeCounts[doc.document_type] || 0) + 1;
        });

        // Update type-specific stats
        if (TEAM === 'srd') {
            document.getElementById('stat-floor-plan').textContent = typeCounts['floor_plan'] || 0;
            document.getElementById('stat-layout').textContent = typeCounts['layout'] || 0;
            document.getElementById('stat-design').textContent = typeCounts['design'] || 0;
        } else if (TEAM === 'scm') {
            document.getElementById('stat-dc-assignment').textContent = typeCounts['dc_assignment'] || 0;
            document.getElementById('stat-logistics-plan').textContent = typeCounts['logistics_plan'] || 0;
            document.getElementById('stat-inventory-plan').textContent = typeCounts['inventory_plan'] || 0;
        }

    } catch (error) {
        console.error('Error loading statistics:', error);
        showNotification('Failed to load statistics', 'error');
    }
}

// Load documents list
async function loadDocuments() {
    showLoading(true);

    try {
        const params = new URLSearchParams({
            page: currentPage,
            limit: 20,
            ...currentFilters
        });

        const response = await fetch(`/api/documents?${params}`);
        if (!response.ok) throw new Error('Failed to load documents');

        const data = await response.json();

        renderDocumentsTable(data.data);
        renderPagination(data);

    } catch (error) {
        console.error('Error loading documents:', error);
        showNotification('Failed to load documents', 'error');
    } finally {
        showLoading(false);
    }
}

// Render documents table
function renderDocumentsTable(documents) {
    const tbody = document.getElementById('documents-tbody');

    if (!documents || documents.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                    No documents found
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = documents.map(doc => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4">
                <span class="font-medium text-gray-900">${escapeHtml(doc.document_name)}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="font-medium text-${TEAM_COLOR}-600">${escapeHtml(doc.branch_id)}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getDocumentTypeBadge(doc.document_type)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                ${formatFileSize(doc.file_size)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                ${formatDate(doc.uploaded_at)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button onclick="downloadDocument('${doc.document_id}')" class="text-blue-600 hover:text-blue-800 mr-3">Download</button>
                <button onclick="deleteDocument('${doc.document_id}', '${escapeHtml(doc.document_name)}')" class="text-red-600 hover:text-red-800">Delete</button>
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

    // Previous
    const prevBtn = createPaginationButton('Previous', page > 1, () => {
        currentPage = page - 1;
        loadDocuments();
    });
    buttonsContainer.appendChild(prevBtn);

    // Pages
    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(total_pages, page + 2);

    for (let i = startPage; i <= endPage; i++) {
        const btn = createPaginationButton(i.toString(), true, () => {
            currentPage = i;
            loadDocuments();
        }, i === page);
        buttonsContainer.appendChild(btn);
    }

    // Next
    const nextBtn = createPaginationButton('Next', page < total_pages, () => {
        currentPage = page + 1;
        loadDocuments();
    });
    buttonsContainer.appendChild(nextBtn);
}

function createPaginationButton(text, enabled, onClick, isActive = false) {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = `px-4 py-2 text-sm font-medium rounded-lg ${
        isActive
            ? `bg-${TEAM_COLOR}-600 text-white`
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

// Open upload modal
function openUploadModal() {
    const modal = document.getElementById('upload-modal');
    document.getElementById('upload-form').reset();
    modal.classList.remove('hidden');
}

// Close upload modal
function closeUploadModal() {
    document.getElementById('upload-modal').classList.add('hidden');
}

// Handle file upload
async function handleUpload(e) {
    e.preventDefault();
    showLoading(true);

    try {
        const branchId = document.getElementById('branch-id').value.trim();
        const documentType = document.getElementById('document-type').value;
        const documentName = document.getElementById('document-name').value.trim();
        const fileInput = document.getElementById('file');
        const file = fileInput.files[0];

        if (!file) throw new Error('Please select a file');

        // Validate file size (50MB)
        if (file.size > 50 * 1024 * 1024) {
            throw new Error('File size exceeds 50MB limit');
        }

        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        formData.append('branch_id', branchId);
        formData.append('document_type', documentType);
        formData.append('document_name', documentName);
        formData.append('team', TEAM);

        const response = await fetch('/api/documents/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to upload document');
        }

        showNotification('Document uploaded successfully', 'success');
        closeUploadModal();
        loadDocumentStats();
        loadDocuments();

    } catch (error) {
        console.error('Error uploading document:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Download document
async function downloadDocument(documentId) {
    try {
        window.location.href = `/api/documents/${documentId}/download`;
    } catch (error) {
        console.error('Error downloading document:', error);
        showNotification('Failed to download document', 'error');
    }
}

// Delete document
async function deleteDocument(documentId, documentName) {
    if (!confirm(`Are you sure you want to delete "${documentName}"?\n\nThis will permanently delete the file from storage.\nThis action cannot be undone.`)) {
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`/api/documents/${documentId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete document');
        }

        showNotification('Document deleted successfully', 'success');
        loadDocumentStats();
        loadDocuments();

    } catch (error) {
        console.error('Error deleting document:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Utility Functions

function getDocumentTypeBadge(type) {
    const typeLabels = {
        // SRD types
        'floor_plan': 'Floor Plan',
        'layout': 'Layout',
        'design': 'Design',
        'rendering': 'Rendering',
        'specification': 'Specification',
        // SCM types
        'dc_assignment': 'DC Assignment',
        'logistics_plan': 'Logistics Plan',
        'inventory_plan': 'Inventory Plan',
        'supplier_info': 'Supplier Info',
        // Common
        'other': 'Other'
    };

    const label = typeLabels[type] || type;
    return `<span class="px-2 py-1 text-xs font-medium rounded-full bg-${TEAM_COLOR}-100 text-${TEAM_COLOR}-800">${label}</span>`;
}

function formatFileSize(bytes) {
    if (!bytes) return '-';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
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
    const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';

    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
