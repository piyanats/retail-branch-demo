# HTML Template Structure

## Overview

ระบบใช้ **Jinja2** template engine สำหรับ server-side rendering โดยมี base template และ template inheritance pattern เพื่อความสม่ำเสมอและ maintainability

## Template Directory Structure

```
app/templates/
├── base.html                      # Base template
├── components/                    # Reusable components
│   ├── navbar.html
│   ├── sidebar.html
│   ├── modal.html
│   ├── toast.html
│   ├── pagination.html
│   ├── table.html
│   └── form_field.html
├── layouts/
│   ├── app_layout.html           # Main app layout (with sidebar)
│   └── auth_layout.html          # Auth layout (login/register)
├── pages/
│   ├── dashboard.html
│   ├── admin/
│   │   ├── users.html
│   │   ├── permissions.html
│   │   └── audit_logs.html
│   ├── auth/
│   │   ├── login.html
│   │   └── unauthorized.html
│   ├── legal/
│   │   ├── ppp09_list.html
│   │   ├── ppp09_form.html
│   │   ├── ppp20_list.html
│   │   └── ppp20_form.html
│   ├── new_branch/
│   │   ├── list.html
│   │   └── form.html
│   ├── srd/
│   │   ├── layout_list.html
│   │   └── layout_form.html
│   └── scm/
│       ├── dc_list.html
│       └── dc_form.html
└── errors/
    ├── 404.html
    ├── 403.html
    └── 500.html
```

## Base Template (base.html)

```html
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">

    <title>{% block title %}Retail Branch Management System{% endblock %}</title>

    <!-- Tailwind CSS -->
    <link rel="stylesheet" href="{{ url_for('static', path='/css/output.css') }}">

    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', path='/favicon.ico') }}">

    <!-- Additional head content -->
    {% block head %}{% endblock %}
</head>
<body class="bg-gray-50">
    <!-- Main content -->
    {% block body %}{% endblock %}

    <!-- Toast container -->
    <div id="toast-container" class="fixed top-4 right-4 z-50"></div>

    <!-- JavaScript -->
    <script src="{{ url_for('static', path='/js/utils/api.js') }}"></script>
    <script src="{{ url_for('static', path='/js/utils/validation.js') }}"></script>
    <script src="{{ url_for('static', path='/js/components/toast.js') }}"></script>
    <script src="{{ url_for('static', path='/js/components/modal.js') }}"></script>

    <!-- Page-specific scripts -->
    {% block scripts %}{% endblock %}
</body>
</html>
```

## App Layout (layouts/app_layout.html)

```html
{% extends "base.html" %}

{% block body %}
<div class="min-h-screen flex">
    <!-- Sidebar -->
    {% include "components/sidebar.html" %}

    <!-- Main content area -->
    <div class="flex-1 flex flex-col">
        <!-- Top navbar -->
        {% include "components/navbar.html" %}

        <!-- Page content -->
        <main class="flex-1 overflow-y-auto p-6">
            <div class="max-w-7xl mx-auto">
                <!-- Page header -->
                {% block page_header %}{% endblock %}

                <!-- Page content -->
                {% block content %}{% endblock %}
            </div>
        </main>
    </div>
</div>
{% endblock %}
```

## Navbar Component (components/navbar.html)

```html
<nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="px-6 py-4">
        <div class="flex items-center justify-between">
            <!-- Page title / breadcrumb -->
            <div>
                <h1 class="text-2xl font-semibold text-gray-900">
                    {% block nav_title %}Dashboard{% endblock %}
                </h1>
                {% block breadcrumb %}{% endblock %}
            </div>

            <!-- User menu -->
            <div class="flex items-center space-x-4">
                <!-- Notifications (optional) -->
                <button class="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                </button>

                <!-- User avatar and dropdown -->
                <div class="relative" x-data="{ open: false }">
                    <button
                        @click="open = !open"
                        class="flex items-center space-x-3 focus:outline-none"
                    >
                        <div class="text-right">
                            <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
                            <div class="text-xs text-gray-500">{{ user.email }}</div>
                        </div>
                        <div class="h-10 w-10 rounded-full bg-blue-500 text-white flex items-center justify-center">
                            {{ user.name[0].upper() }}
                        </div>
                    </button>

                    <!-- Dropdown menu -->
                    <div
                        x-show="open"
                        @click.away="open = false"
                        class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-10"
                    >
                        <a href="/profile" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                            Profile
                        </a>
                        <a href="/settings" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                            Settings
                        </a>
                        <hr class="my-2">
                        <form action="/auth/logout" method="POST">
                            <button type="submit" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100">
                                Logout
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</nav>
```

## Sidebar Component (components/sidebar.html)

```html
<aside class="w-64 bg-white border-r border-gray-200">
    <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="px-6 py-6 border-b border-gray-200">
            <h2 class="text-xl font-bold text-gray-900">Retail Branch</h2>
            <p class="text-sm text-gray-500">Management System</p>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            <!-- Dashboard -->
            <a href="/dashboard" class="{{ 'bg-blue-50 text-blue-700' if active_page == 'dashboard' else 'text-gray-700 hover:bg-gray-50' }} flex items-center px-4 py-3 text-sm font-medium rounded-lg">
                <svg class="h-5 w-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Dashboard
            </a>

            <!-- Admin Section (only for admin) -->
            {% if user.user_level == 'admin' %}
            <div class="pt-4">
                <p class="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Admin
                </p>
                <a href="/admin/users" class="{{ 'bg-blue-50 text-blue-700' if active_page == 'admin_users' else 'text-gray-700 hover:bg-gray-50' }} flex items-center px-4 py-3 text-sm font-medium rounded-lg mt-2">
                    <svg class="h-5 w-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                    Users
                </a>
                <a href="/admin/permissions" class="{{ 'bg-blue-50 text-blue-700' if active_page == 'admin_permissions' else 'text-gray-700 hover:bg-gray-50' }} flex items-center px-4 py-3 text-sm font-medium rounded-lg">
                    <svg class="h-5 w-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    Permissions
                </a>
                <a href="/admin/audit-logs" class="{{ 'bg-blue-50 text-blue-700' if active_page == 'admin_audit_logs' else 'text-gray-700 hover:bg-gray-50' }} flex items-center px-4 py-3 text-sm font-medium rounded-lg">
                    <svg class="h-5 w-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Audit Logs
                </a>
            </div>
            {% endif %}

            <!-- Teams Section -->
            <div class="pt-4">
                <p class="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Teams
                </p>

                <!-- New Branch Team -->
                {% if 'new_branch' in user.teams %}
                <a href="/new-branch" class="{{ 'bg-blue-50 text-blue-700' if active_page == 'new_branch' else 'text-gray-700 hover:bg-gray-50' }} flex items-center px-4 py-3 text-sm font-medium rounded-lg mt-2">
                    <svg class="h-5 w-5 mr-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    New Branch
                </a>
                {% endif %}

                <!-- Legal Team -->
                {% if 'legal' in user.teams %}
                <a href="/legal" class="{{ 'bg-purple-50 text-purple-700' if active_page == 'legal' else 'text-gray-700 hover:bg-gray-50' }} flex items-center px-4 py-3 text-sm font-medium rounded-lg mt-2">
                    <svg class="h-5 w-5 mr-3 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                    </svg>
                    Legal
                </a>
                {% endif %}

                <!-- SRD Team -->
                {% if 'srd' in user.teams %}
                <a href="/srd" class="{{ 'bg-orange-50 text-orange-700' if active_page == 'srd' else 'text-gray-700 hover:bg-gray-50' }} flex items-center px-4 py-3 text-sm font-medium rounded-lg mt-2">
                    <svg class="h-5 w-5 mr-3 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                    </svg>
                    SRD Layout
                </a>
                {% endif %}

                <!-- SCM Team -->
                {% if 'scm' in user.teams %}
                <a href="/scm" class="{{ 'bg-green-50 text-green-700' if active_page == 'scm' else 'text-gray-700 hover:bg-gray-50' }} flex items-center px-4 py-3 text-sm font-medium rounded-lg mt-2">
                    <svg class="h-5 w-5 mr-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                    SCM DC
                </a>
                {% endif %}
            </div>
        </nav>
    </div>
</aside>
```

## Modal Component (components/modal.html)

```html
{% macro modal(id, title, size='md') %}
<div id="{{ id }}" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden flex items-center justify-center z-50" data-modal>
    <div class="bg-white rounded-lg shadow-xl max-w-{{ size }} w-full mx-4 transform transition-all">
        <!-- Modal header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
            <button
                type="button"
                class="text-gray-400 hover:text-gray-600 focus:outline-none"
                data-modal-close
            >
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>

        <!-- Modal body -->
        <div class="p-6">
            {{ caller() }}
        </div>
    </div>
</div>
{% endmacro %}
```

## Form Field Component (components/form_field.html)

```html
{% macro input_field(name, label, type='text', required=False, placeholder='', value='') %}
<div class="mb-4">
    <label for="{{ name }}" class="block text-sm font-medium text-gray-700 mb-1">
        {{ label }}
        {% if required %}<span class="text-red-500">*</span>{% endif %}
    </label>
    <input
        type="{{ type }}"
        id="{{ name }}"
        name="{{ name }}"
        value="{{ value }}"
        placeholder="{{ placeholder }}"
        {% if required %}data-validate="required"{% endif %}
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
    >
    <p id="{{ name }}-error" class="mt-1 text-sm text-red-600 hidden"></p>
</div>
{% endmacro %}

{% macro select_field(name, label, options, required=False, value='') %}
<div class="mb-4">
    <label for="{{ name }}" class="block text-sm font-medium text-gray-700 mb-1">
        {{ label }}
        {% if required %}<span class="text-red-500">*</span>{% endif %}
    </label>
    <select
        id="{{ name }}"
        name="{{ name }}"
        {% if required %}data-validate="required"{% endif %}
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
    >
        <option value="">-- Select --</option>
        {% for option in options %}
        <option value="{{ option.value }}" {% if option.value == value %}selected{% endif %}>
            {{ option.label }}
        </option>
        {% endfor %}
    </select>
    <p id="{{ name }}-error" class="mt-1 text-sm text-red-600 hidden"></p>
</div>
{% endmacro %}

{% macro textarea_field(name, label, required=False, placeholder='', rows=4, value='') %}
<div class="mb-4">
    <label for="{{ name }}" class="block text-sm font-medium text-gray-700 mb-1">
        {{ label }}
        {% if required %}<span class="text-red-500">*</span>{% endif %}
    </label>
    <textarea
        id="{{ name }}"
        name="{{ name }}"
        rows="{{ rows }}"
        placeholder="{{ placeholder }}"
        {% if required %}data-validate="required"{% endif %}
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
    >{{ value }}</textarea>
    <p id="{{ name }}-error" class="mt-1 text-sm text-red-600 hidden"></p>
</div>
{% endmacro %}
```

## Table Component (components/table.html)

```html
{% macro table(columns, rows, actions=True) %}
<div class="overflow-x-auto bg-white rounded-lg shadow">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
            <tr>
                {% for column in columns %}
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {{ column.label }}
                </th>
                {% endfor %}
                {% if actions %}
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                </th>
                {% endif %}
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            {% for row in rows %}
            <tr class="hover:bg-gray-50">
                {% for column in columns %}
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ row[column.key] }}
                </td>
                {% endfor %}
                {% if actions %}
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {{ caller(row) }}
                </td>
                {% endif %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endmacro %}
```

## Example: User List Page

```html
{% extends "layouts/app_layout.html" %}
{% from "components/table.html" import table %}
{% from "components/modal.html" import modal %}

{% block title %}Users Management{% endblock %}

{% block nav_title %}Users Management{% endblock %}

{% block page_header %}
<div class="flex justify-between items-center mb-6">
    <div>
        <h2 class="text-2xl font-bold text-gray-900">Users</h2>
        <p class="text-gray-600">Manage system users and their access levels</p>
    </div>
    <button
        onclick="Modal.open('addUserModal')"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
        Add User
    </button>
</div>

<!-- Search and filter -->
<div class="mb-6 flex space-x-4">
    <input
        type="text"
        id="searchInput"
        placeholder="Search users..."
        class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
    >
    <select
        id="userLevelFilter"
        class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
    >
        <option value="">All Levels</option>
        <option value="admin">Admin</option>
        <option value="manager">Manager</option>
        <option value="editor">Editor</option>
        <option value="viewer">Viewer</option>
    </select>
</div>
{% endblock %}

{% block content %}
<!-- Users table -->
{% call table(columns=[
    {'key': 'email', 'label': 'Email'},
    {'key': 'name', 'label': 'Name'},
    {'key': 'user_level', 'label': 'Level'},
    {'key': 'status', 'label': 'Status'}
], rows=users) %}
    <button data-action="edit" data-user-id="{{ row.user_id }}" class="text-blue-600 hover:text-blue-900 mr-3">
        Edit
    </button>
    <button data-action="delete" data-user-id="{{ row.user_id }}" class="text-red-600 hover:text-red-900">
        Delete
    </button>
{% endcall %}

<!-- Add User Modal -->
{% call modal('addUserModal', 'Add New User') %}
    <form id="addUserForm">
        <!-- Form fields here -->
    </form>
{% endcall %}
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', path='/js/pages/admin/users.js') }}"></script>
{% endblock %}
```

## Template Variables Available

**All authenticated pages:**
- `user` - Current user object
  - `user.user_id`
  - `user.email`
  - `user.name`
  - `user.user_level`
  - `user.teams` - List of team names

**Request context:**
- `request.url`
- `request.path`
- `active_page` - Current page identifier

## Jinja2 Filters

```python
# Custom filters (in app/main.py)

@app.template_filter('format_date')
def format_date(value, format='%Y-%m-%d'):
    """Format datetime to string"""
    return value.strftime(format) if value else ''

@app.template_filter('thai_date')
def thai_date(value):
    """Format date to Thai format"""
    # Implementation
    pass

@app.template_filter('file_size')
def file_size(bytes):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
```

## Best Practices

1. **Template Inheritance**: Always extend from base or layout templates
2. **Component Reuse**: Use macros for repeated UI elements
3. **Minimize Logic**: Keep template logic simple, move complex logic to views
4. **XSS Prevention**: Always use `{{ }}` (auto-escapes), use `|safe` filter carefully
5. **Responsive Design**: Use Tailwind responsive classes (sm:, md:, lg:, xl:)
6. **Accessibility**: Use semantic HTML, proper labels, ARIA attributes
7. **Performance**: Minimize template includes, cache when possible

## Related Documentation

- [javascript.md](javascript.md) - Frontend JavaScript
- [../DESIGN.md](../DESIGN.md) - UI/UX design system
- [tailwind.md](tailwind.md) - Tailwind CSS setup
