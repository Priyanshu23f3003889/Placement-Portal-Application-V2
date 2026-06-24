<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "../../states/authState";

const authStore = useAuthStore();
const students = ref([]);
const errmsg = ref("");
const searchQuery = ref("");

const filteredStudents = computed(() => {
    if (!searchQuery.value) return students.value;
    const query = searchQuery.value.toLowerCase();
    return students.value.filter(
        (s) =>
            s.name.toLowerCase().includes(query) ||
            s.email.toLowerCase().includes(query) ||
            s.id.toString().includes(query),
    );
});

const fetchStudents = async () => {
    try {
        const response = await fetch("/api/admin/students", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            students.value = await response.json();
        } else {
            const errorData = await response.json();
            errmsg.value =
                errorData.message ||
                errorData.msg ||
                "Failed to fetch student Data";
        }
    } catch (err) {
        errmsg.value = "Network error occurred";
    }
};

const toggleApproval = async (id) => {
    try {
        const response = await fetch(
            `/api/admin/students/${id}/toggle-approval`,
            {
                method: "PATCH",
                headers: {
                    Authorization: `Bearer ${authStore.token}`,
                    "Content-Type": "application/json",
                },
            },
        );
        if (response.ok) {
            await fetchStudents();
        } else {
            const errorData = await response.json();
            errmsg.value =
                errorData.message || "Failed to toggle approval status";
        }
    } catch (err) {
        errmsg.value = "Network error occurred";
    }
};

const deleteStudent = async (id) => {
    if (!confirm("Are you sure you want to delete this Student?")) return;
    try {
        const response = await fetch(`/api/admin/students/${id}`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });
        if (response.ok) {
            await fetchStudents();
        } else {
            const errorData = await response.json();
            errmsg.value = errorData.message || "Failed to delete student";
        }
    } catch (err) {
        errmsg.value = "Network error occurred";
    }
};

onMounted(async () => {
    await fetchStudents();
});
</script>

<template>
    <div class="container-lg mt-3">
        <div class="d-flex justify-content-between align-items-center">
            <h1>
                Students
                <span class="badge bg-secondary fs-6 align-middle">{{
                    filteredStudents.length
                }}</span>
            </h1>
            <input
                type="text"
                class="form-control w-auto"
                placeholder="Search by ID or Name..."
                v-model="searchQuery"
            />
        </div>
        <hr />
        <p v-if="errmsg" class="text-danger">{{ errmsg }}</p>
    </div>

    <div class="container-lg d-flex flex-wrap">
        <div class="card m-3" v-for="s in filteredStudents">
            <div class="card-body">
                <h2 class="card-title">{{ s.name }}</h2>
                <ul class="card-text">
                    <li>
                        <h5>ID : {{ s.id }}</h5>
                    </li>
                    <li>
                        <h5>Email : {{ s.email }}</h5>
                    </li>
                    <li>
                        <h5>Branch : {{ s.branch }}</h5>
                    </li>
                    <li>
                        <h5>CGPA : {{ s.cgpa }}</h5>
                    </li>
                    <li>
                        <h5>
                            Resume :
                            <a :href="s.resumeUrl">{{ s.resumeUrl }}</a>
                        </h5>
                    </li>
                    <li>
                        <h5
                            :class="[
                                s.isApproved ? 'text-success' : 'text-warning',
                            ]"
                        >
                            {{ s.isApproved ? "Approved" : "BlackListed" }}
                        </h5>
                    </li>
                </ul>
                <div class="d-flex gap-2 mt-3">
                    <button class="btn btn-danger" @click="deleteStudent(s.id)">
                        Delete
                    </button>
                    <button
                        :class="[
                            'btn',
                            s.isApproved ? 'btn-warning' : 'btn-success',
                        ]"
                        @click="toggleApproval(s.id)"
                    >
                        {{ s.isApproved ? "Blacklist" : "Approve" }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
