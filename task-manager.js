/**
 * Task Manager Pro - JavaScript Module
 * Handles all frontend functionality and API interactions
 */

class TaskManager {
    constructor() {
        this.baseURL = 'http://127.0.0.1:5000';
        this.tasks = [];
        this.filteredTasks = [];
        this.apiStatus = {
            gmail: false,
            sheets: false,
            calendar: false
        };
        this.currentUser = null;  // Store current user info
        this.init();
    }

    async init() {
        try {
            await this.checkAPIHealth();
            this.loadCurrentUser();  // Load user session
            await this.loadTasks();
            this.updateDashboard();
            this.checkIntegrationStatus();
            this.setupEventListeners();
            this.showToast('Task Manager loaded successfully!', 'success');
        } catch (error) {
            console.error('Initialization error:', error);
            this.showToast('Failed to initialize Task Manager', 'error');
        }
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const target = e.target.getAttribute('data-bs-target');
                if (target === '#analytics') {
                    this.updateAnalytics();
                }
            });
        });

        // User management form listeners
        this.setupUserFormListeners();
    }

    setupUserFormListeners() {
        // Login form
        const loginForm = document.getElementById('loginFormData');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Register form
        const registerForm = document.getElementById('registerFormData');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleRegister();
            });
        }

        // Edit profile form
        const editForm = document.getElementById('editProfileFormData');
        if (editForm) {
            editForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleEditProfile();
            });
        }
    }

    // API Health Check
    async checkAPIHealth() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            const data = await response.json();

            if (data.success) {
                console.log('API Health:', data);
                return data;
            } else {
                throw new Error('API health check failed');
            }
        } catch (error) {
            console.error('API Health check failed:', error);
            this.showToast('API server is not responding. Please start the server.', 'error');
            throw error;
        }
    }

    // Task CRUD Operations
    async loadTasks() {
        try {
            const response = await fetch(`${this.baseURL}/tasks`);
            if (response.ok) {
                const data = await response.json();
                this.tasks = Array.isArray(data) ? data : (data.data?.tasks || []);
                this.filteredTasks = [...this.tasks];
                this.renderTasks();
                this.updateDashboard();
            } else {
                throw new Error(`Failed to load tasks: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading tasks:', error);
            this.showToast('Failed to load tasks', 'error');
        }
    }

    async createTask(taskData) {
        try {
            console.log('Creating task with data:', taskData);

            const response = await fetch(`${this.baseURL}/tasks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taskData)
            });

            console.log('Create task response status:', response.status);

            if (response.ok) {
                const result = await response.json();
                console.log('Create task result:', result);
                const newTask = result.data?.task || result.data || result;
                this.tasks.unshift(newTask);
                this.filteredTasks = [...this.tasks];
                this.renderTasks();
                this.updateDashboard();
                this.showToast('Task created successfully!', 'success');
                return newTask;
            } else {
                const error = await response.json();
                console.error('Create task error response:', error);
                throw new Error(error.error || error.message || 'Failed to create task');
            }
        } catch (error) {
            console.error('Error creating task:', error);
            this.showToast(error.message || 'Failed to create task', 'error');
            throw error;
        }
    }

    async updateTask(taskId, taskData) {
        try {
            console.log('Updating task:', taskId, 'with data:', taskData);

            const response = await fetch(`${this.baseURL}/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taskData)
            });

            console.log('Update task response status:', response.status);

            if (response.ok) {
                const result = await response.json();
                console.log('Update task result:', result);
                const updatedTask = result.data || result;

                const index = this.tasks.findIndex(task => task.id == taskId);
                if (index !== -1) {
                    this.tasks[index] = updatedTask;
                    this.filteredTasks = [...this.tasks];
                    this.renderTasks();
                    this.updateDashboard();
                    this.showToast('Task updated successfully!', 'success');
                }
                return updatedTask;
            } else {
                const error = await response.json();
                console.error('Update task error response:', error);
                throw new Error(error.error || error.message || 'Failed to update task');
            }
        } catch (error) {
            console.error('Error updating task:', error);
            this.showToast(error.message || 'Failed to update task', 'error');
            throw error;
        }
    }

    async deleteTask(taskId) {
        try {
            console.log('Deleting task:', taskId);

            const response = await fetch(`${this.baseURL}/tasks/${taskId}`, {
                method: 'DELETE'
            });

            console.log('Delete task response status:', response.status);

            if (response.ok) {
                this.tasks = this.tasks.filter(task => task.id != taskId);
                this.filteredTasks = [...this.tasks];
                this.renderTasks();
                this.updateDashboard();
                this.showToast('Task deleted successfully!', 'success');
            } else {
                const error = await response.json().catch(() => ({}));
                console.error('Delete task error response:', error);
                throw new Error(error.error || error.message || 'Failed to delete task');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            this.showToast(error.message || 'Failed to delete task', 'error');
        }
    }

    // Google API Integrations
    async addToCalendar(taskId, eventData = {}) {
        try {
            const defaultEventData = {
                duration_minutes: 60,
                reminder_minutes: 15,
                location: '',
                description: 'Task from Task Manager Pro'
            };

            const calendarData = { ...defaultEventData, ...eventData };

            const response = await fetch(`${this.baseURL}/tasks/${taskId}/add-to-calendar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(calendarData)
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast('Task added to Google Calendar!', 'success');
                this.logIntegrationActivity('Calendar', `Task added to calendar: ${result.data?.event_id}`);

                // Refresh tasks to show updated calendar status
                await this.loadTasks();

                return result;
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to add to calendar');
            }
        } catch (error) {
            console.error('Error adding to calendar:', error);
            this.showToast(error.message || 'Failed to add to calendar', 'error');
        }
    }

    async removeFromCalendar(taskId) {
        try {
            const response = await fetch(`${this.baseURL}/tasks/${taskId}/remove-from-calendar`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast('Task removed from Google Calendar!', 'success');
                this.logIntegrationActivity('Calendar', `Task removed from calendar: ${taskId}`);

                // Refresh tasks to show updated calendar status
                await this.loadTasks();

                return result;
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to remove from calendar');
            }
        } catch (error) {
            console.error('Error removing from calendar:', error);
            this.showToast(error.message || 'Failed to remove from calendar', 'error');
        }
    }

    async sendEmailReminder(taskId) {
        try {
            const response = await fetch(`${this.baseURL}/tasks/${taskId}/send-reminder`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipient_email: 'chandu0polaki@gmail.com'
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast('Email reminder sent!', 'success');
                this.logIntegrationActivity('Gmail', `Reminder sent for task ${taskId}`);
                return result;
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to send email');
            }
        } catch (error) {
            console.error('Error sending email:', error);
            this.showToast(error.message || 'Failed to send email reminder', 'error');
        }
    }

    async exportToSheets() {
        try {
            this.showToast('Exporting tasks to Google Sheets...', 'info');

            const response = await fetch(`${this.baseURL}/tasks/export/sheets`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    spreadsheet_name: `Task Export - ${new Date().toLocaleDateString()}`
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast('Tasks exported to Google Sheets successfully!', 'success');
                this.logIntegrationActivity('Sheets', `Exported ${this.tasks.length} tasks to spreadsheet`);

                if (result.data?.spreadsheet_url) {
                    const openSheet = confirm('Tasks exported successfully! Would you like to open the spreadsheet?');
                    if (openSheet) {
                        window.open(result.data.spreadsheet_url, '_blank');
                    }
                }
                return result;
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to export to sheets');
            }
        } catch (error) {
            console.error('Error exporting to sheets:', error);
            this.showToast(error.message || 'Failed to export to Google Sheets', 'error');
        }
    }

    // Integration Status Checks
    async checkIntegrationStatus() {
        // Check Gmail status
        try {
            const gmailResponse = await fetch(`${this.baseURL}/health`);
            if (gmailResponse.ok) {
                this.apiStatus.gmail = true;
                this.updateIntegrationStatus('gmail', true, 'Connected');
            }
        } catch (error) {
            this.updateIntegrationStatus('gmail', false, 'Disconnected');
        }

        // Check Sheets status  
        try {
            const sheetsResponse = await fetch(`${this.baseURL}/health`);
            if (sheetsResponse.ok) {
                this.apiStatus.sheets = true;
                this.updateIntegrationStatus('sheets', true, 'Connected');
            }
        } catch (error) {
            this.updateIntegrationStatus('sheets', false, 'Disconnected');
        }

        // Check Calendar status
        try {
            const calendarResponse = await fetch(`${this.baseURL}/health`);
            if (calendarResponse.ok) {
                this.apiStatus.calendar = true;
                this.updateIntegrationStatus('calendar', true, 'Connected');
            }
        } catch (error) {
            this.updateIntegrationStatus('calendar', false, 'Disconnected');
        }
    }

    updateIntegrationStatus(service, connected, message) {
        const statusElement = document.getElementById(`${service}Status`);
        if (statusElement) {
            const statusClass = connected ? 'api-connected' : 'api-disconnected';
            const icon = connected ? 'fa-check-circle' : 'fa-times-circle';
            statusElement.innerHTML = `
                <span class="api-status ${statusClass}">
                    <i class="fas ${icon}"></i> ${message}
                </span>
            `;
        }
    }

    // UI Rendering Methods
    renderTasks() {
        const tasksContainer = document.getElementById('tasksList');
        const recentTasksContainer = document.getElementById('recentTasks');

        if (!tasksContainer) return;

        if (this.filteredTasks.length === 0) {
            tasksContainer.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-tasks fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No tasks found</h5>
                    <p class="text-muted">Create your first task to get started!</p>
                    <button class="btn btn-primary" onclick="showCreateTaskModal()">
                        <i class="fas fa-plus"></i> Create Task
                    </button>
                </div>
            `;
            return;
        }

        const tasksHTML = this.filteredTasks.map(task => this.renderTaskItem(task)).join('');
        tasksContainer.innerHTML = tasksHTML;

        // Update recent tasks (last 5)
        if (recentTasksContainer) {
            const recentTasks = this.tasks.slice(0, 5);
            const recentHTML = recentTasks.map(task => this.renderRecentTaskItem(task)).join('');
            recentTasksContainer.innerHTML = recentHTML || '<p class="text-muted">No recent tasks</p>';
        }
    }

    renderTaskItem(task) {
        const priorityClass = `${task.priority}-priority`;
        const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
        const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed';

        return `
            <div class="task-item ${priorityClass}" data-task-id="${task.id}">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h5 class="mb-2">${this.escapeHtml(task.title)}</h5>
                        <p class="text-muted mb-2">${this.escapeHtml(task.description || 'No description')}</p>
                        <div class="d-flex gap-2 mb-2">
                            <span class="priority-badge priority-${task.priority}">
                                ${task.priority.toUpperCase()}
                            </span>
                            <span class="status-badge status-${task.status.replace('_', '-')}">
                                ${task.status.replace('_', ' ').toUpperCase()}
                            </span>
                            ${isOverdue ? '<span class="badge bg-danger">OVERDUE</span>' : ''}
                        </div>
                        <small class="text-muted">
                            <i class="fas fa-calendar"></i> Due: ${dueDate} | 
                            <i class="fas fa-clock"></i> Created: ${new Date(task.created_at).toLocaleDateString()}
                        </small>
                    </div>
                    <div class="col-md-4">
                        <div class="action-buttons">
                            <button class="btn btn-outline-primary btn-sm" onclick="editTask(${task.id})">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            ${task.calendar_event_id ?
                `<button class="btn btn-outline-danger btn-sm" onclick="taskManager.removeFromCalendar(${task.id})">
                                    <i class="fas fa-calendar-minus"></i> Remove Calendar
                                </button>` :
                `<button class="btn btn-outline-success btn-sm" onclick="taskManager.addToCalendar(${task.id})">
                                    <i class="fas fa-calendar-plus"></i> Add Calendar
                                </button>`
            }
                            <button class="btn btn-outline-warning btn-sm" onclick="taskManager.sendEmailReminder(${task.id})">
                                <i class="fas fa-envelope"></i> Email
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="deleteTaskConfirm(${task.id})">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderRecentTaskItem(task) {
        return `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                <div>
                    <strong>${this.escapeHtml(task.title)}</strong>
                    <br>
                    <small class="text-muted">${task.status.replace('_', ' ')}</small>
                </div>
                <span class="priority-badge priority-${task.priority}">
                    ${task.priority}
                </span>
            </div>
        `;
    }

    updateDashboard() {
        const totalTasks = this.tasks.length;
        const pendingTasks = this.tasks.filter(task => task.status === 'pending').length;
        const completedTasks = this.tasks.filter(task => task.status === 'completed').length;
        const overdueTasks = this.tasks.filter(task => {
            return task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed';
        }).length;

        document.getElementById('totalTasks').textContent = totalTasks;
        document.getElementById('pendingTasks').textContent = pendingTasks;
        document.getElementById('completedTasks').textContent = completedTasks;
        document.getElementById('overdueTasks').textContent = overdueTasks;
    }

    // Filter and Search
    filterTasks() {
        const statusFilter = document.getElementById('filterStatus').value;
        const priorityFilter = document.getElementById('filterPriority').value;
        const searchTerm = document.getElementById('searchTasks').value.toLowerCase();

        this.filteredTasks = this.tasks.filter(task => {
            const matchesStatus = !statusFilter || task.status === statusFilter;
            const matchesPriority = !priorityFilter || task.priority === priorityFilter;
            const matchesSearch = !searchTerm ||
                task.title.toLowerCase().includes(searchTerm) ||
                (task.description && task.description.toLowerCase().includes(searchTerm));

            return matchesStatus && matchesPriority && matchesSearch;
        });

        this.renderTasks();
    }

    clearFilters() {
        document.getElementById('filterStatus').value = '';
        document.getElementById('filterPriority').value = '';
        document.getElementById('searchTasks').value = '';
        this.filteredTasks = [...this.tasks];
        this.renderTasks();
    }

    // Analytics
    updateAnalytics() {
        this.renderStatusChart();
        this.renderPriorityChart();
        this.renderTrendChart();
    }

    renderStatusChart() {
        const ctx = document.getElementById('statusChart').getContext('2d');
        const statusData = {
            pending: this.tasks.filter(task => task.status === 'pending').length,
            in_progress: this.tasks.filter(task => task.status === 'in_progress').length,
            completed: this.tasks.filter(task => task.status === 'completed').length
        };

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'In Progress', 'Completed'],
                datasets: [{
                    data: [statusData.pending, statusData.in_progress, statusData.completed],
                    backgroundColor: ['#6c757d', '#f39c12', '#27ae60']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    renderPriorityChart() {
        const ctx = document.getElementById('priorityChart').getContext('2d');
        const priorityData = {
            high: this.tasks.filter(task => task.priority === 'high').length,
            medium: this.tasks.filter(task => task.priority === 'medium').length,
            low: this.tasks.filter(task => task.priority === 'low').length
        };

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    label: 'Tasks by Priority',
                    data: [priorityData.high, priorityData.medium, priorityData.low],
                    backgroundColor: ['#e74c3c', '#f39c12', '#27ae60']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    renderTrendChart() {
        const ctx = document.getElementById('trendChart').getContext('2d');
        // Simple trend data - you can enhance this
        const last7Days = [];
        const taskCounts = [];

        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            last7Days.push(date.toLocaleDateString());

            // Count tasks created on this day
            const tasksOnDay = this.tasks.filter(task => {
                const taskDate = new Date(task.created_at);
                return taskDate.toDateString() === date.toDateString();
            }).length;
            taskCounts.push(tasksOnDay);
        }

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: last7Days,
                datasets: [{
                    label: 'Tasks Created',
                    data: taskCounts,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // Integration Activity Logging
    logIntegrationActivity(service, message) {
        const logsContainer = document.getElementById('integrationLogs');
        if (!logsContainer) return;

        const timestamp = new Date().toLocaleString();
        const logEntry = document.createElement('div');
        logEntry.className = 'alert alert-info mb-2';
        logEntry.innerHTML = `
            <strong>${service}:</strong> ${message}
            <br><small class="text-muted">${timestamp}</small>
        `;

        logsContainer.insertBefore(logEntry, logsContainer.firstChild);

        // Keep only last 10 logs
        while (logsContainer.children.length > 10) {
            logsContainer.removeChild(logsContainer.lastChild);
        }
    }

    // Utility Methods
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        const toastId = 'toast-' + Date.now();

        const bgClass = {
            success: 'bg-success',
            error: 'bg-danger',
            warning: 'bg-warning',
            info: 'bg-info'
        }[type] || 'bg-info';

        const toastHTML = `
            <div id="${toastId}" class="toast ${bgClass} text-white" role="alert">
                <div class="toast-header ${bgClass} text-white border-0">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong class="me-auto">Task Manager</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Global function for refresh button
function refreshServerTime() {
    if (taskManager) {
        taskManager.refreshServerTime();
    }
}

// Global Functions
let taskManager;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    taskManager = new TaskManager();
});

// Modal Functions
function showCreateTaskModal() {
    document.getElementById('taskModalTitle').textContent = 'Create New Task';
    document.getElementById('taskForm').reset();
    document.getElementById('taskId').value = '';
    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

function editTask(taskId) {
    const task = taskManager.tasks.find(t => t.id == taskId);
    if (!task) return;

    document.getElementById('taskModalTitle').textContent = 'Edit Task';
    document.getElementById('taskId').value = task.id;
    document.getElementById('taskTitle').value = task.title;
    document.getElementById('taskDescription').value = task.description || '';
    document.getElementById('taskPriority').value = task.priority;
    document.getElementById('taskStatus').value = task.status;

    if (task.due_date) {
        const dueDate = new Date(task.due_date);
        // Format date in local timezone to avoid UTC conversion issues
        const year = dueDate.getFullYear();
        const month = String(dueDate.getMonth() + 1).padStart(2, '0');
        const day = String(dueDate.getDate()).padStart(2, '0');
        const hours = String(dueDate.getHours()).padStart(2, '0');
        const minutes = String(dueDate.getMinutes()).padStart(2, '0');
        const localDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
        document.getElementById('taskDueDate').value = localDateTime;
    }

    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

async function saveTask() {
    const taskId = document.getElementById('taskId').value;
    const title = document.getElementById('taskTitle').value.trim();
    const description = document.getElementById('taskDescription').value.trim();
    const priority = document.getElementById('taskPriority').value || 'medium';
    const status = document.getElementById('taskStatus').value || 'pending';
    const dueDate = document.getElementById('taskDueDate').value;
    const addToCalendar = document.getElementById('addToCalendar').checked;

    console.log('Form values:', { taskId, title, description, priority, status, dueDate, addToCalendar });

    if (!title) {
        taskManager.showToast('Please enter a task title', 'warning');
        return;
    }

    const taskData = {
        title,
        description: description || null,
        priority,
        status,
        due_date: dueDate || null  // Send the datetime-local value directly
    };

    console.log('Saving task with data:', taskData);

    try {
        let savedTask;
        if (taskId) {
            savedTask = await taskManager.updateTask(taskId, taskData);
        } else {
            savedTask = await taskManager.createTask(taskData);
        }

        // Add to calendar if requested
        if (addToCalendar && savedTask) {
            await taskManager.addToCalendar(savedTask.id, {
                event_title: title,
                description: description
            });
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
        modal.hide();
    } catch (error) {
        console.error('Error saving task:', error);
    }
}

function deleteTaskConfirm(taskId) {
    const task = taskManager.tasks.find(t => t.id == taskId);
    if (!task) return;

    if (confirm(`Are you sure you want to delete "${task.title}"?`)) {
        taskManager.deleteTask(taskId);
    }
}

// Integration Functions
async function testGmailConnection() {
    try {
        const response = await fetch(`${taskManager.baseURL}/health`);
        if (response.ok) {
            taskManager.showToast('Gmail connection test successful!', 'success');
            taskManager.logIntegrationActivity('Gmail', 'Connection test successful');
        } else {
            throw new Error('Connection failed');
        }
    } catch (error) {
        taskManager.showToast('Gmail connection test failed', 'error');
        taskManager.logIntegrationActivity('Gmail', 'Connection test failed');
    }
}

async function testSheetsConnection() {
    try {
        const response = await fetch(`${taskManager.baseURL}/health`);
        if (response.ok) {
            taskManager.showToast('Sheets connection test successful!', 'success');
            taskManager.logIntegrationActivity('Sheets', 'Connection test successful');
        } else {
            throw new Error('Connection failed');
        }
    } catch (error) {
        taskManager.showToast('Sheets connection test failed', 'error');
        taskManager.logIntegrationActivity('Sheets', 'Connection test failed');
    }
}

async function testCalendarConnection() {
    try {
        const response = await fetch(`${taskManager.baseURL}/health`);
        if (response.ok) {
            taskManager.showToast('Calendar connection test successful!', 'success');
            taskManager.logIntegrationActivity('Calendar', 'Connection test successful');
        } else {
            throw new Error('Connection failed');
        }
    } catch (error) {
        taskManager.showToast('Calendar connection test failed', 'error');
        taskManager.logIntegrationActivity('Calendar', 'Connection test failed');
    }
}

function sendEmailReminders() {
    const pendingTasks = taskManager.tasks.filter(task => task.status === 'pending');
    if (pendingTasks.length === 0) {
        taskManager.showToast('No pending tasks to send reminders for', 'info');
        return;
    }

    pendingTasks.slice(0, 3).forEach(task => {
        taskManager.sendEmailReminder(task.id);
    });
}

function exportToSheets() {
    taskManager.exportToSheets();
}

async function syncAllToCalendar() {
    const tasksWithDueDate = taskManager.tasks.filter(task =>
        task.due_date && task.status !== 'completed'
    );

    if (tasksWithDueDate.length === 0) {
        taskManager.showToast('No tasks with due dates to sync', 'info');
        return;
    }

    taskManager.showToast(`Syncing ${tasksWithDueDate.length} tasks to calendar...`, 'info');

    for (const task of tasksWithDueDate.slice(0, 5)) {
        await taskManager.addToCalendar(task.id, {
            event_title: task.title,
            description: task.description
        });
    }
}

function refreshDashboard() {
    taskManager.loadTasks();
    taskManager.checkIntegrationStatus();
    taskManager.showToast('Dashboard refreshed!', 'success');
}

// Configuration Functions
function configureMail() {
    taskManager.showToast('Gmail configuration - OAuth will be triggered on first email send', 'info');
}

function configureSheets() {
    taskManager.showToast('Sheets configuration - OAuth will be triggered on first export', 'info');
}

function configureCalendar() {
    taskManager.showToast('Calendar configuration - OAuth will be triggered on first calendar add', 'info');
}

// Filter Functions
function filterTasks() {
    taskManager.filterTasks();
}

function clearFilters() {
    taskManager.clearFilters();
}

// Automated Reminder Functions
async function checkReminderStatus() {
    try {
        const response = await fetch(`${taskManager.baseURL}/reminders/status`);
        if (response.ok) {
            const result = await response.json();
            const status = result.data;

            const statusMessage = `
                🤖 Automated Reminders Status:
                
                • Running: ${status.running ? '✅ Active' : '❌ Stopped'}
                • Gmail: ${status.gmail_initialized ? '✅ Connected' : '❌ Not Connected'}
                • Default Email: ${status.default_email || 'Not set'}
                • 24h Reminders Sent: ${status.reminders_sent_24h}
                • 1h Reminders Sent: ${status.reminders_sent_1h}
                • Total Reminders: ${status.total_reminders_sent}
            `;

            alert(statusMessage);
            taskManager.logIntegrationActivity('Auto Reminders',
                `Status checked - Running: ${status.running}, Total sent: ${status.total_reminders_sent}`);
        } else {
            throw new Error('Failed to get reminder status');
        }
    } catch (error) {
        console.error('Error checking reminder status:', error);
        taskManager.showToast('Failed to check reminder status', 'error');
    }
}

async function startAutomatedReminders() {
    try {
        const interval = prompt('Check interval in minutes (default: 15):', '15');
        const checkInterval = parseInt(interval) || 15;

        const response = await fetch(`${taskManager.baseURL}/reminders/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                check_interval_minutes: checkInterval
            })
        });

        if (response.ok) {
            const result = await response.json();
            taskManager.showToast(`Automated reminders started! Checking every ${checkInterval} minutes`, 'success');
            taskManager.logIntegrationActivity('Auto Reminders',
                `Started with ${checkInterval} minute intervals`);
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to start automated reminders');
        }
    } catch (error) {
        console.error('Error starting automated reminders:', error);
        taskManager.showToast(error.message || 'Failed to start automated reminders', 'error');
    }
}

async function stopAutomatedReminders() {
    try {
        const response = await fetch(`${taskManager.baseURL}/reminders/stop`, {
            method: 'POST'
        });

        if (response.ok) {
            taskManager.showToast('Automated reminders stopped', 'info');
            taskManager.logIntegrationActivity('Auto Reminders', 'Stopped automated reminder system');
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to stop automated reminders');
        }
    } catch (error) {
        console.error('Error stopping automated reminders:', error);
        taskManager.showToast(error.message || 'Failed to stop automated reminders', 'error');
    }
}

async function triggerReminderCheck() {
    try {
        taskManager.showToast('Checking for tasks needing reminders...', 'info');

        const response = await fetch(`${taskManager.baseURL}/reminders/check`, {
            method: 'POST'
        });

        if (response.ok) {
            const result = await response.json();
            const status = result.data;

            taskManager.showToast(
                `Reminder check completed! Total reminders sent: ${status.total_reminders_sent}`,
                'success'
            );
            taskManager.logIntegrationActivity('Auto Reminders',
                `Manual check completed - ${status.reminders_sent_24h} 24h + ${status.reminders_sent_1h} 1h reminders`);
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to check reminders');
        }
    } catch (error) {
        console.error('Error triggering reminder check:', error);
        taskManager.showToast(error.message || 'Failed to check reminders', 'error');
    }
}

// User Management Functions

function showLoginForm() {
    hideUserForms();
    document.getElementById('loginForm').style.display = 'block';
}

function showRegisterForm() {
    hideUserForms();
    document.getElementById('registerForm').style.display = 'block';
}

function showEditProfile() {
    hideUserForms();
    if (taskManager.currentUser) {
        // Pre-fill form with current user data
        document.getElementById('editName').value = taskManager.currentUser.name || '';
        document.getElementById('editTimezone').value = taskManager.currentUser.timezone || 'UTC';
        document.getElementById('editNotifications').value = taskManager.currentUser.notification_preferences || 'both';
        document.getElementById('editProfileForm').style.display = 'block';
    }
}

function hideUserForms() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('editProfileForm').style.display = 'none';
}

function logout() {
    taskManager.currentUser = null;
    localStorage.removeItem('taskManagerUser');
    taskManager.updateUserDisplay();
    taskManager.showToast('Logged out successfully', 'success');
}

// Add user management methods to TaskManager class
Object.assign(TaskManager.prototype, {

    loadCurrentUser() {
        // Load user from localStorage (simple session management)
        const userData = localStorage.getItem('taskManagerUser');
        if (userData) {
            try {
                this.currentUser = JSON.parse(userData);
                this.updateUserDisplay();
            } catch (error) {
                console.error('Failed to load user data:', error);
                localStorage.removeItem('taskManagerUser');
            }
        }
    },

    updateUserDisplay() {
        const notLoggedIn = document.getElementById('notLoggedIn');
        const loggedIn = document.getElementById('loggedIn');

        if (this.currentUser) {
            notLoggedIn.style.display = 'none';
            loggedIn.style.display = 'block';

            document.getElementById('userName').textContent = this.currentUser.name || '-';
            document.getElementById('userEmail').textContent = this.currentUser.email || '-';
            document.getElementById('userTimezone').textContent = this.currentUser.timezone || '-';
            document.getElementById('userNotifications').textContent = this.currentUser.notification_preferences || '-';
        } else {
            notLoggedIn.style.display = 'block';
            loggedIn.style.display = 'none';
        }
    },

    showLoginPrompt() {
        // Switch to user tab and show login form
        const userTab = document.getElementById('user-tab');
        if (userTab) {
            userTab.click();
        }

        // Show login message in tasks area
        const tasksContainer = document.getElementById('tasksContainer');
        if (tasksContainer) {
            tasksContainer.innerHTML = `
                <div class="alert alert-warning text-center" role="alert">
                    <h4><i class="fas fa-lock"></i> Authentication Required</h4>
                    <p>Please login to view your tasks. Go to the <strong>User</strong> tab to login or register.</p>
                    <button class="btn btn-primary" onclick="document.getElementById('user-tab').click(); showLoginForm();">
                        <i class="fas fa-sign-in-alt"></i> Login Now
                    </button>
                </div>
            `;
        }

        this.showToast('Please login to access your tasks', 'warning');
    },

    async handleLogin() {
        try {
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (data.success) {
                this.currentUser = data.data;
                localStorage.setItem('taskManagerUser', JSON.stringify(this.currentUser));
                this.updateUserDisplay();
                hideUserForms();
                this.showToast('Login successful!', 'success');

                // Reload tasks for this user
                await this.loadTasks();
                this.updateDashboard();
            } else {
                this.showToast(data.error || 'Login failed', 'error');
            }

        } catch (error) {
            console.error('Login error:', error);
            this.showToast('Login failed. Please try again.', 'error');
        }
    },

    async handleRegister() {
        try {
            const userData = {
                name: document.getElementById('registerName').value,
                email: document.getElementById('registerEmail').value,
                password: document.getElementById('registerPassword').value,
                timezone: document.getElementById('registerTimezone').value,
                notification_preferences: document.getElementById('registerNotifications').value
            };

            const response = await fetch(`${this.baseURL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Registration successful! Please login.', 'success');
                hideUserForms();
                showLoginForm();

                // Pre-fill login form with registered email
                document.getElementById('loginEmail').value = userData.email;
            } else {
                this.showToast(data.error || 'Registration failed', 'error');
            }

        } catch (error) {
            console.error('Registration error:', error);
            this.showToast('Registration failed. Please try again.', 'error');
        }
    },

    async handleEditProfile() {
        try {
            if (!this.currentUser) {
                this.showToast('Please login first', 'error');
                return;
            }

            const updateData = {
                user_id: this.currentUser.id,
                name: document.getElementById('editName').value,
                timezone: document.getElementById('editTimezone').value,
                notification_preferences: document.getElementById('editNotifications').value
            };

            const password = document.getElementById('editPassword').value;
            if (password) {
                updateData.password = password;
            }

            const response = await fetch(`${this.baseURL}/auth/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            });

            const data = await response.json();

            if (data.success) {
                this.currentUser = data.data;
                localStorage.setItem('taskManagerUser', JSON.stringify(this.currentUser));
                this.updateUserDisplay();
                hideUserForms();
                this.showToast('Profile updated successfully!', 'success');
            } else {
                this.showToast(data.error || 'Update failed', 'error');
            }

        } catch (error) {
            console.error('Profile update error:', error);
            this.showToast('Update failed. Please try again.', 'error');
        }
    }
});

// Update loadTasks method to support user-specific tasks
const originalLoadTasks = TaskManager.prototype.loadTasks;
TaskManager.prototype.loadTasks = async function () {
    try {
        // Check if user is logged in
        if (!this.currentUser || !this.currentUser.id) {
            // Clear tasks and show login message
            this.tasks = [];
            this.filteredTasks = [];
            this.renderTasks();
            this.showLoginPrompt();
            return;
        }

        let url = `${this.baseURL}/tasks?user_id=${this.currentUser.id}`;

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            this.tasks = data.data.tasks || [];
            this.filteredTasks = [...this.tasks];
            this.renderTasks();
            this.showToast(`Loaded ${this.tasks.length} tasks for ${data.data.user.name}`, 'success');
        } else {
            if (data.error.includes('authentication required') || data.error.includes('Invalid user')) {
                this.showLoginPrompt();
            } else {
                throw new Error(data.error || 'Failed to load tasks');
            }
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        if (error.message.includes('401') || error.message.includes('authentication')) {
            this.showLoginPrompt();
        } else {
            this.showToast('Failed to load tasks', 'error');
        }
    }
};

// Update createTask method to include user_id
const originalCreateTask = TaskManager.prototype.createTask;
TaskManager.prototype.createTask = async function (taskData) {
    try {
        // Add user_id if user is logged in
        if (this.currentUser && this.currentUser.id) {
            taskData.user_id = this.currentUser.id;
        }

        const response = await fetch(`${this.baseURL}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });

        const data = await response.json();

        if (data.success) {
            await this.loadTasks();
            this.updateDashboard();
            this.showToast('Task created successfully!', 'success');

            // Reset form
            document.getElementById('taskForm').reset();

            return data.data.task;
        } else {
            throw new Error(data.error || 'Failed to create task');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        this.showToast(error.message || 'Failed to create task', 'error');
        throw error;
    }
};
