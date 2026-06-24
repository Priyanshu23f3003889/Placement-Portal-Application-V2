<script setup>
import { ref, computed } from "vue";
import { useAuthStore } from "../states/authState.js";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const msg = ref("");
const role = ref("STUDENT");
const email = ref("");
const password = ref("");
const name = ref("");
const branch = ref("CSE");
const cgpa = ref("");
const resumeUrl = ref("");
const hrContact = ref("");
const website = ref("");

const isMsg = computed(() => {
    return msg.value !== "";
});

async function register() {
    msg.value = "";
    const data = {
        email: email.value,
        password: password.value,
        role: role.value,
    };

    if (role.value === "STUDENT") {
        data.name = name.value;
        data.branch = branch.value;
        data.cgpa = cgpa.value;
        data.resumeUrl = resumeUrl.value;
    } else if (role.value === "COMPANY") {
        data.name = name.value;
        data.hrContact = hrContact.value;
        data.website = website.value;
    }

    try {
        await authStore.register(data);
        msg.value = "Registration successful! Redirecting to login...";
        setTimeout(() => {
            router.push({ name: "login" });
        }, 1000);
    } catch (error) {
        msg.value = error.message;
    }
}
</script>

<template>
    <div
        class="d-flex justify-content-center align-items-center"
        style="min-height: 100vh; padding: 20px 0"
    >
        <div class="text-center col-11 col-sm-8 col-md-6 col-lg-4">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h1 class="mb-0">
                        <img
                            class="mx-1"
                            src="../assets/logo.png"
                            alt="logo"
                            width="60"
                            height="60"
                        />
                        Register
                    </h1>
                </div>
                <div class="card-body text-start">
                    <form @submit.prevent="register">
                        <div class="mb-3">
                            <label class="form-label d-block"
                                >Register as:</label
                            >
                            <div class="form-check form-check-inline">
                                <input
                                    class="form-check-input"
                                    type="radio"
                                    v-model="role"
                                    value="STUDENT"
                                    id="roleStudent"
                                />
                                <label
                                    class="form-check-label"
                                    for="roleStudent"
                                    >Student</label
                                >
                            </div>
                            <div class="form-check form-check-inline">
                                <input
                                    class="form-check-input"
                                    type="radio"
                                    v-model="role"
                                    value="COMPANY"
                                    id="roleCompany"
                                />
                                <label
                                    class="form-check-label"
                                    for="roleCompany"
                                    >Company</label
                                >
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="email" class="form-label"
                                >Email address</label
                            >
                            <input
                                type="email"
                                v-model="email"
                                class="form-control"
                                id="email"
                                required
                            />
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label"
                                >Password</label
                            >
                            <input
                                type="text"
                                v-model="password"
                                class="form-control"
                                id="password"
                                required
                            />
                        </div>

                        <div class="mb-3">
                            <label for="name" class="form-label">Name</label>
                            <input
                                type="text"
                                v-model="name"
                                class="form-control"
                                id="name"
                                required
                            />
                        </div>

                        <div v-if="role === 'STUDENT'">
                            <div class="mb-3">
                                <label for="branch" class="form-label"
                                    >Branch</label
                                >
                                <select
                                    v-model="branch"
                                    class="form-select"
                                    id="branch"
                                    required
                                >
                                    <option value="CSE">
                                        Computer Science and Engineering
                                    </option>
                                    <option value="ECE">
                                        Electronics and Communication
                                    </option>
                                    <option value="MECH">
                                        Mechanical Engineering
                                    </option>
                                    <option value="CIVIL">
                                        Civil Engineering
                                    </option>
                                    <option value="EE">
                                        Electrical Engineering
                                    </option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="cgpa" class="form-label"
                                    >CGPA</label
                                >
                                <input
                                    type="number"
                                    step="0.01"
                                    v-model="cgpa"
                                    class="form-control"
                                    id="cgpa"
                                    min="0"
                                    max="10"
                                    required
                                />
                            </div>
                            <div class="mb-3">
                                <label for="resumeUrl" class="form-label"
                                    >Resume URL</label
                                >
                                <input
                                    type="url"
                                    v-model="resumeUrl"
                                    class="form-control"
                                    id="resumeUrl"
                                    required
                                    
                                />
                            </div>
                        </div>

                        <div v-if="role === 'COMPANY'">
                            <div class="mb-3">
                                <label for="hrContact" class="form-label"
                                    >HR Contact</label
                                >
                                <input
                                    type="text"
                                    v-model="hrContact"
                                    class="form-control"
                                    id="hrContact"
                                    required
                                />
                            </div>
                            <div class="mb-3">
                                <label for="website" class="form-label"
                                    >Website</label
                                >
                                <input
                                    type="url"
                                    v-model="website"
                                    class="form-control"
                                    id="website"
                                    required
                                />
                            </div>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">
                                Register
                            </button>
                            <router-link to="/login" class="btn btn-link"
                                >Already have an account? Login</router-link
                            >
                        </div>
                    </form>
                </div>
                <div
                    v-if="isMsg"
                    :class="[
                        'alert',
                        msg.includes('successful') ? 'alert-success' : 'alert-danger',
                        'm-3',
                    ]"
                >
                    {{ msg }}
                </div>
            </div>
        </div>
    </div>
</template>
