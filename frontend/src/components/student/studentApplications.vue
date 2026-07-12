<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useAuthStore } from "../../states/authState";

const authStore = useAuthStore();
const applications = ref([]);
const errmsg = ref("");
const searchQuery = ref("");
const exportTaskId = ref(localStorage.getItem('exportTaskId') || null);
const exportStatus = ref(exportTaskId.value ? 'exporting' : 'idle');
let pollTimeout = null;
let isComponentMounted = true;

const filteredApplications = computed(() => {
    if (!searchQuery.value) return applications.value;
    const query = searchQuery.value.toLowerCase();
    return applications.value.filter(
        (a) =>
            a.id.toString().includes(query) ||
            a.companyName.toLowerCase().includes(query) ||
        a.jobTitle.toLowerCase().includes(query) ||
            a.driveId.toString().includes(query)
    );
});

const getStatusClass = (status) => {
    if (status === "REJECTED") return "text-danger";
    if (status === "SHORTLISTED") return "text-success";
    if (status === "SELECTED") return "text-success fw-bold";
    if (status === "APPLIED") return "text-warning";
    return "";
};

const fetchApplications = async () => {
    try {
        const response = await fetch("/api/student/applications", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            applications.value = await response.json();
        } else {
            const errorData = await response.json();
            errmsg.value =
                errorData.message ||
                errorData.msg ||
                "Failed to fetch Applications";
        }
    } catch (err) {
        errmsg.value = "Network error occurred";
    }
};

onMounted(async () => {
    if (exportTaskId.value) {
        checkExportStatus();
    }
    await fetchApplications();
});

onUnmounted(() => {
    isComponentMounted = false;
    if (pollTimeout) clearTimeout(pollTimeout);
});

const checkExportStatus = async () => {
    if (!exportTaskId.value || !isComponentMounted) return;
    try {
        const response = await fetch(`/api/student/applications/export/status/${exportTaskId.value}`, {
            headers: {
                Authorization: `Bearer ${authStore.token}`
            }
        });
        
        if (!isComponentMounted) return;
        
        const data = await response.json();
        if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
            exportStatus.value = data.status === 'SUCCESS' ? 'done' : 'idle';
            if (data.status === 'FAILURE') {
                errmsg.value = "Export task failed.";
            }
            localStorage.removeItem('exportTaskId');
            exportTaskId.value = null;
        } else {
            exportStatus.value = 'exporting';
            if (isComponentMounted) {
                pollTimeout = setTimeout(checkExportStatus, 2000);
            }
        }
    } catch (err) {
        console.error("Error checking export status:", err);
    }
};

const exportData = async () => {
    if (exportStatus.value === 'exporting') return;
    exportStatus.value = 'exporting';
    try {
        const response = await fetch('/api/student/applications/export', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${authStore.token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            if (data.taskId) {
                exportTaskId.value = data.taskId;
                localStorage.setItem('exportTaskId', data.taskId);
                checkExportStatus();
            } else {
                exportStatus.value = 'done';
            }
        } else {
            exportStatus.value = 'idle';
            errmsg.value = "Failed to start export.";
        }
    } catch (err) {
        exportStatus.value = 'idle';
        errmsg.value = "Network error occurred.";
    }
};
</script>

<template>
    <div class="container-lg mt-3">
        <div class="d-flex justify-content-between align-items-center">
            <h1>
                Applications
                <span class="badge bg-secondary fs-6 align-middle">{{
                    filteredApplications.length
                }}</span>
            </h1>

            <button 
                class="btn" 
                :class="exportStatus === 'done' ? 'btn-success text-white' : 'btn-info'"
                :disabled="exportStatus === 'exporting'"
                @click="exportData"
            >
                {{ exportStatus === 'exporting' ? 'Exporting...' : exportStatus === 'done' ? 'Email sent' : 'Export data' }}
            </button>
            
            <input
                type="text"
                class="form-control w-auto"
                placeholder="Search by ID, Name, Company, or Job Title"
                v-model="searchQuery"
            />
        </div>
        <hr />
        <p v-if="errmsg" class="text-danger">{{ errmsg }}</p>
    </div>

    <div class="container-lg d-flex flex-wrap">
        <div class="card m-3" v-for="a in filteredApplications">
            <div class="card-body">
                <h2 class="card-title">{{ a.companyName }}</h2>
                <div class="text-danger mb-3 fw-bold" v-if="!a.isApproved">Blacklisted</div>
                <ul class="card-text">
                    <li>
                        <h5>Application ID : {{ a.id }}</h5>
                    </li>
                    <li>
                        <h5>Drive ID : {{ a.driveId }}</h5>
                    </li>
                    <li>
                        <h5>Job Title : {{ a.jobTitle }}</h5>
                    </li>
                    <li>
                        <h5>
                            Resume :
                            <a :href="a.resumeUrl" target="_blank"
                                >View Resume</a
                            >
                        </h5>
                    </li>
                    <li>
                        <h5>Applied : {{ a.applicationDate }}</h5>
                    </li>
                    <li>
                        <h5>
                            Status :
                            <span :class="getStatusClass(a.status)">{{
                                a.status
                            }}</span>
                        </h5>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>
