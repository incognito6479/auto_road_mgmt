<template>
  <AppLayout>

    <!-- Top action / back bar -->
    <div class="page-top">
      <button class="btn-back" @click="router.push({ name: 'categories' })">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Kategoriyalarga qaytish
      </button>
      <div class="top-actions-right">
        <button
          v-if="authStore.isAdminOrSuperuser && (selectedStudentIds.length === 23 || selectedStudentIds.length === 24)"
          class="btn-start-group"
          @click="openGroupConfirmModal"
        >
          Guruhni boshlash
        </button>
        <button v-if="authStore.isAdminOrSuperuser" class="btn-add" @click="openModal">Yangi O'quvchi Qo'shish</button>
      </div>
    </div>

    <!-- Category Header Card -->
    <div v-if="category" class="category-header-card">
      <div class="cat-details">
        <div class="cat-icon-wrap" v-html="categoryIcon"></div>
        <div class="cat-info-block">
          <h2 class="cat-name">{{ category.name }}</h2>
          <p class="cat-price">Narxi: <span class="price-val">{{ formattedPrice }}</span></p>
        </div>
      </div>
      <div class="cat-stat-badge">
        <span class="stat-count">{{ students.length }}</span>
        <span class="stat-label">Yangi O'quvchi</span>
      </div>
    </div>

    <!-- Filter card -->
    <div v-if="category && !loading && !error" class="filter-card">
      <div class="filter-field">
        <label class="filter-label">Ism yoki Telefon raqami bo'yicha qidirish</label>
        <input
          v-model="filterSearch"
          class="filter-input"
          type="text"
          placeholder="Ism yoki Telefon raqami bo'yicha qidirish"
        />
      </div>

      <div class="filter-field">
        <label class="filter-label">JSHSHR bo'yicha qidirish (faqat raqam)</label>
        <input
          v-model="filterJshshr"
          class="filter-input"
          type="text"
          placeholder="JSHSHR"
        />
      </div>
    </div>

    <!-- Loading, error, or empty states -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Ma'lumotlar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchData">Qayta urinish</button>
    </div>

    <!-- Table of registered students with status new -->
    <div v-else class="table-wrap">
      <div class="table-header">
        <h3>Navbatdagi / Yangi O'quvchilar Ro'yxati</h3>
      </div>
      <table class="stbl">
        <thead>
          <tr>
            <th>
              <input type="checkbox" @change="toggleSelectAll" :checked="isAllSelected" class="th-chk" />
            </th>
            <th>To'liq Ismi</th>
            <th class="th-phone">Telefon Raqami</th>
            <th>JSHSHR</th>
            <th>Passport Ma'lumotlari</th>
            <th>Ro'yxatdan o'tgan sana</th>
            <th>To'langan</th>
            <th>Holat</th>
            <th>Eslatma</th>
            <th>Amallar</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredStudents.length === 0">
            <td colspan="10" class="no-data">Hozircha ushbu kategoriyada yangi o'quvchilar mavjud emas</td>
          </tr>
          <tr v-for="s in filteredStudents" :key="s.id" class="stbl-row">
            <td>
              <input type="checkbox" :value="s.id" v-model="selectedStudentIds" class="td-chk" />
            </td>
            <td class="td-name">{{ s.name }}</td>
            <td class="td-muted td-phone">
              <div>{{ s.phone }}</div>
              <div v-if="s.phone2" style="font-size: 11.5px; color: #6B7280; margin-top: 2px;">
                Qo'shimcha: {{ s.phone2 }}
              </div>
            </td>
            <td class="td-muted">{{ s.jshshr }}</td>
            <td class="td-muted">{{ s.passport }}</td>
            <td class="td-muted">{{ s.date }}</td>
            <td class="td-bold">
              <span v-if="s.enrolledFree" class="status-badge badge-free">Tekin</span>
              <span v-else>{{ s.paymentAmount }}</span>
            </td>
            <td>
              <span class="status-badge badge-new">{{ s.status }}</span>
            </td>
            <td>
              <div class="td-notes" :title="s.notes">{{ s.notes || '-' }}</div>
            </td>
            <td>
              <button class="btn-edit" @click="openEditModal(s)" title="Tahrirlash">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" style="vertical-align: middle;">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- New Student Modal Dialog -->
    <dialog ref="studentModal" class="modal-dialog" closedby="any" aria-labelledby="modal-title">
      <form class="modal-form" @submit.prevent="saveStudent">
        <h3 id="modal-title" class="modal-title">Yangi o'quvchi qo'shish (Yangi holatda)</h3>

        <div v-if="modalError" class="modal-error">
          {{ modalError }}
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label for="std-name" class="form-label">F.I.SH. (To'liq ism)</label>
            <input
              id="std-name"
              v-model="newStudent.full_name"
              type="text"
              placeholder="Masalan: Abdullayev Ali"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-phone" class="form-label">Telefon raqami</label>
            <input
              id="std-phone"
              v-model="newStudent.phone"
              type="tel"
              placeholder="+998 90 123 45 67"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-phone2" class="form-label">Qo'shimcha telefon raqami</label>
            <input
              id="std-phone2"
              v-model="newStudent.phone2"
              type="tel"
              placeholder="+998 90 123 45 67 (ixtiyoriy)"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-jshshr" class="form-label">JSHSHR (14 xonali raqam)</label>
            <input
              id="std-jshshr"
              v-model="newStudent.jshshr"
              type="number"
              placeholder="Masalan: 30101990001014"
              required
              maxlength="14"
              class="form-input"
            />
          </div>

          <div class="form-row-group">
            <div class="form-group half-width">
              <label for="std-pass-serie" class="form-label">Pass. Seriya</label>
              <input
                id="std-pass-serie"
                v-model="newStudent.passport_serie"
                type="text"
                placeholder="AA"
                required
                maxlength="2"
                class="form-input text-uppercase"
              />
            </div>
            <div class="form-group half-width">
              <label for="std-pass-num" class="form-label">Pass. Raqam</label>
              <input
                id="std-pass-num"
                v-model="newStudent.passport_number"
                type="number"
                placeholder="1234567"
                required
                maxlength="7"
                class="form-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Tanlangan Kategoriya</label>
            <input
              v-if="category"
              type="text"
              :value="category.name"
              disabled
              class="form-input disabled-input"
            />
          </div>

          <div v-if="!newStudent.enrolled_free" class="form-group">
            <label for="std-payment" class="form-label">Boshlang'ich to'lov (so'm)</label>
            <input
              id="std-payment"
              v-model="formattedMinPayment"
              type="text"
              placeholder="Masalan: 1 000 000"
              required
              class="form-input"
            />
          </div>

          <div class="form-group checkbox-group" style="grid-column: span 2; display: flex; align-items: center; gap: 8px; margin-top: 8px;">
            <input
              id="std-enrolled-free"
              v-model="newStudent.enrolled_free"
              type="checkbox"
              class="form-checkbox"
            />
            <label for="std-enrolled-free" class="form-checkbox-label" style="font-weight: 600; color: #374151; cursor: pointer; font-size: 13.5px;">Bepul o'qish (Grant)</label>
          </div>

          <div v-if="!newStudent.enrolled_free" class="form-group checkbox-group" style="grid-column: span 2; display: flex; align-items: center; gap: 8px; margin-top: 8px;">
            <input
              id="std-custom-price-chk"
              v-model="newStudent.has_custom_price"
              type="checkbox"
              class="form-checkbox"
            />
            <label for="std-custom-price-chk" class="form-checkbox-label" style="font-weight: 600; color: #374151; cursor: pointer; font-size: 13.5px;">Maxsus shartnoma summasi belgilash</label>
          </div>

          <div v-if="newStudent.has_custom_price && !newStudent.enrolled_free" class="form-group" style="grid-column: span 2;">
            <label for="std-enrolled-amount" class="form-label">Shartnoma summasi (so'm)</label>
            <input
              id="std-enrolled-amount"
              v-model="formattedEnrolledAmount"
              type="text"
              placeholder="Masalan: 4 000 000"
              required
              class="form-input"
            />
          </div>
          <div class="form-group" style="grid-column: span 2;">
            <label for="std-notes" class="form-label">Eslatmalar</label>
            <textarea
              id="std-notes"
              v-model="newStudent.notes"
              placeholder="Qo'shimcha eslatmalar..."
              class="form-input"
              rows="3"
              style="resize: vertical; font-family: inherit; padding: 10px;"
            ></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="saving">
            <span v-if="saving" class="btn-spinner"></span>
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Edit Student Modal Dialog -->
    <dialog ref="editStudentModal" class="modal-dialog" closedby="any" aria-labelledby="edit-modal-title">
      <form class="modal-form" @submit.prevent="updateStudent">
        <h3 id="edit-modal-title" class="modal-title">O'quvchi ma'lumotlarini tahrirlash</h3>

        <div v-if="editModalError" class="modal-error">
          {{ editModalError }}
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label for="edit-std-name" class="form-label">F.I.SH. (To'liq ism)</label>
            <input
              id="edit-std-name"
              v-model="editingStudent.full_name"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="edit-std-phone" class="form-label">Telefon raqami</label>
            <input
              id="edit-std-phone"
              v-model="editingStudent.phone"
              type="tel"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="edit-std-phone2" class="form-label">Qo'shimcha telefon raqami</label>
            <input
              id="edit-std-phone2"
              v-model="editingStudent.phone2"
              type="tel"
              placeholder="+998 90 123 45 67 (ixtiyoriy)"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="edit-std-jshshr" class="form-label">JSHSHR (14 xonali raqam)</label>
            <input
              id="edit-std-jshshr"
              v-model="editingStudent.jshshr"
              type="number"
              required
              maxlength="14"
              class="form-input"
            />
          </div>

          <div class="form-row-group">
            <div class="form-group half-width">
              <label for="edit-std-pass-serie" class="form-label">Pass. Seriya</label>
              <input
                id="edit-std-pass-serie"
                v-model="editingStudent.passport_serie"
                type="text"
                required
                maxlength="2"
                class="form-input text-uppercase"
              />
            </div>
            <div class="form-group half-width">
              <label for="edit-std-pass-num" class="form-label">Pass. Raqam</label>
              <input
                id="edit-std-pass-num"
                v-model="editingStudent.passport_number"
                type="text"
                required
                maxlength="7"
                class="form-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="edit-std-category" class="form-label">Kategoriya</label>
            <div class="select-wrap">
              <select id="edit-std-category" v-model="editingStudent.category" required class="filter-select">
                <option value="" disabled>Kategoriyani tanlang</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
              <span class="select-arrow" style="top: 10px;">▼</span>
            </div>
          </div>

          <div class="form-group">
            <label for="edit-std-status" class="form-label">Holat</label>
            <div class="select-wrap">
              <select id="edit-std-status" v-model="editingStudent.status" required class="filter-select">
                <option value="new">Yangi</option>
                <option value="enrolled">Qabul qilingan</option>
                <option value="finished">Tugatgan</option>
              </select>
              <span class="select-arrow" style="top: 10px;">▼</span>
            </div>
          </div>
          <div class="form-group" style="grid-column: span 2;">
            <label for="edit-std-notes" class="form-label">Eslatmalar</label>
            <textarea
              id="edit-std-notes"
              v-model="editingStudent.notes"
              placeholder="Qo'shimcha eslatmalar..."
              class="form-input"
              rows="3"
              style="resize: vertical; font-family: inherit; padding: 10px;"
            ></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeEditModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="editSaving">
            <span v-if="editSaving" class="btn-spinner"></span>
            {{ editSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Start Group Confirmation Modal Dialog -->
    <dialog ref="groupConfirmModal" class="modal-dialog" closedby="any" aria-labelledby="group-modal-title">
      <form class="modal-form" @submit.prevent="startGroup">
        <h3 id="group-modal-title" class="modal-title">Guruhni boshlash</h3>

        <div class="modal-confirm-body" style="display: flex; flex-direction: column; gap: 16px;">
          <p style="margin: 0; font-size: 14px; color: #4B5563;">
            Tanlangan <strong>{{ selectedStudentIds.length }}</strong> ta o'quvchi bilan yangi guruh boshlamoqchimisiz?
          </p>

          <div class="form-group">
            <label for="group-name-input" class="form-label">Guruh nomi</label>
            <input
              id="group-name-input"
              v-model="groupForm.name"
              type="text"
              required
              class="form-input"
              placeholder="Masalan: B-Guruh 1"
            />
          </div>

          <div class="form-group">
            <label for="group-start-input" class="form-label">Boshlanish sanasi</label>
            <input
              id="group-start-input"
              v-model="groupForm.started_at"
              type="date"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="group-duration-input" class="form-label">Davomiyligi (oylar)</label>
            <input
              id="group-duration-input"
              v-model="groupForm.duration"
              type="number"
              step="0.1"
              required
              class="form-input"
              placeholder="Masalan: 3.5"
            />
          </div>
        </div>

        <div class="modal-actions" style="margin-top: 16px;">
          <button type="button" class="btn-cancel" @click="closeGroupConfirmModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="groupSaving">
            <span v-if="groupSaving" class="btn-spinner"></span>
            {{ groupSaving ? 'Boshlanmoqda...' : 'Tasdiqlash' }}
          </button>
        </div>
      </form>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const categoryId = route.params.id

// ── Filter State ─────────────────────────────────────
const filterSearch = ref('')
const filterJshshr = ref('')

// ── State ───────────────────────────────────────────
const category = ref(null)
const students = ref([])
const categories = ref([])
const loading = ref(false)
const error = ref('')

// ── Selection State ──────────────────────────────────
const selectedStudentIds = ref([])
const groupConfirmModal = ref(null)
const groupSaving = ref(false)

const groupForm = ref({
  name: '',
  started_at: '',
  duration: null,
})

const isAllSelected = computed(() => {
  return filteredStudents.value.length > 0 && selectedStudentIds.value.length === filteredStudents.value.length
})

const toggleSelectAll = (e) => {
  if (e.target.checked) {
    selectedStudentIds.value = filteredStudents.value.map(s => s.id)
  } else {
    selectedStudentIds.value = []
  }
}

const openGroupConfirmModal = () => {
  if (!authStore.isAdminOrSuperuser) {
    alert("Guruh yaratish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  groupForm.value = {
    name: category.value ? `${category.value.name} guruhi` : '',
    started_at: new Date().toISOString().substring(0, 10),
    duration: category.value ? category.value.duration : null,
  }
  if (groupConfirmModal.value) {
    groupConfirmModal.value.showModal()
  }
}

const closeGroupConfirmModal = () => {
  if (groupConfirmModal.value) {
    groupConfirmModal.value.close()
  }
}

const startGroup = async () => {
  if (!authStore.isAdminOrSuperuser) {
    alert("Guruh yaratish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }

  if (!groupForm.value.name.trim() || !groupForm.value.started_at || groupForm.value.duration === null || groupForm.value.duration === undefined) {
    alert("Barcha maydonlarni to'ldiring.")
    return
  }

  groupSaving.value = true
  try {
    const payload = {
      name: groupForm.value.name.trim(),
      started_at: groupForm.value.started_at,
      duration: parseFloat(groupForm.value.duration),
      category: parseInt(categoryId, 10),
      status: 'started',
      student_ids: selectedStudentIds.value,
    }
    await api.post('/groups/', payload)

    selectedStudentIds.value = []
    closeGroupConfirmModal()
    await fetchData()
  } catch (err) {
    console.error(err)
    alert("Guruhni boshlashda xatolik yuz berdi.")
  } finally {
    groupSaving.value = false
  }
}



// ── Edit Modal state ─────────────────────────────────────────
const editStudentModal = ref(null)
const editingStudent = ref({
  id: null,
  full_name: '',
  phone: '',
  phone2: '',
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  category: '',
  status: '',
  notes: '',
})
const editSaving = ref(false)
const editModalError = ref('')

watch(() => editingStudent.value.phone, (newValue) => {
  if (!newValue) return
  let digits = newValue.replace(/\D/g, '')

  if (digits.length > 0 && !digits.startsWith('998')) {
    digits = '998' + digits
  }

  digits = digits.substring(0, 12)

  let formatted = ''
  if (digits.length > 0) {
    formatted += '+' + digits.substring(0, 3)
  }
  if (digits.length > 3) {
    formatted += ' ' + digits.substring(3, 5)
  }
  if (digits.length > 5) {
    formatted += ' ' + digits.substring(5, 8)
  }
  if (digits.length > 8) {
    formatted += ' ' + digits.substring(8, 10)
  }
  if (digits.length > 10) {
    formatted += ' ' + digits.substring(10, 12)
  }

  if (newValue !== formatted) {
    editingStudent.value.phone = formatted
  }
})

watch(() => editingStudent.value.phone2, (newValue) => {
  if (!newValue) return
  let digits = newValue.replace(/\D/g, '')

  if (digits.length > 0 && !digits.startsWith('998')) {
    digits = '998' + digits
  }

  digits = digits.substring(0, 12)

  let formatted = ''
  if (digits.length > 0) {
    formatted += '+' + digits.substring(0, 3)
  }
  if (digits.length > 3) {
    formatted += ' ' + digits.substring(3, 5)
  }
  if (digits.length > 5) {
    formatted += ' ' + digits.substring(5, 8)
  }
  if (digits.length > 8) {
    formatted += ' ' + digits.substring(8, 10)
  }
  if (digits.length > 10) {
    formatted += ' ' + digits.substring(10, 12)
  }

  if (newValue !== formatted) {
    editingStudent.value.phone2 = formatted
  }
})

const openEditModal = (student) => {
  editingStudent.value = {
    id: student.id,
    full_name: student.name,
    phone: student.phone,
    phone2: student.phone2 || '',
    jshshr: student.jshshr,
    passport_serie: student.passportSerie,
    passport_number: student.passportNumber,
    category: student.categoryId || '',
    status: student.rawStatus,
    notes: student.notes || '',
  }
  editModalError.value = ''
  if (editStudentModal.value) {
    editStudentModal.value.showModal()
  }
}

const closeEditModal = () => {
  if (editStudentModal.value) {
    editStudentModal.value.close()
  }
}

const updateStudent = async () => {
  const s = editingStudent.value
  const phoneCleaned = s.phone.replace(/\D/g, '')

  if (!s.full_name.trim() || !phoneCleaned || !s.jshshr || !s.passport_serie.trim() || !s.passport_number || !s.category) {
    editModalError.value = "Barcha maydonlarni to'ldiring."
    return
  }

  if (phoneCleaned.length < 12) {
    editModalError.value = "Telefon raqami noto'g'ri kiritilgan."
    return
  }

  if (String(s.jshshr).length !== 14) {
    editModalError.value = "JSHSHR 14 ta raqam bo'lishi shart."
    return
  }

  const phone2Cleaned = s.phone2 ? s.phone2.replace(/\D/g, '') : null
  if (phone2Cleaned && phone2Cleaned.length < 12) {
    editModalError.value = "Qo'shimcha telefon raqami noto'g'ri kiritilgan."
    return
  }

  editSaving.value = true
  editModalError.value = ''

  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      phone2: phone2Cleaned,
      jshshr: parseInt(s.jshshr, 10),
      passport_serie: s.passport_serie.trim().toUpperCase(),
      passport_number: parseInt(s.passport_number, 10),
      category: parseInt(s.category, 10),
      status: s.status,
      notes: s.notes,
    }

    await api.patch(`/students/${s.id}/`, payload)
    closeEditModal()
    await fetchData()
  } catch (err) {
    console.error(err)
    if (err.response?.data?.phone) {
      editModalError.value = "Ushbu telefon raqamli o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.jshshr) {
      editModalError.value = "Ushbu JSHSHR egasi bo'lgan o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.passport_number) {
      editModalError.value = "Ushbu passport raqamli o'quvchi allaqachon mavjud."
    } else {
      editModalError.value = "Tahrirlashda xatolik yuz berdi. Ma'lumotlarni tekshirib qayta urinib ko'ring."
    }
  } finally {
    editSaving.value = false
  }
}

const filteredStudents = computed(() => {
  return students.value.filter(s => {
    const q = filterSearch.value.toLowerCase()
    const matchSearch = !q || s.name.toLowerCase().includes(q) || s.phone.includes(q)
    const matchJshshr = !filterJshshr.value || s.jshshr.includes(filterJshshr.value)
    return matchSearch && matchJshshr
  })
})

// ── Modal State ──────────────────────────────────────
const studentModal = ref(null)
const newStudent = ref({
  full_name: '',
  phone: '',
  phone2: '',
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  category: categoryId,
  min_payment: null,
  enrolled_free: false,
  has_custom_price: false,
  enrolled_amount: null,
  notes: '',
})
const saving = ref(false)
const modalError = ref('')

// Watch phone for formatting: +998 90 900 90 90
watch(() => newStudent.value.phone, (newValue) => {
  if (!newValue) return
  let digits = newValue.replace(/\D/g, '')

  if (digits.length > 0 && !digits.startsWith('998')) {
    digits = '998' + digits
  }

  // Enforce max 12 digits (998 + 9 digits)
  digits = digits.substring(0, 12)

  let formatted = ''
  if (digits.length > 0) {
    formatted += '+' + digits.substring(0, 3)
  }
  if (digits.length > 3) {
    formatted += ' ' + digits.substring(3, 5)
  }
  if (digits.length > 5) {
    formatted += ' ' + digits.substring(5, 8)
  }
  if (digits.length > 8) {
    formatted += ' ' + digits.substring(8, 10)
  }
  if (digits.length > 10) {
    formatted += ' ' + digits.substring(10, 12)
  }

  if (newValue !== formatted) {
    newStudent.value.phone = formatted
  }
})

watch(() => newStudent.value.phone2, (newValue) => {
  if (!newValue) return
  let digits = newValue.replace(/\D/g, '')

  if (digits.length > 0 && !digits.startsWith('998')) {
    digits = '998' + digits
  }

  digits = digits.substring(0, 12)

  let formatted = ''
  if (digits.length > 0) {
    formatted += '+' + digits.substring(0, 3)
  }
  if (digits.length > 3) {
    formatted += ' ' + digits.substring(3, 5)
  }
  if (digits.length > 5) {
    formatted += ' ' + digits.substring(5, 8)
  }
  if (digits.length > 8) {
    formatted += ' ' + digits.substring(8, 10)
  }
  if (digits.length > 10) {
    formatted += ' ' + digits.substring(10, 12)
  }

  if (newValue !== formatted) {
    newStudent.value.phone2 = formatted
  }
})

// Two-way formatting for min_payment
const formattedMinPayment = computed({
  get() {
    if (newStudent.value.min_payment === null || newStudent.value.min_payment === undefined || isNaN(newStudent.value.min_payment)) {
      return ''
    }
    return String(newStudent.value.min_payment).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      newStudent.value.min_payment = null
    } else {
      newStudent.value.min_payment = parseInt(digits, 10)
    }
  }
})

// Two-way formatting for enrolled_amount
const formattedEnrolledAmount = computed({
  get() {
    if (newStudent.value.enrolled_amount === null || newStudent.value.enrolled_amount === undefined || isNaN(newStudent.value.enrolled_amount)) {
      return ''
    }
    return String(newStudent.value.enrolled_amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      newStudent.value.enrolled_amount = null
    } else {
      newStudent.value.enrolled_amount = parseInt(digits, 10)
    }
  }
})

// ── Icons & pricing helpers ──────────────────────────
const categoryIcon = computed(() => {
  if (!category.value) return ''
  const norm = category.value.name.toUpperCase()
  if (norm.includes('B') && !norm.includes('C')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="12" cy="12" r="9.5"/>
      <circle cx="12" cy="12" r="3.5"/>
      <line x1="12" y1="8.5" x2="12" y2="2.5"/>
      <line x1="6.3" y1="15.5" x2="9.3" y2="13.4"/>
      <line x1="17.7" y1="15.5" x2="14.7" y2="13.4"/>
    </svg>`
  } else if (norm.includes('A')) {
    return `<svg viewBox="0 0 32 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="6" cy="18" r="4"/>
      <circle cx="26" cy="18" r="4"/>
      <path d="M6 18h5l3-7h5l4 7"/>
      <path d="M14 11l1.5-4h3"/>
      <circle cx="20" cy="6" r="1.5"/>
    </svg>`
  } else if (norm.includes('BC') || norm.includes('C')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <rect x="1" y="7" width="14" height="11" rx="1"/>
      <path d="M15 10h5l3 4v3h-8V10z"/>
      <circle cx="5.5" cy="18.5" r="1.5"/>
      <circle cx="18.5" cy="18.5" r="1.5"/>
    </svg>`
  } else if (norm.includes('D')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <rect x="2" y="4" width="20" height="14" rx="2"/>
      <line x1="2" y1="9" x2="22" y2="9"/>
      <line x1="12" y1="4" x2="12" y2="18"/>
      <circle cx="6" cy="20" r="1.5"/>
      <circle cx="18" cy="20" r="1.5"/>
      <line x1="6" y1="18" x2="6" y2="21"/>
      <line x1="18" y1="18" x2="18" y2="21"/>
    </svg>`
  } else {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="12" cy="12" r="9.5"/>
      <path d="M12 8v8M8 12h8" stroke="#2D6A4F" stroke-width="1.6" stroke-linecap="round"/>
    </svg>`
  }
})

const formattedPrice = computed(() => {
  if (!category.value || !category.value.price) return "0 so'm"
  return Number(category.value.price).toLocaleString('uz-UZ') + " so'm"
})

// ── Fetch Category & Students ────────────────────────
const fetchData = async () => {
  loading.value = true
  error.value = ''
  try {
    const [catRes, stdRes, allCatsRes] = await Promise.all([
      api.get(`/categories/${categoryId}/`),
      api.get(`/students/?category=${categoryId}&status=new`),
      api.get(`/categories/`)
    ])
    category.value = catRes.data
    const stdList = Array.isArray(stdRes.data) ? stdRes.data : (stdRes.data?.results || [])
    students.value = stdList.map(mapStudent)
    categories.value = Array.isArray(allCatsRes.data) ? allCatsRes.data : (allCatsRes.data?.results || [])
  } catch (err) {
    console.error(err)
    error.value = "Ma'lumotlarni yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

const formatPrice = (price) => {
  if (price === null || price === undefined) return "0 so'm"
  return Number(price).toLocaleString('uz-UZ') + " so'm"
}

const mapStudent = (s) => {
  const dateStr = s.created_at ? new Date(s.created_at).toLocaleDateString('uz-UZ') : ''
  return {
    id: s.id,
    name: s.full_name,
    phone: formatPhoneDisplay(s.phone),
    phone2: s.phone2 ? formatPhoneDisplay(s.phone2) : '',
    jshshr: String(s.jshshr),
    passport: `${s.passport_serie} ${s.passport_number}`,
    passportSerie: s.passport_serie,
    passportNumber: s.passport_number,
    date: dateStr,
    status: "Yangi",
    rawStatus: s.status,
    categoryId: s.category_id,
    enrolledFree: s.enrolled_free || false,
    paymentAmount: formatPrice(s.payment_amount),
    notes: s.notes || '',
  }
}

const formatPhoneDisplay = (p) => {
  if (!p) return ''
  if (p.includes(' ')) return p
  const digits = p.replace(/\D/g, '')
  if (digits.length === 12) {
    return `+${digits.substring(0, 3)} ${digits.substring(3, 5)} ${digits.substring(5, 8)} ${digits.substring(8, 10)} ${digits.substring(10, 12)}`
  }
  return p
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchData()
  
  // Light dismiss fallback
  if (studentModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    studentModal.value.addEventListener('click', (event) => {
      if (event.target !== studentModal.value) return
      const rect = studentModal.value.getBoundingClientRect()
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      )
      if (!isInside) {
        closeModal()
      }
    })
  }
})

// ── Modal Actions ────────────────────────────────────────────
const openModal = () => {
  if (!authStore.isAdminOrSuperuser) {
    alert("O'quvchini ro'yxatdan o'tkazish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  newStudent.value = {
    full_name: '',
    phone: '',
    phone2: '',
    jshshr: '',
    passport_serie: '',
    passport_number: '',
    category: categoryId,
    min_payment: null,
    enrolled_free: false,
    has_custom_price: false,
    enrolled_amount: null,
    notes: '',
  }
  modalError.value = ''
  if (studentModal.value) {
    studentModal.value.showModal()
  }
}

const closeModal = () => {
  if (studentModal.value) {
    studentModal.value.close()
  }
}

const saveStudent = async () => {
  if (!authStore.isAdminOrSuperuser) {
    modalError.value = "O'quvchini ro'yxatdan o'tkazish faqat admin va superuser uchun ruxsat etilgan."
    return
  }

  const s = newStudent.value
  const phoneCleaned = s.phone.replace(/\D/g, '')
  
  if (s.enrolled_free) {
    s.min_payment = 0
  }
  
  if (!s.full_name.trim() || !phoneCleaned || !s.jshshr || !s.passport_serie.trim() || !s.passport_number || s.min_payment === null) {
    modalError.value = "Barcha maydonlarni to'ldiring."
    return
  }
  
  if (s.has_custom_price && !s.enrolled_free && s.enrolled_amount === null) {
    modalError.value = "Shartnoma summasini kiriting."
    return
  }
  
  if (phoneCleaned.length < 12) {
    modalError.value = "Telefon raqami noto'g'ri kiritilgan."
    return
  }
  
  if (String(s.jshshr).length !== 14) {
    modalError.value = "JSHSHR 14 ta raqam bo'lishi shart."
    return
  }
  
  const phone2Cleaned = s.phone2 ? s.phone2.replace(/\D/g, '') : null
  if (phone2Cleaned && phone2Cleaned.length < 12) {
    modalError.value = "Qo'shimcha telefon raqami noto'g'ri kiritilgan."
    return
  }

  saving.value = true
  modalError.value = ''
  
  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      phone2: phone2Cleaned,
      jshshr: parseInt(s.jshshr, 10),
      passport_serie: s.passport_serie.trim().toUpperCase(),
      passport_number: parseInt(s.passport_number, 10),
      category: parseInt(s.category, 10),
      min_payment: parseInt(s.min_payment, 10),
      enrolled_free: s.enrolled_free || false,
      enrolled_amount: (s.has_custom_price && !s.enrolled_free) ? parseInt(s.enrolled_amount, 10) : null,
      notes: s.notes,
      status: 'new' // Set student status to new!
    }
    
    await api.post('/students/', payload)
    closeModal()
    await fetchData()
  } catch (err) {
    console.error(err)
    if (err.response?.data?.phone) {
      modalError.value = "Ushbu telefon raqamli o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.jshshr) {
      modalError.value = "Ushbu JSHSHR egasi bo'lgan o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.passport_number) {
      modalError.value = "Ushbu passport raqamli o'quvchi allaqachon mavjud."
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi. Ma'lumotlarni tekshirib qayta urinib ko'ring."
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* ── Top actions / back link ──────────────────────────────── */
.page-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s, border-color 0.15s;
}
.btn-back:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
}

.btn-add {
  padding: 10px 20px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s, transform 0.1s;
}
.btn-add:hover { background: #245C43; transform: translateY(-1px); }

/* ── Category Header Card ─────────────────────────────────── */
.category-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 14px;
  padding: 24px 28px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  margin-bottom: 24px;
}

.cat-details {
  display: flex;
  align-items: center;
  gap: 20px;
}

.cat-icon-wrap {
  width: 68px;
  height: 68px;
  background: #d1fae5;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cat-info-block {
  text-align: left;
}

.cat-name {
  font-size: 20px;
  font-weight: 800;
  color: #111827;
  margin: 0 0 6px 0;
}

.cat-price {
  font-size: 14px;
  color: #6B7280;
  margin: 0;
  font-weight: 500;
}

.price-val {
  font-weight: 700;
  color: #111827;
  font-size: 15px;
}

.cat-stat-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-count {
  font-size: 36px;
  font-weight: 900;
  color: #2D6A4F;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  font-weight: 600;
  color: #6B7280;
  margin-top: 4px;
}

/* ── States ─────────────────────────────────────────── */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
}
.state-text {
  font-size: 15px;
  color: #6B7280;
  font-weight: 500;
  margin: 12px 0 0 0;
}
.state-error .state-text {
  color: #DC2626;
}
.btn-retry {
  margin-top: 16px;
  padding: 8px 16px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.btn-retry:hover {
  background: #245C43;
}

/* Spinner */
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(45, 106, 79, 0.2);
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Table ─────────────────────────────────────────────────── */
.table-wrap {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  overflow-x: auto;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.table-header {
  padding: 16px 20px;
  border-bottom: 1px solid #F3F4F6;
  text-align: left;
}

.table-header h3 {
  margin: 0;
  font-size: 15.5px;
  font-weight: 700;
  color: #111827;
}

.stbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}

.stbl thead th {
  padding: 13px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 700;
  color: #111827;
  border-bottom: 2px solid #F3F4F6;
  white-space: nowrap;
  background: white;
}

.stbl tbody .stbl-row td {
  padding: 13px 16px;
  border-bottom: 1px solid #F9FAFB;
  vertical-align: middle;
}

.stbl tbody .stbl-row:last-child td { border-bottom: none; }
.stbl tbody .stbl-row:hover td { background: #FAFAFA; }

.td-notes {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #6B7280;
  font-size: 13px;
}

.td-name {
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  text-align: left;
}

.td-muted { color: #6B7280; text-align: left; }

/* No data row */
.no-data {
  text-align: center;
  padding: 48px;
  color: #9CA3AF;
  font-size: 14.5px;
}

/* ── Status badges ──────────────────────────────────────────── */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.badge-new {
  background: white;
  color: #374151;
  border: 1.5px solid #D1D5DB;
}

.badge-free {
  background: #E8F5E9;
  color: #2E7D32;
  border: 1.5px solid #A5D6A7;
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

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  border-bottom: 1px solid #E5E7EB;
  padding-bottom: 12px;
  text-align: left;
}

.modal-error {
  padding: 10px 12px;
  background: #FEE2E2;
  border-left: 4px solid #EF4444;
  color: #991B1B;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  text-align: left;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row-group {
  display: flex;
  gap: 16px;
}

.half-width {
  flex: 1;
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

.disabled-input {
  background: #F3F4F6;
  color: #9CA3AF;
  border-color: #E5E7EB;
  cursor: not-allowed;
}

.text-uppercase {
  text-transform: uppercase;
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
.btn-save:hover:not(:disabled) {
  background: #245C43;
}
.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ── Filter card ─────────────────────────────────────────── */
.filter-card {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 20px;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.filter-input {
  padding: 9px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  outline: none;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.15s;
}
.filter-input:focus { border-color: #2D6A4F; }
.filter-input::placeholder { color: #9CA3AF; }

.btn-edit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: white;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  color: #374151;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  padding: 0;
}
.btn-edit:hover {
  background: #F9FAFB;
  border-color: #9CA3AF;
}

/* Select wrapper */
.select-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-select {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  padding: 9px 34px 9px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  background: white;
  outline: none;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: border-color 0.15s;
}
.filter-select:focus { border-color: #2D6A4F; }

.select-arrow {
  position: absolute;
  right: 10px;
  color: #9CA3AF;
  pointer-events: none;
  flex-shrink: 0;
}

.top-actions-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-start-group {
  padding: 10px 20px;
  background: #3B82F6;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s, transform 0.1s;
}
.btn-start-group:hover {
  background: #2563EB;
  transform: translateY(-1px);
}

.modal-confirm-body {
  padding: 10px 0;
  text-align: left;
  font-size: 14.5px;
  color: #374151;
  line-height: 1.5;
}

.modal-confirm-sub {
  margin-top: 8px;
  font-size: 13px;
  color: #6B7280;
}

.th-chk, .td-chk {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #2D6A4F;
}

/* Strict phone column width */
.th-phone, .td-phone {
  width: 175px !important;
  min-width: 175px !important;
  max-width: 175px !important;
  white-space: nowrap !important;
}

@media (max-width: 900px) {
  .filter-card { grid-template-columns: 1fr; }
  .table-wrap  { overflow-x: auto; }
}
</style>
