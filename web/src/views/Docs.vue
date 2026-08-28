<script setup lang="ts">
import { ref } from "vue";

const sections = [
  { id: "pengantar", label: "Pengantar" },
  { id: "memulai", label: "Cara Memulai" },
  { id: "navigasi", label: "Navigasi Aplikasi" },
  { id: "scan-baru", label: "Membuat Scan Baru" },
  { id: "scan-live", label: "Memantau Scan" },
  { id: "baca-hasil", label: "Membaca Hasil Scanning" },
  { id: "laporan", label: "Laporan & Format" },
  { id: "bandingkan", label: "Membandingkan Scan" },
  { id: "pengaturan", label: "Pengaturan (Settings)" },
  { id: "faq", label: "FAQ & Troubleshooting" },
];

const activeSection = ref("pengantar");

function scrollTo(id: string) {
  activeSection.value = id;
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}
</script>

<template>
  <div class="p-8">
    <div class="flex gap-8">
      <!-- In-page nav -->
      <aside class="w-56 shrink-0 hidden lg:block">
        <div class="sticky top-8 glass rounded-xl p-4 space-y-1">
          <p class="text-xs font-semibold text-txt-tertiary uppercase tracking-wider px-2 mb-2">Daftar Isi</p>
          <button
            v-for="s in sections"
            :key="s.id"
            @click="scrollTo(s.id)"
            :class="[
              'w-full text-left px-3 py-1.5 rounded-lg text-xs transition-all',
              activeSection === s.id
                ? 'bg-[rgba(0,240,255,0.1)] text-neon-cyan border border-[rgba(0,240,255,0.2)]'
                : 'text-txt-secondary hover:text-txt-primary hover:bg-[rgba(255,255,255,0.03)] border border-transparent',
            ]"
          >
            {{ s.label }}
          </button>
        </div>
      </aside>

      <!-- Content -->
      <div class="flex-1 max-w-4xl space-y-10">
        <header>
          <h1 class="text-2xl font-bold text-neon-cyan">Dokumentasi DeepEye Scanner Suite</h1>
          <p class="text-sm text-txt-secondary mt-2">
            Panduan lengkap cara menggunakan aplikasi ini, ditulis dengan bahasa sederhana agar mudah dipahami
            oleh siapa pun — dari pengguna awam sampai security tester berpengalaman.
          </p>
        </header>

        <!-- PENGANTAR -->
        <section id="pengantar" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">1. Pengantar — Apa itu DeepEye Scanner Suite?</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-3">
            DeepEye Scanner Suite adalah aplikasi <span class="text-neon-cyan">DAST</span>
            (Dynamic Application Security Testing) — yaitu alat yang memindai website atau API secara
            langsung untuk mencari celah keamanan (vulnerability). Aplikasi ini bekerja dengan cara
            mengirimkan berbagai "serangan percobaan" yang tidak berbahaya ke target, lalu mencatat
            responsnya untuk menentukan apakah ada celah yang bisa dieksploitasi.
          </p>
          <p class="text-sm text-txt-secondary leading-relaxed mb-3">
            Aplikasi ini cocok untuk:
          </p>
          <ul class="text-sm text-txt-secondary space-y-1 mb-3 list-disc pl-5">
            <li><span class="text-txt-primary">Developer</span> yang ingin tahu apakah aplikasinya aman sebelum dirilis.</li>
            <li><span class="text-txt-primary">Security tester / pentester</span> yang butuh alat scan otomatis untuk mempercepat kerja.</li>
            <li><span class="text-txt-primary">Pemilik bisnis</span> yang ingin memahami risiko keamanan websitenya.</li>
            <li><span class="text-txt-primary">Mahasiswa / pelajar</span> yang sedang belajar keamanan siber.</li>
          </ul>
          <p class="text-sm text-txt-secondary leading-relaxed mb-2">Arsitektur singkatnya:</p>
          <div class="bg-bg-primary rounded-lg p-4 text-xs text-txt-secondary font-mono leading-relaxed overflow-x-auto">
            Tampilan Web (Vue 3) → Backend API (FastAPI + SQLite) → Mesin Scan (deep_eye.py)
          </div>
          <div class="mt-3 text-sm text-txt-secondary space-y-1">
            <p>• <span class="text-neon-cyan">Tampilan Web</span> — halaman yang sedang Anda buka sekarang; tempat membuat scan dan melihat hasil.</p>
            <p>• <span class="text-neon-cyan">Backend API</span> — server yang menyimpan data scan dan menjembatani web dengan mesin scan.</p>
            <p>• <span class="text-neon-cyan">Mesin Scan</span> — engine Python yang benar-benar melakukan pemindaian, dilengkapi 50+ modul pengecekan celah keamanan dan orkestrasi Multi-AI (11+ provider AI seperti OpenAI, Claude, Gemini, Ollama, Groq, dan lainnya) untuk membantu menganalisis hasil dan mengurangi alarm palsu.</p>
          </div>
          <div class="mt-4 rounded-lg border border-[rgba(255,80,80,0.3)] bg-[rgba(255,80,80,0.06)] p-4">
            <p class="text-sm text-txt-primary font-semibold mb-1">Peringatan Penting</p>
            <p class="text-xs text-txt-secondary leading-relaxed">
              Hanya lakukan scan pada target yang <span class="text-neon-cyan">Anda miliki atau sudah mendapat izin tertulis</span>
              (authorization). Memindai website milik orang lain tanpa izin adalah tindakan ilegal di banyak negara.
              Aplikasi ini mewajibkan Anda mencentang pernyataan "authorized" sebelum scan dimulai.
            </p>
          </div>
        </section>

        <!-- MEMULAI -->
        <section id="memulai" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">2. Cara Memulai</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-3">Langkah menjalankan aplikasi di komputer Anda:</p>
          <ol class="text-sm text-txt-secondary space-y-3 list-decimal pl-5">
            <li>
              <span class="text-txt-primary">Pastikan prasyarat terpasang:</span>
              Python 3.x, Node.js, dan pnpm. Detail instalasi lengkap ada di file <code class="text-neon-cyan">README.md</code> di root project.
            </li>
            <li>
              <span class="text-txt-primary">Jalankan skrip dev:</span>
              <div class="bg-bg-primary rounded-lg p-3 mt-2 text-xs font-mono text-neon-green">./scripts/dev.sh</div>
              <p class="mt-1 text-xs">Skrip ini otomatis menjalankan backend (port 8000) dan frontend (port 5173) sekaligus.</p>
            </li>
            <li>
              <span class="text-txt-primary">Buka aplikasi:</span>
              <p class="mt-1 text-xs">
                Web: <code class="text-neon-cyan">http://localhost:5173</code> ·
                API: <code class="text-neon-cyan">http://localhost:8000/api/health</code> ·
                Swagger API: <code class="text-neon-cyan">http://localhost:8000/docs</code>
              </p>
            </li>
            <li>
              <span class="text-txt-primary">(Opsional) siapkan AI provider:</span>
              <p class="mt-1 text-xs">Fitur analisis AI tetap berjalan tanpa AI provider (scan tetap jalan), tapi untuk hasil lebih akurat Anda bisa mengonfigurasi API key di halaman <span class="text-neon-cyan">Settings</span>.</p>
            </li>
          </ol>
        </section>

        <!-- NAVIGASI -->
        <section id="navigasi" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">3. Navigasi Aplikasi</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-4">
            Menu utama ada di sidebar kiri. Berikut penjelasan singkat tiap halaman:
          </p>
          <div class="space-y-3">
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Dashboard</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Halaman utama — ringkasan kondisi keamanan Anda. Elemen di dalamnya, per item:</p>
              <ul class="text-xs text-txt-secondary space-y-1.5 mt-2 list-disc pl-4">
                <li><span class="text-txt-primary">4 kartu statistik</span> — <em>Total Scans</em> (jumlah semua scan), <em>Running</em> (scan sedang berjalan), <em>Completed</em> (scan selesai), dan <em>Avg Duration</em> (rata-rata lama scan).</li>
                <li><span class="text-txt-primary">Grafik donat Severity</span> — distribusi semua temuan per tingkat keparahan (Critical/High/Medium/Low/Info). Warna merah = paling berbahaya. Ini cara tercepat menilai kondisi keamanan target Anda secara sekilas.</li>
                <li><span class="text-txt-primary">Grafik riwayat scan</span> — jumlah scan per hari dalam 7 hari terakhir, untuk melihat aktivitas pemindaian Anda.</li>
                <li><span class="text-txt-primary">Tabel Recent Scans</span> — 10 scan terakhir dengan kolom: ID scan, Target (URL), Status (running/completed/failed), waktu dibuat, dan tombol <span class="text-neon-cyan">View</span> untuk membuka halaman detail scan (Live, Findings, Reports).</li>
              </ul>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">New Scan</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Halaman untuk membuat scan baru. Berisi wizard (urutan langkah) yang memandu Anda mengatur target dan parameter scan. Detailnya ada di bagian 4.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Compare Scans</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Membandingkan dua scan (misalnya sebelum &amp; sesudah perbaikan) untuk melihat findings baru yang muncul dan findings lama yang sudah diperbaiki. Detailnya ada di bagian 8.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Settings</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Konfigurasi aplikasi: pengaturan AI provider, koneksi, dan maintenance (update database CVE &amp; build RAG). Detailnya ada di bagian 9.</p>
            </div>
          </div>
          <p class="text-sm text-txt-secondary leading-relaxed mt-4 mb-3">
            Setelah sebuah scan dibuat, muncul 3 halaman detail yang spesifik untuk scan tersebut:
          </p>
          <div class="space-y-3">
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Live (Terminal)</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Menampilkan log proses scan secara real-time, seperti melihat terminal. Berguna untuk memantau progres dan mengetahui jika ada error.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Findings</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Daftar celah keamanan yang ditemukan. Ini halaman paling penting — cara membacanya dibahas lengkap di bagian 6.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Reports</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Daftar file laporan hasil scan yang bisa diunduh dalam berbagai format. Detailnya ada di bagian 7.</p>
            </div>
          </div>
        </section>

        <!-- SCAN BARU -->
        <section id="scan-baru" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">4. Panduan Membuat Scan Baru</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-2">
            Klik <span class="text-neon-cyan">New Scan</span> di sidebar. Wizard akan menuntun Anda mengisi beberapa hal:
          </p>
          <p class="text-xs text-txt-tertiary italic leading-relaxed mb-4">
            Tip: di aplikasi, setiap opsi kini memiliki ikon <span class="text-neon-cyan">?</span> — arahkan kursor ke ikon tersebut untuk melihat penjelasan singkatnya tanpa harus membuka dokumentasi ini.
          </p>

          <div class="space-y-5">
            <div>
              <p class="text-sm font-semibold text-neon-cyan mb-1">a. Target URL</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                Alamat website/API yang ingin dipindai, contoh: <code class="text-neon-cyan">https://example.com</code>.
                Pastikan URL lengkap termasuk protokol (http:// atau https://).
              </p>
            </div>

            <div>
              <p class="text-sm font-semibold text-neon-cyan mb-1">b. Scope (Batasan)</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                Tentukan bagian mana saja dari target yang boleh dipindai, menggunakan bahasa sehari-hari (natural language).
                Contoh: <em>"scan hanya halaman utama dan halaman blog, jangan area admin"</em>.
                Ini mencegah scanner menjelajah terlalu dalam ke area yang tidak diinginkan (dan menghemat waktu).
              </p>
            </div>

            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">c. Mode Scan (Recon &amp; Scan Mode)</p>
              <p class="text-xs text-txt-secondary leading-relaxed mb-2">
                Mode berupa toggle (saklar) yang bisa dikombinasikan. Jika tidak ada yang dipilih, scanner berjalan standar terhadap URL target saja.
              </p>
              <div class="text-xs text-txt-secondary space-y-2">
                <p><span class="text-txt-primary">Quick Scan</span> (<code class="text-neon-cyan">quick_scan</code>) — paling cepat, hanya mengecek hal-hal paling umum. Cocok untuk cek cepat harian.</p>
                <p><span class="text-txt-primary">Full Scan</span> (<code class="text-neon-cyan">full_scan</code>) — semua modul dijalankan dengan eksplorasi maksimal. Paling lengkap tapi paling lama.</p>
                <p><span class="text-txt-primary">Enable Recon</span> (<code class="text-neon-cyan">enable_recon</code>) — mode pengintaian aktif: sebelum menyerang, scanner mengumpulkan informasi target (teknologi, subdomain, endpoint tersembunyi) agar serangan lebih tepat sasaran.</p>
                <p><span class="text-txt-primary">Scan Subdomains</span> (<code class="text-neon-cyan">scan_subdomains</code>) — mencari dan ikut memindai subdomain (misal api.example.com, dev.example.com), karena subdomain sering jadi titik lemah yang terlupakan.</p>
              </div>
            </div>

            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">d. Parameter Teknis (opsional)</p>
              <div class="text-xs text-txt-secondary space-y-2">
                <p><span class="text-txt-primary">Threads</span> (rentang 1–50, default 5) — berapa banyak permintaan berjalan bersamaan. Semakin besar = semakin cepat, tapi semakin berat beban ke target dan semakin besar risiko memicu rate limiting/WAF. Default 5 sudah aman untuk kebanyakan website; gunakan 1 untuk target yang sangat sensitif.</p>
                <p><span class="text-txt-primary">Depth</span> (rentang 1–10, default 2) — kedalaman crawler mengikuti link. Depth 1 = hanya halaman awal; depth 2 = halaman awal + link di dalamnya; dan seterusnya. Semakin dalam = semakin banyak halaman dipindai = semakin lama. Untuk aplikasi besar, coba 3–4.</p>
              </div>
            </div>

            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">d2. Secret Scanning</p>
              <p class="text-xs text-txt-secondary leading-relaxed mb-2">
                Saklar <span class="text-txt-primary">Secrets Scanner</span> mencari "rahasia yang bocor" — kredensial yang tidak sengaja terekspos di halaman web, file JavaScript, atau respons API. Aplikasi punya 20 pola rahasia yang bisa dipilih satu per satu sesuai kebutuhan:
              </p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                <span class="text-txt-tertiary">Cloud:</span> AWS Access Key, AWS Secret Key, GCP Service Account, Azure Client Secret ·
                <span class="text-txt-tertiary">Token platform:</span> GitHub Token, GitLab Token, Slack Token, Google API Key ·
                <span class="text-txt-tertiary">Pembayaran &amp; layanan:</span> Stripe API Key, Twilio, SendGrid, Mailgun ·
                <span class="text-txt-tertiary">AI &amp; lainnya:</span> OpenAI API Key, JWT Secret, Private Key (RSA/SSH), Database URL, Firebase Config, NPM Token, Heroku API Key, Telegram Bot Token.
              </p>
              <p class="text-xs text-txt-tertiary leading-relaxed mt-2">Semakin sedikit pola dipilih = semakin cepat.</p>
            </div>

            <div>
              <p class="text-sm font-semibold text-neon-cyan mb-1">e. Import OpenAPI/Swagger (Opsional)</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                Jika target punya dokumentasi API dalam format OpenAPI/Swagger (file JSON/YAML), Anda bisa meng-upload-nya.
                Scanner akan menggunakan daftar endpoint dari file tersebut sehingga cakupan scan API jadi jauh lebih lengkap.
              </p>
            </div>

            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">f. Pilih Checks (Modul Pengecekan)</p>
              <p class="text-xs text-txt-secondary leading-relaxed mb-2">
                Aplikasi punya 15 kategori dengan total 67 modul pengecekan. Agar mudah, gunakan preset:
              </p>
              <div class="text-xs text-txt-secondary space-y-1.5">
                <p><span class="text-neon-green">Quick</span> — hanya modul-modul paling kritis &amp; cepat.</p>
                <p><span class="text-neon-green">Full</span> — semua 67 modul dijalankan.</p>
                <p><span class="text-neon-green">API Focus</span> — fokus ke celah yang sering ada di API (REST/GraphQL).</p>
                <p><span class="text-neon-green">Custom</span> — pilih sendiri kategori yang diinginkan (misal hanya Injection dan Auth).</p>
              </div>
              <p class="text-xs text-txt-secondary leading-relaxed mt-3 mb-2">
                Detail lengkap 15 kategori dan 67 modul pengecekan:
              </p>
              <div class="overflow-x-auto">
                <table class="w-full text-xs">
                  <thead>
                    <tr class="text-left text-txt-tertiary border-b border-[rgba(0,240,255,0.08)]">
                      <th class="pb-2 pr-4 font-semibold">Kategori</th>
                      <th class="pb-2 pr-4 font-semibold">Fungsi Sederhana</th>
                      <th class="pb-2 font-semibold">Modul di Dalamnya</th>
                    </tr>
                  </thead>
                  <tbody class="text-txt-secondary align-top">
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Injection</td>
                      <td class="py-2 pr-4">Menguji apakah input "nakal" bisa memerintah database/sistem/template di belakang layar.</td>
                      <td class="py-2">SQL Injection, XSS, Stored XSS, Command Injection, NoSQL Injection, LDAP Injection, XML Injection, SSTI, SSTI Engines, CRLF Injection (termasuk deep header), SSE Injection.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">SSRF &amp; Path Traversal</td>
                      <td class="py-2 pr-4">Menguji apakah server bisa dipaksa mengakses alamat internal atau membaca file di luar yang diizinkan.</td>
                      <td class="py-2">SSRF, SSRF Cloud (metadata cloud), Path Traversal, LFI, RFI, Open Redirect (termasuk deep).</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Auth &amp; Session</td>
                      <td class="py-2 pr-4">Menguji celah login, sesi, dan mekanisme otorisasi.</td>
                      <td class="py-2">CSRF, Authentication Bypass, Broken Authentication, JWT Vulnerabilities (termasuk deep), OAuth Testing, SAML Attacks.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Config &amp; Exposure</td>
                      <td class="py-2 pr-4">Mencari konfigurasi yang salah dan data yang tidak sengaja terekspos.</td>
                      <td class="py-2">Security Misconfiguration, Information Disclosure, Sensitive Data Exposure, CORS Misconfiguration (termasuk CSP), Cloud Misconfig, Email Injection.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">XXE &amp; Deserialization</td>
                      <td class="py-2 pr-4">Menguji parsing XML dan objek ter-serialisasi yang bisa disalahgunakan.</td>
                      <td class="py-2">XXE, Insecure Deserialization.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">HTTP Header Attacks</td>
                      <td class="py-2 pr-4">Memanipulasi header HTTP untuk menyerang server/proxy.</td>
                      <td class="py-2">Host Header Injection (termasuk deep), HTTP Method Override, HTTP Smuggling, H2 Smuggle.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">API &amp; GraphQL</td>
                      <td class="py-2 pr-4">Menguji endpoint API REST dan GraphQL, termasuk akses data antar-user.</td>
                      <td class="py-2">API Vulnerabilities, API Security, API BOLA Deep (akses objek antar user), GraphQL Vulnerabilities (termasuk deep).</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Business Logic</td>
                      <td class="py-2 pr-4">Menguji logika bisnis seperti manipulasi harga, kondisi balapan, dan manipulasi field massal.</td>
                      <td class="py-2">Business Logic, Race Condition, Mass Assignment.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">File &amp; Webshell</td>
                      <td class="py-2 pr-4">Menguji upload file berbahaya dan script "pintu belakang".</td>
                      <td class="py-2">File Upload, PHP Webshell.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">WebSocket</td>
                      <td class="py-2 pr-4">Menguji koneksi real-time WebSocket.</td>
                      <td class="py-2">WebSocket, WebSocket Deep.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Cache &amp; Supply Chain</td>
                      <td class="py-2 pr-4">Meracuni cache CDN/proxy dan memeriksa skrip pihak ketiga.</td>
                      <td class="py-2">Cache Poisoning, Cache Deception, Supply Chain JS.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Recon &amp; Discovery</td>
                      <td class="py-2 pr-4">Menemukan aset tersembunyi target.</td>
                      <td class="py-2">Directory Bruteforce, Port Scanner, Subdomain Takeover, WAF Fingerprint.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Mobile</td>
                      <td class="py-2 pr-4">Analisis aplikasi mobile Android/iOS.</td>
                      <td class="py-2">Frida Mobile, Android Static, iOS Plist, Mobile SSL Pinning, Mobile AI Chain.</td>
                    </tr>
                    <tr class="border-b border-[rgba(0,240,255,0.05)]">
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Specialized</td>
                      <td class="py-2 pr-4">Modul khusus untuk ancaman spesifik.</td>
                      <td class="py-2">Anomaly Detector, Secret Scanning, Log4Shell.</td>
                    </tr>
                    <tr>
                      <td class="py-2 pr-4 text-neon-cyan whitespace-nowrap">Parameter Pollution</td>
                      <td class="py-2 pr-4">Mengirim parameter ganda/membingungkan untuk melewati filter.</td>
                      <td class="py-2">HPP Pollution.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <p class="text-sm font-semibold text-neon-cyan mb-1">g. Format Laporan</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                Pilih format laporan yang ingin dihasilkan: HTML, PDF, JSON, SARIF, JUnit, CSV, atau XLSX.
                Bisa pilih lebih dari satu. Penjelasan tiap format ada di bagian 7.
              </p>
            </div>

            <div class="rounded-lg border border-[rgba(255,80,80,0.3)] bg-[rgba(255,80,80,0.06)] p-4">
              <p class="text-sm font-semibold text-txt-primary mb-1">h. Checkbox "Authorized" — Wajib Dicentang</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                Anda harus mencentang pernyataan bahwa target yang dipindai adalah milik Anda atau Anda punya izin.
                Tanpa centang ini, tombol Start Scan tidak bisa ditekan. Ini pengingat etika dan hukum:
                <span class="text-neon-cyan">jangan pernah scan target tanpa otorisasi</span>.
              </p>
            </div>

            <div>
              <p class="text-sm font-semibold text-neon-cyan mb-1">i. Mulai Scan</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                Klik <span class="text-neon-cyan">Start Scan</span>. Anda akan diarahkan ke halaman Live untuk memantau progres secara real-time.
              </p>
            </div>
          </div>
        </section>

        <!-- SCAN LIVE -->
        <section id="scan-live" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">5. Memantau Scan Berjalan</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-3">
            Setelah scan dimulai, halaman <span class="text-neon-cyan">Live</span> menampilkan log proses scan
            secara streaming (real-time), mirip terminal. Beberapa hal yang bisa Anda lihat di sini:
          </p>
          <ul class="text-sm text-txt-secondary space-y-1.5 list-disc pl-5">
            <li>Progres modul yang sedang berjalan (misal "Running SQLi tests on /login").</li>
            <li>Peringatan atau error yang terjadi (misal target tidak bisa diakses).</li>
            <li>Indikasi awal temuan — jika scanner menemukan sesuatu yang mencurigakan, biasanya muncul di log sebelum scan selesai.</li>
          </ul>
          <p class="text-sm text-txt-secondary leading-relaxed mt-3">
            Jika ingin menghentikan scan sebelum selesai (misal target down atau salah konfigurasi),
            gunakan tombol <span class="text-neon-cyan">Stop</span> di halaman detail scan. Temuan yang sudah terkumpul tetap tersimpan.
          </p>
        </section>

        <!-- BACA HASIL -->
        <section id="baca-hasil" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-neon-cyan mb-3">6. Cara Membaca Hasil Scanning (Findings)</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-4">
            Halaman <span class="text-neon-cyan">Findings</span> adalah tempat paling penting: di sini Anda melihat
            semua celah keamanan yang ditemukan scanner. Berikut cara membacanya pelan-pelan.
          </p>

          <div class="mb-5">
            <p class="text-sm font-semibold text-txt-primary mb-2">6.1 Tingkat Keparahan (Severity)</p>
            <p class="text-xs text-txt-secondary leading-relaxed mb-3">
              Setiap temuan diberi label severity (keparahan). Gunakan filter di atas tabel untuk menyaring berdasarkan level.
              Urutan dari yang paling berbahaya:
            </p>
            <div class="space-y-2">
              <div class="bg-bg-primary rounded-lg p-3 flex items-start gap-3">
                <span class="sev-badge sev-critical shrink-0">CRITICAL</span>
                <p class="text-xs text-txt-secondary leading-relaxed">Paling berbahaya, harus segera diperbaiki. Penyerang bisa mengambil alih sistem tanpa hambatan.<br><span class="text-txt-tertiary italic">Contoh sederhana: bisa menjalankan perintah OS di server, atau mengambil alih database tanpa login.</span></p>
              </div>
              <div class="bg-bg-primary rounded-lg p-3 flex items-start gap-3">
                <span class="sev-badge sev-high shrink-0">HIGH</span>
                <p class="text-xs text-txt-secondary leading-relaxed">Berbahaya, prioritaskan perbaikan minggu ini. Penyerang bisa mencuri atau mengubah data penting.<br><span class="text-txt-tertiary italic">Contoh sederhana: SQL Injection yang membocorkan data user.</span></p>
              </div>
              <div class="bg-bg-primary rounded-lg p-3 flex items-start gap-3">
                <span class="sev-badge sev-medium shrink-0">MEDIUM</span>
                <p class="text-xs text-txt-secondary leading-relaxed">Perlu diperbaiki tapi tidak seurgent High/Critical. Biasanya butuh kondisi tertentu untuk dieksploitasi.<br><span class="text-txt-tertiary italic">Contoh sederhana: informasi versi software yang memudahkan penyerang mencari celah.</span></p>
              </div>
              <div class="bg-bg-primary rounded-lg p-3 flex items-start gap-3">
                <span class="sev-badge sev-low shrink-0">LOW</span>
                <p class="text-xs text-txt-secondary leading-relaxed">Risiko kecil, perbaiki saat ada waktu luang.<br><span class="text-txt-tertiary italic">Contoh sederhana: header keamanan HTTP yang tidak lengkap.</span></p>
              </div>
              <div class="bg-bg-primary rounded-lg p-3 flex items-start gap-3">
                <span class="sev-badge sev-info shrink-0">INFO</span>
                <p class="text-xs text-txt-secondary leading-relaxed">Bukan celah keamanan, hanya informasi yang mungkin berguna.<br><span class="text-txt-tertiary italic">Contoh sederhana: daftar email yang terekspos atau teknologi yang terdeteksi.</span></p>
              </div>
            </div>
          </div>

          <div class="mb-5">
            <p class="text-sm font-semibold text-txt-primary mb-2">6.2 Membaca Tabel Daftar Findings</p>
            <p class="text-xs text-txt-secondary leading-relaxed mb-2">Setiap baris di tabel menunjukkan satu temuan dengan kolom:</p>
            <ul class="text-xs text-txt-secondary space-y-1.5 list-disc pl-5">
              <li><span class="text-txt-primary">Severity</span> — tingkat keparahan (lihat 6.1).</li>
              <li><span class="text-txt-primary">Type</span> — jenis celah, misal <code class="text-neon-cyan">SQL Injection</code>, <code class="text-neon-cyan">XSS</code>, <code class="text-neon-cyan">SSRF</code>. Jika belum tahu artinya, cari istilahnya di internet atau baca bagian remediation untuk konteksnya.</li>
              <li><span class="text-txt-primary">URL / Lokasi</span> — halaman atau endpoint tempat celah ditemukan.</li>
              <li><span class="text-txt-primary">Parameter</span> — bagian spesifik dari URL atau form yang rentan (misal parameter <code class="text-neon-cyan">?id=</code> atau field login <code class="text-neon-cyan">username</code>).</li>
            </ul>
          </div>

          <div class="mb-5">
            <p class="text-sm font-semibold text-txt-primary mb-2">6.3 Detail Temuan (Klik Baris untuk Expand)</p>
            <p class="text-xs text-txt-secondary leading-relaxed mb-2">
              Klik sebuah baris untuk membuka detail lengkap. Setiap detail berisi bagian-bagian berikut:
            </p>
            <div class="space-y-3">
              <div class="bg-bg-primary rounded-lg p-4">
                <p class="text-sm font-semibold text-neon-cyan mb-1">Parameter &amp; Payload</p>
                <p class="text-xs text-txt-secondary leading-relaxed">
                  <span class="text-txt-primary">Parameter</span>: bagian target yang diserang.<br>
                  <span class="text-txt-primary">Payload</span>: data percobaan yang dikirim scanner. Ini adalah "serangan simulasi" — bukan serangan sungguhan. Contoh: <code class="text-neon-cyan">' OR 1=1--</code> untuk menguji SQL Injection. Jika payload ini berhasil "menipu" target, berarti ada celah.
                </p>
              </div>
              <div class="bg-bg-primary rounded-lg p-4">
                <p class="text-sm font-semibold text-neon-cyan mb-1">Evidence (Bukti)</p>
                <p class="text-xs text-txt-secondary leading-relaxed">
                  Bukti konkret bahwa celah benar-benar ada — misalnya respons server yang berubah saat payload dikirim, data yang bocor di respons, atau error database yang muncul. Ini bagian terpenting untuk membedakan temuan asli vs alarm palsu.
                </p>
              </div>
              <div class="bg-bg-primary rounded-lg p-4">
                <p class="text-sm font-semibold text-neon-green mb-1">Remediation (Cara Memperbaiki)</p>
                <p class="text-xs text-txt-secondary leading-relaxed">
                  <span class="text-neon-green">Bagian paling penting untuk developer.</span> Berisi langkah-langkah konkret memperbaiki celah. Baca ini dulu, bukan malah panik melihat severity-nya.
                </p>
              </div>
              <div class="bg-bg-primary rounded-lg p-4">
                <p class="text-sm font-semibold text-neon-cyan mb-1">AI Summary (jika tersedia)</p>
                <p class="text-xs text-txt-secondary leading-relaxed">
                  Jika AI provider dikonfigurasi di Settings, AI akan menganalisis temuan dan memberi ringkasan — termasuk kemungkinan apakah ini <span class="text-txt-primary">false positive</span> (alarm palsu) atau temuan asli. AI membantu mengurangi kepanikan akibat alert yang ternyata tidak berbahaya.
                </p>
              </div>
              <div class="bg-bg-primary rounded-lg p-4">
                <p class="text-sm font-semibold text-neon-cyan mb-1">CVE References (jika ada)</p>
                <p class="text-xs text-txt-secondary leading-relaxed">
                  Link ke database CVE (Common Vulnerabilities and Exposures) jika celah tersebut sudah dikenal publik. Berguna untuk membaca detail teknis resmi tentang celah tersebut.
                </p>
              </div>
            </div>
          </div>

          <div class="rounded-lg border border-[rgba(255,200,0,0.25)] bg-[rgba(255,200,0,0.05)] p-4 mb-3">
            <p class="text-sm font-semibold text-txt-primary mb-1">Tentang False Positive (Alarm Palsu)</p>
            <p class="text-xs text-txt-secondary leading-relaxed">
              Tidak semua temuan scanner adalah celah sungguhan. Kadang scanner keliru mengira sesuatu sebagai celah
              padahal bukan — ini disebut <span class="text-neon-cyan">false positive</span>. Karena itu:
              (1) selalu baca evidence dan AI Summary, (2) validasi manual temuan Critical/High sebelum melaporkan ke tim lain,
              (3) gunakan fitur AI provider untuk membantu menyaring false positive secara otomatis.
            </p>
          </div>

          <div>
            <p class="text-sm font-semibold text-txt-primary mb-2">6.4 Contoh Membaca Satu Temuan</p>
            <p class="text-xs text-txt-secondary leading-relaxed mb-3">
              Misal muncul temuan seperti ini:
            </p>
            <div class="bg-bg-primary rounded-lg p-4 text-xs text-txt-secondary space-y-2">
              <p><span class="text-txt-tertiary">Severity:</span> <span class="sev-badge sev-medium">MEDIUM</span></p>
              <p><span class="text-txt-tertiary">Type:</span> <span class="text-txt-primary">SQL Injection</span></p>
              <p><span class="text-txt-tertiary">URL:</span> <span class="text-txt-primary">https://target.com/products?id=123</span></p>
              <p><span class="text-txt-tertiary">Parameter:</span> <span class="text-txt-primary">id</span></p>
              <p><span class="text-txt-tertiary">Payload:</span> <span class="text-neon-cyan">123' AND '1'='1</span></p>
              <p><span class="text-txt-tertiary">Evidence:</span> <span class="text-txt-primary">Respons berbeda saat payload dikirim (halaman berubah dari normal ke kondisi kosong)</span></p>
              <p><span class="text-txt-tertiary">Remediation:</span> <span class="text-neon-green">Gunakan parameterized query (prepared statement), jangan menyusun query SQL dengan string concatenation</span></p>
            </div>
            <p class="text-xs text-txt-secondary leading-relaxed mt-3">
              Cara membacanya: "Ada kemungkinan celah SQL Injection pada parameter <code class="text-neon-cyan">id</code> di halaman products.
              Scanner mengirim karakter <code class="text-neon-cyan">' AND '1'='1</code> dan respons berubah, yang mengindikasikan input
              pengguna masuk ke query SQL tanpa filtrasi. Severity MEDIUM (bisa naik ke HIGH jika terbukti data sensitif bisa diambil).
              Solusinya: perbaiki kode query menggunakan prepared statement sesuai bagian remediation."
            </p>
          </div>
        </section>

        <!-- LAPORAN -->
        <section id="laporan" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">7. Laporan &amp; Format</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-3">
            Halaman <span class="text-neon-cyan">Reports</span> berisi file laporan hasil scan yang bisa diunduh.
            Laporan hanya muncul jika formatnya dipilih saat membuat scan. Pilih format sesuai kebutuhan:
          </p>
          <div class="bg-bg-primary rounded-lg p-4">
            <table class="w-full text-xs">
              <thead>
                <tr class="text-left text-txt-tertiary border-b border-[rgba(0,240,255,0.08)]">
                  <th class="pb-2 pr-4 font-semibold">Format</th>
                  <th class="pb-2 pr-4 font-semibold">Kegunaan Utama</th>
                </tr>
              </thead>
              <tbody class="text-txt-secondary">
                <tr class="border-b border-[rgba(0,240,255,0.05)]">
                  <td class="py-2 pr-4 text-neon-cyan">HTML</td>
                  <td class="py-2">Laporan utama untuk dibaca manusia. Ada executive summary dari AI. Buka di browser.</td>
                </tr>
                <tr class="border-b border-[rgba(0,240,255,0.05)]">
                  <td class="py-2 pr-4 text-neon-cyan">PDF</td>
                  <td class="py-2">Untuk dikirim ke manajemen/klien. Rapi dan siap dicetak.</td>
                </tr>
                <tr class="border-b border-[rgba(0,240,255,0.05)]">
                  <td class="py-2 pr-4 text-neon-cyan">JSON</td>
                  <td class="py-2">Format data mentah untuk diintegrasikan dengan aplikasi/skrip lain.</td>
                </tr>
                <tr class="border-b border-[rgba(0,240,255,0.05)]">
                  <td class="py-2 pr-4 text-neon-cyan">SARIF</td>
                  <td class="py-2">Standar untuk diimpor ke tool keamanan lain (misal GitHub Code Scanning).</td>
                </tr>
                <tr class="border-b border-[rgba(0,240,255,0.05)]">
                  <td class="py-2 pr-4 text-neon-cyan">JUnit XML</td>
                  <td class="py-2">Untuk CI/CD pipeline — scan bisa dijalankan otomatis dan hasil tampil sebagai test report.</td>
                </tr>
                <tr class="border-b border-[rgba(0,240,255,0.05)]">
                  <td class="py-2 pr-4 text-neon-cyan">CSV</td>
                  <td class="py-2">Daftar temuan untuk diolah di spreadsheet atau tool analisis.</td>
                </tr>
                <tr>
                  <td class="py-2 pr-4 text-neon-cyan">XLSX</td>
                  <td class="py-2">Excel — cocok untuk filtering dan sorting manual oleh tim non-teknis.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-sm text-txt-secondary leading-relaxed mt-4">
            Laporan juga dilengkapi pemetaan ke standar compliance (<span class="text-neon-cyan">PCI-DSS v4, SOC 2, ISO 27001:2022</span>),
            sehingga temuan bisa langsung dihubungkan dengan persyaratan audit yang harus dipenuhi organisasi.
          </p>
        </section>

        <!-- BANDNGKAN -->
        <section id="bandingkan" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">8. Membandingkan Scan (Compare Scans)</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-3">
            Fitur ini menjawab pertanyaan: <em>"Setelah saya perbaiki aplikasi, hasilnya membaik atau malah makin buruk?"</em>
          </p>
          <p class="text-sm text-txt-secondary leading-relaxed mb-3">Cara pakai:</p>
          <ol class="text-sm text-txt-secondary space-y-2 list-decimal pl-5">
            <li>Jalankan scan pertama (misal sebelum perbaikan) — ini jadi <span class="text-neon-cyan">baseline</span>.</li>
            <li>Lakukan perbaikan pada aplikasi Anda.</li>
            <li>Jalankan scan kedua dengan konfigurasi sama.</li>
            <li>Buka halaman <span class="text-neon-cyan">Compare Scans</span>, lalu gunakan dua dropdown: pilih scan pertama (baseline) sebagai <span class="text-txt-primary">Scan A</span> dan scan kedua sebagai <span class="text-txt-primary">Scan B</span>, lalu tekan tombol <span class="text-neon-cyan">Compare</span>.</li>
          </ol>
          <p class="text-sm text-txt-secondary leading-relaxed mt-3 mb-2">Hasilnya dibagi 3 bagian (klik tiap judul untuk membuka detail):</p>
          <div class="space-y-3">
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">New (Temuan Baru)</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Celah yang ada di Scan B tapi tidak ada di Scan A. Jika muncul banyak, artinya perubahan Anda justru memperkenalkan masalah baru.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Resolved (Sudah Diperbaiki)</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Celah yang ada di Scan A tapi hilang di Scan B. Ini bukti bahwa perbaikan Anda berhasil.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Persisting (Masih Ada)</p>
              <p class="text-xs text-txt-secondary leading-relaxed">Jumlah celah yang ada di kedua scan (tidak baru dan belum diperbaiki). Jika angka ini tidak turun dari waktu ke waktu, prioritaskan perbaikan di sini.</p>
            </div>
          </div>
          <p class="text-sm text-txt-secondary leading-relaxed mt-3">
            Tip: jalankan scan dengan preset dan konfigurasi yang sama persis agar perbandingan adil dan akurat.
          </p>
        </section>

        <!-- PENGATURAN -->
        <section id="pengaturan" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">9. Pengaturan (Settings)</h2>
          <p class="text-sm text-txt-secondary leading-relaxed mb-4">
            Halaman <span class="text-neon-cyan">Settings</span> berisi konfigurasi aplikasi, terbagi dalam 8 tab.
            Setiap opsi di aplikasi juga punya ikon <span class="text-neon-cyan">?</span> untuk penjelasan cepat. Setelah mengubah apa pun, klik tombol <span class="text-neon-cyan">Save</span> di bawah. Berikut detail per tab:
          </p>

          <div class="space-y-4">
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Tab "Providers" — AI Providers</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                DeepEye mendukung 11+ AI provider: OpenAI, Anthropic Claude, Google Gemini, Ollama (lokal), Groq,
                Mistral, OpenRouter, xAI Grok, LiteLLM, LM Studio, dan OrcaRouter. Anda bisa mengaktifkan lebih dari satu.
                AI digunakan untuk: menganalisis temuan, membuat ringkasan eksekutif, dan menyaring false positive.
                Isi API key provider yang Anda punya lalu klik <span class="text-neon-cyan">Test</span> untuk memastikan koneksi berhasil.
                Jika tidak ada AI provider, scan tetap berjalan normal — hanya fitur analisis AI yang tidak tersedia.
              </p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">Tab "Scanner" — Perilaku Dasar Scanner</p>
              <ul class="text-xs text-txt-secondary space-y-1.5 list-disc pl-4">
                <li><span class="text-txt-primary">Default Depth (1–10)</span> — nilai bawaan kedalaman crawler untuk scan baru.</li>
                <li><span class="text-txt-primary">Default Threads (1–50)</span> — nilai bawaan jumlah permintaan paralel untuk scan baru.</li>
                <li><span class="text-txt-primary">AI Provider</span> — provider AI utama yang dipakai untuk analisis temuan (harus sudah dikonfigurasi di tab Providers).</li>
                <li><span class="text-txt-primary">Proxy</span> — alamat proxy untuk semua lalu lintas scan, contoh <code class="text-neon-cyan">http://127.0.0.1:8080</code> (berguna saat memakai Burp Suite/mitmproxy).</li>
                <li><span class="text-txt-primary">Tiga saklar mode default</span> — Enable Recon, Full Scan, Quick Scan: menyetel mode yang otomatis aktif pada scan baru.</li>
              </ul>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">Tab "Notifications" — Pemberitahuan Hasil Scan</p>
              <p class="text-xs text-txt-secondary leading-relaxed mb-2">Dua saklar utama: <span class="text-txt-primary">Enable Notifications</span> (nyalakan semua notifikasi) dan <span class="text-txt-primary">Notify on Critical Only</span> (hanya kirim notifikasi jika ada temuan Critical — agar tidak berisik).</p>
              <ul class="text-xs text-txt-secondary space-y-1.5 list-disc pl-4">
                <li><span class="text-txt-primary">Email</span> — isi SMTP Server, SMTP Port, Username, Password, From Address, dan daftar To Addresses (penerima). Notifikasi hasil scan dikirim ke email penerima.</li>
                <li><span class="text-txt-primary">Slack</span> — isi Webhook URL (dari aplikasi Slack incoming webhook), Channel tujuan, Bot Name, dan Icon.</li>
                <li><span class="text-txt-primary">Discord</span> — isi Webhook URL (dari Discord channel settings), Bot Name, dan Avatar URL.</li>
              </ul>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">Tab "Proxy" — Proxy &amp; TLS</p>
              <ul class="text-xs text-txt-secondary space-y-1.5 list-disc pl-4">
                <li><span class="text-txt-primary">Intercepting Proxy (mitmweb)</span> — nyalakan jika ingin melihat semua lalu lintas scan di mitmproxy. Isi Bind Host, Proxy Port, Web UI Port, dan opsi <span class="text-txt-primary">Required</span> (jika dicentang, scan batal berjalan saat mitmweb belum siap — mencegah scan tanpa inspeksi).</li>
                <li><span class="text-txt-primary">Scanner Proxy</span> — Enable HTTP Proxy + alamat proxy HTTP dan HTTPS manual, alternatif dari setting proxy di tab Scanner.</li>
                <li><span class="text-txt-primary">TLS Fingerprint Evasion</span> — menyamar sebagai browser asli (Chrome/Edge/Safari versi tertentu) pada level sidik jari TLS, untuk melewati WAF yang mendeteksi tool otomatis. Pilih target impersonation sesuai kebutuhan.</li>
              </ul>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">Tab "Compliance" — Pemetaan Standar Audit</p>
              <p class="text-xs text-txt-secondary leading-relaxed mb-2">
                Nyalakan <span class="text-txt-primary">Enable Compliance Mapping</span>, lalu centang framework yang relevan dengan organisasi Anda:
              </p>
              <ul class="text-xs text-txt-secondary space-y-1.5 list-disc pl-4">
                <li><span class="text-txt-primary">PCI-DSS v4</span> — wajib jika aplikasi memproses pembayaran kartu.</li>
                <li><span class="text-txt-primary">SOC 2</span> — untuk kebutuhan audit layanan SaaS.</li>
                <li><span class="text-txt-primary">ISO 27001:2022</span> — standar manajemen keamanan informasi umum.</li>
              </ul>
              <p class="text-xs text-txt-tertiary leading-relaxed mt-2">Hasilnya: setiap temuan diberi tag kontrol terkait, sehingga laporan langsung siap dipakai untuk audit.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">Tab "Advanced" — Opsi Lanjutan (per grup)</p>
              <div class="text-xs text-txt-secondary space-y-2">
                <p><span class="text-txt-primary">Browser Automation</span> — Enable JavaScript Rendering (render halaman JS penuh via Playwright, wajib untuk aplikasi SPA seperti React/Vue — lebih lambat tapi cakupan jauh lebih luas), Screenshot (simpan gambar tiap halaman), Browser Use AI (AI mengendalikan browser untuk eksplorasi otomatis), dan 3 timeout (page navigation, page overall, dan navigation umum) agar scan tidak menggantung di halaman lambat.</p>
                <p><span class="text-txt-primary">Stealth (anti-deteksi)</span> — UA Rotation (ganti user-agent berkala), Jitter Min/Max (jeda acak antar request dalam detik agar pola terlihat manusiawi), dan Proxy Pool (daftar proxy yang dipakai bergantian untuk menghindari pemblokiran IP).</p>
                <p><span class="text-txt-primary">URL Filtering</span> — Exclude Extensions (jangan scan URL berakhiran tertentu, misal .png/.jpg agar hemat waktu), Exclude Patterns (URL yang cocok pola regex akan dilewati), dan Max Response Size (batas ukuran respons dalam byte yang disimpan — mencegah memori jebol).</p>
                <p><span class="text-txt-primary">AI Triage</span> — Enable AI Triage (AI menyaring temuan), Drop False Positives (buang temuan yang dinilai AI sebagai alarm palsu), Drop Threshold (0–1; semakin rendah semakin agresif pembuangannya), dan Min Severity (temuan di bawah level ini tidak masuk laporan akhir).</p>
                <p><span class="text-txt-primary">RAG (CVE Knowledge Base)</span> — Enable RAG (perkaya analisis dengan database CVE), Auto Rebuild (bangun ulang indeks otomatis), Index Path (lokasi file indeks, default <code class="text-neon-cyan">data/cve_rag_index.pkl</code>), Top K (jumlah dokumen CVE relevan yang diambil), Min Score (ambang relevansi).</p>
                <p><span class="text-txt-primary">Rate Limiting</span> — Enable Rate Limiting, Requests per Second (batas request/detik), Burst Size (toleransi lonjakan sesaat), dan Delay on Error (jeda tambahan saat target mulai menolak request — menyelamatkan scan agar tidak diblokir total).</p>
                <p><span class="text-txt-primary">Logging</span> — Level (DEBUG paling detail sampai CRITICAL paling ringkas), Log File (lokasi file), Log to File (tulis ke file atau tidak), Max File Size, dan Backup Count (jumlah file log lama yang disimpan saat rotasi).</p>
                <p><span class="text-txt-primary">Database</span> — type (SQLite, terkunci), Path (lokasi file database), dan Auto-Cleanup Days (hapus otomatis data scan lebih tua dari N hari — 0 berarti nonaktif).</p>
                <p><span class="text-txt-primary">Auth Macros / Login Replay</span> — untuk aplikasi yang butuh login: Enable Login Replay, Macro Path (file rekaman langkah login oleh Playwright), Recheck Interval (cek ulang sesi login tiap N detik), dan Abort on Fail (hentikan scan jika login gagal).</p>
                <p><span class="text-txt-primary">Bug Bounty</span> — Format laporan khusus platform (HackerOne/Bugcrowd/generic) dan Output Directory (folder penyimpanan), agar temuan siap di-submit ke program bug bounty.</p>
              </div>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-2">Tab "Templates"</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                Daftar scan template yang tersimpan di sistem (nama, path, dan tags). Template adalah konfigurasi scan siap pakai —
                berguna jika Anda sering menjalankan scan dengan pengaturan sama berulang kali.
              </p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Tab "Maintenance" — Perawatan Berkala</p>
              <p class="text-xs text-txt-secondary leading-relaxed">
                Dua fungsi penting yang sebaiknya dijalankan berkala (misal seminggu sekali):<br>
                • <span class="text-txt-primary">Update CVE</span> — mengambil data celah keamanan terbaru dari NVD (National Vulnerability Database) agar scanner mengenali CVE baru.<br>
                • <span class="text-txt-primary">Build RAG</span> — membangun ulang indeks pengetahuan CVE untuk fitur analisis berbasis RAG agar hasil AI lebih kontekstual.
              </p>
            </div>
          </div>
        </section>

        <!-- FAQ -->
        <section id="faq" class="glass rounded-xl p-6 scroll-mt-8">
          <h2 class="text-lg font-semibold text-txt-primary mb-3">10. FAQ &amp; Troubleshooting</h2>
          <div class="space-y-4">
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Q: Scan gagal / tidak mulai. Apa yang harus dicek?</p>
              <p class="text-xs text-txt-secondary leading-relaxed">A: (1) Pastikan backend berjalan — buka <code class="text-neon-cyan">http://localhost:8000/api/health</code> di browser. (2) Pastikan URL target benar dan bisa diakses. (3) Cek halaman Live untuk melihat pesan error. (4) Pastikan checkbox authorized sudah dicentang.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Q: Hasilnya 0 temuan, apakah target pasti aman?</p>
              <p class="text-xs text-txt-secondary leading-relaxed">A: Tidak selalu. Scanner mungkin belum menjangkau semua halaman (coba naikkan depth atau pakai OpenAPI spec), atau target memang cukup aman. Tidak ada scanner yang menjamin 100% bebas celah — gunakan hasil sebagai bahan evaluasi, bukan jaminan mutlak.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Q: Terlalu banyak findings, bingung mulai dari mana?</p>
              <p class="text-xs text-txt-secondary leading-relaxed">A: Filter dengan severity <span class="sev-badge sev-critical">CRITICAL</span> dan <span class="sev-badge sev-high">HIGH</span> terlebih dulu. Perbaiki yang itu dulu, lalu lanjut ke MEDIUM. Baca remediation dan AI Summary tiap temuan sebelum panik — banyak temuan yang ternyata false positive.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Q: Bisakah scan tanpa internet / AI provider cloud?</p>
              <p class="text-xs text-txt-secondary leading-relaxed">A: Bisa. Scan dasar tidak butuh AI. Untuk analisis AI lokal, gunakan provider Ollama atau LM Studio yang berjalan di komputer sendiri tanpa mengirim data ke cloud.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Q: Berapa lama scan butuh waktu?</p>
              <p class="text-xs text-txt-secondary leading-relaxed">A: Tergantung mode, depth, dan ukuran target. Quick scan biasanya beberapa menit; full scan pada website besar bisa berjam-jam. Gunakan mode Recon dulu untuk estimasi awal.</p>
            </div>
            <div class="bg-bg-primary rounded-lg p-4">
              <p class="text-sm font-semibold text-neon-cyan mb-1">Q: Di mana data hasil scan disimpan?</p>
              <p class="text-xs text-txt-secondary leading-relaxed">A: Data scan disimpan di database SQLite (backend) dan file laporan di folder <code class="text-neon-cyan">reports/</code> di root project. Semua data lokal di mesin Anda.</p>
            </div>
          </div>
        </section>

        <footer class="text-center text-xs text-txt-tertiary pb-4">
          DeepEye Scanner Suite v0.1.0 — Dokumentasi ini dibuat agar keamanan siber mudah dipahami semua orang.
        </footer>
      </div>
    </div>
  </div>
</template>
