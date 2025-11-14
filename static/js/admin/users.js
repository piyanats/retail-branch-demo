/**
 * Admin User Management
 *
 * Handles all user management functionality including:
 * - User list with pagination and filtering
 * - Create/Edit/Deactivate users
 * - Manage user teams
 */

// State management
const state = {
    currentPage: 1,
    limit: 20,
    filters: {
        search: '',
        user_level: '',
        status: ''
    },
    users: [],
    totalPages: 0,
    totalUsers: 0,
    currentUserId: null
};

// Team name mapping
const TEAM_NAMES = {
    'new_branch': 'New Branch',
    'legal': 'Legal',
    'srd': 'SRD',
    'scm': 'SCM'
};

const TEAM_COLORS = {
    'new_branch': 'bg-blue-100 text-blue-800',
    'legal': 'bg-purple-100 text-purple-800',
    'srd': 'bg-orange-100 text-orange-800',
    'scm': 'bg-green-100 text-green-800'
};

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadUsers();
});

function initializeEventListeners() {
    // Add user button
    document.getElementById('btn-add-user').addEventListener('click', showAddUserModal);
    document.getElementById('btn-cancel-add-user').addEventListener('click', hideAddUserModal);
    document.getElementById('form-add-user').addEventListener('submit', handleAddUser);

    // Edit user
    document.getElementById('btn-cancel-edit-user').addEventListener('click', hideEditUserModal);
    document.getElementById('form-edit-user').addEventListener('submit', handleEditUser);

    // Manage teams
    document.getElementById('btn-close-manage-teams').addEventListener('click', hideManageTeamsModal);
    document.getElementById('form-add-team').addEventListener('submit', handleAddTeam);

    // Deactivate
    document.getElementById('btn-cancel-deactivate').addEventListener('click', hideDeactivateModal);
    document.getElementById('btn-confirm-deactivate').addEventListener('click', handleDeactivateUser);

    // Filters
    document.getElementById('btn-apply-filters').addEventListener('click', applyFilters);
    document.getElementById('btn-reset-filters').addEventListener('click', resetFilters);

    // Search on Enter
    document.getElementById('filter-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            applyFilters();
        }
    });
}

// ============================================================================
// Load Users
// ============================================================================

async function loadUsers() {
    showLoading();

    try {
        const params = new URLSearchParams({
            page: state.currentPage,
            limit: state.limit,
            ...(state.filters.search && { search: state.filters.search }),
            ...(state.filters.user_level && { user_level: state.filters.user_level }),
            ...(state.filters.status && { status: state.filters.status })
        });

        const response = await API.get(`/admin/users?${params}`);

        state.users = response.data;
        state.totalPages = response.total_pages;
        state.totalUsers = response.total;

        renderUsers();
        renderPagination();
        hideLoading();

    } catch (error) {
        console.error('Failed to load users:', error);
        Toast.error('Failed to load users: ' + error.message);
        hideLoading();
        showEmptyState();
    }
}

function renderUsers() {
    const tbody = document.getElementById('users-table-body');

    if (state.users.length === 0) {
        showEmptyState();
        return;
    }

    tbody.innerHTML = state.users.map(user => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${escapeHtml(user.email)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${escapeHtml(user.name)}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${renderUserLevelBadge(user.user_level)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${user.team_count > 0
                    ? `<button onclick="showManageTeamsModal('${user.user_id}')" class="text-sm text-blue-600 hover:text-blue-800">${user.team_count} team(s)</button>`
                    : '<span class="text-sm text-gray-500">No teams</span>'
                }
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${renderStatusBadge(user.is_active)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${user.last_login ? formatDateTime(user.last_login) : 'Never'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                    <button onclick="showEditUserModal('${user.user_id}')" class="text-blue-600 hover:text-blue-900" title="Edit">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        </svg>
                    </button>
                    <button onclick="showManageTeamsModal('${user.user_id}')" class="text-purple-600 hover:text-purple-900" title="Manage Teams">
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
                        </svg>
                    </button>
                    ${user.is_active
                        ? `<button onclick="showDeactivateModal('${user.user_id}', '${escapeHtml(user.name)}')" class="text-red-600 hover:text-red-900" title="Deactivate">
                            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>
                            </svg>
                        </button>`
                        : `<button onclick="handleActivateUser('${user.user_id}')" class="text-green-600 hover:text-green-900" title="Activate">
                            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </button>`
                    }
                </div>
            </td>
        </tr>
    `).join('');

    document.getElementById('users-table-container').classList.remove('hidden');
    document.getElementById('empty-state').classList.add('hidden');
}

function renderPagination() {
    const container = document.getElementById('pagination-container');

    if (state.totalPages === 0) {
        container.classList.add('hidden');
        return;
    }

    container.classList.remove('hidden');

    // Update info text
    const start = (state.currentPage - 1) * state.limit + 1;
    const end = Math.min(state.currentPage * state.limit, state.totalUsers);
    document.getElementById('page-start').textContent = start;
    document.getElementById('page-end').textContent = end;
    document.getElementById('total-users').textContent = state.totalUsers;

    // Render pagination buttons
    const buttonsHtml = [];

    // Previous button
    buttonsHtml.push(`
        <button onclick="changePage(${state.currentPage - 1})" ${state.currentPage === 1 ? 'disabled' : ''}
            class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${state.currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}">
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
        </button>
    `);

    // Page numbers (show max 7 pages)
    const maxPages = 7;
    let startPage = Math.max(1, state.currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(state.totalPages, startPage + maxPages - 1);

    if (endPage - startPage < maxPages - 1) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }

    if (startPage > 1) {
        buttonsHtml.push(renderPageButton(1));
        if (startPage > 2) {
            buttonsHtml.push('<span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">...</span>');
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        buttonsHtml.push(renderPageButton(i));
    }

    if (endPage < state.totalPages) {
        if (endPage < state.totalPages - 1) {
            buttonsHtml.push('<span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">...</span>');
        }
        buttonsHtml.push(renderPageButton(state.totalPages));
    }

    // Next button
    buttonsHtml.push(`
        <button onclick="changePage(${state.currentPage + 1})" ${state.currentPage === state.totalPages ? 'disabled' : ''}
            class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${state.currentPage === state.totalPages ? 'opacity-50 cursor-not-allowed' : ''}">
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
            </svg>
        </button>
    `);

    document.getElementById('pagination-buttons').innerHTML = buttonsHtml.join('');
}

function renderPageButton(page) {
    const isActive = page === state.currentPage;
    return `
        <button onclick="changePage(${page})"
            class="${isActive
                ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
            } relative inline-flex items-center px-4 py-2 border text-sm font-medium">
            ${page}
        </button>
    `;
}

function changePage(page) {
    if (page < 1 || page > state.totalPages || page === state.currentPage) {
        return;
    }
    state.currentPage = page;
    loadUsers();
}

// ============================================================================
// Filters
// ============================================================================

function applyFilters() {
    state.filters.search = document.getElementById('filter-search').value.trim();
    state.filters.user_level = document.getElementById('filter-user-level').value;
    state.filters.status = document.getElementById('filter-status').value;
    state.currentPage = 1; // Reset to first page
    loadUsers();
}

function resetFilters() {
    document.getElementById('filter-search').value = '';
    document.getElementById('filter-user-level').value = '';
    document.getElementById('filter-status').value = '';
    state.filters = { search: '', user_level: '', status: '' };
    state.currentPage = 1;
    loadUsers();
}

// ============================================================================
// Add User
// ============================================================================

function showAddUserModal() {
    document.getElementById('form-add-user').reset();
    document.getElementById('modal-add-user').classList.remove('hidden');
}

function hideAddUserModal() {
    document.getElementById('modal-add-user').classList.add('hidden');
}

async function handleAddUser(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const userData = {
        email: formData.get('email'),
        name: formData.get('name'),
        user_level: formData.get('user_level')
    };

    try {
        await API.post('/admin/users', userData);
        Toast.success('User created successfully');
        hideAddUserModal();
        loadUsers();
    } catch (error) {
        console.error('Failed to create user:', error);
        Toast.error('Failed to create user: ' + error.message);
    }
}

// ============================================================================
// Edit User
// ============================================================================

async function showEditUserModal(userId) {
    try {
        const user = await API.get(`/admin/users/${userId}`);

        document.getElementById('edit-user-id').value = user.user_id;
        document.getElementById('edit-email').value = user.email;
        document.getElementById('edit-name').value = user.name;
        document.getElementById('edit-user-level').value = user.user_level;

        document.getElementById('modal-edit-user').classList.remove('hidden');
    } catch (error) {
        console.error('Failed to load user:', error);
        Toast.error('Failed to load user details');
    }
}

function hideEditUserModal() {
    document.getElementById('modal-edit-user').classList.add('hidden');
}

async function handleEditUser(e) {
    e.preventDefault();

    const userId = document.getElementById('edit-user-id').value;
    const formData = new FormData(e.target);
    const userData = {
        name: formData.get('name'),
        user_level: formData.get('user_level')
    };

    try {
        await API.put(`/admin/users/${userId}`, userData);
        Toast.success('User updated successfully');
        hideEditUserModal();
        loadUsers();
    } catch (error) {
        console.error('Failed to update user:', error);
        Toast.error('Failed to update user: ' + error.message);
    }
}

// ============================================================================
// Deactivate/Activate User
// ============================================================================

function showDeactivateModal(userId, userName) {
    state.currentUserId = userId;
    document.getElementById('deactivate-user-name').textContent = userName;
    document.getElementById('modal-confirm-deactivate').classList.remove('hidden');
}

function hideDeactivateModal() {
    document.getElementById('modal-confirm-deactivate').classList.add('hidden');
    state.currentUserId = null;
}

async function handleDeactivateUser() {
    if (!state.currentUserId) return;

    try {
        await API.post(`/admin/users/${state.currentUserId}/deactivate`);
        Toast.success('User deactivated successfully');
        hideDeactivateModal();
        loadUsers();
    } catch (error) {
        console.error('Failed to deactivate user:', error);
        Toast.error('Failed to deactivate user: ' + error.message);
    }
}

async function handleActivateUser(userId) {
    if (!confirm('Are you sure you want to activate this user?')) {
        return;
    }

    try {
        await API.post(`/admin/users/${userId}/activate`);
        Toast.success('User activated successfully');
        loadUsers();
    } catch (error) {
        console.error('Failed to activate user:', error);
        Toast.error('Failed to activate user: ' + error.message);
    }
}

// ============================================================================
// Manage Teams
// ============================================================================

async function showManageTeamsModal(userId) {
    state.currentUserId = userId;
    document.getElementById('manage-teams-user-id').value = userId;

    try {
        const response = await API.get(`/admin/users/${userId}/teams`);
        renderTeamsList(response.teams);
        document.getElementById('modal-manage-teams').classList.remove('hidden');
    } catch (error) {
        console.error('Failed to load user teams:', error);
        Toast.error('Failed to load user teams');
    }
}

function hideManageTeamsModal() {
    document.getElementById('modal-manage-teams').classList.add('hidden');
    state.currentUserId = null;
    loadUsers(); // Refresh to update team counts
}

function renderTeamsList(teams) {
    const container = document.getElementById('current-teams-list');

    if (teams.length === 0) {
        container.innerHTML = '<p class="text-sm text-gray-500">No teams assigned</p>';
        return;
    }

    container.innerHTML = teams.map(team => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
            <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${TEAM_COLORS[team.team_name]}">
                    ${TEAM_NAMES[team.team_name]}
                </span>
                <select onchange="handleUpdateTeamRole('${team.user_team_id}', this.value)"
                    class="text-sm rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                    <option value="viewer" ${team.role === 'viewer' ? 'selected' : ''}>Viewer</option>
                    <option value="editor" ${team.role === 'editor' ? 'selected' : ''}>Editor</option>
                    <option value="manager" ${team.role === 'manager' ? 'selected' : ''}>Manager</option>
                </select>
            </div>
            <button onclick="handleRemoveFromTeam('${team.user_team_id}')"
                class="text-red-600 hover:text-red-800">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
        </div>
    `).join('');
}

async function handleAddTeam(e) {
    e.preventDefault();

    const userId = document.getElementById('manage-teams-user-id').value;
    const teamName = document.getElementById('add-team-name').value;
    const role = document.getElementById('add-team-role').value;

    try {
        await API.post(`/admin/users/${userId}/teams?team_name=${teamName}&role=${role}`);
        Toast.success('Team added successfully');
        e.target.reset();

        // Refresh teams list
        const response = await API.get(`/admin/users/${userId}/teams`);
        renderTeamsList(response.teams);
    } catch (error) {
        console.error('Failed to add team:', error);
        Toast.error('Failed to add team: ' + error.message);
    }
}

async function handleUpdateTeamRole(userTeamId, newRole) {
    try {
        await API.put(`/admin/teams/${userTeamId}?role=${newRole}`);
        Toast.success('Team role updated successfully');
    } catch (error) {
        console.error('Failed to update team role:', error);
        Toast.error('Failed to update team role: ' + error.message);

        // Refresh the teams list to revert the change
        const userId = document.getElementById('manage-teams-user-id').value;
        const response = await API.get(`/admin/users/${userId}/teams`);
        renderTeamsList(response.teams);
    }
}

async function handleRemoveFromTeam(userTeamId) {
    if (!confirm('Are you sure you want to remove this team access?')) {
        return;
    }

    try {
        await API.delete(`/admin/teams/${userTeamId}`);
        Toast.success('Team access removed successfully');

        // Refresh teams list
        const userId = document.getElementById('manage-teams-user-id').value;
        const response = await API.get(`/admin/users/${userId}/teams`);
        renderTeamsList(response.teams);
    } catch (error) {
        console.error('Failed to remove team:', error);
        Toast.error('Failed to remove team: ' + error.message);
    }
}

// ============================================================================
// UI Helpers
// ============================================================================

function renderUserLevelBadge(level) {
    const colors = {
        'admin': 'bg-red-100 text-red-800',
        'manager': 'bg-yellow-100 text-yellow-800',
        'editor': 'bg-blue-100 text-blue-800',
        'viewer': 'bg-gray-100 text-gray-800'
    };

    return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colors[level]}">${level}</span>`;
}

function renderStatusBadge(isActive) {
    if (isActive) {
        return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>';
    } else {
        return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">Inactive</span>';
    }
}

function showLoading() {
    document.getElementById('loading-state').classList.remove('hidden');
    document.getElementById('users-table-container').classList.add('hidden');
    document.getElementById('empty-state').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading-state').classList.add('hidden');
}

function showEmptyState() {
    document.getElementById('empty-state').classList.remove('hidden');
    document.getElementById('users-table-container').classList.add('hidden');
    document.getElementById('pagination-container').classList.add('hidden');
}

function formatDateTime(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString('th-TH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
