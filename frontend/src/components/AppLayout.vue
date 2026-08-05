<template>
  <div class="app-shell" :class="{ 'mobile-nav-open': mobileNavOpen }">

    <!-- Backdrop behind the mobile drawer -->
    <div v-if="mobileNavOpen" class="mobile-backdrop" @click="mobileNavOpen = false"></div>

    <!-- ━━━━━━━━━━━━━━━━━━ SIDEBAR ━━━━━━━━━━━━━━━━━━ -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed, 'sidebar-mobile-open': mobileNavOpen }">

      <!-- Brand -->
      <div class="sidebar-brand">
        <div class="brand-left" v-if="showNavLabels">
          <div class="brand-icon-wrap">
            <img src="/car-icon.jpg" alt="Logo" class="brand-logo" />
          </div>
          <div class="branch-select-big-wrap" v-if="authStore.isSuperuser">
            <select
              :value="branchStore.activeBranch"
              @change="onBranchChange"
              class="branch-select-big"
            >
              <option value="">BARCHA FILIALLAR</option>
              <option
                v-for="b in branchStore.branches"
                :key="b.id"
                :value="b.name"
              >
                {{ b.name.toUpperCase() }}
              </option>
            </select>
            <div class="branch-select-big-icon">▼</div>
          </div>
          <div class="branch-label-big" v-else :title="ownBranchLabel">
            {{ ownBranchLabel.toUpperCase() }}
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
        <!-- Students and teaching staff get a single "my profile" entry -->
        <button
          v-if="ownProfileRoute"
          class="nav-btn"
          :class="{ active: route.path === ownProfileRoute }"
          @click="go(ownProfileRoute)"
        >
          <span class="nav-ico" v-html="icons.students"></span>
          <span class="nav-label" v-if="showNavLabels">Mening Profilim</span>
        </button>

        <template v-if="navItems.length">
          <template v-for="item in navItems" :key="item.path || item.label">
            <!-- Dropdown group -->
            <div v-if="item.children" class="nav-group">
              <button
                class="nav-btn nav-btn-parent"
                :class="{ 'group-active': isChildActive(item) }"
                @click="toggleGroup(item.label)"
              >
                <span class="nav-ico" v-html="item.icon"></span>
                <span class="nav-label" v-if="showNavLabels">{{ item.label }}</span>
                <span v-if="showNavLabels" class="nav-arrow" :class="{ 'rotated': isGroupOpen(item) }">
                  <svg viewBox="0 0 20 20" fill="currentColor" width="12" height="12"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
                </span>
              </button>
              <div v-if="isGroupOpen(item) && showNavLabels" class="nav-children">
                <button
                  v-for="child in item.children"
                  :key="child.label"
                  class="nav-sub-btn"
                  :class="{ 'sub-active': route.path === child.path && route.query.role === child.role }"
                  @click="goRole(child.path, child.role)"
                >
                  <span class="sub-dot"></span>
                  {{ child.label }}
                </button>
              </div>
            </div>

            <!-- Regular item -->
            <button
              v-else
              class="nav-btn"
              :class="{ active: route.path === item.path }"
              @click="go(item.path)"
            >
              <span class="nav-ico" v-html="item.icon"></span>
              <span class="nav-label" v-if="showNavLabels">{{ item.label }}</span>
            </button>
          </template>
        </template>
      </nav>

    </aside>

    <!-- ━━━━━━━━━━━━━━━━━━ MAIN ━━━━━━━━━━━━━━━━━━ -->
    <div class="main-area">

      <!-- Topbar -->
      <header class="topbar">
        <button class="btn-mobile-menu" @click="mobileNavOpen = true" aria-label="Menyuni ochish">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>

        <h1 class="topbar-title">{{ pageTitle }}</h1>

        <div class="topbar-end">
          <!-- Current user -->
          <span class="topbar-username">{{ currentUserDisplayName }}</span>

          <!-- Notification -->
          <button class="notif-btn" aria-label="Bildirishnomalar" @click="go('/notifications')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            <span v-if="unreadNotifCount > 0" class="notif-badge-num">{{ unreadNotifCount > 99 ? '99+' : unreadNotifCount }}</span>
          </button>

          <!-- User dropdown -->
          <div class="user-wrap" ref="userWrapRef">
            <button id="user-menu-btn" class="user-trigger" @click="showDropdown = !showDropdown">
              <img :src="authStore.user?.image || '/default_photo.png'" alt="User" class="user-ava" />
              <span class="user-greeting">{{ currentUserDisplayName }}</span>
              <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"
                   :style="{ transform: showDropdown ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }">
                <path fill-rule="evenodd"
                      d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                      clip-rule="evenodd"/>
              </svg>
            </button>

            <transition name="dd">
              <div v-if="showDropdown" class="user-dropdown">
                <button id="change-password-btn" class="dropdown-item" @click="openChangePasswordModal">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                  Parolni o'zgartirish
                </button>
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

      <!-- Change Password Modal -->
      <dialog ref="changePasswordModal" class="modal-dialog" closedby="any">
        <form class="modal-form" @submit.prevent="submitChangePassword">
          <div class="modal-head">
            <h3 class="modal-title">Parolni o'zgartirish</h3>
            <button type="button" class="btn-close" @click="closeChangePasswordModal">✕</button>
          </div>
          <div v-if="changePasswordError" class="modal-error">{{ changePasswordError }}</div>
          <div v-if="changePasswordSuccess" class="modal-success">{{ changePasswordSuccess }}</div>

          <div class="form-group">
            <label class="form-label">Yangi parol <span class="req">*</span></label>
            <input v-model="changePasswordForm.new_password" type="password" class="form-input" required autocomplete="new-password" />
          </div>
          <div class="form-group">
            <label class="form-label">Yangi parolni tasdiqlang <span class="req">*</span></label>
            <input v-model="changePasswordForm.confirm_password" type="password" class="form-input" required autocomplete="new-password" />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="closeChangePasswordModal">Bekor qilish</button>
            <button type="submit" class="btn-save" :disabled="changePasswordSaving">
              {{ changePasswordSaving ? "Saqlanmoqda..." : "Saqlash" }}
            </button>
          </div>
        </form>
      </dialog>

      <!-- Page body: slotted content scrolls here -->
      <main class="page-body" ref="pageBodyRef">
        <slot />
      </main>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import api from '@/services/api'
import { initDualScrollbars } from '@/utils/dualScrollbar'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const branchStore = useBranchStore()

function onBranchChange(e) {
  if (!authStore.isSuperuser) return
  branchStore.setActiveBranch(e.target.value)
  window.location.reload()
}

// Non-superuser accounts are locked to their own branch — no switching allowed.
const ownBranchLabel = computed(() => {
  return authStore.user?.branch_name || "AutoRoad School"
})

function syncBranchForCurrentUser() {
  const user = authStore.user
  if (!user) return
  if (authStore.isSuperuser) {
    branchStore.fetchBranches()
    return
  }
  const ownBranch = user.branch_name
  if (ownBranch && (branchStore.activeBranch !== ownBranch || branchStore.activeBranchId !== user.branch)) {
    // `user.branch` is the branch id straight from the user record — no lookup needed.
    branchStore.setActiveBranch(ownBranch, user.branch ?? null)
  }
}

const isSidebarCollapsed = ref(localStorage.getItem('sidebar_collapsed') === 'true')
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebar_collapsed', isSidebarCollapsed.value)
}

// On phones the sidebar is an off-canvas drawer instead of a fixed column.
const mobileNavOpen = ref(false)
watch(() => route.fullPath, () => { mobileNavOpen.value = false })

const isMobile = ref(typeof window !== 'undefined' && window.innerWidth <= 900)
function handleViewportResize() {
  isMobile.value = window.innerWidth <= 900
  if (!isMobile.value) mobileNavOpen.value = false
}

// "Collapsed" is a desktop-only affordance: the mobile drawer always shows
// full labels, so nav items stay readable however the desktop state was left.
const showNavLabels = computed(() => isMobile.value || !isSidebarCollapsed.value)

function go(path) {
  router.push(path)
}

function goRole(path, role) {
  router.push({ path, query: role ? { role } : undefined })
}

// ── Nav group (dropdown) state ─────────────────────────────────
// A group auto-opens whenever one of its children is the active route, and
// otherwise stays closed unless the user explicitly clicks it open — that
// manual override is session-only (never persisted) and is cleared on every
// navigation, so a dropdown never stays stuck open on unrelated pages.
const manuallyOpenedGroups = ref(new Set())

function isChildActive(item) {
  if (!item.children) return false
  return item.children.some(c => route.path === c.path && (route.query.role || null) === (c.role || null))
}

function isGroupOpen(item) {
  return isChildActive(item) || manuallyOpenedGroups.value.has(item.label)
}

function toggleGroup(label) {
  if (manuallyOpenedGroups.value.has(label)) {
    manuallyOpenedGroups.value.delete(label)
  } else {
    manuallyOpenedGroups.value.add(label)
  }
}

watch(() => route.path, () => {
  manuallyOpenedGroups.value.clear()
})

// ── Dynamic page title ───────────────────────────────────────
const pageTitles = {
  '/':                  "Ko'rinish",
  '/pending-students':  "Kutilayotgan Talabalar",
  '/students':          "O'quvchilar Boshqaruvi",
  '/groups':            "Guruhlar Boshqaruvi",
  '/instructors':       "Instruktorlar",
  '/vehicles':          "Avtomobillar",
  '/cars':              "Avtomobillar",
  '/lessons':           "Darslar",
  '/billing':           "Moliya Boshqaruvi",
  '/finances/accepted': "Tushumlar (Qabul qilingan to'lovlar)",
  '/finances/payments': "To'lovlar (To'langan statusda)",
  '/finances/returned': "Pul Qaytarish (Qaytarilgan statusda)",
  '/finances/bonus':    "Agent Bonuslari (Bonus statusda)",
  '/finances/bank':     "Bank uchun To'lovlar (Bank statusda)",
  '/finances/teachers': "O'qituvchilar To'lovlari",
  '/finances/instructors': "Instruktorlar To'lovlari",
  '/finances/debts':    "Qarzdorlar Ro'yxati",
  '/users':             "Foydalanuvchilar",
  '/learning-places':   "O'quv Joylari",
  '/agents':            "Agentlar Boshqaruvi",
  '/certificates':      "Sertifikatlar",
  '/holidays':          "Bayramlar Boshqaruvi",
  '/vehicles':          "Avtomobillar",
  '/notifications':     "Bildirishnomalar",
  '/reports':           "Hisobotlar",
  '/settings':          "Sozlamalar",
}

const roleTitles = {
  coordinator: "O'qituvchilar",
  instructor: 'Instruktorlar',
  mechanic: 'Mexaniklar',
  admin: 'Adminlar',
}

const pageTitle = computed(() => {
  if (route.path === '/users' && route.query.role && roleTitles[route.query.role]) {
    return roleTitles[route.query.role]
  }
  if (route.path.startsWith('/users/')) return "Foydalanuvchi Ma'lumotlari"
  if (route.path.startsWith('/agents/')) return "Agent Ma'lumotlari"
  if (route.path.startsWith('/learning-places/')) return "O'quv Joyi Ma'lumotlari"
  if (route.path.startsWith('/students/')) return "O'quvchi Ma'lumotlari"
  if (route.path.startsWith('/groups/')) return "Guruh Ma'lumotlari"
  if (route.path.startsWith('/vehicles/')) return "Avtomobil Ma'lumotlari"
  return pageTitles[route.path] ?? "Ko'rinish"
})

// ── User dropdown ────────────────────────────────────────────
const showDropdown = ref(false)
const userWrapRef = ref(null)
const unreadNotifCount = ref(0)

const currentUserDisplayName = computed(() => {
  const u = authStore.user
  if (!u) return 'Xush kelibsiz'
  if (u.full_name && u.full_name.trim()) return u.full_name.trim()
  if (u.first_name || u.last_name) return `${u.first_name || ''} ${u.last_name || ''}`.trim()
  if (u.phone) return u.phone
  return 'Xush kelibsiz'
})

function handleOutsideClick(e) {
  if (userWrapRef.value && !userWrapRef.value.contains(e.target)) {
    showDropdown.value = false
  }
}

async function fetchUnreadCount() {
  // Notifications polling is superuser-only — other roles don't need to hit
  // the backend on a timer just to keep a badge count updated.
  if (!authStore.isSuperuser) return
  try {
    const res = await api.get('/notifications/unread_count/')
    unreadNotifCount.value = res.data.unread_count || 0
  } catch (err) {
    console.error("Unread notifications count Error:", err)
  }
}

let unreadTimer = null

watch(() => route.path, () => {
  fetchUnreadCount()
})

watch(() => authStore.user, () => {
  fetchUnreadCount()
  syncBranchForCurrentUser()
}, { immediate: true })

// ── Dual (top+bottom) table scrollbars ───────────────────────
// Tables render/resize asynchronously (loading states, filters), so a
// MutationObserver on the page body re-scans for new/changed table wrappers
// instead of wiring this per-view.
const pageBodyRef = ref(null)
let dualScrollObserver = null
let dualScrollRaf = null

function scheduleDualScrollScan() {
  if (dualScrollRaf) cancelAnimationFrame(dualScrollRaf)
  dualScrollRaf = requestAnimationFrame(() => {
    if (pageBodyRef.value) initDualScrollbars(pageBodyRef.value)
  })
}

watch(() => route.fullPath, () => {
  nextTick(scheduleDualScrollScan)
})

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  window.addEventListener('resize', handleViewportResize)
  fetchUnreadCount()
  if (authStore.isSuperuser) {
    unreadTimer = setInterval(fetchUnreadCount, 5000)
  }
  syncBranchForCurrentUser()

  nextTick(scheduleDualScrollScan)
  if (pageBodyRef.value && typeof MutationObserver !== 'undefined') {
    dualScrollObserver = new MutationObserver(scheduleDualScrollScan)
    dualScrollObserver.observe(pageBodyRef.value, { childList: true, subtree: true })
  }
  window.addEventListener('resize', scheduleDualScrollScan)
})
onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
  window.removeEventListener('resize', handleViewportResize)
  window.removeEventListener('resize', scheduleDualScrollScan)
  if (unreadTimer) clearInterval(unreadTimer)
  if (dualScrollObserver) dualScrollObserver.disconnect()
  if (dualScrollRaf) cancelAnimationFrame(dualScrollRaf)
})

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}

// ── Change password ──────────────────────────────────────────
const changePasswordModal = ref(null)
const changePasswordSaving = ref(false)
const changePasswordError = ref('')
const changePasswordSuccess = ref('')
const changePasswordForm = ref({ new_password: '', confirm_password: '' })

function openChangePasswordModal() {
  showDropdown.value = false
  changePasswordError.value = ''
  changePasswordSuccess.value = ''
  changePasswordForm.value = { new_password: '', confirm_password: '' }
  changePasswordModal.value?.showModal()
}

function closeChangePasswordModal() {
  changePasswordModal.value?.close()
}

async function submitChangePassword() {
  const f = changePasswordForm.value
  changePasswordError.value = ''
  changePasswordSuccess.value = ''

  if (f.new_password !== f.confirm_password) {
    changePasswordError.value = "Yangi parollar mos kelmadi."
    return
  }
  if (f.new_password.length < 4) {
    changePasswordError.value = "Yangi parol kamida 4 ta belgidan iborat bo'lishi kerak."
    return
  }

  changePasswordSaving.value = true
  try {
    await api.post('/users/change-password/', {
      new_password: f.new_password,
    })
    changePasswordSuccess.value = "Parol muvaffaqiyatli o'zgartirildi."
    setTimeout(() => closeChangePasswordModal(), 1200)
  } catch (err) {
    changePasswordError.value = err.response?.data?.detail || "Parolni o'zgartirishda xatolik yuz berdi."
  } finally {
    changePasswordSaving.value = false
  }
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
  agents: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="17" height="17"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
  holidays: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="17" height="17"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line><path d="M8 14h.01"></path><path d="M12 14h.01"></path><path d="M16 14h.01"></path></svg>`,
  certificates: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="17" height="17"><circle cx="12" cy="8" r="6"></circle><path d="M8.21 13.89L7 23l5-3 5 3-1.21-9.12"></path></svg>`,
}

const allNavItems = [
  { path: '/',                  label: 'Bosh sahifa',      icon: icons.dashboard },
  { path: '/categories',        label: 'Kategoriyalar',   icon: icons.pending },
  { path: '/students',          label: 'Talabalar',        icon: icons.students },
  { path: '/groups',            label: 'Guruhlar',         icon: icons.groups },
  {
    label: 'Moliya',
    icon: icons.billing,
    children: [
      { label: 'Tushumlar',       path: '/finances/accepted' },
      { label: "Xarajatlar",       path: '/finances/payments' },
      // Returning money is superuser-only — admins never see this entry.
      { label: 'Pul qaytarish',   path: '/finances/returned', superuserOnly: true },
      { label: 'Agentlar',        path: '/finances/bonus' },
      { label: 'Bank uchun',      path: '/finances/bank' },
      { label: "O'qituvchilar",   path: '/finances/teachers' },
      { label: 'Instruktorlar',   path: '/finances/instructors' },
      { label: 'Qarzdorlar',      path: '/finances/debts' },
    ]
  },
  {
    label: 'Xodimlar',
    icon: icons.users,
    children: [
      { label: "O'qituvchilar",  path: '/users', role: 'coordinator' },
      { label: 'Instruktorlar',  path: '/users', role: 'instructor' },
      { label: 'Mexaniklar',     path: '/users', role: 'mechanic' },
      { label: 'Adminlar',       path: '/users', role: 'admin' },
    ]
  },
  { path: '/learning-places',   label: "O'quv Joylari",    icon: icons.learningPlaces },
  { path: '/agents',            label: 'Agentlar',         icon: icons.agents },
  { path: '/certificates',      label: 'Sertifikatlar',    icon: icons.certificates },
  { path: '/holidays',          label: 'Bayramlar',        icon: icons.holidays },
  { path: '/vehicles',          label: 'Avtomobillar',     icon: icons.vehicles },
  { path: '/lessons',           label: 'Darslar',          icon: icons.lessons },
]

// Paths each non-admin role is allowed to see in the sidebar. Kept in step with
// the router's ROLE_ROUTES allowlist so the nav never offers a dead link.
const ROLE_NAV_PATHS = {
  mechanic: ['/groups', '/students', '/vehicles', '/lessons', '/learning-places'],
  instructor: ['/lessons'],
  coordinator: ['/lessons'],
}

const navItems = computed(() => {
  const role = authStore.user?.role
  const isSuper = authStore.isSuperuser

  // Superusers see everything as-is.
  if (isSuper) return allNavItems

  // Admins see everything except the superuser-only finance entries.
  if (role === 'admin') {
    return allNavItems.map(item => {
      if (!item.children) return item
      const children = item.children.filter(c => !c.superuserOnly)
      return children.length ? { ...item, children } : null
    }).filter(Boolean)
  }

  const allowedPaths = ROLE_NAV_PATHS[role]
  if (!allowedPaths) return []
  return allNavItems.filter(item => item.path && allowedPaths.includes(item.path))
})

// Teaching staff and students both work out of a single "my profile" entry.
const ownProfileRoute = computed(() => {
  const u = authStore.user
  if (!u) return null
  if (u.role === 'student') return `/students/${u.id}`
  if (u.role === 'instructor' || u.role === 'coordinator') return `/users/${u.id}`
  return null
})
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
.nav-btn.group-active { color: rgba(255,255,255,0.9); background: rgba(255,255,255,0.05); }

.nav-ico { display: flex; align-items: center; flex-shrink: 0; opacity: 0.9; }

/* Nav dropdown arrow */
.nav-arrow {
  margin-left: auto;
  display: flex;
  align-items: center;
  opacity: 0.5;
  transition: transform 0.2s ease;
}
.nav-arrow.rotated {
  transform: rotate(180deg);
  opacity: 0.8;
}

/* Nav children (sub-items under dropdown parent) */
.nav-children {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 2px 0 2px 4px;
  border-left: 2px solid rgba(255,255,255,0.08);
  margin-left: 14px;
  overflow: hidden;
  animation: slideDown 0.15s ease;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: translateY(0); }
}

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

.topbar-username {
  font-size: 13.5px;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.notif-btn {
  position: relative;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #F9FAFB;
  border: 1.5px solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4B5563;
  cursor: pointer;
  overflow: visible !important;
  transition: all 0.2s ease;
}
.notif-btn:hover { background: #F3F4F6; border-color: #CBD5E1; color: #1F2937; }

.notif-badge-num {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #EF4444;
  color: white;
  font-size: 10.5px;
  font-weight: 800;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.45);
  z-index: 10;
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

.branch-select-big-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  margin-left: 4px;
}

.branch-select-big {
  appearance: none;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.12);
  color: #F9FAFB;
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  padding: 6px 24px 6px 10px;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  cursor: pointer;
  outline: none;
  width: 100%;
  transition: all 0.15s ease;
}

.branch-select-big:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.branch-select-big option {
  background: #1E293B;
  color: #F3F4F6;
  font-size: 13px;
  font-weight: 700;
}

.branch-label-big {
  flex: 1;
  margin-left: 4px;
  background: rgba(255, 255, 255, 0.06);
  color: #F9FAFB;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: default;
}

.branch-select-big-icon {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 9px;
  color: #CBD5E1;
  pointer-events: none;
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

/* ── Mobile drawer ─────────────────────────────────── */
.btn-mobile-menu {
  display: none;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 9px;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  color: #374151;
  flex-shrink: 0;
  margin-right: 10px;
}
.btn-mobile-menu:hover { background: #F3F4F6; }

.mobile-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(2px);
  z-index: 90;
}

@media (max-width: 900px) {
  .btn-mobile-menu { display: flex; }

  /* Sidebar slides in over the content instead of taking column space. */
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 250px !important;
    transform: translateX(-100%);
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 100;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.3);
  }
  .sidebar.sidebar-mobile-open { transform: translateX(0); }

  /* Collapsed mode is a desktop-only affordance — always show full labels
     in the drawer, and hide the desktop collapse toggle. */
  .sidebar .nav-label { display: inline !important; }
  .sidebar.sidebar-collapsed .nav-btn { justify-content: flex-start; padding: 10px 12px; }
  .sidebar.sidebar-collapsed .sidebar-brand { justify-content: space-between; padding: 18px 14px; }
  .btn-toggle-sidebar { display: none; }

  .topbar { padding: 0 14px; height: 56px; }
  .topbar-title { font-size: 16px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .topbar-end { gap: 8px; }
  .topbar-username { display: none; }

  .page-body { padding: 14px 12px 20px; }
}

@media (max-width: 560px) {
  .user-greeting { display: none; }
  .user-trigger { padding: 5px 8px 5px 6px; }
  .notif-btn { width: 34px; height: 34px; }
  .topbar-title { font-size: 15px; }
}

/* ── Change password modal ─────────────────────────────── */
.modal-dialog {
  border: none;
  border-radius: 20px;
  padding: 0;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: white;
  margin: auto;
}
.modal-dialog::backdrop {
  background: rgba(17, 24, 39, 0.45);
  backdrop-filter: blur(6px);
}
.modal-form { padding: 0; }
.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 24px 16px;
  border-bottom: 1px solid #F3F4F6;
  margin-bottom: 20px;
}
.modal-title { font-size: 17px; font-weight: 700; color: #111827; margin: 0; }
.btn-close {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #F3F4F6;
  border: none;
  color: #6B7280;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.modal-error, .modal-success {
  margin: 0 24px 16px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
}
.modal-error { background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }
.modal-success { background: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
.form-group { padding: 0 24px; margin-bottom: 16px; display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 12.5px; font-weight: 600; color: #374151; }
.req { color: #DC2626; }
.form-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 13.5px;
  border: 1.5px solid #D1D5DB;
  border-radius: 10px;
  outline: none;
  background: #F9FAFB;
  color: #111827;
  box-sizing: border-box;
}
.form-input:focus { border-color: #2D6A4F; background: white; }
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 24px;
}
.btn-cancel {
  padding: 10px 18px;
  border: 1px solid #D1D5DB;
  background: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
}
.btn-save {
  padding: 10px 22px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13.5px;
  border: none;
  cursor: pointer;
}
.btn-save:disabled { opacity: 0.7; cursor: not-allowed; }
</style>

<style>
html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; }

/* Injected by dualScrollbar.js: a top scrollbar strip mirroring the table
   wrapper's own bottom scrollbar, so long tables are scrollable from the
   top too. Not scoped — the elements are created outside Vue's render. */
.dual-scroll-top {
  overflow-x: auto;
  overflow-y: hidden;
  height: 14px;
  margin-bottom: 4px;
}
.dual-scroll-top-spacer {
  height: 1px;
}
.dual-scroll-top::-webkit-scrollbar {
  height: 10px;
}
.dual-scroll-top::-webkit-scrollbar-track {
  background: #F1F4F9;
  border-radius: 5px;
}
.dual-scroll-top::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 5px;
}
.dual-scroll-top::-webkit-scrollbar-thumb:hover {
  background: #9CA3AF;
}
</style>
