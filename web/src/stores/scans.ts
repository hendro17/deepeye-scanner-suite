import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "../api/client";

function startScan(id: number) {
  return api.scans.start(id);
}

function stopScan(id: number) {
  return api.scans.stop(id);
}

export const useScansStore = defineStore("scans", () => {
  const scans = ref<any[]>([]);
  const loading = ref(false);

  async function fetchScans() {
    loading.value = true;
    try {
      scans.value = await api.scans.list();
    } finally {
      loading.value = false;
    }
  }

  async function createScan(body: any) {
    const res = await api.scans.create(body);
    await fetchScans();
    return res;
  }

  return { scans, loading, fetchScans, createScan, startScan, stopScan };
});
