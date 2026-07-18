<template>
  <div class="app-shell">

    <!-- ━━━━━━━━━━━━━━━━━━ SIDEBAR ━━━━━━━━━━━━━━━━━━ -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">

      <!-- Brand -->
      <div class="sidebar-brand">
        <div class="brand-left" v-if="!isSidebarCollapsed">
          <div class="brand-icon-wrap">
            <img src="/car-icon.jpg" alt="AUTOROAD SCHOOL" class="brand-logo" />
          </div>
          <div class="brand-name">
            <span>AUTOROAD</span>
            <span>SCHOOL</span>
          </div>
        </div>
        <button class="btn-toggle-sidebar" @click="toggleSidebar" :title="isSidebarCollapsed ? 'Menyuni ochish' : 'Menyuni yopish'">
          <svg v-if="isSidebarCollapsed" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
      </div>

      <!-- Main navigation -->
      <nav class="sidebar-nav">

        <!-- Bosh sahifa + sub-item -->
        <!-- All nav items -->
        <button
          v-for="item in allNavItems"
          :key="item.path"
          class="nav-btn"
          :class="{ active: route.path === item.path }"
          @click="go(item.path)"
        >
          <span class="nav-ico" v-html="item.icon"></span>
          <span class="nav-label" v-if="!isSidebarCollapsed">{{ item.label }}</span>
        </button>

      </nav>

      <!-- Bottom: Settings -->
      <div class="sidebar-bottom">
        <button
          class="nav-btn"
          :class="{ active: route.path === '/settings' }"
          @click="go('/settings')"
        >
          <span class="nav-ico" v-html="icons.settings"></span>
          <span class="nav-label" v-if="!isSidebarCollapsed">Sozlamalar</span>
        </button>
      </div>

    </aside>

    <!-- ━━━━━━━━━━━━━━━━━━ MAIN ━━━━━━━━━━━━━━━━━━ -->
    <div class="main-area">

      <!-- Topbar -->
      <header class="topbar">
        <h1 class="topbar-title">{{ pageTitle }}</h1>

        <div class="topbar-end">
          <!-- Search -->
          <div class="search-wrap">
            <svg viewBox="0 0 20 20" fill="none" stroke="#9ca3af" stroke-width="2" width="16" height="16">
              <circle cx="8.5" cy="8.5" r="5.5"/>
              <line x1="13" y1="13" x2="18" y2="18"/>
            </svg>
            <input class="search-inp" type="text" placeholder="Qidirish..." />
          </div>

          <!-- Notification -->
          <button class="notif-btn" aria-label="Bildirishnomalar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            <span class="notif-dot"></span>
          </button>

          <!-- User dropdown -->
          <div class="user-wrap" ref="userWrapRef">
            <button id="user-menu-btn" class="user-trigger" @click="showDropdown = !showDropdown">
              <img src="/car-icon.jpg" alt="Admin" class="user-ava" />
              <span class="user-greeting">Xush kelibsiz, Admin</span>
              <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"
                   :style="{ transform: showDropdown ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }">
                <path fill-rule="evenodd"
                      d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                      clip-rule="evenodd"/>
              </svg>
            </button>

            <transition name="dd">
              <div v-if="showDropdown" class="user-dropdown">
                <button id="logout-btn" class="dropdown-item logout-item" @click="handleLogout">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                    <polyline points="16 17 21 12 16 7"/>
                    <line x1="21" y1="12" x2="9" y2="12"/>
                  </svg>
                  Chiqish
                </button>
              </div>
            </transition>
          </div>

        </div>
      </header>

      <!-- Page body: slotted content scrolls here -->
      <main class="page-body">
        <slot />
      </main>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isSidebarCollapsed = ref(localStorage.getItem('sidebar_collapsed') === 'true')
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebar_collapsed', isSidebarCollapsed.value)
}

function go(path) {
  router.push(path)
}

// ── Dynamic page title ───────────────────────────────────────
const pageTitles = {
  '/':                  "Ko'rinish",
  '/pending-students':  "Kutilayotgan Talabalar",
  '/students':          "O'quvchilar Boshqaruvi",
  '/groups':            "Guruhlar Boshqaruvi",
  '/instructors':       "Instruktorlar",
  '/vehicles':          "Avtomobillar",
  '/lessons':           "Darslar",
  '/billing':           "To'lovlar",
  '/users':             "Foydalanuvchilar",
  '/reports':           "Hisobotlar",
  '/settings':          "Sozlamalar",
}

const pageTitle = computed(() => pageTitles[route.path] ?? "Ko'rinish")

// ── User dropdown ────────────────────────────────────────────
const showDropdown = ref(false)
const userWrapRef = ref(null)

function handleOutsideClick(e) {
  if (userWrapRef.value && !userWrapRef.value.contains(e.target)) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}

// ── Inline SVG icons ─────────────────────────────────────────
const icons = {
  dashboard: `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>`,
  students:  `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v2h20v-2c0-3.3-6.7-5-10-5z"/></svg>`,
  instructors:`<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M16 11c1.7 0 3-1.3 3-3s-1.3-3-3-3-3 1.3-3 3 1.3 3 3 3zM8 11c1.7 0 3-1.3 3-3S9.7 5 8 5 5 6.3 5 8s1.3 3 3 3zm0 2c-2.3 0-7 1.2-7 3.5V19h14v-2.5C15 14.2 10.3 13 8 13zm8 0c-.3 0-.6 0-1 .1 1.2.9 2 2.1 2 3.4V19h6v-2.5c0-2.3-4.7-3.5-7-3.5z"/></svg>`,
  vehicles:  `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>`,
  lessons:   `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 14H8v-2h8v2zm0-4H8v-2h8v2zm0-4H8V6h8v2z"/></svg>`,
  billing:   `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>`,
  reports:   `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14H7v-4h5v4zm5 0h-4v-7h4v7z"/></svg>`,
  pending:   `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M6 2v6l4 4-4 4v6h12v-6l-4-4 4-4V2H6zm10 14.5V20H8v-3.5l4-4 4 4zm-4-5l-4-4V4h8v3.5l-4 4z"/></svg>`,
  settings:  `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54C14.6 3.17 14.4 3 14.16 3h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L3.74 9.47c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>`,
  groups:    `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 3-1.34 3-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 2.01 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>`,
  users:     `<svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>`,
  learningPlaces: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="17" height="17"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>`,
}

const allNavItems = [
  { path: '/',                  label: 'Bosh sahifa',      icon: icons.dashboard },
  { path: '/categories',        label: 'Kategoriyalar',   icon: icons.pending },
  { path: '/students',          label: 'Talabalar',        icon: icons.students },
  { path: '/groups',            label: 'Guruhlar',         icon: icons.groups },
  { path: '/billing',           label: "To'lovlar",        icon: icons.billing },
  { path: '/users',             label: 'Foydalanuvchilar', icon: icons.users },
  { path: '/learning-places',   label: "O'quv Joylari",    icon: icons.learningPlaces },
  { path: '/instructors',       label: 'Instruktorlar',    icon: icons.instructors },
  { path: '/vehicles',          label: 'Avtomobillar',     icon: icons.vehicles },
  { path: '/lessons',           label: 'Darslar',          icon: icons.lessons },
  { path: '/reports',           label: 'Hisobotlar',       icon: icons.reports },
]
</script>

<style scoped>
/* ─── Reset ────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
button { cursor: pointer; background: none; border: none; font-family: inherit; }

/* ─── App shell ─────────────────────────────────────────────── */
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
  background: #F1F4F9;
}

/* ━━━━━━━━━━━━━━━━━━━━ SIDEBAR ━━━━━━━━━━━━━━━━━━━━ */
.sidebar {
  width: 224px;
  flex-shrink: 0;
  background: #1B2430;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar.sidebar-collapsed {
  width: 68px;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 18px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
  height: 79px;
}

.sidebar.sidebar-collapsed .sidebar-brand {
  justify-content: center;
  padding: 18px 0;
}

.brand-icon-wrap {
  width: 42px;
  height: 42px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.brand-logo {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.brand-name {
  display: flex;
  flex-direction: column;
  color: white;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: 0.08em;
  line-height: 1.4;
}

.sidebar-nav {
  flex: 1;
  padding: 10px 8px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sidebar-nav::-webkit-scrollbar { display: none; }

/* Nav group (parent + sub-items) */
.nav-group {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

/* Main nav button */
.nav-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.55);
  font-size: 13.5px;
  font-weight: 500;
  text-align: left;
  transition: background 0.15s, color 0.15s;
}
.nav-btn:hover { background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.9); }
.nav-btn.active { background: #2D6A4F; color: white; }

.nav-ico { display: flex; align-items: center; flex-shrink: 0; opacity: 0.9; }

.brand-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-toggle-sidebar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.6);
  transition: background 0.15s, color 0.15s;
}

.btn-toggle-sidebar:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

.sidebar.sidebar-collapsed .nav-btn {
  justify-content: center;
  padding: 12px;
}

/* Sub-item */
.nav-sub-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px 7px 36px;
  border-radius: 7px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12.5px;
  font-weight: 500;
  text-align: left;
  transition: background 0.15s, color 0.15s;
  width: 100%;
}
.nav-sub-btn:hover { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.75); }
.nav-sub-btn.sub-active { color: #74C69D; background: rgba(45, 106, 79, 0.18); }

.sub-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
  opacity: 0.7;
}

.sidebar-bottom {
  padding: 8px;
  border-top: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}

/* ━━━━━━━━━━━━━━━━━━━━ MAIN AREA ━━━━━━━━━━━━━━━━━━━━ */
.main-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Topbar ─────────────────────────────────────────── */
.topbar {
  height: 60px;
  background: white;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  z-index: 10;
}

.topbar-title {
  font-size: 19px;
  font-weight: 700;
  color: #111827;
}

.topbar-end {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-wrap {
  display: flex;
  align-items: center;
  gap: 7px;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  padding: 7px 12px;
  width: 210px;
}

.search-inp {
  border: none;
  background: transparent;
  outline: none;
  font-size: 13px;
  color: #374151;
  width: 100%;
  font-family: inherit;
}
.search-inp::placeholder { color: #9CA3AF; }

.notif-btn {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6B7280;
  transition: background 0.15s;
}
.notif-btn:hover { background: #F3F4F6; }

.notif-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  border: 1.5px solid white;
}

.user-wrap { position: relative; }

.user-trigger {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 10px 5px 6px;
  border-radius: 10px;
  border: 1px solid #E5E7EB;
  background: white;
  color: #374151;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.15s;
}
.user-trigger:hover { background: #F9FAFB; }

.user-ava {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  mix-blend-mode: multiply;
  background: #f0f0f0;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 160px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.10);
  overflow: hidden;
  z-index: 100;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 14px;
  font-size: 13.5px;
  color: #374151;
  transition: background 0.15s;
  text-align: left;
}
.dropdown-item:hover { background: #F9FAFB; }
.logout-item { color: #dc2626; }

.dd-enter-active, .dd-leave-active { transition: opacity 0.15s, transform 0.15s; }
.dd-enter-from, .dd-leave-to { opacity: 0; transform: translateY(-6px); }

/* ── Page body ─────────────────────────────────────── */
.page-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 24px;
}
.page-body::-webkit-scrollbar { width: 5px; }
.page-body::-webkit-scrollbar-track { background: transparent; }
.page-body::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 4px; }
</style>

<style>
html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; }
</style>
