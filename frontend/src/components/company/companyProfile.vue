<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../../states/authState";
import logout from "../logoutButton.vue";

const authStore = useAuthStore();
const company = ref({});
const hrContact = ref("");
const website = ref("");
const message = ref("");
const messageStatus = ref("");

const fetchCompany = async () => {
    try {
        const response = await fetch("/api/company/profile", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            const data = await response.json();
            company.value = data;
            hrContact.value = data.hrContact;
            website.value = data.website;
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
    await fetchCompany();
});

async function update(hrContact, website) {
    message.value = "";
    try {
        const response = await fetch("/api/company/profile/update", {
            method: "PATCH",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ hrContact, website }),
        });
        const data = await response.json();
        if (response.ok) {
            message.value = data.message || "Updated";
            messageStatus.value = "success";
            await fetchCompany();
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
                        {{ company.name }}
                    </h1>
                    <p
                        :class="[
                            company.isApproved
                                ? 'text-success'
                                : 'text-warning',
                            'fw-bold',
                        ]"
                    >
                        {{
                            company.isApproved
                                ? "Approved"
                                : "BlackListed/pending Approval"
                        }}
                    </p>
                </div>
                <div class="card-body">
                    <form @submit.prevent="update(hrContact, website)">
                        <div class="mb-3">
                            <label class="form-label">Email Address</label>
                            <span class="form-control bg-secondary-subtle"
                                >{{ company.email }}
                            </span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Company ID</label>
                            <span class="form-control bg-secondary-subtle">{{
                                company.id
                            }}</span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">HR Contact</label>
                            <input
                                class="form-control"
                                :placeholder="company.hrContact"
                                v-model="hrContact"
                            />
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Website</label>
                            <input
                                class="form-control"
                                type="url"
                                :placeholder="company.website"
                                v-model="website"
                            />
                        </div>
                        <div class="d-flex gap-2 justify-content-center align-items-center">
                            <button
                                v-if="
                                    company.hrContact !== hrContact ||
                                    website !== company.website
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
