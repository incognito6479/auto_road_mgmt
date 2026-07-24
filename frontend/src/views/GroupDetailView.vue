<template>
  <AppLayout>

    <!-- Header navigation -->
    <div class="detail-header-nav">
      <button class="btn-back" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
        Orqaga
      </button>
      <div class="header-title-wrap">
        <h2 class="group-title">{{ group ? group.name : 'Guruh yuklanmoqda...' }}</h2>
        <span v-if="group" class="group-category-pill">{{ group.category_name }}</span>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Guruh ma'lumotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchGroupDetail">Qayta urinish</button>
    </div>

    <div v-else-if="group" class="detail-content">

      <!-- Group summary card -->
      <div class="summary-card">
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">Guruh nomi</span>
            <span class="summary-val font-bold">{{ group.name }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Kategoriya</span>
            <span class="summary-val">{{ group.category_name }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Boshlangan sana</span>
            <span class="summary-val">{{ formatDate(group.started_at) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Ish kunlari</span>
            <span class="summary-val font-bold">{{ group.working_days ? group.working_days + ' kun' : '-' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Dars kunlari</span>
            <span class="summary-val">{{ weekendsText(group.working_weekends) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Davomiyligi</span>
            <span class="summary-val font-bold">{{ group.duration ? group.duration + ' oy' : '-' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">O'quvchilar soni</span>
            <span class="summary-val font-bold">{{ group.student_count }} ta</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Holat</span>
            <span class="summary-val">
              <span class="status-badge" :class="statusClass(group.status)">
                {{ statusText(group.status) }}
              </span>
            </span>
          </div>
        </div>
        <div v-if="group.notes" class="notes-block">
          <span class="notes-label">Izoh:</span> {{ group.notes }}
        </div>
      </div>

      <!-- Students table section -->
      <div class="table-card">
        <div class="table-card-header">
          <h3 class="section-title">A'zo o'quvchilar</h3>
          <div class="search-wrap-flex">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Ism yoki telefon..."
              class="search-input"
            />
            <input
              v-model="searchJshshr"
              type="text"
              placeholder="JSHSHR..."
              class="search-input-jshshr"
            />
          </div>
        </div>

        <div class="table-container">
          <table class="students-table">
            <thead>
              <tr>
                <th>O'quvchi F.I.SH.</th>
                <th class="th-phone">Telefon</th>
                <th>JSHSHR</th>
                <th>Eslatmasi</th>
                <th>O'quv Joyi & Vaqti</th>
                <th v-if="authStore.isSuperuser || authStore.isMechanic">Instruktor</th>
                <th v-if="authStore.isSuperuser || authStore.isMechanic">O'qituvchi</th>
                <th v-if="!authStore.isMechanic">Shartnoma summasi</th>
                <th v-if="!authStore.isMechanic">To'langan</th>
                <th v-if="!authStore.isMechanic">Qoldiq</th>
                <th v-if="!authStore.isMechanic" style="text-align: center;">Amallar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredEnrollments.length === 0">
                <td :colspan="tableColspan" class="td-empty">Hech qanday o'quvchi topilmadi.</td>
              </tr>
              <tr v-for="e in filteredEnrollments" :key="e.id" class="stbl-row clickable-row" @click="goToStudentDetail(e.student)">
                <td class="td-name">{{ e.student_name }}</td>
                <td class="td-phone">
                  <div>{{ formatPhone(e.student_phone) }}</div>
                  <div v-if="e.student_phone2" style="font-size: 11.5px; color: #6B7280; margin-top: 2px;">
                    Qo'shimcha: {{ formatPhone(e.student_phone2) }}
                  </div>
                </td>
                <td class="td-jshshr">{{ e.student_jshshr }}</td>
                <td class="td-notes">{{ e.notes || '-' }}</td>

                <!-- Learning Place & Time Column -->
                <td class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.learning_place_name || e.learning_time || e.learning_days">
                      <span class="assign-name">{{ formatSchedule(e) }}</span>
                      <button class="btn-assign-edit" @click.stop="openScheduleModal(e)" title="O'quv joyi va vaqtini o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-assign-plus" @click.stop="openScheduleModal(e)" title="O'quv joyi va vaqtini biriktirish">+</button>
                    </template>
                  </div>
                </td>

                <!-- Instructor Column -->
                <td v-if="authStore.isSuperuser || authStore.isMechanic" class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.instructor_name">
                      <span class="assign-name">{{ e.instructor_name }}</span>
                      <button class="btn-assign-edit" @click.stop="openAssignModal(e, 'instructor')" title="Instruktorni o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-assign-plus" @click.stop="openAssignModal(e, 'instructor')" title="Instruktor biriktirish">+</button>
                    </template>
                  </div>
                </td>

                <!-- Coordinator Column -->
                <td v-if="authStore.isSuperuser || authStore.isMechanic" class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.coordinator_name">
                      <span class="assign-name">{{ e.coordinator_name }}</span>
                      <button class="btn-assign-edit" @click.stop="openAssignModal(e, 'coordinator')" title="O'qituvchini o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-assign-plus" @click.stop="openAssignModal(e, 'coordinator')" title="O'qituvchi biriktirish">+</button>
                    </template>
                  </div>
                </td>

                <!-- Payment Info Columns (Hidden for mechanic) -->
                <td v-if="!authStore.isMechanic">
                  <span v-if="e.enrolled_free" class="free-badge">Tekin</span>
                  <span v-else>{{ formatMoney(e.enrolled_amount) }} so'm</span>
                </td>
                <td v-if="!authStore.isMechanic">
                  <span v-if="e.enrolled_free">-</span>
                  <span v-else class="paid-val">{{ formatMoney(e.paid_amount) }} so'm</span>
                </td>
                <td v-if="!authStore.isMechanic">
                  <span v-if="e.enrolled_free">-</span>
                  <span v-else :class="{'balance-warning': (e.enrolled_amount - e.paid_amount) > 0}">
                    {{ formatMoney(e.enrolled_amount - e.paid_amount) }} so'm
                  </span>
                </td>
                <td v-if="!authStore.isMechanic" style="text-align: center;" @click.stop>
                  <button
                    v-if="authStore.isAdminOrSuperuser && !e.enrolled_free && e.paid_amount < e.enrolled_amount"
                    class="btn-pay"
                    @click.stop="openPayModal(e)"
                  >
                    To'lash
                  </button>
                  <span v-else-if="!e.enrolled_free && e.paid_amount >= e.enrolled_amount" class="fully-paid-badge">To'liq to'langan</span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Payment Modal Dialog -->
    <dialog ref="payModal" class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">To'lov Qabul Qilish</h3>
        <button class="btn-close" @click="closePayModal">✕</button>
      </div>

      <form @submit.prevent="submitPayment" class="modal-form">
        <div v-if="payError" class="modal-error">
          {{ payError }}
        </div>

        <div v-if="activeEnrollment" class="pay-info-summary">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
          <p>Jami shartnoma: <strong>{{ formatMoney(activeEnrollment.enrolled_amount) }} so'm</strong></p>
          <p>Shu vaqtgacha to'langan: <strong>{{ formatMoney(activeEnrollment.paid_amount) }} so'm</strong></p>
          <p>Qolgan qarzdorlik: <strong class="balance-warning">{{ formatMoney(activeEnrollment.enrolled_amount - activeEnrollment.paid_amount) }} so'm</strong></p>
        </div>

        <div class="form-group">
          <label class="form-label">To'lanayotgan summa (so'm) <span class="req">*</span></label>
          <input
            v-model="formattedInputPrice"
            type="text"
            placeholder="Summani kiriting..."
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">To'lov usuli <span class="req">*</span></label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select v-model="paymentForm.method" required class="form-input select-input" style="width: 100%; appearance: none;">
              <option value="cash">Naqd pullar (Cash)</option>
              <option value="click">Click</option>
              <option value="payme">Payme</option>
              <option value="uzum">Uzum</option>
              <option value="card">Bank kartasi (Terminal)</option>
              <option value="transfer">Bank o'tkazmasi (Perevod)</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Eslatma / Izoh</label>
          <textarea
            v-model="paymentForm.notes"
            rows="3"
            placeholder="Qo'shimcha izoh..."
            class="form-input text-area-input"
          ></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closePayModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="paySaving">
            <span v-if="paySaving" class="btn-spinner"></span>
            {{ paySaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Assign Instructor / Coordinator Modal Dialog -->
    <dialog ref="assignModal" class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">
          {{ assignType === 'instructor' ? "Instruktor Biriktirish" : "O'qituvchi Biriktirish" }}
        </h3>
        <button class="btn-close" @click="closeAssignModal">✕</button>
      </div>

      <form @submit.prevent="submitAssign" class="modal-form">
        <div v-if="assignError" class="modal-error">
          {{ assignError }}
        </div>

        <div v-if="activeEnrollment" class="pay-info-summary">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
          <p>Telefon: <strong>{{ formatPhone(activeEnrollment.student_phone) }}</strong></p>
        </div>

        <div class="form-group">
          <label class="form-label">
            {{ assignType === 'instructor' ? "Instruktorni tanlang" : "O'qituvchini tanlang" }}
          </label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select v-model="selectedAssignUserId" class="form-input select-input" style="width: 100%; appearance: none;">
              <option :value="null">&lt; Biriktirilmagan &gt;</option>
              <option v-for="u in assignUserOptions" :key="u.id" :value="u.id">
                {{ getUserDisplayName(u) }}
              </option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeAssignModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="assignSaving">
            <span v-if="assignSaving" class="btn-spinner"></span>
            {{ assignSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Schedule Modal Dialog (Learning Place, Time & Days) -->
    <dialog ref="scheduleModal" class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">O'quv Joyi va Vaqtini Belgilash</h3>
        <button class="btn-close" @click="closeScheduleModal">✕</button>
      </div>

      <form @submit.prevent="submitSchedule" class="modal-form">
        <div v-if="scheduleError" class="modal-error">
          {{ scheduleError }}
        </div>

        <div v-if="activeEnrollment" class="pay-info-summary">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
          <p>Telefon: <strong>{{ formatPhone(activeEnrollment.student_phone) }}</strong></p>
        </div>

        <div class="form-group">
          <label class="form-label">O'quv joyi (Filial / Xona)</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select v-model="scheduleForm.learning_place" class="form-input select-input" style="width: 100%; appearance: none;">
              <option :value="null">&lt; Tanlanmagan &gt;</option>
              <option v-for="p in learningPlaces" :key="p.id" :value="p.id">
                {{ p.place_name }}
              </option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Dars vaqti</label>
          <input
            v-model="scheduleForm.learning_time"
            type="text"
            placeholder="Masalan: 09:00 yoki 14:00 - 16:00"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Dars kunlari</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select v-model="scheduleForm.learning_days" class="form-input select-input" style="width: 100%; appearance: none;">
              <option :value="null">&lt; Tanlanmagan &gt;</option>
              <option value="Mo-Wed-Fri">Mo-Wed-Fri (Dushanba - Chorshanba - Juma)</option>
              <option value="Tue-Thu-Sat">Tue-Thu-Sat (Seshanba - Payshanba - Shanba)</option>
              <option value="everyday">everyday (Har kuni)</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeScheduleModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="scheduleSaving">
            <span v-if="scheduleSaving" class="btn-spinner"></span>
            {{ scheduleSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const groupId = route.params.id

const goToStudentDetail = (studentId) => {
  if (studentId) {
    router.push(`/students/${studentId}`)
  }
}

const group = ref(null)
const loading = ref(false)
const error = ref('')
const allUsers = ref([])
const learningPlaces = ref([])

const weekendsText = (w) => {
  switch (w) {
    case 'everyday': return 'Har kuni (Mon-Sat)'
    case 'mon-wed-fri': return 'Dush-Chorsh-Juma'
    case 'tue-wed-sat': return 'Ses-Paysh-Shanba'
    default: return w || '-'
  }
}

// Search state
const searchQuery = ref('')
const searchJshshr = ref('')

// Payment state
const payModal = ref(null)
const activeEnrollment = ref(null)
const paySaving = ref(false)
const payError = ref('')
const paymentForm = ref({
  amount: null,
  method: 'cash',
  notes: '',
})

// Assignment modal state
const assignModal = ref(null)
const assignType = ref('instructor') // 'instructor' or 'coordinator'
const selectedAssignUserId = ref(null)
const assignSaving = ref(false)
const assignError = ref('')

// Schedule modal state
const scheduleModal = ref(null)
const scheduleSaving = ref(false)
const scheduleError = ref('')
const scheduleForm = ref({
  learning_place: null,
  learning_time: '',
  learning_days: null,
})

const tableColspan = computed(() => {
  let count = 5 // Student Name, Phone, JSHSHR, Notes, Learning Place & Time
  if (authStore.isSuperuser || authStore.isMechanic) count += 2 // Instructor, Coordinator
  if (!authStore.isMechanic) count += 4 // Shartnoma, Paid, Qoldiq, Amallar
  return count
})

const assignUserOptions = computed(() => {
  return allUsers.value.filter(u => u.role === assignType.value)
})

const getUserDisplayName = (u) => {
  if (!u) return ''
  const name = `${u.first_name || ''} ${u.last_name || ''}`.trim()
  return name ? `${name} (${formatPhone(u.phone)})` : formatPhone(u.phone)
}

const formatSchedule = (e) => {
  const parts = []
  if (e.learning_place_name) parts.push(e.learning_place_name)
  if (e.learning_time) parts.push(e.learning_time)
  if (e.learning_days) parts.push(e.learning_days)
  return parts.join(' - ') || '-'
}

// Two-way space formatting for payment amount
const formattedInputPrice = computed({
  get() {
    if (paymentForm.value.amount === null || paymentForm.value.amount === undefined || isNaN(paymentForm.value.amount)) {
      return ''
    }
    return String(paymentForm.value.amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      paymentForm.value.amount = null
    } else {
      paymentForm.value.amount = parseInt(digits, 10)
    }
  }
})

const fetchGroupDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get(`/groups/${groupId}/`)
    group.value = response.data
  } catch (err) {
    console.error(err)
    error.value = "Guruh tafsilotlarini yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.get('/users/')
    allUsers.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (err) {
    console.error("Foydalanuvchilarni yuklashda xatolik:", err)
  }
}

const fetchLearningPlaces = async () => {
  try {
    const response = await api.get('/learning-places/')
    learningPlaces.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (err) {
    console.error("O'quv joylarini yuklashda xatolik:", err)
  }
}

const filteredEnrollments = computed(() => {
  if (!group.value?.enrollments) return []
  return group.value.enrollments.filter(e => {
    const q = searchQuery.value.toLowerCase()
    const matchSearch = !searchQuery.value || 
      e.student_name.toLowerCase().includes(q) || 
      e.student_phone.includes(q) ||
      (e.student_phone2 && e.student_phone2.includes(q))
    const matchJshshr = !searchJshshr.value || 
      (e.student_jshshr && String(e.student_jshshr).includes(searchJshshr.value))
    return matchSearch && matchJshshr
  })
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('uz-UZ')
}

const formatPhone = (phoneStr) => {
  if (!phoneStr) return '-'
  if (phoneStr.length === 12) {
    return `+${phoneStr.substring(0, 3)} (${phoneStr.substring(3, 5)}) ${phoneStr.substring(5, 8)}-${phoneStr.substring(8, 10)}-${phoneStr.substring(10, 12)}`
  }
  return phoneStr
}

const formatMoney = (amount) => {
  if (amount === null || amount === undefined) return '0'
  return String(amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

const statusText = (status) => {
  if (status === 'started') return 'Boshlangan'
  if (status === 'finished') return 'Tugatgan'
  if (status === 'canceled') return 'Bekor qilingan'
  return status
}

const statusClass = (status) => {
  return {
    'badge-started': status === 'started',
    'badge-finished': status === 'finished',
    'badge-canceled': status === 'canceled',
  }
}

// Payment modal actions
const openPayModal = (enrollment) => {
  if (!authStore.isAdminOrSuperuser) {
    alert("To'lovni qabul qilish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  activeEnrollment.value = enrollment
  payError.value = ''
  paymentForm.value = {
    amount: enrollment.enrolled_amount - enrollment.paid_amount,
    method: 'cash',
    notes: '',
  }
  if (payModal.value) {
    payModal.value.showModal()
  }
}

const closePayModal = () => {
  if (payModal.value) {
    payModal.value.close()
  }
  activeEnrollment.value = null
}

const submitPayment = async () => {
  if (!authStore.isAdminOrSuperuser) {
    payError.value = "To'lovni qabul qilish faqat admin va superuser uchun ruxsat etilgan."
    return
  }

  if (paymentForm.value.amount === null || paymentForm.value.amount === undefined || paymentForm.value.amount <= 0) {
    payError.value = "To'g'ri to'lov summasini kiriting."
    return
  }

  paySaving.value = true
  payError.value = ''
  try {
    const payload = {
      enrollment: activeEnrollment.value.id,
      amount: parseInt(paymentForm.value.amount, 10),
      method: paymentForm.value.method,
      notes: paymentForm.value.notes.trim() || null,
      status: 'accepted'
    }
    await api.post('/payments/', payload)
    closePayModal()
    await fetchGroupDetail()
  } catch (err) {
    console.error(err)
    payError.value = "To'lovni saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    paySaving.value = false
  }
}

// Assign modal actions
const openAssignModal = (enrollment, type) => {
  activeEnrollment.value = enrollment
  assignType.value = type
  assignError.value = ''
  if (type === 'instructor') {
    selectedAssignUserId.value = enrollment.instructor || null
  } else {
    selectedAssignUserId.value = enrollment.coordinator || null
  }
  if (assignModal.value) {
    assignModal.value.showModal()
  }
}

const closeAssignModal = () => {
  if (assignModal.value) {
    assignModal.value.close()
  }
}

const submitAssign = async () => {
  if (!activeEnrollment.value) return
  assignSaving.value = true
  assignError.value = ''
  try {
    const payload = {}
    if (assignType.value === 'instructor') {
      payload.instructor = selectedAssignUserId.value
    } else {
      payload.coordinator = selectedAssignUserId.value
    }
    await api.patch(`/enrollments/${activeEnrollment.value.id}/`, payload)
    closeAssignModal()
    await fetchGroupDetail()
  } catch (err) {
    console.error(err)
    assignError.value = "Biriktirishda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    assignSaving.value = false
  }
}

// Schedule modal actions
const openScheduleModal = (enrollment) => {
  activeEnrollment.value = enrollment
  scheduleError.value = ''
  scheduleForm.value = {
    learning_place: enrollment.learning_place || null,
    learning_time: enrollment.learning_time || '',
    learning_days: enrollment.learning_days || null,
  }
  if (scheduleModal.value) {
    scheduleModal.value.showModal()
  }
}

const closeScheduleModal = () => {
  if (scheduleModal.value) {
    scheduleModal.value.close()
  }
}

const submitSchedule = async () => {
  if (!activeEnrollment.value) return
  scheduleSaving.value = true
  scheduleError.value = ''
  try {
    const payload = {
      learning_place: scheduleForm.value.learning_place,
      learning_time: scheduleForm.value.learning_time ? scheduleForm.value.learning_time.trim() : null,
      learning_days: scheduleForm.value.learning_days,
    }
    await api.patch(`/enrollments/${activeEnrollment.value.id}/`, payload)
    closeScheduleModal()
    await fetchGroupDetail()
  } catch (err) {
    console.error(err)
    scheduleError.value = "Saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    scheduleSaving.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchGroupDetail()
  fetchUsers()
  fetchLearningPlaces()

  const dialogs = [payModal.value, assignModal.value, scheduleModal.value]
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
</script>

<style scoped>
/* ── Navigation ── */
.detail-header-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  color: #374151;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-back:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
  color: #111827;
}

.header-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}
.group-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}
.group-category-pill {
  background: #E8F5E9;
  color: #2D6A4F;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
}

/* ── Content Layout ── */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Summary Card */
.summary-card {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.summary-val {
  font-size: 14.5px;
  color: #111827;
}

.font-bold {
  font-weight: 700;
}

/* Status Badges */
.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-started {
  background: #D1FAE5;
  color: #065F46;
}

.badge-finished {
  background: #DBEAFE;
  color: #1E40AF;
}

.badge-canceled {
  background: #FEE2E2;
  color: #991B1B;
}

.notes-block {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #F3F4F6;
  font-size: 13.5px;
  color: #4B5563;
}
.notes-label {
  font-weight: 600;
  color: #111827;
}

/* ── Table Card ── */
.table-card {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-title {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: #111827;
}

.search-wrap-flex {
  display: flex;
  gap: 10px;
}

.search-input, .search-input-jshshr {
  padding: 8px 14px;
  font-size: 13px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  width: 220px;
  outline: none;
  transition: border-color 0.15s;
}

.search-input:focus, .search-input-jshshr:focus {
  border-color: #2D6A4F;
}

.search-input-jshshr {
  width: 150px;
}

/* Table */
.table-container {
  overflow-x: auto;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.students-table th {
  background: #F9FAFB;
  padding: 12px 16px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #E5E7EB;
  white-space: nowrap;
}

.students-table td {
  padding: 14px 16px;
  color: #4B5563;
  border-bottom: 1px solid #E5E7EB;
  vertical-align: middle;
}

.students-table tbody tr { cursor: pointer; }
.students-table tbody tr:hover td { background: #FAFAFA; }
.students-table tr:last-child td {
  border-bottom: none;
}

.td-name {
  font-weight: 600;
  color: #111827;
}

.th-phone, .td-phone {
  width: 175px !important;
  min-width: 175px !important;
  max-width: 175px !important;
  white-space: nowrap !important;
  font-family: monospace;
  font-size: 12px;
}

.td-jshshr {
  font-family: monospace;
  font-size: 12px;
}

.td-notes {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-empty {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
  font-weight: 500;
}

/* Assignment Cells */
.td-assign {
  white-space: nowrap;
}
.assign-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.assign-name {
  font-weight: 500;
  color: #111827;
  font-size: 13px;
}
.btn-assign-plus {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: 1px dashed #2D6A4F;
  background: #ECFDF5;
  color: #2D6A4F;
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-assign-plus:hover {
  background: #2D6A4F;
  color: white;
  border-style: solid;
}
.btn-assign-edit {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: none;
  background: #F3F4F6;
  color: #4B5563;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.btn-assign-edit:hover {
  background: #E5E7EB;
  color: #111827;
}

/* Pay Button */
.btn-pay {
  padding: 6px 14px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 12.5px;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-pay:hover {
  background: #245C43;
}

.fully-paid-badge {
  font-size: 11.5px;
  font-weight: 600;
  color: #047857;
  background: #ecfdf5;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

.free-badge {
  font-size: 11.5px;
  font-weight: 600;
  color: #B45309;
  background: #FFFBEB;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

.balance-warning {
  color: #DC2626;
  font-weight: 700;
}

.paid-val {
  color: #047857;
  font-weight: 600;
}

/* Pay summary info */
.pay-info-summary {
  background: #F3F4F6;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 18px;
  font-size: 13.5px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pay-info-summary p {
  margin: 0;
  color: #4B5563;
}
.pay-info-summary strong {
  color: #111827;
}

.text-area-input {
  resize: vertical;
  min-height: 80px;
}

/* ── Modal Dialog ───────────────────────────────────── */
.modal-dialog {
  border: none;
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  background: white;
  max-height: 90vh;
  overflow-y: auto;
  margin: auto;
}
.modal-dialog::backdrop {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
}

.modal-form {
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 14px 24px;
  border-bottom: 1px solid #E5E7EB;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.btn-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #9CA3AF;
  cursor: pointer;
}
.btn-close:hover { color: #111827; }

.modal-error {
  padding: 10px 12px;
  background: #FEE2E2;
  border-left: 4px solid #EF4444;
  color: #991B1B;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: left;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.form-input {
  padding: 10px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}
.form-input:focus {
  border-color: #2D6A4F;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.btn-cancel {
  padding: 9px 16px;
  background: #F3F4F6;
  color: #374151;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-cancel:hover {
  background: #E5E7EB;
}

.btn-save {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 20px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-save:hover {
  background: #245C43;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
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
</style>
