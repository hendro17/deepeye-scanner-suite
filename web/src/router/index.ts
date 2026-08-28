import { createRouter, createWebHashHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import NewScan from "../views/NewScan.vue";
import ScanLive from "../views/ScanLive.vue";
import Findings from "../views/Findings.vue";
import Reports from "../views/Reports.vue";
import Settings from "../views/Settings.vue";
import CompareScans from "../views/CompareScans.vue";
import Docs from "../views/Docs.vue";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", name: "dashboard", component: Dashboard },
    { path: "/scan/new", name: "new-scan", component: NewScan },
    { path: "/scan/:id/live", name: "scan-live", component: ScanLive, props: true },
    { path: "/scan/:id/findings", name: "findings", component: Findings, props: true },
    { path: "/scan/:id/reports", name: "reports", component: Reports, props: true },
    { path: "/settings", name: "settings", component: Settings },
    { path: "/compare", name: "compare-scans", component: CompareScans },
    { path: "/docs", name: "docs", component: Docs },
  ],
});

export default router;
