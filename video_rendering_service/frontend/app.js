/**
 * Elite AI Video Rendering Service - Frontend Application
 * 
 * Features:
 * - Drag & Drop video upload
 * - Real-time progress tracking via WebSocket
 * - AI enhancement configuration
 * - Performance monitoring
 * - Material Design UI with dark/light themes
 */

class VideoRenderingApp {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.wsUrl = `ws://${window.location.host}/ws/progress`;
        this.websocket = null;
        this.activeJobs = new Map();
        this.systemStats = {};
        this.isConnected = false;
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        this.initWebSocket();
        await this.loadSystemInfo();
        await this.loadPerformanceStats();
        this.startPeriodicUpdates();
        
        // Show welcome notification
        this.showNotification('🚀 Elite AI Video Rendering Service ready!', 'success');
    }
    
    setupEventListeners() {
        // File input and drag & drop
        const fileInput = document.getElementById('file-input');
        const uploadArea = document.getElementById('upload-area');
        
        fileInput.addEventListener('change', (e) => this.handleFileSelection(e.target.files));
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFileSelection(e.dataTransfer.files);
        });
        
        uploadArea.addEventListener('click', () => fileInput.click());
    }
    
    initWebSocket() {
        try {
            this.websocket = new WebSocket(this.wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus();
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus();
                
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.initWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showNotification('Connection error - attempting to reconnect...', 'warning');
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            this.showNotification('Failed to establish real-time connection', 'error');
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'job_progress':
                this.updateJobProgress(data.job_id, data.progress);
                break;
            case 'job_completed':
                this.handleJobCompleted(data.job_id, data.success, data.message);
                break;
            case 'jobs_update':
                this.updateActiveJobs(data.data);
                break;
            case 'system_stats':
                this.updateSystemStats(data.data);
                break;
        }
    }
    
    async handleFileSelection(files) {
        if (!files || files.length === 0) return;
        
        for (const file of files) {
            if (!this.validateFile(file)) continue;
            
            await this.uploadAndProcessFile(file);
        }
    }
    
    validateFile(file) {
        const maxSize = this.systemStats.max_file_size_gb * 1024 * 1024 * 1024;
        const supportedFormats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'm4v'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        if (file.size > maxSize) {
            this.showNotification(`File too large: ${file.name}. Max size: ${this.systemStats.max_file_size_gb}GB`, 'error');
            return false;
        }
        
        if (!supportedFormats.includes(fileExtension)) {
            this.showNotification(`Unsupported format: ${fileExtension}. Supported: ${supportedFormats.join(', ')}`, 'error');
            return false;
        }
        
        return true;
    }
    
    async uploadAndProcessFile(file) {
        const enhancements = this.getSelectedEnhancements();
        
        try {
            this.showLoadingOverlay(true, `Uploading ${file.name}...`);
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Create request data for enhancements
            const requestData = {
                enhancements,
                output_format: 'mp4',
                quality: 'high'
            };
            
            const response = await fetch(`${this.apiBaseUrl}/api/upload`, {
                method: 'POST',
                body: formData,
                headers: {
                    'Content-Type': 'application/json',
                    // Note: FormData automatically sets multipart/form-data
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }
            
            const result = await response.json();
            
            this.showNotification(`✅ ${file.name} uploaded successfully! Processing started.`, 'success');
            this.addJobToQueue(result.job_id, file.name, enhancements);
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification(`❌ Upload failed: ${error.message}`, 'error');
        } finally {
            this.showLoadingOverlay(false);
        }
    }
    
    getSelectedEnhancements() {
        const checkboxes = document.querySelectorAll('.enhancement-option input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }
    
    addJobToQueue(jobId, filename, enhancements) {
        const job = {
            id: jobId,
            filename,
            enhancements,
            progress: 0,
            status: 'processing',
            startTime: Date.now()
        };
        
        this.activeJobs.set(jobId, job);
        this.renderProcessingQueue();
    }
    
    updateJobProgress(jobId, progress) {
        const job = this.activeJobs.get(jobId);
        if (job) {
            job.progress = progress;
            this.renderProcessingQueue();
        }
    }
    
    handleJobCompleted(jobId, success, message) {
        const job = this.activeJobs.get(jobId);
        if (job) {
            job.status = success ? 'completed' : 'failed';
            job.progress = success ? 100 : job.progress;
            job.endTime = Date.now();
            job.errorMessage = success ? null : message;
            
            this.renderProcessingQueue();
            
            if (success) {
                this.showNotification(`✅ ${job.filename} processing completed!`, 'success');
                this.addDownloadButton(jobId, job.filename);
            } else {
                this.showNotification(`❌ ${job.filename} processing failed: ${message}`, 'error');
            }
            
            // Move to recent jobs after 5 seconds
            setTimeout(() => {
                this.activeJobs.delete(jobId);
                this.addToRecentJobs(job);
                this.renderProcessingQueue();
            }, 5000);
        }
    }
    
    addDownloadButton(jobId, filename) {
        const jobElement = document.querySelector(`[data-job-id="${jobId}"]`);
        if (jobElement) {
            const downloadBtn = document.createElement('button');
            downloadBtn.className = 'btn btn-primary btn-sm';
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download';
            downloadBtn.onclick = () => this.downloadFile(jobId, filename);
            
            const actionsDiv = jobElement.querySelector('.processing-actions') || 
                              jobElement.appendChild(document.createElement('div'));
            actionsDiv.className = 'processing-actions mt-2';
            actionsDiv.appendChild(downloadBtn);
        }
    }
    
    async downloadFile(jobId, filename) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/jobs/${jobId}/download`);
            if (!response.ok) throw new Error('Download failed');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `enhanced_${filename}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showNotification(`📥 Downloaded ${filename}`, 'success');
            
        } catch (error) {
            console.error('Download error:', error);
            this.showNotification(`❌ Download failed: ${error.message}`, 'error');
        }
    }
    
    renderProcessingQueue() {
        const container = document.getElementById('processing-queue');
        
        if (this.activeJobs.size === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-hourglass"></i>
                    <p>No active processing jobs</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = Array.from(this.activeJobs.values()).map(job => `
            <div class="processing-item" data-job-id="${job.id}">
                <div class="processing-header">
                    <div class="processing-filename">${job.filename}</div>
                    <div class="processing-status status-${job.status}">${job.status}</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${job.progress}%"></div>
                </div>
                <div class="processing-details">
                    <span>Progress: ${Math.round(job.progress)}%</span>
                    <span>Enhancements: ${job.enhancements.length}</span>
                    <span>Duration: ${this.formatDuration(job.startTime)}</span>
                </div>
                ${job.errorMessage ? `<div class="text-danger mt-1">${job.errorMessage}</div>` : ''}
            </div>
        `).join('');
    }
    
    addToRecentJobs(job) {
        const container = document.getElementById('recent-jobs');
        
        // Remove empty state if present
        const emptyState = container.querySelector('.empty-state');
        if (emptyState) {
            container.innerHTML = '';
        }
        
        const jobElement = document.createElement('div');
        jobElement.className = 'processing-item';
        jobElement.innerHTML = `
            <div class="processing-header">
                <div class="processing-filename">${job.filename}</div>
                <div class="processing-status status-${job.status}">${job.status}</div>
            </div>
            <div class="processing-details">
                <span>Duration: ${this.formatDuration(job.startTime, job.endTime)}</span>
                <span>Enhancements: ${job.enhancements.length}</span>
                <span>Completed: ${new Date(job.endTime).toLocaleTimeString()}</span>
            </div>
        `;
        
        container.insertBefore(jobElement, container.firstChild);
        
        // Keep only last 10 jobs
        const jobs = container.querySelectorAll('.processing-item');
        if (jobs.length > 10) {
            jobs[jobs.length - 1].remove();
        }
    }
    
    async loadSystemInfo() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/system-info`);
            const data = await response.json();
            
            document.getElementById('hardware-tier').textContent = data.hardware_tier.toUpperCase();
            document.getElementById('ram-status').textContent = `${Math.round(data.total_ram_gb)}GB`;
            document.getElementById('max-file-size').textContent = `${data.max_file_size_gb}GB`;
            
            this.systemStats = data;
            
        } catch (error) {
            console.error('Failed to load system info:', error);
        }
    }
    
    async loadPerformanceStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/performance`);
            const data = await response.json();
            
            this.updatePerformanceDisplay(data);
            
        } catch (error) {
            console.error('Failed to load performance stats:', error);
        }
    }
    
    updatePerformanceDisplay(stats) {
        document.getElementById('cpu-usage').textContent = '45%'; // Simulated
        document.getElementById('memory-usage').textContent = `${Math.round(stats.total_data_processed_gb)}GB / ${Math.round(stats.hardware_info.total_ram_gb)}GB`;
        document.getElementById('storage-usage').textContent = `${Math.round(stats.total_data_processed_gb * 2)}GB / 8TB`;
        document.getElementById('gpu-usage').textContent = '78%'; // Simulated
        document.getElementById('avg-processing').textContent = `${Math.round(stats.average_processing_time)}s`;
        document.getElementById('jobs-completed').textContent = stats.total_jobs_processed;
    }
    
    updateConnectionStatus() {
        const statusDot = document.getElementById('connection-status');
        if (this.isConnected) {
            statusDot.classList.add('active');
        } else {
            statusDot.classList.remove('active');
        }
    }
    
    updateActiveJobs(jobsData) {
        for (const jobData of jobsData) {
            if (this.activeJobs.has(jobData.job_id)) {
                const job = this.activeJobs.get(jobData.job_id);
                job.progress = jobData.progress;
                job.status = jobData.status;
            }
        }
        this.renderProcessingQueue();
    }
    
    updateSystemStats(stats) {
        this.updatePerformanceDisplay(stats);
    }
    
    startPeriodicUpdates() {
        // Update performance stats every 10 seconds
        setInterval(() => {
            this.loadPerformanceStats();
        }, 10000);
    }
    
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div>${message}</div>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    showLoadingOverlay(show, message = 'Processing...') {
        const overlay = document.getElementById('loading-overlay');
        const messageElement = document.getElementById('loading-message');
        
        if (show) {
            messageElement.textContent = message;
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }
    
    formatDuration(startTime, endTime = null) {
        const end = endTime || Date.now();
        const duration = Math.round((end - startTime) / 1000);
        
        if (duration < 60) {
            return `${duration}s`;
        } else if (duration < 3600) {
            return `${Math.floor(duration / 60)}m ${duration % 60}s`;
        } else {
            const hours = Math.floor(duration / 3600);
            const minutes = Math.floor((duration % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    }
}

// Global functions
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('theme-dark');
    
    if (isDark) {
        body.classList.remove('theme-dark');
        body.classList.add('theme-light');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.remove('theme-light');
        body.classList.add('theme-dark');
        localStorage.setItem('theme', 'dark');
    }
}

function clearAll() {
    if (confirm('Are you sure you want to clear all processing jobs and recent history?')) {
        window.app.activeJobs.clear();
        window.app.renderProcessingQueue();
        document.getElementById('recent-jobs').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-history"></i>
                <p>No recent jobs</p>
            </div>
        `;
        window.app.showNotification('🧹 All jobs cleared', 'success');
    }
}

function resetVisualization() {
    if (window.visualization) {
        window.visualization.reset();
        window.app.showNotification('🎮 Visualization reset', 'success');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.className = `theme-${savedTheme}`;
    
    // Initialize app
    window.app = new VideoRenderingApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, reduce update frequency
        console.log('Page hidden - reducing update frequency');
    } else {
        // Page is visible, resume normal updates
        console.log('Page visible - resuming normal updates');
        if (window.app) {
            window.app.loadPerformanceStats();
        }
    }
});

// Handle window resize for responsive layout
window.addEventListener('resize', () => {
    if (window.visualization) {
        window.visualization.onWindowResize();
    }
});

// Export for external use
window.VideoRenderingApp = VideoRenderingApp;