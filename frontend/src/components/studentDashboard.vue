<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../states/authState";
import LogoutButton from "./logoutButton.vue";

const authStore = useAuthStore();
const studentName = ref("");
const errorMsg = ref("");

onMounted(async () => {
    try {
        const response = await fetch("/api/student", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            const data = await response.json();
            studentName.value = data.name;
        } else {
            const err = await response.json();
            errorMsg.value = err.message || "Failed to fetch student data";
        }
    } catch (err) {
        errorMsg.value = "Network error occurred";
    }
});
</script>

<template>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center">
            <h1>STUDENT DASHBOARD</h1>
            <LogoutButton />
        </div>
        <div v-if="studentName">
            <h3 class="mt-3">Welcome, {{ studentName }}!</h3>
        </div>
        <div v-else-if="!errorMsg">
            <p>Loading...</p>
        </div>
        <div v-if="errorMsg" class="alert alert-danger mt-3">
            {{ errorMsg }}
        </div>
    </div>
</template>
