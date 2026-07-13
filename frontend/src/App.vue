<script setup>
import { useExportStore } from "./states/exportState";
import { onMounted } from "vue";

const exportStore = useExportStore();

onMounted(() => {
    if (exportStore.exportTaskId) {
        exportStore.startPolling();
    }
});
</script>

<template>
  <div v-if="exportStore.globalMessage" :class="['alert', 'alert-' + exportStore.globalMessageType, 'alert-dismissible', 'fade', 'show', 'position-fixed', 'top-0', 'start-50', 'translate-middle-x', 'mt-4', 'shadow', 'text-center']" role="alert" style="min-width: 300px; z-index: 1050;">
    {{ exportStore.globalMessage }}
    <button type="button" class="btn-close" @click="exportStore.clearMessage()" aria-label="Close"></button>
  </div>
  <router-view></router-view>
</template>
