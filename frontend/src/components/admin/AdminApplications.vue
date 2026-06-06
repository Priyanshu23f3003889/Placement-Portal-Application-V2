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
        const response = await fetch("/api/admin/applications", {
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
    await fetchApplications();
});
</script>

<template>
    <div class="container-lg mt-3">
        <div class="d-flex justify-content-between align-items-center">
            <h1>Applications</h1>
            <input
                type="text"
                class="form-control w-auto"
                placeholder="Search by ID or Name or job title"
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
                            <a
                                :href="a.resumeUrl"
                                target="_blank"
                                >View Resume</a
                            >
                        </h5>
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
