<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../../states/authState";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const message = ref("");
const messageStatus = ref("");

const companyId = ref("");
const jobTitle = ref("");
const jobDescription = ref("");
const deadline = ref("");
const branch = ref("");
const mincgpa = ref("");
const status = ref("");
const driveId = ref("");

const fetchDrive = async () => {
    try {
        const response = await fetch(`/api/company/editdrive/${route.params.id}`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
        });

        if (response.ok) {
            const data = await response.json();
            companyId.value = data.companyId;
            jobTitle.value = data.jobTitle;
            jobDescription.value = data.jobDescription;
            deadline.value = data.deadline;
            branch.value = data.branch;
            mincgpa.value = data.cgpa;
            status.value = data.status;
            driveId.value = data.id;
        } else {
            const err = await response.json();
            message.value =
                err.message || errorData.msg || "Failed to fetch drive data";
            messageStatus.value = "danger";
        }
    } catch (err) {
        message.value = "Network error occurred";
        messageStatus.value = "danger";
    }
};

async function edit(driveId, jobTitle, jobDesc, branch, mincgpa, deadline) {
    try {
        const data = {
            jobTitle: jobTitle,
            jobDescription: jobDesc,
            branch: branch,
            cgpa: mincgpa,
            deadline: deadline,
        };
        const response = await fetch(`/api/company/editdrive/${driveId}`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${authStore.token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            router.push({ name: "company-drives" });
        } else {
            const err = await response.json();
            message.value = err.message || "Failed to fetch company data";
            messageStatus.value = "danger";
        }
    } catch (err) {
        message.value = "Network error occurred";
        messageStatus.value = "danger";
    }
}

onMounted(async () => {
    await fetchDrive();
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
                    <h1 class="mb-3">Edit Drive</h1>
                </div>
                <div class="card-body">
                    <form
                        @submit.prevent="
                            edit(
                                driveId,
                                jobTitle,
                                jobDescription,
                                branch,
                                mincgpa,
                                deadline,
                            )
                        "
                    >
                        <div class="mb-3">
                            <label class="form-label">Company ID</label>
                            <span class="form-control bg-secondary-subtle">{{
                                companyId
                            }}</span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Drive ID</label>
                            <span class="form-control bg-secondary-subtle">{{
                                driveId
                            }}</span>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Status</label>
                            <span
                                :class="[
                                    'form-control',
                                    'bg-secondary-subtle',
                                    status === 'APPROVED'
                                        ? 'text-success'
                                        : 'text-warning-emphasis',
                                ]"
                                >{{ status }}</span
                            >
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Job Tiltle</label>
                            <input
                                class="form-control"
                                required
                                v-model="jobTitle"
                            />
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Job Description</label>
                            <textarea
                                class="form-control"
                                required
                                v-model="jobDescription"
                            />
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Branch</label>
                            <select
                                v-model="branch"
                                class="form-select"
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
                                <option value="CIVIL">Civil Engineering</option>
                                <option value="EE">
                                    Electrical Engineering
                                </option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Minimum CGPA</label>
                            <input
                                type="number"
                                step="0.01"
                                v-model="mincgpa"
                                class="form-control"
                                id="cgpa"
                                min="0"
                                max="10"
                                required
                            />
                        </div>
                        <div class="mb-3">
                            <label class="form-label"
                                >Application Deadline</label
                            >
                            <input
                                class="form-control"
                                required
                                v-model="deadline"
                                type="datetime-local"
                            />
                        </div>
                        <div class="row gap-2">
                            <button type="submit" class="btn btn-success">
                                Edit
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
