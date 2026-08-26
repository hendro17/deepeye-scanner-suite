<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="flex h-screen w-screen overflow-hidden bg-bg-primary">
    <!-- Sidebar -->
    <aside class="w-64 shrink-0 flex flex-col glass border-r" style="border-radius: 0;">
      <div class="p-6 border-b border-[rgba(0,240,255,0.08)]">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center"
               style="background: linear-gradient(135deg, #00f0ff, #00ff88);">
            <span class="font-bold text-bg-primary text-lg">D</span>
          </div>
          <div>
            <h1 class="font-bold text-lg leading-tight">DeepEye</h1>
            <p class="text-xs text-txt-secondary">Scanner Suite</p>
          </div>
        </div>
      </div>

      <nav class="flex-1 p-3 space-y-1">
        <RouterLink to="/" v-slot="{ isActive }">
          <div :class="['flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all cursor-pointer',
            isActive ? 'bg-[rgba(0,240,255,0.1)] text-neon-cyan border border-[rgba(0,240,255,0.2)]'
                     : 'text-txt-secondary hover:text-txt-primary hover:bg-[rgba(255,255,255,0.03)] border border-transparent']">
            <span>Dashboard</span>
          </div>
        </RouterLink>

        <RouterLink to="/scan/new" v-slot="{ isActive }">
          <div :class="['flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all cursor-pointer',
            isActive ? 'bg-[rgba(0,240,255,0.1)] text-neon-cyan border border-[rgba(0,240,255,0.2)]'
                     : 'text-txt-secondary hover:text-txt-primary hover:bg-[rgba(255,255,255,0.03)] border border-transparent']">
            <span>New Scan</span>
          </div>
        </RouterLink>

        <RouterLink to="/compare" v-slot="{ isActive }">
          <div :class="['flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all cursor-pointer',
            isActive ? 'bg-[rgba(0,240,255,0.1)] text-neon-cyan border border-[rgba(0,240,255,0.2)]'
                     : 'text-txt-secondary hover:text-txt-primary hover:bg-[rgba(255,255,255,0.03)] border border-transparent']">
            <span>Compare Scans</span>
          </div>
        </RouterLink>

        <RouterLink to="/settings" v-slot="{ isActive }">
          <div :class="['flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all cursor-pointer',
            isActive ? 'bg-[rgba(0,240,255,0.1)] text-neon-cyan border border-[rgba(0,240,255,0.2)]'
                     : 'text-txt-secondary hover:text-txt-primary hover:bg-[rgba(255,255,255,0.03)] border border-transparent']">
            <span>Settings</span>
          </div>
        </RouterLink>
      </nav>

      <div class="p-4 border-t border-[rgba(0,240,255,0.08)]">
        <p class="text-xs text-txt-tertiary">v0.1.0 · MIT License</p>
      </div>
    </aside>

    <!-- Main -->
    <main class="flex-1 overflow-y-auto custom-scroll">
      <RouterView />
    </main>
  </div>
</template>
