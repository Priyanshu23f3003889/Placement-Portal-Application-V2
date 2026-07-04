<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../../states/authState";
import logout from "../logoutButton.vue";

const authStore = useAuthStore();
const student = ref({});
const resumeUrl = ref("");
const cgpa = ref("");
const message = ref("");
const messageStatus = ref("");

const fetchStudent = async () => {
    try {
        const response = await fetch("/api/student/profile", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            const data = await response.json();
            student.value = data;
            resumeUrl.value = data.resumeUrl;
            cgpa.value = data.cgpa;
        } else {
            const err = await response.json();
            message.value = err.message || "Failed to fetch company data";
            messageStatus.value = "danger";
        }
    } catch (err) {
        message.value = "Network error occurred";
        messageStatus.value = "danger";
    }
};

onMounted(async () => {
    await fetchStudent();
});

async function update(cgpa, resumeUrl) {
    message.value = "";
    try {
        const response = await fetch("/api/student/profile/update", {
            method: "PATCH",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ cgpa, resumeUrl }),
        });
        const data = await response.json();
        if (response.ok) {
            message.value = data.message || "Updated";
            messageStatus.value = "success";
            await fetchStudent();
        } else {
            message.value = data.message || "Failed to update profile";
            messageStatus.value = "danger";
        }
    } catch (err) {
        message.value = "Network error occurred";
        messageStatus.value = "danger";
    }
}
</script>

<template>
    <div
        class="d-flex justify-content-center align-items-center py-2"
        style="min-height: 90vh"
    >
        <div class="col-11 col-sm-8 col-md-6 col-lg-4">
            <div class="card">
                <div class="card-header">
                    <h1 class="mb-3">
                        {{ student.name }}
                    </h1>
                </div>
                <div class="card-body">
                    <form @submit.prevent="update(cgpa, resumeUrl)">
                        <div class="mb-3">
                            <label class="form-label">Student ID</label>
                            <span class="form-control bg-secondary-subtle">{{
                                student.id
                            }}</span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email Address</label>
                            <span class="form-control bg-secondary-subtle"
                                >{{ student.email }}
                            </span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Branch</label>
                            <span class="form-control bg-secondary-subtle"
                                >{{ student.branch }}
                            </span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">CGPA</label>
                            <input
                                class="form-control"
                                :placeholder="student.cgpa"
                                v-model="cgpa"
                                type="number"
                                step="0.01"
                                min="0"
                                max="10"
                            />
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Resume</label>
                            <input
                                class="form-control"
                                type="url"
                                :placeholder="student.resumeUrl"
                                v-model="resumeUrl"
                            />
                        </div>
                        <div class="d-flex gap-2 justify-content-center align-items-center">
                            <button
                                v-if="
                                    student.resumeUrl !== resumeUrl ||
                                    student.cgpa !== cgpa
                                "
                                type="submit"
                                class="btn btn-primary"
                            >
                                Update
                            </button>
                            <logout />
                        </div>
                    </form>
                </div>
                <div
                    v-if="message !== ''"
                    :class="['alert', 'alert-' + messageStatus, 'm-2']"
                >
                    {{ message }}
                </div>
            </div>
        </div>
    </div>
</template>
