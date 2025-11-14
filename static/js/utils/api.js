/**
 * API Client Utility
 * Wrapper for fetch API with automatic CSRF token handling
 */

const API = {
    baseURL: '',

    /**
     * Get CSRF token from meta tag
     */
    getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.content || '';
    },

    /**
     * Handle API response
     */
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({
                error: 'An error occurred',
                code: response.status
            }));
            throw new Error(error.error || error.detail || 'Request failed');
        }
        return response.json();
    },

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const url = new URL(`${this.baseURL}${endpoint}`, window.location.origin);

        // Add query parameters
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.append(key, params[key]);
            }
        });

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
        });

        return this.handleResponse(response);
    },

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': this.getCsrfToken(),
            },
            credentials: 'same-origin',
            body: JSON.stringify(data),
        });

        return this.handleResponse(response);
    },

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': this.getCsrfToken(),
            },
            credentials: 'same-origin',
            body: JSON.stringify(data),
        });

        return this.handleResponse(response);
    },

    /**
     * DELETE request
     */
    async delete(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': this.getCsrfToken(),
            },
            credentials: 'same-origin',
        });

        return this.handleResponse(response);
    },

    /**
     * Upload file with progress tracking
     */
    async upload(endpoint, formData, onProgress = null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Track upload progress
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }

            // Handle completion
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        resolve(JSON.parse(xhr.responseText));
                    } catch (e) {
                        resolve(xhr.responseText);
                    }
                } else {
                    try {
                        const error = JSON.parse(xhr.responseText);
                        reject(new Error(error.error || error.detail || 'Upload failed'));
                    } catch (e) {
                        reject(new Error('Upload failed'));
                    }
                }
            });

            // Handle errors
            xhr.addEventListener('error', () => {
                reject(new Error('Network error'));
            });

            // Send request
            xhr.open('POST', `${this.baseURL}${endpoint}`);
            xhr.setRequestHeader('X-CSRF-Token', this.getCsrfToken());
            xhr.withCredentials = true;
            xhr.send(formData);
        });
    }
};

// Export for use in other scripts
window.API = API;
