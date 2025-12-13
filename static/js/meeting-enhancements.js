// Meeting Conflicts Detection and User Experience Enhancements

class MeetingConflictDetector {
    constructor() {
        this.conflicts = new Set();
        this.init();
    }

    init() {
        // Check for conflicts when page loads
        this.checkAllConflicts();
        
        // Set up real-time conflict checking
        this.setupConflictChecking();
        
        // Initialize bulk operations
        this.initBulkOperations();
    }

    checkAllConflicts() {
        const meetings = this.getMeetingsFromDOM();
        const conflicts = this.detectConflicts(meetings);
        this.displayConflicts(conflicts);
    }

    getMeetingsFromDOM() {
        const meetingElements = document.querySelectorAll('[data-meeting-id]');
        const meetings = [];
        
        meetingElements.forEach(element => {
            const meeting = {
                id: element.dataset.meetingId,
                date: element.dataset.meetingDate,
                startTime: element.dataset.meetingStartTime,
                endTime: element.dataset.meetingEndTime,
                chairId: element.dataset.chairId,
                element: element
            };
            meetings.push(meeting);
        });
        
        return meetings;
    }

    detectConflicts(meetings) {
        const conflicts = [];
        
        // Group meetings by chair
        const chairMeetings = {};
        meetings.forEach(meeting => {
            if (meeting.chairId) {
                if (!chairMeetings[meeting.chairId]) {
                    chairMeetings[meeting.chairId] = [];
                }
                chairMeetings[meeting.chairId].push(meeting);
            }
        });
        
        // Check for time conflicts
        Object.values(chairMeetings).forEach(chairMeetingList => {
            for (let i = 0; i < chairMeetingList.length; i++) {
                for (let j = i + 1; j < chairMeetingList.length; j++) {
                    const meeting1 = chairMeetingList[i];
                    const meeting2 = chairMeetingList[j];
                    
                    if (this.hasTimeConflict(meeting1, meeting2)) {
                        conflicts.push({
                            type: 'time_conflict',
                            meetings: [meeting1, meeting2],
                            message: 'Chair has conflicting meeting times'
                        });
                    }
                }
            }
        });
        
        // Check for same-day overcommitment
        Object.values(chairMeetings).forEach(chairMeetingList => {
            const dailyCounts = {};
            chairMeetingList.forEach(meeting => {
                const date = meeting.date;
                dailyCounts[date] = (dailyCounts[date] || 0) + 1;
            });
            
            Object.entries(dailyCounts).forEach(([date, count]) => {
                if (count > 2) { // More than 2 meetings per day
                    const dayMeetings = chairMeetingList.filter(m => m.date === date);
                    conflicts.push({
                        type: 'overcommitment',
                        meetings: dayMeetings,
                        message: `Chair has ${count} meetings on ${date}`
                    });
                }
            });
        });
        
        return conflicts;
    }

    hasTimeConflict(meeting1, meeting2) {
        // Same date check
        if (meeting1.date !== meeting2.date) return false;
        
        const start1 = this.parseTime(meeting1.startTime);
        const end1 = this.parseTime(meeting1.endTime);
        const start2 = this.parseTime(meeting2.startTime);
        const end2 = this.parseTime(meeting2.endTime);
        
        // Check for overlap
        return (start1 < end2) && (start2 < end1);
    }

    parseTime(timeString) {
        if (!timeString) return null;
        const [hours, minutes] = timeString.split(':').map(Number);
        return hours * 60 + minutes; // Convert to minutes for easy comparison
    }

    displayConflicts(conflicts) {
        // Remove existing conflict indicators
        document.querySelectorAll('.conflict-indicator').forEach(el => el.remove());
        
        conflicts.forEach(conflict => {
            conflict.meetings.forEach(meeting => {
                this.addConflictIndicator(meeting.element, conflict);
            });
        });
        
        // Show conflicts summary if any
        if (conflicts.length > 0) {
            this.showConflictsSummary(conflicts);
        }
    }

    addConflictIndicator(element, conflict) {
        const indicator = document.createElement('div');
        indicator.className = 'conflict-indicator alert alert-warning alert-sm p-2 mt-1';
        indicator.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <small>${conflict.message}</small>
        `;
        element.appendChild(indicator);
    }

    showConflictsSummary(conflicts) {
        const existingSummary = document.getElementById('conflicts-summary');
        if (existingSummary) existingSummary.remove();
        
        const summary = document.createElement('div');
        summary.id = 'conflicts-summary';
        summary.className = 'alert alert-danger mb-3';
        summary.innerHTML = `
            <h5><i class="fas fa-exclamation-triangle"></i> Meeting Conflicts Detected</h5>
            <p>Found ${conflicts.length} conflict(s) that need attention:</p>
            <ul class="mb-2">
                ${conflicts.map(c => `<li>${c.message}</li>`).join('')}
            </ul>
            <button class="btn btn-sm btn-outline-danger" onclick="conflictDetector.resolveConflicts()">
                <i class="fas fa-tools"></i> Help Resolve
            </button>
        `;
        
        // Insert at top of main content
        const mainContent = document.querySelector('.container, .container-fluid');
        if (mainContent) {
            mainContent.insertBefore(summary, mainContent.firstChild);
        }
    }

    setupConflictChecking() {
        // Check conflicts when meetings change
        const observer = new MutationObserver(() => {
            this.checkAllConflicts();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['data-chair-id', 'data-meeting-date', 'data-meeting-start-time']
        });
    }

    resolveConflicts() {
        const modal = new bootstrap.Modal(document.getElementById('conflictResolutionModal') || this.createConflictModal());
        modal.show();
    }

    createConflictModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'conflictResolutionModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Resolve Meeting Conflicts</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Here are some options to resolve the detected conflicts:</p>
                        <div class="accordion" id="resolutionAccordion">
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#autoResolve">
                                        <i class="fas fa-magic me-2"></i> Auto-Resolve (Recommended)
                                    </button>
                                </h2>
                                <div id="autoResolve" class="accordion-collapse collapse show">
                                    <div class="accordion-body">
                                        <p>Automatically suggest alternative chairs for conflicting meetings.</p>
                                        <button class="btn btn-primary" onclick="conflictDetector.autoResolve()">
                                            <i class="fas fa-wand-magic-sparkles"></i> Suggest Alternatives
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#manualResolve">
                                        <i class="fas fa-hand-paper me-2"></i> Manual Resolution
                                    </button>
                                </h2>
                                <div id="manualResolve" class="accordion-collapse collapse">
                                    <div class="accordion-body">
                                        <p>Manually reassign chairs or adjust meeting times.</p>
                                        <div id="manualOptions">
                                            <!-- Dynamic content populated by JS -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        return modal;
    }

    autoResolve() {
        // This would integrate with backend API to suggest alternatives
        this.showToast('Auto-resolution feature would suggest alternative chairs based on availability and preferences.', 'info');
    }

    initBulkOperations() {
        this.createBulkOperationsToolbar();
        this.setupBulkSelection();
    }

    createBulkOperationsToolbar() {
        const toolbar = document.createElement('div');
        toolbar.id = 'bulk-operations-toolbar';
        toolbar.className = 'bulk-operations-toolbar';
        toolbar.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1050;
            display: none;
            min-width: 300px;
        `;
        
        toolbar.innerHTML = `
            <div class="d-flex align-items-center justify-content-between">
                <span id="selection-count" class="text-muted">0 selected</span>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="bulkOperations.exportSelected()">
                        <i class="fas fa-download"></i> Export
                    </button>
                    <button class="btn btn-outline-warning" onclick="bulkOperations.editSelected()">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-outline-danger" onclick="bulkOperations.deleteSelected()">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                    <button class="btn btn-outline-secondary" onclick="bulkOperations.clearSelection()">
                        <i class="fas fa-times"></i> Clear
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(toolbar);
    }

    setupBulkSelection() {
        // Add checkboxes to meeting rows
        const meetingRows = document.querySelectorAll('[data-meeting-id]');
        meetingRows.forEach(row => {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'bulk-select-checkbox form-check-input me-2';
            checkbox.dataset.meetingId = row.dataset.meetingId;
            
            checkbox.addEventListener('change', this.updateBulkToolbar.bind(this));
            
            // Insert checkbox at beginning of row
            row.insertBefore(checkbox, row.firstChild);
        });
        
        // Add select all checkbox
        this.addSelectAllCheckbox();
    }

    addSelectAllCheckbox() {
        const tableHeader = document.querySelector('thead tr');
        if (tableHeader) {
            const selectAllCell = document.createElement('th');
            selectAllCell.innerHTML = '<input type="checkbox" id="select-all" class="form-check-input" title="Select All">';
            tableHeader.insertBefore(selectAllCell, tableHeader.firstChild);
            
            document.getElementById('select-all').addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('.bulk-select-checkbox');
                checkboxes.forEach(cb => cb.checked = e.target.checked);
                this.updateBulkToolbar();
            });
        }
    }

    updateBulkToolbar() {
        const selected = document.querySelectorAll('.bulk-select-checkbox:checked');
        const toolbar = document.getElementById('bulk-operations-toolbar');
        const countSpan = document.getElementById('selection-count');
        
        if (selected.length > 0) {
            toolbar.style.display = 'block';
            countSpan.textContent = `${selected.length} selected`;
        } else {
            toolbar.style.display = 'none';
        }
    }

    showToast(message, type = 'success') {
        // Create and show bootstrap toast
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast element after hiding
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1060';
        document.body.appendChild(container);
        return container;
    }
}

// Bulk Operations Manager
class BulkOperations {
    exportSelected() {
        const selectedIds = this.getSelectedIds();
        if (selectedIds.length === 0) return;
        
        // Create download link
        const params = new URLSearchParams();
        selectedIds.forEach(id => params.append('ids[]', id));
        
        const url = `/admin/meetings/export?${params.toString()}`;
        window.open(url, '_blank');
    }

    editSelected() {
        const selectedIds = this.getSelectedIds();
        if (selectedIds.length === 0) return;
        
        if (selectedIds.length === 1) {
            // Edit single meeting
            window.location.href = `/admin/meetings/${selectedIds[0]}/edit`;
        } else {
            // Bulk edit modal
            this.showBulkEditModal(selectedIds);
        }
    }

    deleteSelected() {
        const selectedIds = this.getSelectedIds();
        if (selectedIds.length === 0) return;
        
        if (confirm(`Are you sure you want to delete ${selectedIds.length} meeting(s)? This action cannot be undone.`)) {
            this.performBulkDelete(selectedIds);
        }
    }

    clearSelection() {
        document.querySelectorAll('.bulk-select-checkbox:checked').forEach(cb => cb.checked = false);
        document.getElementById('select-all').checked = false;
        conflictDetector.updateBulkToolbar();
    }

    getSelectedIds() {
        return Array.from(document.querySelectorAll('.bulk-select-checkbox:checked'))
                    .map(cb => cb.dataset.meetingId);
    }

    showBulkEditModal(selectedIds) {
        // Implementation for bulk edit modal
        conflictDetector.showToast(`Bulk edit for ${selectedIds.length} meetings would open here`, 'info');
    }

    async performBulkDelete(selectedIds) {
        try {
            const response = await fetch('/admin/meetings/bulk-delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content')
                },
                body: JSON.stringify({ meeting_ids: selectedIds })
            });
            
            if (response.ok) {
                conflictDetector.showToast(`Successfully deleted ${selectedIds.length} meetings`, 'success');
                window.location.reload();
            } else {
                throw new Error('Failed to delete meetings');
            }
        } catch (error) {
            conflictDetector.showToast('Error deleting meetings. Please try again.', 'danger');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.conflictDetector = new MeetingConflictDetector();
    window.bulkOperations = new BulkOperations();
    
    // Enhanced error handling
    window.addEventListener('error', function(e) {
        console.error('Application error:', e.error);
        conflictDetector.showToast('An unexpected error occurred. Please refresh the page.', 'danger');
    });
    
    // Enhanced form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                conflictDetector.showToast('Please correct the errors in the form', 'warning');
            }
            this.classList.add('was-validated');
        });
    });
});