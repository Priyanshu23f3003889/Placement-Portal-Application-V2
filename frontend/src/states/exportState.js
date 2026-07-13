import { defineStore } from 'pinia';
import { useAuthStore } from './authState';

export const useExportStore = defineStore('export', {
    state: () => ({
        exportTaskId: localStorage.getItem('exportTaskId') || null,
        exportStatus: localStorage.getItem('exportTaskId') ? 'exporting' : 'idle',
        globalMessage: null,
        globalMessageType: 'success',
        pollTimeout: null
    }),
    actions: {
        async startPolling() {
            if (!this.exportTaskId) return;
            if (this.pollTimeout) clearTimeout(this.pollTimeout);
            
            const authStore = useAuthStore();
            try {
                const response = await fetch(`/api/student/applications/export/status/${this.exportTaskId}`, {
                    headers: {
                        Authorization: `Bearer ${authStore.token}`
                    }
                });
                
                const data = await response.json();
                if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
                    this.exportStatus = 'idle';
                    this.globalMessage = data.status === 'SUCCESS' ? "Export complete! Email sent successfully." : "Export task failed.";
                    this.globalMessageType = data.status === 'SUCCESS' ? 'success' : 'danger';
                    
                    localStorage.removeItem('exportTaskId');
                    this.exportTaskId = null;
                } else {
                    this.exportStatus = 'exporting';
                    this.pollTimeout = setTimeout(() => this.startPolling(), 2000);
                }
            } catch (err) {
                console.error("Error checking export status:", err);
            }
        },
        setTask(taskId) {
            this.exportTaskId = taskId;
            this.exportStatus = 'exporting';
            localStorage.setItem('exportTaskId', taskId);
            this.startPolling();
        },
        clearMessage() {
            this.globalMessage = null;
        }
    }
});
