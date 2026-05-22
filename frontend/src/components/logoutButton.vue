<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const logout = () => {
    router.push("/logout");
};
</script>

<template>
    <button @click="logout" class="btn btn-danger">Logout</button>
</template>
