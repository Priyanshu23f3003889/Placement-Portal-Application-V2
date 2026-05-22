<script setup>
import { ref, computed } from "vue";
import { useAuthStore } from "../states/authState.js";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const msg = ref("");
const email = ref("");
const password = ref("");
const isMsg = computed(() => {
    return msg.value !== "";
});

async function login() {
    msg.value = "";
    try {
        await authStore.login(email.value, password.value);
        if (authStore.role === "ADMIN") {
            router.push({ name: "admin-dashboard" });
        } else if (authStore.role === "COMPANY") {
            router.push({ name: "company-dashboard" });
        } else if (authStore.role === "STUDENT") {
            router.push({ name: "student-dashboard" });
        }
    } catch (error) {
        msg.value = error.message;
    }
}
</script>

<template>
    <div
        class="d-flex justify-content-center align-items-center"
        style="height: 100vh"
    >
        <div class="text-center col-11 col-sm-8 col-md-6 col-lg-4">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h1 class="mb-0">Login</h1>
                </div>
                <div class="card-body">
                    <form @submit.prevent="login">
                        <div class="mb-3">
                            <label for="exampleInputEmail1" class="form-label"
                                >Email address</label
                            >
                            <input
                                type="email"
                                v-model="email"
                                class="form-control"
                            />
                        </div>
                        <div class="mb-3">
                            <label
                                for="exampleInputPassword1"
                                class="form-label"
                                >Password</label
                            >
                            <input
                                type="password"
                                v-model="password"
                                class="form-control"
                                id="exampleInputPassword1"
                            />
                        </div>
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">
                                Submit
                            </button>
                            <router-link to="/register" class="btn btn-link"
                                >Don't have an account? Register</router-link
                            >
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <div
        v-if="isMsg"
        class="alert alert-danger position-fixed bottom-0 end-0 m-3"
        role="alert"
    >
        {{ msg }}
    </div>
</template>
