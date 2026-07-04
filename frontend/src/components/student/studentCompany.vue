<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "../../states/authState";

const authStore = useAuthStore();
const companies = ref([]);
const errmsg = ref("");
const searchQuery = ref("");

const filteredCompanies = computed(() => {
    if (!searchQuery.value) return companies.value;
    const query = searchQuery.value.toLowerCase();
    return companies.value.filter(
        (c) =>
            c.name.toLowerCase().includes(query) ||
            c.email.toLowerCase().includes(query) ||
            c.id.toString().includes(query),
    );
});

const fetchCompanies = async () => {
  try {
        const response = await fetch("/api/student/companies", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            companies.value = await response.json();
        } else {
            const errorData = await response.json();
            errmsg.value =
                errorData.message ||
                errorData.msg ||
                "Failed to fetch Company Data";
        }
    } catch (err) {
        errmsg.value = "Network error occurred";
    }
};

onMounted(async () => {
    await fetchCompanies();
});
</script>

<template>
    <div class="container-lg mt-3">
        <div class="d-flex justify-content-between align-items-center">
            <h1>
                Companies
                <span class="badge bg-secondary fs-6 align-middle">{{
                    filteredCompanies.length
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
        <div class="card m-3" v-for="c in filteredCompanies">
            <div class="card-body">
                <h2 class="card-title">{{ c.name }}</h2>
                <ul class="card-text">
                    <li>
                        <h5>ID : {{ c.id }}</h5>
                    </li>
                    <li>
                        <h5>Email : {{ c.email }}</h5>
                    </li>
                    <li>
                        <h5>HR Contact : {{ c.hrContact }}</h5>
                    </li>
                    <li>
                        <h5>
                            Website :
                            <a :href="c.website" target="_blank">{{ c.website }}</a>
                        </h5>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>
