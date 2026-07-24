<template>
  <AppLayout>

    <!-- Top Action Bar -->
    <div class="page-top">
      <div class="top-title-wrap">
        <h2 class="page-main-title">{{ rolePageTitle }}</h2>
        <p class="page-sub-title">{{ rolePageSub }}</p>
      </div>
      <button v-if="authStore.isSuperuser" class="btn-add" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="16" height="16" style="margin-right: 6px;">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Yangi Foydalanuvchi
      </button>
    </div>

    <!-- Filter Card -->
    <div class="filter-card">
      <div class="filter-field">
        <label class="filter-label">F.I.SH. yoki Telefon raqami bo'yicha qidirish</label>
        <div class="search-input-wrap">
          <input
            v-model="filterSearch"
            type="text"
            placeholder="Qidiruv..."
            class="filter-input"
          />
          <svg class="search-ico" viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="14" height="14">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="12.5" y1="12.5" x2="16" y2="16"/>
          </svg>
        </div>
      </div>

      <!-- Active role badge indicator -->
      <div v-if="filterRole" class="filter-role-badge">
        <span class="role-badge" :class="roleClass(filterRole, false)">{{ roleMeta[filterRole]?.title }}</span>
        <span class="filter-role-hint">bo'yicha ko'rsatilmoqda</span>
      </div>
    </div>

    <!-- Table Container -->
    <div class="table-card">
      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p class="state-text">Foydalanuvchilar yuklanmoqda...</p>
      </div>

      <div v-else-if="error" class="state-container state-error">
        <p class="state-text">{{ error }}</p>
        <button class="btn-retry" @click="fetchUsers">Qayta urinish</button>
      </div>

      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 60px;">ID</th>
              <th>F.I.SH.</th>
              <th>Telefon</th>
              <th>Roli</th>
              <th>JSHSHR</th>
              <th>Pasport</th>
              <th>Qo'shilgan sana</th>
              <th v-if="authStore.isSuperuser" style="text-align: center; width: 100px;">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredUsers.length === 0">
              <td :colspan="authStore.isSuperuser ? 8 : 7" class="td-empty">Foydalanuvchilar topilmadi.</td>
            </tr>
            <tr v-for="u in filteredUsers" :key="u.id" class="table-row clickable" @click="goToUserDetail(u.id)">
              <td class="td-id">#{{ u.id }}</td>
              <td class="td-name">
                <div class="user-fullname user-link-title">{{ getUserFullName(u) }}</div>
                <div v-if="u.email" class="user-email">{{ u.email }}</div>
              </td>
              <td class="td-phone">{{ formatPhone(u.phone) }}</td>
              <td class="td-role">
                <span class="role-badge" :class="roleClass(u.role, u.is_superuser)">
                  {{ roleText(u.role, u.is_superuser) }}
                </span>
              </td>
              <td class="td-jshshr">{{ u.jshshr || '-' }}</td>
              <td class="td-passport">{{ formatPassport(u.passport_serie, u.passport_number) }}</td>
              <td class="td-date">{{ formatDate(u.date_joined) }}</td>
              <td v-if="authStore.isSuperuser" style="text-align: center;" @click.stop>
                <div class="action-btn-group">
                  <button class="btn-action btn-edit" @click.stop="openEditModal(u)" title="Tahrirlash">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button class="btn-action btn-delete" @click.stop="openDeleteModal(u)" title="O'chirish (is_active=false)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Beautiful Create / Edit User Dialog -->
    <dialog ref="userModal" class="modal-dialog user-modal-dialog">
      <div class="user-modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg v-if="!isEditing" viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="22" height="22">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <line x1="20" y1="8" x2="20" y2="14"></line>
              <line x1="17" y1="11" x2="23" y2="11"></line>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="22" height="22">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div>
            <h3 class="user-modal-title">{{ isEditing ? 'Foydalanuvchini Tahrirlash' : 'Yangi Foydalanuvchi Yaratish' }}</h3>
            <p class="user-modal-sub">Tizim xodimi ma'lumotlari va ruxsat darajasini kiriting</p>
          </div>
        </div>
        <button class="user-btn-close" @click="closeUserModal" title="Yopish">✕</button>
      </div>

      <form @submit.prevent="saveUser" class="user-modal-form">
        <div v-if="modalError" class="modal-alert modal-alert-error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="flex-shrink: 0;">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>{{ modalError }}</span>
        </div>

        <!-- Section 1: Asosiy Ma'lumotlar -->
        <div class="form-section">
          <div class="section-tag">Asosiy Ma'lumotlar</div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Telefon raqami (Login) <span class="req">*</span></label>
              <div class="input-icon-wrap">
                <svg class="field-ico" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                </svg>
                <input
                  v-model="userForm.phone"
                  type="text"
                  placeholder="+998 90 123 45 67"
                  required
                  class="form-input with-icon"
                  @input="onPhoneInput"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Qo'shimcha telefon</label>
              <div class="input-icon-wrap">
                <svg class="field-ico" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                </svg>
                <input
                  v-model="userForm.phone2"
                  type="text"
                  placeholder="+998 90 123 45 67"
                  class="form-input with-icon"
                  @input="onPhone2Input"
                />
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Ismi</label>
              <div class="input-icon-wrap">
                <svg class="field-ico" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <input
                  v-model="userForm.first_name"
                  type="text"
                  placeholder="Ali"
                  class="form-input with-icon"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Familiyasi</label>
              <div class="input-icon-wrap">
                <svg class="field-ico" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <input
                  v-model="userForm.last_name"
                  type="text"
                  placeholder="Valiyev"
                  class="form-input with-icon"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Section 2: Visual Role Cards Selector -->
        <div class="form-section">
          <div class="section-tag">
            Foydalanuvchi Roli <span class="req">*</span>
            <span v-if="isRoleLocked" class="role-locked-note">— navlink orqali belgilangan</span>
          </div>

          <div class="role-cards-grid">
            <div
              v-for="r in modalRoleOptions"
              :key="r.key"
              class="role-card-item"
              :class="{ 'selected': userForm.role === r.key, 'locked': isRoleLocked }"
              @click="!isRoleLocked && (userForm.role = r.key)"
            >
              <div class="role-card-left">
                <div class="role-icon-avatar" :class="'role-avatar-' + r.key" v-html="r.icon"></div>
                <div class="role-card-info">
                  <div class="role-card-title-row">
                    <span class="role-card-name">{{ r.title }}</span>
                    <span class="role-badge" :class="r.badgeClass">{{ roleText(r.key, r.key === 'superuser') }}</span>
                  </div>
                  <p class="role-card-sub">{{ r.desc }}</p>
                </div>
              </div>

              <div class="role-card-radio">
                <div class="radio-outer" :class="{ 'checked': userForm.role === r.key }">
                  <div class="radio-inner" v-if="userForm.role === r.key"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 3: Shaxsni Tasdiqlash -->
        <div class="form-section">
          <div class="section-tag">Shaxsni Tasdiqlash</div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">JSHSHR (14 ta raqam)</label>
              <div class="input-icon-wrap">
                <svg class="field-ico" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                  <rect x="3" y="4" width="18" height="16" rx="2"></rect>
                  <line x1="7" y1="8" x2="17" y2="8"></line>
                  <line x1="7" y1="12" x2="13" y2="12"></line>
                </svg>
                <input
                  v-model="userForm.jshshr"
                  type="text"
                  maxlength="14"
                  placeholder="31201950000000"
                  class="form-input with-icon font-mono"
                  @input="onJshshrInput"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Pasport seriyasi va raqami</label>
              <div class="passport-flex">
                <input
                  v-model="userForm.passport_serie"
                  type="text"
                  maxlength="2"
                  placeholder="AA"
                  class="form-input passport-serie"
                  @input="userForm.passport_serie = userForm.passport_serie.toUpperCase()"
                />
                <input
                  v-model="userForm.passport_number"
                  type="text"
                  maxlength="7"
                  placeholder="1234567"
                  class="form-input passport-num font-mono"
                  @input="userForm.passport_number = userForm.passport_number.replace(/\D/g, '')"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Section 4: Kirish Xavfsizligi -->
        <div class="form-section">
          <div class="section-tag">Kirish Xavfsizligi</div>

          <div class="form-group">
            <label class="form-label">
              Parol
              <span v-if="!isEditing" class="req">*</span>
              <span v-else class="opt-hint">(O'zgartirish shart bo'lmasa bo'sh qoldiring)</span>
            </label>
            <div class="input-icon-wrap">
              <svg class="field-ico" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              <input
                v-model="userForm.password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="isEditing ? 'Yangi parol (ixtiyoriy)' : 'Parolni kiriting'"
                :required="!isEditing"
                class="form-input with-icon"
              />
              <button type="button" class="btn-toggle-pw" @click="showPassword = !showPassword">
                <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" width="16" height="16">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" width="16" height="16">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="user-modal-actions">
          <button type="button" class="btn-cancel" @click="closeUserModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="saving">
            <span v-if="saving" class="btn-spinner"></span>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="16" height="16">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Delete Confirmation Dialog -->
    <dialog ref="deleteModal" class="modal-dialog modal-dialog-sm">
      <div class="modal-header">
        <h3 class="modal-title">Foydalanuvchini O'chirish</h3>
        <button class="btn-close" @click="closeDeleteModal">✕</button>
      </div>

      <div class="modal-body" style="padding: 20px 24px;">
        <div class="delete-warning-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" width="48" height="48">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <p class="delete-confirm-text">
          Haqiqatan ham <strong>{{ deletingUser ? getUserFullName(deletingUser) : '' }}</strong> foydalanuvchisini o'chirmoqchimisiz?
        </p>
        <p class="delete-confirm-sub">Foydalanuvchi tizimda <code>is_active=false</code> holatiga o'tkaziladi va faoliyatsizlantiriladi.</p>

        <div v-if="deleteError" class="modal-alert modal-alert-error" style="margin-top: 12px;">
          {{ deleteError }}
        </div>

        <div class="modal-actions" style="margin-top: 24px;">
          <button type="button" class="btn-cancel" @click="closeDeleteModal">Bekor qilish</button>
          <button type="button" class="btn-delete-confirm" :disabled="deleting" @click="confirmDelete">
            <span v-if="deleting" class="btn-spinner"></span>
            {{ deleting ? "O'chirilmoqda..." : "Ha, O'chirish" }}
          </button>
        </div>
      </div>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const users = ref([])
const loading = ref(false)
const error = ref('')

function goToUserDetail(id) {
  if (id) router.push(`/users/${id}`)
}

// Filters — filterRole is driven by route query
const filterSearch = ref('')
const filterRole = computed(() => route.query.role || '')

// Role page title/subtitle mapping
const roleMeta = {
  coordinator: { title: "O'qituvchilar",  sub: "Nazariy dars o'qituvchilari ro'yxati" },
  instructor:  { title: 'Instruktorlar',   sub: "Amaliy dars instruktorlari ro'yxati" },
  mechanic:    { title: 'Mexaniklar',      sub: "Mexaniklar ro'yxati" },
  admin:       { title: 'Adminlar',        sub: "Admin va superuser foydalanuvchilar ro'yxati" },
}
const rolePageTitle = computed(() => roleMeta[filterRole.value]?.title ?? 'Foydalanuvchilar Boshqaruvi')
const rolePageSub   = computed(() => roleMeta[filterRole.value]?.sub   ?? "Tizim xodimlari, instruktorlar va adminlar ro'yxati")

// User modal state
const userModal = ref(null)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const modalError = ref('')
const showPassword = ref(false)
const defaultUserForm = () => ({
  phone: '',
  phone2: '',
  first_name: '',
  last_name: '',
  role: 'coordinator',
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  password: '',
})
const userForm = ref(defaultUserForm())

// Role options for visual selector
const roleOptions = [
  {
    key: 'coordinator',
    title: "O'qituvchi",
    badgeClass: 'badge-coordinator',
    desc: "Nazariy darslar",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`
  },
  {
    key: 'instructor',
    title: 'Instruktor',
    badgeClass: 'badge-instructor',
    desc: "Amaliy darslar",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`
  },
  {
    key: 'mechanic',
    title: 'Mexanik',
    badgeClass: 'badge-mechanic',
    desc: "O'quvchilar koordinatsiyasi va ma'lumotlarini boshqarish",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`
  },
  {
    key: 'admin',
    title: 'Admin',
    badgeClass: 'badge-admin',
    desc: "Barcha guruhlar, to'lovlar, o'quvchilar boshqaruvi",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`
  },
  {
    key: 'student',
    title: "O'quvchi",
    badgeClass: 'badge-student',
    desc: "Avtomaktab o'quvchisi",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>`
  },
  {
    key: 'superuser',
    title: 'Superuser',
    badgeClass: 'badge-superuser',
    desc: "Cheksiz huquqlar va to'lovlarni tahrirlash",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`
  },
]

// When creating via a navlink (filterRole is set), show only that role card.
// When editing or no role filter is active, show all options.
const modalRoleOptions = computed(() => {
  if (!isEditing.value && filterRole.value) {
    return roleOptions.filter(r => r.key === filterRole.value)
  }
  return roleOptions
})

const isRoleLocked = computed(() => !isEditing.value && filterRole.value !== '')

// Delete modal state
const deleteModal = ref(null)
const deletingUser = ref(null)
const deleting = ref(false)
const deleteError = ref('')

const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/users/')
    users.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (err) {
    console.error(err)
    error.value = "Foydalanuvchilar ro'yxatini yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

const filteredUsers = computed(() => {
  return users.value.filter(u => {
    const role = filterRole.value
    // admin filter also includes superusers
    const matchRole = !role ||
      u.role === role ||
      (role === 'superuser' && u.is_superuser) ||
      (role === 'admin' && (u.role === 'admin' || u.is_superuser))
    const q = filterSearch.value.toLowerCase().trim()
    const fullName = `${u.first_name || ''} ${u.last_name || ''}`.toLowerCase()
    const phoneClean = (u.phone || '').replace(/\D/g, '')
    const phone2Clean = (u.phone2 || '').replace(/\D/g, '')
    const qClean = q.replace(/\D/g, '')
    
    const matchSearch = !q || fullName.includes(q) || (u.phone && u.phone.toLowerCase().includes(q)) || (qClean && (phoneClean.includes(qClean) || phone2Clean.includes(qClean)))
    return matchRole && matchSearch
  })
})

const getUserFullName = (u) => {
  if (!u) return '-'
  const full = `${u.first_name || ''} ${u.last_name || ''}`.trim()
  return full || u.phone || `Foydalanuvchi #${u.id}`
}

const formatPhone = (p) => {
  if (!p) return '-'
  const digits = p.replace(/\D/g, '')
  if (digits.length === 12) {
    return `+${digits.substring(0, 3)} (${digits.substring(3, 5)}) ${digits.substring(5, 8)}-${digits.substring(8, 10)}-${digits.substring(10, 12)}`
  }
  return p
}

const formatPassport = (serie, number) => {
  if (!serie && !number) return '-'
  return `${serie || ''} ${number || ''}`.trim()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('uz-UZ')
}

const roleText = (role, isSuperuser) => {
  if (isSuperuser || role === 'superuser') return 'Superuser'
  if (role === 'admin') return 'Admin'
  if (role === 'instructor') return 'Instruktor'
  if (role === 'mechanic') return 'Mexanik'
  if (role === 'coordinator') return "O'qituvchi"
  if (role === 'student') return "O'quvchi"
  return role || 'Xodim'
}

const roleClass = (role, isSuperuser) => {
  if (isSuperuser || role === 'superuser') return 'badge-superuser'
  if (role === 'admin') return 'badge-admin'
  if (role === 'instructor') return 'badge-instructor'
  if (role === 'mechanic') return 'badge-mechanic'
  if (role === 'student') return 'badge-student'
  return 'badge-coordinator'
}

// Auto format phone input (+998 XX XXX XX XX)
const onPhoneInput = (e) => {
  let val = e.target.value
  let digits = val.replace(/\D/g, '')
  
  if (!digits.startsWith('998')) {
    if ('998'.startsWith(digits)) {
      digits = '998'
    } else {
      digits = '998' + digits
    }
  }
  digits = digits.substring(0, 12)
  
  let formatted = '+' + digits.substring(0, 3)
  if (digits.length > 3) formatted += ' ' + digits.substring(3, 5)
  if (digits.length > 5) formatted += ' ' + digits.substring(5, 8)
  if (digits.length > 8) formatted += ' ' + digits.substring(8, 10)
  if (digits.length > 10) formatted += ' ' + digits.substring(10, 12)
  
  userForm.value.phone = formatted
}

const onPhone2Input = (e) => {
  let val = e.target.value
  let digits = val.replace(/\D/g, '')
  if (!digits) {
    userForm.value.phone2 = ''
    return
  }
  if (!digits.startsWith('998')) {
    if ('998'.startsWith(digits)) {
      digits = '998'
    } else {
      digits = '998' + digits
    }
  }
  digits = digits.substring(0, 12)
  
  let formatted = '+' + digits.substring(0, 3)
  if (digits.length > 3) formatted += ' ' + digits.substring(3, 5)
  if (digits.length > 5) formatted += ' ' + digits.substring(5, 8)
  if (digits.length > 8) formatted += ' ' + digits.substring(8, 10)
  if (digits.length > 10) formatted += ' ' + digits.substring(10, 12)
  userForm.value.phone2 = formatted
}

const onJshshrInput = (e) => {
  userForm.value.jshshr = e.target.value.replace(/\D/g, '')
}

// Modal logic
const openCreateModal = () => {
  if (!authStore.isSuperuser) {
    alert("Faqat superuser foydalanuvchi yaratishi mumkin.")
    return
  }
  isEditing.value = false
  editingId.value = null
  modalError.value = ''
  showPassword.value = false
  // Pre-select the role matching the active nav filter (default: coordinator)
  const defaultRole = filterRole.value && filterRole.value !== '' ? filterRole.value : 'coordinator'
  userForm.value = {
    phone: '+998 ',
    first_name: '',
    last_name: '',
    role: defaultRole,
    jshshr: '',
    passport_serie: '',
    passport_number: '',
    password: '',
  }
  if (userModal.value) {
    userModal.value.showModal()
  }
}

const openEditModal = (u) => {
  if (!authStore.isSuperuser) {
    alert("Faqat superuser foydalanuvchini tahrirlashi mumkin.")
    return
  }
  isEditing.value = true
  editingId.value = u.id
  modalError.value = ''
  showPassword.value = false
  userForm.value = {
    phone: formatPhone(u.phone),
    first_name: u.first_name || '',
    last_name: u.last_name || '',
    role: u.is_superuser ? 'superuser' : (u.role || 'coordinator'),
    jshshr: u.jshshr ? String(u.jshshr) : '',
    passport_serie: u.passport_serie || '',
    passport_number: u.passport_number ? String(u.passport_number) : '',
    password: '',
  }
  if (userModal.value) {
    userModal.value.showModal()
  }
}

const closeUserModal = () => {
  if (userModal.value) {
    userModal.value.close()
  }
}

const saveUser = async () => {
  if (!authStore.isSuperuser) {
    modalError.value = "Faqat superuser foydalanuvchini saqlashi mumkin."
    return
  }

  const phoneCleaned = userForm.value.phone.replace(/\D/g, '')
  if (phoneCleaned.length < 12) {
    modalError.value = "Telefon raqami noto'g'ri kiritilgan."
    return
  }

  if (!isEditing.value && !userForm.value.password) {
    modalError.value = "Yangi foydalanuvchi uchun parol kiritish majburiy."
    return
  }

  saving.value = true
  modalError.value = ''

  try {
    const payload = {
      phone: phoneCleaned,
      first_name: userForm.value.first_name.trim(),
      last_name: userForm.value.last_name.trim(),
      role: userForm.value.role,
      is_superuser: userForm.value.role === 'superuser',
      is_staff: userForm.value.role === 'admin' || userForm.value.role === 'superuser',
    }

    if (userForm.value.jshshr) {
      payload.jshshr = parseInt(userForm.value.jshshr, 10)
    } else {
      payload.jshshr = null
    }

    if (userForm.value.passport_serie) {
      payload.passport_serie = userForm.value.passport_serie.trim().toUpperCase()
    }
    if (userForm.value.passport_number) {
      payload.passport_number = parseInt(userForm.value.passport_number, 10)
    }

    if (userForm.value.password) {
      payload.password = userForm.value.password
    }

    if (isEditing.value) {
      await api.patch(`/users/${editingId.value}/`, payload)
    } else {
      await api.post('/users/', payload)
    }

    closeUserModal()
    await fetchUsers()
  } catch (err) {
    console.error(err)
    if (err.response?.data?.phone) {
      modalError.value = "Ushbu telefon raqamli foydalanuvchi allaqachon mavjud."
    } else if (err.response?.data?.jshshr) {
      modalError.value = "Ushbu JSHSHR egasi bo'lgan foydalanuvchi mavjud."
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
    }
  } finally {
    saving.value = false
  }
}

// Delete logic
const openDeleteModal = (u) => {
  if (!authStore.isSuperuser) {
    alert("Faqat superuser foydalanuvchini o'chirishi mumkin.")
    return
  }
  deletingUser.value = u
  deleteError.value = ''
  if (deleteModal.value) {
    deleteModal.value.showModal()
  }
}

const closeDeleteModal = () => {
  if (deleteModal.value) {
    deleteModal.value.close()
  }
  deletingUser.value = null
}

const confirmDelete = async () => {
  if (!deletingUser.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    await api.delete(`/users/${deletingUser.value.id}/`)
    closeDeleteModal()
    await fetchUsers()
  } catch (err) {
    console.error(err)
    deleteError.value = "O'chirishda xatolik yuz berdi."
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchUsers()

  // Light dismiss fallback
  const dialogs = [userModal.value, deleteModal.value]
  dialogs.forEach(dialog => {
    if (dialog && !('closedBy' in HTMLDialogElement.prototype)) {
      dialog.addEventListener('click', (event) => {
        if (event.target !== dialog) return
        const rect = dialog.getBoundingClientRect()
        const isInside = (
          rect.top <= event.clientY &&
          event.clientY <= rect.top + rect.height &&
          rect.left <= event.clientX &&
          event.clientX <= rect.left + rect.width
        )
        if (!isInside) {
          dialog.close()
        }
      })
    }
  })
})

// Re-fetch when route query role changes
watch(() => route.query.role, () => {
  filterSearch.value = ''
})
</script>

<style scoped>
/* Top Header */
.page-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-main-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}
.page-sub-title {
  font-size: 13px;
  color: #6B7280;
  margin-top: 2px;
}

.btn-add {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  background: #2D6A4F;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  box-shadow: 0 2px 4px rgba(45, 106, 79, 0.2);
}
.btn-add:hover {
  background: #1B4332;
}

/* Filter Card */
.filter-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #E5E7EB;
}
.filter-role-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  flex-shrink: 0;
}
.filter-role-hint {
  font-size: 12.5px;
  color: #6B7280;
  white-space: nowrap;
}
.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}
.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}
.search-input-wrap, .select-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.filter-input, .filter-select {
  width: 100%;
  padding: 9px 12px;
  font-size: 13.5px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  outline: none;
  background: #F9FAFB;
  color: #111827;
  transition: border-color 0.2s, background 0.2s;
}
.filter-input:focus, .filter-select:focus {
  border-color: #2D6A4F;
  background: white;
}
.search-ico {
  position: absolute;
  right: 12px;
  pointer-events: none;
}
.select-arrow {
  position: absolute;
  right: 12px;
  pointer-events: none;
  color: #6B7280;
}
.filter-select {
  appearance: none;
  -webkit-appearance: none;
}

/* Table Card */
.table-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  overflow: hidden;
}
.table-wrap {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 13.5px;
}
.data-table th {
  background: #F9FAFB;
  color: #4B5563;
  font-weight: 600;
  padding: 12px 16px;
  border-bottom: 1px solid #E5E7EB;
  white-space: nowrap;
}
.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #F3F4F6;
  color: #1F2937;
  vertical-align: middle;
}
.table-row.clickable {
  cursor: pointer;
  transition: background 0.15s ease;
}
.table-row.clickable:hover {
  background: #F0FDF4;
}
.user-link-title {
  color: #2D6A4F;
  font-weight: 600;
}
.user-link-title:hover {
  text-decoration: underline;
}
.td-id {
  color: #6B7280;
  font-size: 12.5px;
  font-weight: 600;
}
.user-fullname {
  font-weight: 600;
  color: #111827;
}
.user-email {
  font-size: 11.5px;
  color: #6B7280;
  margin-top: 1px;
}
.td-phone {
  font-weight: 500;
}
.td-jshshr, .td-passport {
  font-family: monospace;
  font-size: 12.5px;
  color: #374151;
}
.td-empty {
  text-align: center;
  padding: 32px;
  color: #6B7280;
}

/* Role Badges */
.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}
.badge-superuser {
  background: #EDE9FE;
  color: #6D28D9;
}
.badge-admin {
  background: #D1FAE5;
  color: #065F46;
}
.badge-instructor {
  background: #FEF3C7;
  color: #92400E;
}
.badge-mechanic {
  background: #E0F2FE;
  color: #0369A1;
}
.badge-coordinator {
  background: #E0E7FF;
  color: #3730A3;
}
.badge-student {
  background: #EFF6FF;
  color: #1D4ED8;
}

/* Action Buttons */
.action-btn-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.btn-edit {
  background: #F3F4F6;
  color: #374151;
}
.btn-edit:hover {
  background: #E5E7EB;
  color: #111827;
}
.btn-delete {
  background: #FEE2E2;
  color: #DC2626;
}
.btn-delete:hover {
  background: #FCA5A5;
  color: #991B1B;
}

/* States */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 12px;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E5E7EB;
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.state-text { color: #6B7280; font-size: 14px; }
.state-error { color: #DC2626; }
.btn-retry {
  padding: 8px 16px;
  background: #2D6A4F;
  color: white;
  border-radius: 6px;
  font-size: 13px;
}

/* Modal Dialog Base */
.modal-dialog {
  border: none;
  border-radius: 20px;
  padding: 0;
  width: 100%;
  max-width: 580px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  margin: auto;
}
.modal-dialog-sm {
  max-width: 440px;
}
.modal-dialog::backdrop {
  background: rgba(17, 24, 39, 0.45);
  backdrop-filter: blur(6px);
}

/* Premium User Modal Header */
.user-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 28px 18px 28px;
  border-bottom: 1px solid #F3F4F6;
}
.header-badge-wrap {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}
.header-badge-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
  border: 1px solid #A7F3D0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(45, 106, 79, 0.1);
}
.user-modal-title {
  font-size: 19px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px 0;
}
.user-modal-sub {
  font-size: 12.5px;
  color: #6B7280;
  margin: 0;
}
.user-btn-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #F3F4F6;
  border: none;
  color: #6B7280;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, transform 0.15s;
}
.user-btn-close:hover {
  background: #E5E7EB;
  color: #111827;
  transform: rotate(90deg);
}

/* User Modal Form */
.user-modal-form {
  padding: 20px 28px 28px 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.section-tag {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #2D6A4F;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-tag::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #E5E7EB;
}
.role-locked-note {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0;
  text-transform: none;
  color: #9CA3AF;
  background: #F3F4F6;
  padding: 2px 8px;
  border-radius: 20px;
  white-space: nowrap;
}

.form-row {
  display: flex;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}
.form-label {
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 4px;
}
.req { color: #DC2626; }
.opt-hint {
  font-size: 11px;
  color: #6B7280;
  font-weight: 400;
}

/* Inputs with Icons */
.input-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.field-ico {
  position: absolute;
  left: 12px;
  pointer-events: none;
  z-index: 1;
}
.form-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 13.5px;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  outline: none;
  background: #F9FAFB;
  color: #111827;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.form-input.with-icon {
  padding-left: 36px;
}
.form-input:focus {
  border-color: #2D6A4F;
  background: white;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
}
.font-mono {
  font-family: monospace;
}

/* Visual Role Cards Selector */
.role-cards-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.role-card-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border: 1.5px solid #E5E7EB;
  border-radius: 12px;
  background: #FAFAFA;
  cursor: pointer;
  transition: all 0.2s ease;
}
.role-card-item:hover {
  border-color: #A7F3D0;
  background: #F0FDF4;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.08);
}
.role-card-item.selected {
  border-color: #2D6A4F;
  background: #ECFDF5;
  box-shadow: 0 4px 14px rgba(45, 106, 79, 0.14);
}
.role-card-item.locked {
  cursor: default;
  pointer-events: none;
  opacity: 0.95;
}
.role-card-item.locked:hover {
  transform: none;
  box-shadow: 0 4px 14px rgba(45, 106, 79, 0.14);
  border-color: #2D6A4F;
  background: #ECFDF5;
}
.role-card-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}
.role-icon-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.role-avatar-superuser { background: #EDE9FE; color: #6D28D9; }
.role-avatar-admin { background: #D1FAE5; color: #065F46; }
.role-avatar-instructor { background: #FEF3C7; color: #92400E; }
.role-avatar-mechanic { background: #E0F2FE; color: #0369A1; }
.role-avatar-coordinator { background: #E0E7FF; color: #3730A3; }

.role-card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.role-card-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.role-card-name {
  font-size: 13.5px;
  font-weight: 700;
  color: #111827;
}
.role-card-sub {
  font-size: 11.5px;
  color: #6B7280;
  margin: 0;
  line-height: 1.3;
}
.role-card-radio {
  margin-left: 12px;
}
.radio-outer {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #D1D5DB;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s, background 0.2s;
}
.radio-outer.checked {
  border-color: #2D6A4F;
  background: #2D6A4F;
}
.radio-inner {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
}

.passport-flex {
  display: flex;
  gap: 8px;
}
.passport-serie {
  width: 70px;
  text-transform: uppercase;
  text-align: center;
  font-weight: 600;
}

/* Toggle Password button */
.btn-toggle-pw {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  padding: 4px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

/* Modal Actions */
.user-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid #F3F4F6;
}
.btn-cancel {
  padding: 10px 20px;
  background: #F3F4F6;
  color: #4B5563;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-cancel:hover { background: #E5E7EB; }

.btn-save {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.25);
  transition: background 0.2s, transform 0.1s;
}
.btn-save:hover {
  background: linear-gradient(135deg, #245C43 0%, #143527 100%);
}
.btn-delete-confirm {
  padding: 10px 22px;
  background: #DC2626;
  color: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
}
.btn-delete-confirm:hover { background: #B91C1C; }

.modal-alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 13px;
}
.modal-alert-error {
  background: #FEE2E2;
  color: #991B1B;
  border: 1px solid #FCA5A5;
}

.delete-warning-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}
.delete-confirm-text {
  text-align: center;
  font-size: 15px;
  color: #111827;
}
.delete-confirm-sub {
  text-align: center;
  font-size: 12.5px;
  color: #6B7280;
  margin-top: 6px;
}
code {
  background: #F3F4F6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}
</style>
