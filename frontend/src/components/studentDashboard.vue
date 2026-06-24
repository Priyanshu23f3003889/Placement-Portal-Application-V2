<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../states/authState";
import navbar from "./navbar.vue";

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
    <navbar role="student" :name="studentName"></navbar>
    <router-view />
</template>
