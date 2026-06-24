<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "../../states/authState";

const authStore = useAuthStore();
const applications = ref([]);
const errmsg = ref("");
const searchQuery = ref("");

const filteredApplications = computed(() => {
    if (!searchQuery.value) return applications.value;
    const query = searchQuery.value.toLowerCase();
    return applications.value.filter(
        (a) =>
            a.name.toLowerCase().includes(query) ||
            a.id.toString().includes(query) ||
            a.companyName.toLowerCase().includes(query) ||
            a.jobTitle.toLowerCase().includes(query),
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
        const response = await fetch("/api/company/applications", {
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

const changeStatus = async (appId, rejected) => {
    try {
        const response = await fetch(`/api/company/applications/changestatus/${appId}/${rejected}`, {
            method: "PATCH",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
          fetchApplications();
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

function getButtonText(s) {
  if (s === "APPLIED") {
    return "Shortlist";
  } else if (s === "SHORTLISTED") {
    return "Select";
  } else if (s === "REJECTED") {
    return "Shortlist Again";
  }
};

onMounted(async () => {
    await fetchApplications();
});
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
        <div class="card m-3" v-for="a in filteredApplications" :key="a.id">
            <div class="card-body">
                <h2 class="card-title">{{ a.name }}</h2>
                <ul class="card-text">
                    <li>
                        <h5>Student ID : {{ a.studentId }}</h5>
                    </li>
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
                <div class="d-flex gap-2 ">
                    <button v-if = "a.status !== 'SELECTED'"
                        class="btn btn-success"
                        @click = "changeStatus(a.id, 0)"
                    >
                       {{ getButtonText(a.status) }}
                    </button>

                    <button 
                        v-if = "a.status !== 'REJECTED'"
                        class="btn btn-danger"
                        @click = "changeStatus(a.id, 1)"
                    >
                       Reject
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
