<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "../../states/authState";

const authStore = useAuthStore();
const placements = ref([]);
const errmsg = ref("");
const searchQuery = ref("");

const filteredDrives = computed(() => {
    if (!searchQuery.value) return placements.value;
    const query = searchQuery.value.toLowerCase();
    return placements.value.filter(
        (p) =>
            (p.jobTitle && p.jobTitle.toLowerCase().includes(query)) ||
            (p.companyName && p.companyName.toLowerCase().includes(query)) ||
            (p.driveId && p.driveId.toString().includes(query)) ||
            (p.year && p.year.toString().includes(query))
    );
});

const fetchPlacements = async () => {
    try {
        const response = await fetch("/api/student/placements", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            placements.value = await response.json();
            errmsg.value = "";
        } else {
            const errorData = await response.json();
            errmsg.value =
                errorData.message ||
                errorData.msg ||
                "Failed to fetch Placement Data";
        }
    } catch (err) {
        errmsg.value = "Network error occurred";
    }
};

onMounted(async () => {
    await fetchPlacements();
});

</script>

<template>
    <div class="container-lg mt-3">
        <div class="d-flex justify-content-between align-items-center">
            <h1>
                Placements
                <span class="badge bg-secondary fs-6 align-middle">{{
                    filteredDrives.length
                }}</span>
            </h1>
            <input
                type="text"
                class="form-control w-auto"
                placeholder="Drive ID, Job Title, Company Name..."
                v-model="searchQuery"
            />
        </div>
        <hr />
        <p v-if="errmsg" class="text-danger">{{ errmsg }}</p>
    </div>

    <div class="container-lg d-flex flex-wrap">
        <div class="card m-3" v-for="p in filteredDrives">
            <div class="card-body">
                <h2 class="card-title">{{ p.companyName }}</h2>
                <ul class="card-text">
                    <li>
                        <h5>Placement ID : {{ p.id }}</h5>
                    </li>
                    <li>
                        <h5>Drive ID : {{ p.driveId }}</h5>
                    </li>
                    <li>
                        <h5>Position : {{ p.position }}</h5>
                    </li>
                    <li>
                        <h5>Packege (LPA) : {{ p.salary }}</h5>
                    </li>
                    <li>
                        <h5>Year : {{ p.year }}</h5>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>
