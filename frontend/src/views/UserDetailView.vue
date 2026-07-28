<template>
  <AppLayout>

    <!-- Top Action Bar with Back button -->
    <div class="page-top">
      <div class="top-left">
        <button class="btn-back" @click="goBack" title="Orqaga">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Foydalanuvchilar ro'yxatiga qarash
        </button>
        <h2 class="page-main-title">{{ user?.full_name || 'Foydalanuvchi Ma\'lumotlari' }}</h2>
      </div>

      <button v-if="authStore.isSuperuser && user" class="btn-edit-profile" @click="openEditModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" style="margin-right: 6px;">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
        Tahrirlash
      </button>
    </div>

    <!-- Loading / Error States -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Foydalanuvchi ma'lumotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchUserDetail">Qayta urinish</button>
    </div>

    <div v-else-if="user" class="detail-container">

      <!-- Profile Overview Card -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-large" @click="openImageModal(user.image || '/default_photo.png')" title="Rasmni kattalashtirish" style="cursor: pointer;">
            <img :src="user.image || '/default_photo.png'" alt="Profile" class="user-avatar-img" />
          </div>
          <div class="profile-identity">
            <h3 class="profile-name">{{ user.full_name || (user.first_name + ' ' + user.last_name) }}</h3>
            <div class="role-badge-wrap">
              <span class="role-badge" :class="roleClass(user.role, user.is_superuser)">
                {{ roleText(user.role, user.is_superuser) }}
              </span>
            </div>
          </div>
        </div>

        <div class="profile-grid">
          <div class="info-item">
            <span class="info-label">Asosiy Telefon</span>
            <span class="info-value">{{ formatPhone(user.phone) }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Qo'shimcha Telefon</span>
            <span class="info-value">{{ formatPhone(user.phone2) || '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">JSHSHR</span>
            <span class="info-value">{{ user.jshshr || '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Pasport</span>
            <span class="info-value">{{ formatPassport(user.passport_serie, user.passport_number) }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Email</span>
            <span class="info-value">{{ user.email || '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Qo'shilgan sana</span>
            <span class="info-value">{{ formatDate(user.date_joined) }}</span>
          </div>
        </div>

        <div v-if="user.notes" class="notes-block">
          <span class="info-label">Qo'shimcha izoh:</span>
          <p class="notes-text">{{ user.notes }}</p>
        </div>
      </div>

      <!-- Linked Groups & Students Section -->
      <div class="linked-section">
        <div class="section-header">
          <h3 class="section-title">Biriktirilgan Guruhlar va O'quvchilar</h3>
          <span class="count-badge">{{ groupsList.length }} ta guruh</span>
        </div>

        <div v-if="loadingEnrollments" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="groupsList.length === 0" class="empty-groups">
          <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="40" height="40">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
          </svg>
          <p class="empty-title">Biriktirilgan guruhlar topilmadi</p>
          <p class="empty-sub">Ushbu xodimga hali birorta guruh o'quvchilari biriktirilmagan.</p>
        </div>

        <div v-else class="groups-accordion">
          <div v-for="g in groupsList" :key="g.id || g.name" class="group-accordion-card">
            <div class="group-card-header">
              <div class="group-info-main">
                <span class="group-badge">{{ g.category_name }}</span>
                <h4 class="group-name">{{ g.name }}</h4>
                <span v-if="g.working_days" class="group-days-badge">{{ g.working_days }} kun</span>
                <span v-if="g.duration" class="group-duration-badge">{{ g.duration }} oy</span>
              </div>
              <div class="group-meta">
                <span class="student-count-chip">{{ g.students.length }} ta o'quvchi</span>
              </div>
            </div>

            <div class="table-wrap">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>O'quvchi F.I.SH.</th>
                    <th>Telefon</th>
                    <th>Holati</th>
                    <th>Dars Kunlari</th>
                    <th>Dars Vaqti</th>
                    <th>O'quv Joyi</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="e in g.students" :key="e.id" class="table-row" @click="goStudent(e.student)" style="cursor: pointer;">
                    <td class="td-name">
                      <div class="student-link">{{ e.student_name }}</div>
                      <div class="student-jshshr">JSHSHR: {{ e.student_jshshr || '-' }}</div>
                    </td>
                    <td class="td-phone">{{ formatPhone(e.student_phone) }}</td>
                    <td>
                      <span class="status-chip" :class="e.status">
                        {{ statusText(e.status) }}
                      </span>
                    </td>
                    <td>{{ formatLessonDays(e.learning_days) }}</td>
                    <td>{{ e.learning_time || '-' }}</td>
                    <td>{{ e.learning_place_name || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Edit User Modal -->
    <dialog ref="userModal" class="modal-dialog">
      <div class="user-modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="22" height="22">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div>
            <h3 class="user-modal-title">Foydalanuvchini Tahrirlash</h3>
            <p class="user-modal-sub">Profil ma'lumotlarini yangilang</p>
          </div>
        </div>
        <button class="user-btn-close" @click="closeModal" title="Yopish">✕</button>
      </div>

      <form @submit.prevent="saveUser" class="user-modal-form">
        <div v-if="modalError" class="modal-alert modal-alert-error">
          <span>{{ modalError }}</span>
        </div>

        <div class="form-group">
          <label class="form-label required">To'liq ismi (F.I.SH.)</label>
          <input v-model="editForm.full_name" type="text" class="form-input" required />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label required">Telefon raqami</label>
            <input v-model="editForm.phone" type="text" class="form-input" required />
          </div>

          <div class="form-group">
            <label class="form-label">Qo'shimcha telefon</label>
            <input v-model="editForm.phone2" type="text" class="form-input" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">JSHSHR</label>
            <input v-model="editForm.jshshr" type="number" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Roli</label>
            <select v-model="editForm.role" class="form-input">
              <option value="instructor">Instruktor</option>
              <option value="coordinator">O'qituvchi</option>
              <option value="mechanic">Mexanik</option>
              <option value="admin">Admin</option>
              <option value="superuser">Superuser</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Pasport seriyasi</label>
            <input v-model="editForm.passport_serie" type="text" maxlength="2" class="form-input" placeholder="AA" />
          </div>

          <div class="form-group">
            <label class="form-label">Pasport raqami</label>
            <input v-model="editForm.passport_number" type="number" class="form-input" placeholder="1234567" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Foydalanuvchi Rasmi (Foto)</label>
          <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
            <img v-if="editForm.existingImage" :src="editForm.existingImage" alt="Current Photo" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 1px solid #E5E7EB; flex-shrink: 0;" />
            <input type="file" accept="image/*" class="form-input" style="width: 100%;" @change="onUserFileChange" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Qo'shimcha izoh</label>
          <textarea v-model="editForm.notes" rows="3" class="form-input form-textarea"></textarea>
        </div>

        <div class="user-modal-footer">
          <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="saving">
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Image Zoom Modal -->
    <dialog ref="imageZoomModal" class="image-zoom-dialog" @click="imageZoomModal?.close()">
      <div class="image-zoom-content" @click.stop>
        <button type="button" class="image-zoom-close" @click="imageZoomModal?.close()">✕</button>
        <img :src="zoomedImageUrl" alt="Enlarged Photo" class="zoomed-img" />
      </div>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatPhone, formatPassport, formatDate } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const user = ref(null)
const loading = ref(true)
const error = ref(null)

const enrollments = ref([])
const loadingEnrollments = ref(false)

const userModal = ref(null)
const saving = ref(false)
const modalError = ref(null)

const editForm = ref({
  full_name: '',
  phone: '',
  phone2: '',
  role: '',
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  notes: ''
})

const userInitials = computed(() => {
  if (!user.value) return 'U'
  const name = user.value.full_name || `${user.value.first_name || ''} ${user.value.last_name || ''}`.strip()
  if (!name) return 'U'
  const parts = name.split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.slice(0, 2).toUpperCase()
})

const groupsList = computed(() => {
  const groupsMap = {}
  enrollments.value.forEach(e => {
    const gKey = e.group || 'no-group'
    if (!groupsMap[gKey]) {
      groupsMap[gKey] = {
        id: e.group,
        name: e.group ? `Guruh #${e.group}` : 'Guruhsiz',
        category_name: e.category_name || 'B',
        working_days: e.working_days,
        duration: e.duration,
        students: []
      }
    }
    groupsMap[gKey].students.push(e)
  })
  return Object.values(groupsMap)
})

async function fetchUserDetail() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/users/${route.params.id}/`)
    user.value = res.data
    fetchLinkedEnrollments()
  } catch (err) {
    error.value = "Foydalanuvchi ma'lumotlarini yuklashda xatolik"
  } finally {
    loading.value = false
  }
}

async function fetchLinkedEnrollments() {
  if (!user.value) return
  loadingEnrollments.value = true
  try {
    // Check role to query either instructor or coordinator
    const paramKey = user.value.role === 'instructor' ? 'instructor' : 'coordinator'
    const res = await api.get('/enrollments/', {
      params: { [paramKey]: user.value.id, page_size: 200 }
    })
    enrollments.value = res.data.results ? res.data.results : res.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingEnrollments.value = false
  }
}

function roleClass(role, isSuperuser) {
  if (isSuperuser) return 'role-superuser'
  switch (role) {
    case 'admin': return 'role-admin'
    case 'instructor': return 'role-instructor'
    case 'coordinator': return 'role-coordinator'
    case 'mechanic': return 'role-mechanic'
    default: return 'role-default'
  }
}

function roleText(role, isSuperuser) {
  if (isSuperuser) return 'Superuser'
  switch (role) {
    case 'admin': return 'Admin'
    case 'instructor': return 'Instruktor'
    case 'coordinator': return "O'qituvchi"
    case 'mechanic': return 'Mexanik'
    default: return role
  }
}

const formatLessonDays = (days) => {
  if (!days) return '-'
  switch (days) {
    case 'everyday': return 'Har kuni (Dush-Shanba)'
    case 'Mo-Wed-Fri':
    case 'mon-wed-fri': return 'Dushanba - Chorshanba - Juma'
    case 'Tue-Thu-Sat':
    case 'tue-wed-sat': return 'Seshanba - Payshanba - Shanba'
    default: return days
  }
}

function statusText(st) {
  switch (st) {
    case 'new': return 'Yangi'
    case 'enrolled': return 'Qabul qilingan'
    case 'finished': return 'Tugatgan'
    case 'canceled': return 'Bekor qilingan'
    default: return st
  }
}

const imageZoomModal = ref(null)
const zoomedImageUrl = ref('')

function openImageModal(url) {
  if (!url) return
  zoomedImageUrl.value = url
  imageZoomModal.value?.showModal()
}

const selectedUserFile = ref(null)
function onUserFileChange(e) {
  selectedUserFile.value = e.target.files?.[0] || null
}

function openEditModal() {
  modalError.value = null
  selectedUserFile.value = null
  editForm.value = {
    full_name: user.value.full_name || '',
    phone: formatPhone(user.value.phone),
    phone2: user.value.phone2 || '',
    role: user.value.role || 'instructor',
    jshshr: user.value.jshshr || '',
    passport_serie: user.value.passport_serie || '',
    passport_number: user.value.passport_number || '',
    notes: user.value.notes || '',
    existingImage: user.value.image || null,
  }
  userModal.value?.showModal()
}

function closeModal() {
  userModal.value?.close()
}

async function saveUser() {
  saving.value = true
  modalError.value = null
  try {
    const phoneCleaned = editForm.value.phone ? editForm.value.phone.replace(/\D/g, '') : ''
    const payload = {
      full_name: editForm.value.full_name.trim(),
      phone: phoneCleaned,
      phone2: editForm.value.phone2 ? editForm.value.phone2.trim() : null,
      role: editForm.value.role,
      jshshr: editForm.value.jshshr ? parseInt(editForm.value.jshshr, 10) : null,
      passport_serie: editForm.value.passport_serie ? editForm.value.passport_serie.trim().toUpperCase() : null,
      passport_number: editForm.value.passport_number ? parseInt(editForm.value.passport_number, 10) : null,
      notes: editForm.value.notes || '',
    }

    let res
    if (selectedUserFile.value) {
      const formData = new FormData()
      Object.keys(payload).forEach(k => {
        if (payload[k] !== null && payload[k] !== undefined) {
          formData.append(k, payload[k])
        }
      })
      formData.append('image', selectedUserFile.value)
      res = await api.patch(`/users/${user.value.id}/`, formData)
    } else {
      res = await api.patch(`/users/${user.value.id}/`, payload)
    }

    user.value = res.data
    closeModal()
  } catch (err) {
    console.error(err)
    modalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    saving.value = false
  }
}

function goBack() {
  if (user.value?.role) {
    router.push({ path: '/users', query: { role: user.value.role } })
  } else {
    router.push('/users')
  }
}

function goStudent(studentId) {
  if (studentId) {
    router.push(`/students/${studentId}`)
  }
}

onMounted(() => {
  fetchUserDetail()
})
</script>

<style scoped>
.page-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.top-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: #2D6A4F;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;

  &:hover { text-decoration: underline; }
}

.page-main-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}

.btn-edit-profile {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  background: #2D6A4F;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  padding: 24px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F3F4F6;
}

.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #1B2430;
  color: white;
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-name {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.role-badge-wrap { margin-top: 4px; }

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.role-superuser { background: #FEE2E2; color: #991B1B; }
.role-admin { background: #FEF3C7; color: #92400E; }
.role-instructor { background: #DCFCE7; color: #166534; }
.role-coordinator { background: #E0F2FE; color: #075985; }
.role-mechanic { background: #F3E8FF; color: #6B21A8; }
.role-default { background: #F3F4F6; color: #374151; }

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #6B7280;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.notes-block {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #F3F4F6;
}

.notes-text {
  font-size: 14px;
  color: #374151;
  background: #F9FAFB;
  padding: 10px 14px;
  border-radius: 8px;
  margin-top: 4px;
}

.linked-section {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.count-badge {
  background: #F3F4F6;
  color: #374151;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.empty-groups {
  text-align: center;
  padding: 40px 0;
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin-top: 8px;
}

.empty-sub {
  font-size: 13px;
  color: #6B7280;
}

.groups-accordion {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.group-accordion-card {
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  overflow: hidden;
}

.group-card-header {
  background: #F9FAFB;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #E5E7EB;
}

.group-info-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.group-badge {
  background: #2D6A4F;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 12px;
}

.group-name {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
}

.group-days-badge {
  background: #E0F2FE;
  color: #0369A1;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.group-duration-badge {
  background: #FEF3C7;
  color: #92400E;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.student-count-chip {
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
}

.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;

  th {
    background: #FAFAFA;
    padding: 10px 16px;
    text-align: left;
    font-weight: 600;
    color: #4B5563;
    border-bottom: 1px solid #E5E7EB;
  }

  td {
    padding: 12px 16px;
    border-bottom: 1px solid #F3F4F6;
    color: #1F2937;
  }
}

.student-link {
  font-weight: 600;
  color: #2D6A4F;

  &:hover { text-decoration: underline; }
}

.student-jshshr {
  font-size: 11px;
  color: #9CA3AF;
}

.status-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;

  &.new { background: #E0F2FE; color: #0369A1; }
  &.enrolled { background: #DCFCE7; color: #15803D; }
  &.finished { background: #F3F4F6; color: #4B5563; }
}

.modal-dialog {
  border: none;
  border-radius: 20px;
  padding: 0;
  width: 90%;
  max-width: 620px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: white;
  margin: auto;
  overflow: hidden;

  &::backdrop {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(6px);
  }

  *, *::before, *::after {
    box-sizing: border-box;
  }
}

.user-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F3F4F6;
}

.header-badge-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-badge-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.2);

  svg {
    stroke: white;
  }
}

.user-modal-title { font-size: 17px; font-weight: 700; color: #111827; }
.user-modal-sub { font-size: 12px; color: #6B7280; margin-top: 2px; }
.user-btn-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.user-modal-form { padding: 24px; width: 100%; box-sizing: border-box; }
.form-group { margin-bottom: 16px; width: 100%; min-width: 0; box-sizing: border-box; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; width: 100%; box-sizing: border-box; }

.form-label {
  display: block;
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;

  &.required::after {
    content: " *";
    color: #EF4444;
  }
}

.form-input {
  width: 100%;
  box-sizing: border-box;
  padding: 11px 14px;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  font-size: 14px;
  background-color: #FAFAFA;
  color: #111827;
  outline: none;
  transition: all 0.2s ease;

  &:focus {
    border-color: #2D6A4F;
    background-color: white;
    box-shadow: 0 0 0 3.5px rgba(45, 106, 79, 0.12);
  }
}

select.form-input {
  cursor: pointer;
}

.form-textarea {
  resize: vertical;
}

.user-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 26px;
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
  transition: background 0.15s ease;

  &:hover {
    background: #F9FAFB;
  }
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 22px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13.5px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.25);
  transition: all 0.15s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(45, 106, 79, 0.35);
  }
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-placeholder-large {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F3F4F6;
  border-radius: 50%;
}

/* Image Zoom Modal */
.image-zoom-dialog {
  border: none;
  background: transparent;
  padding: 0;
  max-width: 90vw;
  max-height: 90vh;
  margin: auto;
  overflow: visible;
}
.image-zoom-dialog::backdrop {
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(5px);
}
.image-zoom-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-zoom-close {
  position: absolute;
  top: -16px;
  right: -16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: white;
  color: #111827;
  font-weight: 700;
  font-size: 14px;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}
.zoomed-img {
  max-width: 85vw;
  max-height: 85vh;
  border-radius: 14px;
  object-fit: contain;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}
</style>
