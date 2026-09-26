// Vesper Web UI - Real-time updates via SSE

class VesperUI {
    constructor() {
        this.stages = new Map();
        this.totalTests = 0;
        this.completedStages = 0;
        this.eventSource = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.connectionStatus = document.getElementById('connection-status');
        this.stagesContainer = document.getElementById('stages-container');
        this.overallStatus = document.getElementById('overall-status');
        this.totalDuration = document.getElementById('total-duration');
        this.diffContainer = document.getElementById('diff-container');
        
        // Summary elements
        this.summaryDuration = document.getElementById('summary-duration');
        this.summaryStages = document.getElementById('summary-stages');
        this.summaryTests = document.getElementById('summary-tests');
        this.summaryFindings = document.getElementById('summary-findings');
        
        this.connect();
    }
    
    connect() {
        this.updateConnectionStatus('connecting');
        
        this.eventSource = new EventSource('/events');
        
        this.eventSource.addEventListener('stage', (event) => {
            const data = JSON.parse(event.data);
            this.handleStageUpdate(data);
        });
        
        this.eventSource.addEventListener('complete', (event) => {
            const data = JSON.parse(event.data);
            this.handleComplete(data);
        });
        
        this.eventSource.addEventListener('error', (event) => {
            const data = JSON.parse(event.data);
            this.handleError(data);
        });
        
        this.eventSource.onopen = () => {
            this.updateConnectionStatus('connected');
            this.reconnectAttempts = 0;
        };
        
        this.eventSource.onerror = () => {
            this.updateConnectionStatus('error');
            this.eventSource.close();
            
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
            }
        };
    }
    
    updateConnectionStatus(status) {
        const dot = this.connectionStatus.querySelector('.status-dot');
        const text = this.connectionStatus.querySelector('.status-text');
        
        dot.className = 'status-dot';
        
        switch (status) {
            case 'connecting':
                text.textContent = 'Connecting...';
                break;
            case 'connected':
                dot.classList.add('connected');
                text.textContent = 'Connected';
                break;
            case 'error':
                dot.classList.add('error');
                text.textContent = 'Disconnected';
                break;
        }
    }
    
    handleStageUpdate(data) {
        const { stage, status, timestamp, ...details } = data;
        
        let stageElement = document.getElementById(`stage-${stage}`);
        
        if (!stageElement) {
            stageElement = this.createStageElement(stage, status, details);
            this.stagesContainer.appendChild(stageElement);
        } else {
            this.updateStageElement(stageElement, status, details);
        }
        
        this.stages.set(stage, { status, details, timestamp });
        
        // Update summary
        this.updateSummary(details);
        
        // Show diff when workflow is complete
        if (stage === 'report' && status === 'written') {
            this.showDiffViewer();
        }
    }
    
    createStageElement(stageName, status, details) {
        const element = document.createElement('div');
        element.id = `stage-${stageName}`;
        element.className = `stage-card ${status}`;
        
        element.innerHTML = `
            <div class="stage-header">
                <span class="stage-name">${this.formatStageName(stageName)}</span>
                <span class="stage-status ${status}">${status}</span>
            </div>
            <div class="stage-details">
                ${this.renderStageDetails(details)}
            </div>
        `;
        
        return element;
    }
    
    updateStageElement(element, status, details) {
        element.className = `stage-card ${status}`;
        
        const statusBadge = element.querySelector('.stage-status');
        statusBadge.className = `stage-status ${status}`;
        statusBadge.textContent = status;
        
        const detailsContainer = element.querySelector('.stage-details');
        detailsContainer.innerHTML = this.renderStageDetails(details);
    }
    
    renderStageDetails(details) {
        if (!details || Object.keys(details).length === 0) {
            return '<div class="duration">Waiting...</div>';
        }
        
        let html = '';
        
        if (details.counts) {
            const { tests, failures, errors, skipped } = details.counts;
            html += `<div class="test-counts">Tests: ${tests} | Failures: ${failures} | Errors: ${errors} | Skipped: ${skipped}</div>`;
        }
        
        if (details.duration_seconds) {
            html += `<div class="duration">Duration: ${details.duration_seconds}s</div>`;
        }
        
        if (details.note) {
            html += `<div class="note">${details.note}</div>`;
        }
        
        if (details.error) {
            html += `<div class="note" style="color: var(--error-color)">Error: ${details.error}</div>`;
        }
        
        return html;
    }
    
    updateSummary(details) {
        if (details.counts) {
            this.totalTests = Math.max(this.totalTests, details.counts.tests);
            this.summaryTests.textContent = this.totalTests;
        }
        
        // Count completed stages
        this.completedStages = this.stages.size;
        this.summaryStages.textContent = `${this.completedStages}/8`;
        
        // Update findings based on stage results
        const reproducedStages = Array.from(this.stages.values()).filter(s => s.status === 'reproduced').length;
        this.summaryFindings.textContent = reproducedStages > 0 ? `${reproducedStages} found` : 'None';
    }
    
    showDiffViewer() {
        // Show the actual bug vs fix diff
        this.diffContainer.innerHTML = `
            <div class="diff-viewer">
                <div class="diff-column">
                    <div class="diff-header">Original before repair</div>
                    <div class="diff-content">
                        <div class="diff-removed">        if (!today.isBefore(expiry)) return subtotalCents;  // SEEDED BUG (Sprint 2): expiry day incorrectly excluded — violates R3 "inclusive"</div>
                        <div class="diff-removed">        // Split before multiplying to avoid overflow for large subtotals.</div>
                    </div>
                </div>
                <div class="diff-column">
                    <div class="diff-header">Candidate proposed repair</div>
                    <div class="diff-content">
                        <div class="diff-added">        if (today.isAfter(expiry)) return subtotalCents;  // R3: expiry is inclusive; discount expires only after the expiry date</div>
                        <div class="diff-added">        // Split before multiplying to avoid overflow for large subtotals</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    formatStageName(stageName) {
        // Convert stage names to readable format
        return stageName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    handleComplete(data) {
        const { status, duration } = data;
        
        this.overallStatus.className = `status-badge ${status === 'ok' ? 'passed' : 'failed'}`;
        this.overallStatus.textContent = status === 'ok' ? 'Passed' : 'Failed';
        this.totalDuration.textContent = `${duration}s`;
        this.summaryDuration.textContent = `${duration}s`;
        
        this.eventSource.close();
        this.updateConnectionStatus('connected');
    }
    
    handleError(data) {
        const { message } = data;
        
        this.overallStatus.className = 'status-badge failed';
        this.overallStatus.textContent = 'Error';
        this.totalDuration.textContent = message;
        
        this.eventSource.close();
        this.updateConnectionStatus('error');
    }
}

// Initialize the UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VesperUI();
});
