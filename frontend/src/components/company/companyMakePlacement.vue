<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../../states/authState";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const authStore = useAuthStore();

const message = ref("");
const messageStatus = ref("");

const salary = ref("");
const application = ref({});

const fetchApplication = async () => {
    try {
        const response = await fetch(
            `/api/company/application/${route.params.applicationId}`,
            {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${authStore.token}`,
                    "Content-Type": "application/json",
                },
            },
        );

        if (response.ok) {
            const data = await response.json();
            application.value = data;
        } else {
            const err = await response.json();
            message.value =
                err.message || err.msg || "Failed to fetch application data";
            messageStatus.value = "danger";
        }
    } catch (err) {
        message.value = "Network error occurred";
        messageStatus.value = "danger";
    }
};

async function place(salary) {
  try {
    if (!confirm("Are you sure you want to Make Placement ?")) { return; }
        const data = {
            salary: salary,
        };
        const response = await fetch(`/api/company/makeplacement/${application.value.id}`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            router.push({ name: "company-applications" });
        } else {
            const err = await response.json();
            message.value = err.message ||err.msg|| "Failed to fetch company data";
            messageStatus.value = "danger";
        }
    } catch (err) {
        message.value = "Network error occurred";
        messageStatus.value = "danger";
    }
}

onMounted(async () => {
    await fetchApplication();
});
</script>

<template>
    <div
        class="d-flex justify-content-center align-items-center py-2"
        style="min-height: 90vh"
    >
        <div class="col-11 col-sm-8 col-md-6 col-lg-4">
            <div class="card">
                <div class="card-header">
                    <h1 class="mb-3">{{ application.studentName }}</h1>
                </div>
                <div class="card-body">
                    <form @submit.prevent="place(salary)">
                        <div class="mb-3">
                            <label class="form-label">Application ID</label>
                            <span class="form-control bg-secondary-subtle">{{
                                application.id
                            }}</span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Drive ID</label>
                            <span class="form-control bg-secondary-subtle">{{
                                application.driveId
                            }}</span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Job Title</label>
                            <span class="form-control bg-secondary-subtle">{{
                                application.jobTitle
                            }}</span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Package (LPA)</label>
                            <input
                                type="number"
                                step="0.01"
                                v-model="salary"
                                class="form-control"
                                min="1"
                                required
                            />
                        </div>
                        <div class="row gap-2">
                            <button type="submit" class="btn btn-success">
                                Place
                            </button>
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
