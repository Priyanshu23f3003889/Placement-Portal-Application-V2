<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "../../states/authState";

const authStore = useAuthStore();
const drives = ref([]);
const errmsg = ref("");
const searchQuery = ref("");

const filteredDrives = computed(() => {
    if (!searchQuery.value) return drives.value;
    const query = searchQuery.value.toLowerCase();
    return drives.value.filter(
        (d) =>
            (d.jobTitle && d.jobTitle.toLowerCase().includes(query)) ||
            (d.companyName && d.companyName.toLowerCase().includes(query)) ||
            (d.id && d.id.toString().includes(query)),
    );
});

const fetchDrives = async () => {
    try {
        const response = await fetch("/api/admin/Drives", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            drives.value = await response.json();
        } else {
            const errorData = await response.json();
            errmsg.value =
                errorData.message ||
                errorData.msg ||
                "Failed to fetch Drives Data";
        }
    } catch (err) {
        errmsg.value = "Network error occurred";
    }
};

const toggleApproval = async (id) => {
    try {
        const response = await fetch(
            `/api/admin/drives/${id}/toggle-approval`,
            {
                method: "PATCH",
                headers: {
                    Authorization: `Bearer ${authStore.token}`,
                    "Content-Type": "application/json",
                },
            },
        );
        if (response.ok) {
            await fetchDrives();
        } else {
            const errorData = await response.json();
            errmsg.value =
                errorData.message || "Failed to toggle approval status";
        }
    } catch (err) {
        errmsg.value = "Network error occurred";
    }
};

onMounted(async () => {
    await fetchDrives();
});
</script>

<template>
    <div class="container-lg mt-3">
        <div class="d-flex justify-content-between align-items-center">
            <h1>Drives</h1>
            <input
                type="text"
                class="form-control w-auto"
                placeholder="Search by ID, Job Title or Company Name..."
                v-model="searchQuery"
            />
        </div>
        <hr />
        <p v-if="errmsg" class="text-danger">{{ errmsg }}</p>
    </div>

    <div class="container-lg d-flex flex-wrap">
        <div class="card m-3" v-for="d in filteredDrives" :key="d.id">
            <div class="card-body">
                <h2 class="card-title">{{ d.jobTitle || d.joTitle }}</h2>
                <ul class="card-text">
                    <h5>{{ d.jobDescription }}</h5>
                    <li>
                        <h5>Drive ID : {{ d.id }}</h5>
                    </li>
                    <li>
                        <h5>Company Name : {{ d.companyName }}</h5>
                    </li>
                    <li>
                        <h5>Branch : {{ d.branch }}</h5>
                    </li>
                    <li>
                        <h5>Minimum CGPA : {{ d.cgpa }}</h5>
                    </li>
                    <li>
                        <h5>Deadline : {{ d.deadline }}</h5>
                    </li>

                    <li>
                        <h5>
                            Status :
                            <span
                                :class="{
                                    'text-success': d.status === 'APPROVED',
                                    'text-warning': d.status === 'PENDING',
                                    'text-danger': d.status === 'CLOSED',
                                }"
                            >
                                {{
                                    d.status === "APPROVED"
                                        ? "ONGONIG"
                                        : d.status
                                }}
                            </span>
                        </h5>
                    </li>
                </ul>
                <div
                    class="d-flex gap-2 mt-3"
                    v-if="d.status !== 'CLOSED'"
                >
                    <button
                        :class="[
                            'btn',
                            d.status === 'APPROVED'
                                ? 'btn-warning'
                                : 'btn-success',
                        ]"
                        @click="toggleApproval(d.id)"
                    >
                        {{
                            d.status === "APPROVED"
                                ? "Disapprove"
                                : "Approve"
                        }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
