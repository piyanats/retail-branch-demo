# Frontend JavaScript Specifications

## Overview

เอกสารนี้กำหนด JavaScript patterns และ specifications สำหรับ frontend ของระบบ Retail Branch Management System โดยใช้ **Vanilla JavaScript** (ไม่ใช้ framework) เพื่อความเรียบง่ายและ performance

## Core Principles

1. **Progressive Enhancement**: HTML ทำงานได้โดยไม่ต้องมี JavaScript
2. **Unobtrusive JavaScript**: แยก JavaScript ออกจาก HTML
3. **No jQuery**: ใช้ modern JavaScript (ES6+) และ native APIs
4. **Keep It Simple**: เขียนโค้ดที่อ่านง่าย maintainable
5. **Performance First**: Minimize DOM manipulation, use event delegation

## File Structure

```
static/js/
├── app.js                  # Main application entry point
├── utils/
│   ├── api.js             # API client utilities
│   ├── dom.js             # DOM manipulation helpers
│   ├── validation.js      # Form validation utilities
│   └── storage.js         # localStorage/sessionStorage helpers
├── components/
│   ├── modal.js           # Modal/Dialog component
│   ├── toast.js           # Toast notification component
│   ├── dropdown.js        # Dropdown component
│   ├── tabs.js            # Tabs component
│   └── fileUpload.js      # File upload component
├── pages/
│   ├── admin/
│   │   ├── users.js       # User management page
│   │   ├── permissions.js # Permissions management page
│   │   └── auditLogs.js   # Audit logs page
│   ├── legal/
│   │   ├── ppp09.js       # ภ.พ.09 management
│   │   └── ppp20.js       # ภ.พ.20 management
│   ├── newBranch.js       # New branch tracking
│   ├── srdLayout.js       # SRD layout management
│   └── scmDc.js           # SCM DC management
└── main.js                # Initialize all components and pages
```

## API Client (utils/api.js)

### API Wrapper Functions

```javascript
// utils/api.js

/**
 * API client for making HTTP requests
 */
const API = {
  /**
   * Base URL for API endpoints
   */
  baseURL: window.location.origin,

  /**
   * GET request
   * @param {string} endpoint - API endpoint path
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Response data
   */
  async get(endpoint, params = {}) {
    const url = new URL(`${this.baseURL}${endpoint}`);
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined) {
        url.searchParams.append(key, params[key]);
      }
    });

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      credentials: 'same-origin', // Include cookies
    });

    return this.handleResponse(response);
  },

  /**
   * POST request
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request body data
   * @returns {Promise<Object>} Response data
   */
  async post(endpoint, data) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  },

  /**
   * PUT request
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request body data
   * @returns {Promise<Object>} Response data
   */
  async put(endpoint, data) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  },

  /**
   * PATCH request
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request body data
   * @returns {Promise<Object>} Response data
   */
  async patch(endpoint, data) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  },

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint path
   * @returns {Promise<Object>} Response data
   */
  async delete(endpoint) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      },
      credentials: 'same-origin',
    });

    return this.handleResponse(response);
  },

  /**
   * Upload file(s)
   * @param {string} endpoint - API endpoint path
   * @param {FormData} formData - Form data with files
   * @param {Function} onProgress - Progress callback
   * @returns {Promise<Object>} Response data
   */
  async upload(endpoint, formData, onProgress = null) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Progress tracking
      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            onProgress(percentComplete);
          }
        });
      }

      xhr.addEventListener('load', async () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            resolve(data);
          } catch (error) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(error);
          } catch {
            reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
          }
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Network error occurred'));
      });

      xhr.open('POST', `${this.baseURL}${endpoint}`);
      xhr.withCredentials = true; // Include cookies
      xhr.send(formData);
    });
  },

  /**
   * Download file
   * @param {string} endpoint - API endpoint path
   * @param {string} filename - Filename for download
   */
  async download(endpoint, filename) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      credentials: 'same-origin',
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  /**
   * Handle API response
   * @private
   */
  async handleResponse(response) {
    // Handle redirects (e.g., to login page)
    if (response.redirected) {
      window.location.href = response.url;
      return;
    }

    // Parse JSON response
    const data = await response.json();

    // Check for errors
    if (!response.ok) {
      throw {
        status: response.status,
        ...data
      };
    }

    return data;
  }
};
```

## Form Validation (utils/validation.js)

```javascript
// utils/validation.js

/**
 * Form validation utilities
 */
const Validation = {
  /**
   * Validation rules
   */
  rules: {
    required: (value) => value !== null && value !== undefined && value !== '',
    email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    minLength: (value, length) => value.length >= length,
    maxLength: (value, length) => value.length <= length,
    number: (value) => !isNaN(value) && value !== '',
    positive: (value) => Number(value) > 0,
    postalCode: (value) => /^\d{5}$/.test(value),
    phone: (value) => /^0\d{1,2}-?\d{3,4}-?\d{4}$/.test(value),
  },

  /**
   * Validate single field
   * @param {HTMLElement} field - Input field element
   * @returns {boolean} Is valid
   */
  validateField(field) {
    const rules = field.dataset.validate?.split('|') || [];
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    for (const rule of rules) {
      const [ruleName, ...params] = rule.split(':');

      if (ruleName === 'required' && !this.rules.required(value)) {
        isValid = false;
        errorMessage = field.dataset.errorRequired || 'This field is required';
        break;
      }

      if (value && !this.rules[ruleName]?.(value, ...params)) {
        isValid = false;
        errorMessage = field.dataset[`error${ruleName.charAt(0).toUpperCase() + ruleName.slice(1)}`] || `Invalid ${ruleName}`;
        break;
      }
    }

    this.setFieldError(field, isValid ? null : errorMessage);
    return isValid;
  },

  /**
   * Validate entire form
   * @param {HTMLFormElement} form - Form element
   * @returns {boolean} Is valid
   */
  validateForm(form) {
    const fields = form.querySelectorAll('[data-validate]');
    let isValid = true;

    fields.forEach(field => {
      if (!this.validateField(field)) {
        isValid = false;
      }
    });

    return isValid;
  },

  /**
   * Set field error state
   * @param {HTMLElement} field - Input field element
   * @param {string|null} message - Error message
   */
  setFieldError(field, message) {
    const errorElement = document.getElementById(`${field.id}-error`);

    if (message) {
      field.classList.add('border-red-500');
      field.classList.remove('border-gray-300');
      if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
      }
    } else {
      field.classList.remove('border-red-500');
      field.classList.add('border-gray-300');
      if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.add('hidden');
      }
    }
  },

  /**
   * Clear all form errors
   * @param {HTMLFormElement} form - Form element
   */
  clearErrors(form) {
    const fields = form.querySelectorAll('[data-validate]');
    fields.forEach(field => this.setFieldError(field, null));
  }
};
```

## Toast Notifications (components/toast.js)

```javascript
// components/toast.js

/**
 * Toast notification component
 */
const Toast = {
  /**
   * Show toast notification
   * @param {string} message - Message to display
   * @param {string} type - Type: 'success', 'error', 'warning', 'info'
   * @param {number} duration - Duration in milliseconds (default: 3000)
   */
  show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-4 rounded-lg shadow-lg text-white z-50 transform transition-all duration-300 ${this.getTypeClass(type)}`;
    toast.textContent = message;
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px)';

    document.body.appendChild(toast);

    // Animate in
    setTimeout(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    }, 10);

    // Auto remove
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-20px)';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  /**
   * Get Tailwind classes for toast type
   * @private
   */
  getTypeClass(type) {
    const classes = {
      success: 'bg-green-500',
      error: 'bg-red-500',
      warning: 'bg-orange-500',
      info: 'bg-blue-500'
    };
    return classes[type] || classes.info;
  },

  success(message, duration) {
    this.show(message, 'success', duration);
  },

  error(message, duration) {
    this.show(message, 'error', duration);
  },

  warning(message, duration) {
    this.show(message, 'warning', duration);
  },

  info(message, duration) {
    this.show(message, 'info', duration);
  }
};
```

## Modal Component (components/modal.js)

```javascript
// components/modal.js

/**
 * Modal dialog component
 */
const Modal = {
  /**
   * Open modal
   * @param {string} modalId - Modal element ID
   */
  open(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Focus first input
    const firstInput = modal.querySelector('input, select, textarea');
    if (firstInput) {
      setTimeout(() => firstInput.focus(), 100);
    }
  },

  /**
   * Close modal
   * @param {string} modalId - Modal element ID
   */
  close(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.add('hidden');
    document.body.style.overflow = '';
  },

  /**
   * Initialize modal click handlers
   */
  init() {
    // Close modal on backdrop click
    document.querySelectorAll('[data-modal]').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          this.close(modal.id);
        }
      });
    });

    // Close modal on close button click
    document.querySelectorAll('[data-modal-close]').forEach(button => {
      button.addEventListener('click', (e) => {
        const modalId = button.closest('[data-modal]')?.id;
        if (modalId) {
          this.close(modalId);
        }
      });
    });

    // ESC key to close modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const openModal = document.querySelector('[data-modal]:not(.hidden)');
        if (openModal) {
          this.close(openModal.id);
        }
      }
    });
  }
};
```

## File Upload Component (components/fileUpload.js)

```javascript
// components/fileUpload.js

/**
 * File upload component with drag & drop
 */
class FileUpload {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.options = {
      multiple: options.multiple || false,
      accept: options.accept || '*/*',
      maxSize: options.maxSize || 10 * 1024 * 1024, // 10MB default
      endpoint: options.endpoint,
      onSuccess: options.onSuccess || (() => {}),
      onError: options.onError || (() => {}),
      onProgress: options.onProgress || (() => {})
    };

    this.files = [];
    this.init();
  }

  init() {
    this.createUI();
    this.attachEvents();
  }

  createUI() {
    this.container.innerHTML = `
      <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer" data-drop-zone>
        <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <p class="mt-2 text-sm text-gray-600">
          <span class="font-semibold text-blue-600">Click to upload</span> or drag and drop
        </p>
        <p class="mt-1 text-xs text-gray-500">
          ${this.getAcceptText()}
        </p>
      </div>
      <input type="file" class="hidden" data-file-input ${this.options.multiple ? 'multiple' : ''} accept="${this.options.accept}">
      <div class="mt-4" data-file-list></div>
    `;
  }

  attachEvents() {
    const dropZone = this.container.querySelector('[data-drop-zone]');
    const fileInput = this.container.querySelector('[data-file-input]');

    // Click to select files
    dropZone.addEventListener('click', () => fileInput.click());

    // File selected
    fileInput.addEventListener('change', (e) => {
      this.handleFiles(Array.from(e.target.files));
    });

    // Drag & drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      });
    });

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('border-blue-500', 'bg-blue-50');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('border-blue-500', 'bg-blue-50');
      });
    });

    dropZone.addEventListener('drop', (e) => {
      const files = Array.from(e.dataTransfer.files);
      this.handleFiles(files);
    });
  }

  handleFiles(files) {
    // Validate files
    const validFiles = files.filter(file => {
      if (file.size > this.options.maxSize) {
        Toast.error(`File "${file.name}" is too large. Max size: ${this.formatFileSize(this.options.maxSize)}`);
        return false;
      }
      return true;
    });

    this.files = this.options.multiple ? [...this.files, ...validFiles] : validFiles;
    this.renderFileList();
  }

  renderFileList() {
    const fileList = this.container.querySelector('[data-file-list]');
    fileList.innerHTML = this.files.map((file, index) => `
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2">
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-900">${file.name}</p>
          <p class="text-xs text-gray-500">${this.formatFileSize(file.size)}</p>
          <div class="mt-1 w-full bg-gray-200 rounded-full h-1.5 hidden" data-progress-${index}>
            <div class="bg-blue-600 h-1.5 rounded-full" style="width: 0%" data-progress-bar-${index}></div>
          </div>
        </div>
        <button type="button" class="ml-4 text-red-600 hover:text-red-800" data-remove="${index}">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    `).join('');

    // Attach remove handlers
    fileList.querySelectorAll('[data-remove]').forEach(button => {
      button.addEventListener('click', () => {
        const index = parseInt(button.dataset.remove);
        this.removeFile(index);
      });
    });
  }

  removeFile(index) {
    this.files.splice(index, 1);
    this.renderFileList();
  }

  async upload() {
    if (this.files.length === 0) {
      Toast.error('Please select at least one file');
      return;
    }

    const formData = new FormData();
    this.files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const data = await API.upload(this.options.endpoint, formData, (progress) => {
        this.options.onProgress(progress);
        // Update all progress bars
        this.files.forEach((_, index) => {
          const progressBar = this.container.querySelector(`[data-progress-bar-${index}]`);
          const progressContainer = this.container.querySelector(`[data-progress-${index}]`);
          if (progressBar && progressContainer) {
            progressContainer.classList.remove('hidden');
            progressBar.style.width = `${progress}%`;
          }
        });
      });

      this.options.onSuccess(data);
      this.files = [];
      this.renderFileList();
    } catch (error) {
      this.options.onError(error);
    }
  }

  getAcceptText() {
    const accept = this.options.accept;
    if (accept === '*/*') return 'Any file type';
    if (accept.includes('image')) return 'Images (PNG, JPG, JPEG)';
    if (accept.includes('pdf')) return 'PDF files only';
    return accept;
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
}
```

## Pagination Component

```javascript
// utils/pagination.js

/**
 * Render pagination controls
 * @param {Object} pagination - Pagination data from API
 * @param {Function} onPageChange - Callback when page changes
 * @returns {string} HTML string
 */
function renderPagination(pagination, onPageChange) {
  const { page, total_pages, has_prev, has_next } = pagination;

  let html = '<div class="flex items-center justify-between mt-4">';

  // Previous button
  html += `
    <button
      class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      ${!has_prev ? 'disabled' : ''}
      data-page="${page - 1}"
    >
      Previous
    </button>
  `;

  // Page info
  html += `
    <span class="text-sm text-gray-700">
      Page <span class="font-medium">${page}</span> of <span class="font-medium">${total_pages}</span>
    </span>
  `;

  // Next button
  html += `
    <button
      class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      ${!has_next ? 'disabled' : ''}
      data-page="${page + 1}"
    >
      Next
    </button>
  `;

  html += '</div>';

  return html;
}
```

## Event Delegation Pattern

```javascript
// Example: User management page with event delegation

document.addEventListener('DOMContentLoaded', () => {
  const userTable = document.getElementById('user-table');

  // Single event listener for all action buttons
  userTable.addEventListener('click', async (e) => {
    const button = e.target.closest('[data-action]');
    if (!button) return;

    const action = button.dataset.action;
    const userId = button.dataset.userId;

    switch (action) {
      case 'edit':
        await editUser(userId);
        break;
      case 'delete':
        await deleteUser(userId);
        break;
      case 'view-permissions':
        await viewPermissions(userId);
        break;
    }
  });
});
```

## Debounce & Throttle Utilities

```javascript
// utils/dom.js

/**
 * Debounce function execution
 */
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

/**
 * Throttle function execution
 */
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Usage example: Search with debounce
const searchInput = document.getElementById('search');
const handleSearch = debounce(async (query) => {
  const results = await API.get('/api/search', { q: query });
  renderResults(results);
}, 500);

searchInput.addEventListener('input', (e) => {
  handleSearch(e.target.value);
});
```

## Error Handling Best Practices

```javascript
// Centralized error handler
async function handleAPICall(apiFunction, errorMessage = 'An error occurred') {
  try {
    return await apiFunction();
  } catch (error) {
    console.error('API Error:', error);

    // Handle specific error codes
    if (error.status === 401) {
      window.location.href = '/auth/login';
      return;
    }

    if (error.status === 403) {
      Toast.error('You do not have permission to perform this action');
      return;
    }

    if (error.code === 'VALIDATION_ERROR' && error.details) {
      // Show validation errors
      Object.keys(error.details).forEach(field => {
        const fieldElement = document.getElementById(field);
        if (fieldElement) {
          Validation.setFieldError(fieldElement, error.details[field][0]);
        }
      });
      return;
    }

    Toast.error(error.message || errorMessage);
  }
}

// Usage
await handleAPICall(
  () => API.post('/api/admin/users', userData),
  'Failed to create user'
);
```

## Browser Support

**Minimum Requirements:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Polyfills Not Required:**
- Fetch API (native support)
- Promises (native support)
- ES6 features (native support)

## Performance Guidelines

1. **Minimize DOM Access**: Cache DOM queries
2. **Event Delegation**: Use single listener on parent instead of multiple listeners
3. **Debounce/Throttle**: Use for scroll, resize, input events
4. **Lazy Loading**: Load scripts/components only when needed
5. **Avoid Memory Leaks**: Remove event listeners when elements are removed

## Security Considerations

1. **XSS Prevention**: Always sanitize user input before inserting into DOM
2. **CSRF**: Include CSRF tokens in POST requests (handled by backend)
3. **No eval()**: Never use eval() or Function() constructor
4. **Content Security Policy**: Follow CSP headers set by backend
5. **Secure Cookies**: Session cookies are HttpOnly and Secure

## Related Documentation

- [templates.md](templates.md) - HTML template structure
- [../development/api-standards.md](../development/api-standards.md) - API conventions
- [../DESIGN.md](../DESIGN.md) - UI/UX design system
