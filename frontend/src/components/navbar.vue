<script setup>
import { computed } from "vue";
import LogoutButton from "./logoutButton.vue";

const props = defineProps(["role"]);

const isAdmin = computed(() => {
    return props.role === "admin";
});

const isStudent = computed(() => {
    return props.role === "student";
});

const isCompany = computed(() => {
    return props.role === "company";
});
</script>

<template>
    <nav class="navbar navbar-expand-lg bg-primary" data-bs-theme="dark">
        <div class="container-fluid">
            <span
                class="navbar-brand mb-0 fs-2 fw-bold text-white text-capitalize"
                >{{ role }}</span
            >
            <button
                class="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarNav"
                aria-controls="navbarNav"
                aria-expanded="false"
                aria-label="Toggle navigation"
            >
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav mx-auto mb-2 mb-lg-0 fs-5 gap-3">
                    <template v-if="isAdmin">
                        <li class="nav-item">
                            <router-link
                                class="nav-link text-white"
                                exact-active-class="active fw-bold"
                                to="/admin/companies"
                                >Companies</router-link
                            >
                        </li>
                        <li class="nav-item">
                            <router-link
                                class="nav-link text-white"
                                exact-active-class="active fw-bold"
                                to="/admin/students"
                                >Students</router-link
                            >
                        </li>
                        <li class="nav-item">
                            <router-link
                                class="nav-link text-white"
                                exact-active-class="active fw-bold"
                                to="/admin/drives"
                                >Drives</router-link
                            >
                        </li>
                        <li class="nav-item">
                            <router-link
                                class="nav-link text-white"
                                exact-active-class="active fw-bold"
                                to="/admin/applications"
                                >Applications</router-link
                            >
                        </li>
                    </template>

                    <template v-if="isStudent">
                        <li class="nav-item">
                            <a
                                class="nav-link text-white active fw-bold"
                                aria-current="page"
                                href="#"
                                >Companies</a
                            >
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-white" href="#"
                                >Applied Drives</a
                            >
                        </li>
                    </template>

                    <template v-if="isCompany">
                        <li class="nav-item">
                            <a
                                class="nav-link text-white active fw-bold"
                                aria-current="page"
                                href="#"
                                >Drives</a
                            >
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-white" href="#">History</a>
                        </li>
                    </template>
                </ul>
                <div class="d-flex mt-2 mt-lg-0 gap-2">
                    <button v-if="!isAdmin" class="btn btn-outline-light">
                        Profile
                    </button>
                    <LogoutButton v-if="isAdmin"></LogoutButton>
                </div>
            </div>
        </div>
    </nav>
</template>
