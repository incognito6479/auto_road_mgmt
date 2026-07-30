<template>
  <AppLayout>

    <!-- Page Header -->
    <div class="page-top">
      <div>
        <h2 class="page-main-title">Avtomobillar Boshqaruvi (Cars)</h2>
        <p class="page-sub-title">O'quv avtomobillari ro'yxati, holati (mavjud, ta'mirlashda), sug'urta va texnik ko'rik muddatlari</p>
      </div>

      <button v-if="authStore.canEditCars" class="btn-primary-action" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>Yangi Avtomobil Qo'shish</span>
      </button>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-cards-grid">
      <div class="card-metric card-blue">
        <div class="card-metric-icon">🚗</div>
        <div>
          <span class="metric-lbl">Jami Avtomobillar</span>
          <h4 class="metric-val text-blue">{{ totalCount }} ta</h4>
        </div>
      </div>

      <div class="card-metric card-green">
        <div class="card-metric-icon">✅</div>
        <div>
          <span class="metric-lbl">Mavjud (Yaroqli)</span>
          <h4 class="metric-val text-green">{{ availableCarsCount }} ta</h4>
        </div>
      </div>

      <div class="card-metric card-orange">
        <div class="card-metric-icon">🛠️</div>
        <div>
          <span class="metric-lbl">Ta'mirlashda / Mavjud emas</span>
          <h4 class="metric-val text-orange">{{ nonAvailableCarsCount }} ta</h4>
        </div>
      </div>
    </div>

    <!-- Table Section with Search Toolbar -->
    <div class="table-section-card margin-top">
      <div class="toolbar-bar">
        <div class="toolbar-left-controls">
          <div class="search-box">
            <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
              <circle cx="8.5" cy="8.5" r="5.5"/>
              <line x1="13" y1="13" x2="18" y2="18"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Avtomobil nomi bo'yicha..."
              class="search-input"
            />
          </div>

          <div class="filter-item">
            <label class="flabel-inline">Holati:</label>
            <div class="select-wrap-relative">
              <select v-model="filterStatus" class="fselect-field">
                <option value="">Barcha holatlar</option>
                <option value="available">🟢 Mavjud</option>
                <option value="repairing">🟡 Ta'mirlashda</option>
                <option value="not_available">🔴 Mavjud emas</option>
              </select>
              <div class="select-chevron-icon">▼</div>
            </div>
          </div>
        </div>

        <div class="total-count">
          Jami: <strong>{{ cars.length }}</strong> ta avtomobil
        </div>
      </div>

      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Avtomobillar ro'yxati yuklanmoqda...</span>
        </div>

        <div v-else-if="cars.length === 0" class="empty-state">
          <p>Avtomobillar topilmadi</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th style="width: 50px;">ID</th>
              <th style="min-width: 170px;">Avtomobil & Davlat Raqami</th>
              <th style="width: 120px;">Holati (Status)</th>
              <th style="min-width: 140px;">Instruktor</th>
              <th style="width: 110px;">Sug'urta</th>
              <th style="width: 110px;">Texnik Ko'rik</th>
              <th style="width: 130px;">Moy Holati</th>
              <th style="width: 120px;">Oxirgi Yuvilgan</th>
              <th>Izoh / Eslatmalari</th>
              <th style="text-align: right; width: 90px;">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="car in cars" :key="car.id" class="table-row clickable" @click="goToCarDetail(car.id)" style="cursor: pointer;">
              <td class="td-id">#{{ car.id }}</td>

              <!-- Car Title -->
              <td class="td-name">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <img :src="car.image || '/default_car_photo.png'" alt="Car" style="width: 48px; height: 34px; object-fit: cover; border-radius: 6px; border: 1px solid #E5E7EB;" />
                  <div>
                    <div class="car-title font-bold text-primary">{{ car.car_name }}<span v-if="car.manufact_year" class="year-inline"> ({{ car.manufact_year }})</span></div>
                    <div class="plate-sub font-mono">{{ car.plate_number }}</div>
                  </div>
                </div>
              </td>

              <!-- Status -->
              <td>
                <span class="status-badge-pill" :class="car.status">
                  {{ statusText(car.status) }}
                </span>
              </td>

              <!-- Instructor -->
              <td>
                <span v-if="car.instructor_name" class="instructor-badge link-value" @click.stop="goUser(car.instructor)">👤 {{ car.instructor_name }}</span>
                <span v-else class="text-muted">Biriktirilmagan</span>
              </td>

              <!-- Policy days-left -->
              <td>
                <span v-if="car.policy_date" class="status-badge days-left-badge" :class="getDateStatus(car.policy_date).chipClass">
                  {{ daysLeftText(getDateStatus(car.policy_date)) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>

              <!-- Tech inspection days-left -->
              <td>
                <span v-if="car.tech_inspection_date" class="status-badge days-left-badge" :class="getDateStatus(car.tech_inspection_date).chipClass">
                  {{ daysLeftText(getDateStatus(car.tech_inspection_date)) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>

              <!-- Oil status -->
              <td>
                <span class="status-badge days-left-badge" :class="oilStatus(car).chipClass">
                  {{ oilStatus(car).label }}
                </span>
              </td>

              <!-- Last washed -->
              <td>
                <span class="text-muted">{{ lastWashedText(car) }}</span>
              </td>

              <!-- Notes -->
              <td class="td-notes">{{ car.notes || '-' }}</td>

              <!-- Actions -->
              <td style="text-align: right;" @click.stop>
                <div class="row-actions">
                  <button v-if="authStore.canEditCars" class="btn-action-edit" @click.stop="openEditModal(car)" title="Tahrirlash">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button v-if="authStore.isAdminOrSuperuser" class="btn-action-delete" @click.stop="confirmDelete(car)" title="O'chirish">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
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

    <!-- CREATE / EDIT MODAL -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header-banner primary-banner">
            <div class="header-left-info">
              <div class="header-icon-box">🚘</div>
              <div>
                <h3>{{ isEditing ? "Avtomobilni Tahrirlash" : "Yangi Avtomobil Qo'shish" }}</h3>
                <p>Avtomobil ma'lumotlari hamda sug'urta/texnik ko'rik sanalarini kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeModal">✕</button>
          </div>

          <form @submit.prevent="saveCar" class="modal-body">
            <div v-if="modalError" class="alert-error">{{ modalError }}</div>

            <!-- Car Name -->
            <div class="form-group">
              <label class="flabel required">Avtomobil Nomi & Davlat Raqami *</label>
              <input
                v-model="form.car_name"
                type="text"
                class="finput"
                placeholder="Masalan: Cobalt 01 A 777 AA"
                required
              />
            </div>

            <!-- Car Image -->
            <div class="form-group">
              <label class="flabel">Avtomobil Rasmi</label>
              <input
                type="file"
                accept="image/*"
                class="finput"
                @change="onCarFileChange"
              />
            </div>

            <!-- Status Select -->
            <div class="form-group">
              <label class="flabel required">Avtomobil Holati (Status) *</label>
              <div class="select-wrap-relative">
                <select v-model="form.status" class="finput fselect-modal-field status-select-fixed" required>
                  <option value="available">🟢 Mavjud (Yaroqli)</option>
                  <option value="repairing">🟡 Ta'mirlashda</option>
                  <option value="not_available">🔴 Mavjud emas</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <!-- Manufact Year -->
            <div class="form-group">
              <label class="flabel">Ishlab Chiqarilgan Yili</label>
              <input
                v-model.number="form.manufact_year"
                type="number"
                class="finput"
                placeholder="Masalan: 2023"
                min="1990"
                max="2030"
              />
            </div>

            <!-- Instructor (searchable) -->
            <div class="form-group">
              <label class="flabel">Biriktirilgan Instruktor</label>
              <div class="searchable-select" @click.stop>
                <input
                  type="text"
                  class="finput"
                  v-model="instructorSearchText"
                  @focus="instructorDropdownOpen = true"
                  @input="instructorDropdownOpen = true"
                  @blur="onInstructorBlur"
                  placeholder="Instruktorni qidirish..."
                  autocomplete="off"
                />
                <div v-if="instructorDropdownOpen" class="searchable-dropdown">
                  <div
                    class="searchable-option"
                    :class="{ selected: !form.instructor }"
                    @mousedown.prevent="selectInstructor(null)"
                  >Biriktirilmagan</div>
                  <div
                    v-for="i in filteredInstructorOptions"
                    :key="i.id"
                    class="searchable-option"
                    :class="{ selected: form.instructor === i.id }"
                    @mousedown.prevent="selectInstructor(i)"
                  >{{ i.full_name || i.phone }}</div>
                  <div v-if="filteredInstructorOptions.length === 0" class="searchable-empty">Instruktor topilmadi</div>
                </div>
              </div>
            </div>

            <!-- Mileage -->
            <div class="form-group">
              <label class="flabel">Probeg (km)</label>
              <input
                v-model.number="form.mileage"
                type="number"
                class="finput"
                placeholder="Masalan: 45000"
                min="0"
              />
            </div>

            <!-- Oil Change Date -->
            <div class="form-group">
              <label class="flabel">Moy Almashtirilgan Sana</label>
              <input
                v-model="form.oil_change_date"
                type="date"
                class="finput"
              />
            </div>

            <!-- Oil Change Mileage -->
            <div class="form-group">
              <label class="flabel">Moy Almashtirilgandagi Probeg (km)</label>
              <input
                v-model.number="form.oil_change_mileage"
                type="number"
                class="finput"
                placeholder="Masalan: 42000"
                min="0"
              />
            </div>

            <!-- Oil Change Interval -->
            <div class="form-group">
              <label class="flabel">Moy Almashtirish Oralig'i (km)</label>
              <input
                v-model.number="form.oil_change_interval_km"
                type="number"
                class="finput"
                placeholder="Masalan: 5000"
                min="0"
              />
            </div>

            <!-- Policy Date -->
            <div class="form-group">
              <label class="flabel">Sug'urta Amal Qilish Muddati</label>
              <input
                v-model="form.policy_date"
                type="date"
                class="finput"
              />
            </div>

            <!-- Tech Inspection Date -->
            <div class="form-group">
              <label class="flabel">Texnik Ko'rik Muddati</label>
              <input
                v-model="form.tech_inspection_date"
                type="date"
                class="finput"
              />
            </div>

            <!-- Notes -->
            <div class="form-group">
              <label class="flabel">Izoh / Eslatmalari</label>
              <textarea
                v-model="form.notes"
                rows="3"
                class="finput textarea-field"
                placeholder="Qo'shimcha izoh yoki biriktirilgan instruktor ma'lumoti..."
              ></textarea>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
              <button type="submit" class="btn-save" :disabled="saving">
                {{ saving ? "Saqlanmoqda..." : (isEditing ? "Tahrirlashni Saqlash" : "Saqlash") }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- DELETE CONFIRMATION MODAL -->
    <Transition name="modal">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
        <div class="modal-card modal-sm">
          <div class="modal-header-banner red-banner">
            <h3>Avtomobilni O'chirish</h3>
            <button class="btn-modal-close" @click="showDeleteModal = false">✕</button>
          </div>
          <div class="modal-body-pad">
            <p>Haqiqatdan ham <strong>{{ carToDelete?.car_name }}</strong> avtomobilini o'chirmoqchimisiz?</p>
            <div class="modal-footer margin-top">
              <button type="button" class="btn-cancel" @click="showDeleteModal = false">Bekor qilish</button>
              <button type="button" class="btn-delete-confirm" :disabled="deleting" @click="deleteCar">
                {{ deleting ? "O'chirilmoqda..." : "Ha, O'chirish" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const cars = ref([])
const loading = ref(true)

function goToCarDetail(id) {
  if (id) router.push(`/vehicles/${id}`)
}

function goUser(id) {
  if (id) router.push(`/users/${id}`)
}
const totalCount = ref(0)
const searchQuery = ref('')
const filterStatus = ref('')

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const modalError = ref(null)

const showDeleteModal = ref(false)
const carToDelete = ref(null)
const deleting = ref(false)

const form = ref({
  car_name: '',
  status: 'available',
  instructor: null,
  mileage: null,
  oil_change_date: '',
  oil_change_mileage: null,
  oil_change_interval_km: 5000,
  policy_date: '',
  tech_inspection_date: '',
  notes: ''
})

const instructors = ref([])
async function fetchInstructors() {
  try {
    const res = await api.get('/users/', { params: { role: 'instructor', page_size: 1000 } })
    instructors.value = res.data.results || res.data || []
  } catch (err) {
    console.error("Instruktorlarni yuklashda xatolik:", err)
  }
}

// ── Searchable instructor select ──────────────────────
const instructorSearchText = ref('')
const instructorDropdownOpen = ref(false)
const filteredInstructorOptions = computed(() => {
  const q = instructorSearchText.value.trim().toLowerCase()
  if (!q) return instructors.value
  return instructors.value.filter(i =>
    (i.full_name || '').toLowerCase().includes(q) || (i.phone || '').includes(q)
  )
})
function selectInstructor(i) {
  form.value.instructor = i ? i.id : null
  instructorSearchText.value = i ? (i.full_name || i.phone) : ''
  instructorDropdownOpen.value = false
}
function onInstructorBlur() {
  setTimeout(() => { instructorDropdownOpen.value = false }, 150)
}

const availableCarsCount = computed(() => cars.value.filter(c => c.status === 'available').length)
const nonAvailableCarsCount = computed(() => cars.value.filter(c => c.status === 'repairing' || c.status === 'not_available').length)

async function fetchCars() {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value.trim()) {
      params.car_name = searchQuery.value.trim()
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    const res = await api.get('/cars/', { params })
    cars.value = res.data.results || res.data || []
    totalCount.value = res.data.count || cars.value.length
  } catch (err) {
    console.error("Avtomobillarni yuklashda xatolik:", err)
  } finally {
    loading.value = false
  }
}

watch([searchQuery, filterStatus], () => {
  fetchCars()
})

onMounted(() => {
  fetchCars()
  fetchInstructors()
})

function statusText(st) {
  switch (st) {
    case 'available': return 'Mavjud'
    case 'repairing': return 'Ta\'mirlashda'
    case 'not_available': return 'Mavjud emas'
    default: return st || 'Mavjud'
  }
}

function getDateStatus(targetDateStr) {
  if (!targetDateStr) return { status: 'none', label: '-', chipClass: 'chip-gray' }

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const target = new Date(targetDateStr)
  target.setHours(0, 0, 0, 0)

  const diffTime = target - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    const overDays = Math.abs(diffDays)
    return {
      status: 'expired',
      days: overDays,
      label: `Muddati o'tgan (${overDays} kun oldin)`,
      chipClass: 'chip-red'
    }
  } else if (diffDays <= 30) {
    return {
      status: 'near',
      days: diffDays,
      label: diffDays === 0 ? "Bugun tugaydi!" : `${diffDays} kun qoldi (Yaqinlashmoqda)`,
      chipClass: 'chip-yellow'
    }
  } else {
    return {
      status: 'ok',
      days: diffDays,
      label: `${diffDays} kun qoldi`,
      chipClass: 'chip-green'
    }
  }
}

function daysLeftText(dateStatus) {
  if (dateStatus.status === 'expired') return `${dateStatus.days} kun o'tgan`
  if (dateStatus.days === 0) return 'Bugun'
  return `${dateStatus.days} kun`
}

function oilStatus(car) {
  if (car.mileage == null || car.oil_change_mileage == null) {
    return { label: "Noma'lum", chipClass: 'chip-gray' }
  }
  const intervalKm = car.oil_change_interval_km || 5000
  const remaining = intervalKm - (car.mileage - car.oil_change_mileage)
  if (remaining <= 0) return { label: `${Math.abs(remaining)} km o'tgan`, chipClass: 'chip-red' }
  if (remaining <= 500) return { label: `${remaining} km qoldi`, chipClass: 'chip-yellow' }
  return { label: `${remaining} km qoldi`, chipClass: 'chip-green' }
}

function lastWashedText(car) {
  if (!car.last_washed_at) return 'Hali yuvilmagan'
  const d = new Date(car.last_washed_at)
  if (isNaN(d.getTime())) return 'Hali yuvilmagan'
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  return `${day}.${month}.${d.getFullYear()}`
}

const selectedCarFile = ref(null)

function onCarFileChange(e) {
  const file = e.target.files?.[0]
  selectedCarFile.value = file || null
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  modalError.value = null
  selectedCarFile.value = null
  form.value = {
    car_name: '',
    status: 'available',
    instructor: null,
    mileage: null,
    oil_change_date: '',
    oil_change_mileage: null,
    oil_change_interval_km: 5000,
    manufact_year: new Date().getFullYear(),
    policy_date: '',
    tech_inspection_date: '',
    notes: ''
  }
  instructorSearchText.value = ''
  instructorDropdownOpen.value = false
  showModal.value = true
}

function openEditModal(car) {
  isEditing.value = true
  editingId.value = car.id
  modalError.value = null
  selectedCarFile.value = null
  form.value = {
    car_name: car.car_name,
    status: car.status || 'available',
    instructor: car.instructor || null,
    mileage: car.mileage ?? null,
    oil_change_date: car.oil_change_date || '',
    oil_change_mileage: car.oil_change_mileage ?? null,
    oil_change_interval_km: car.oil_change_interval_km ?? 5000,
    manufact_year: car.manufact_year,
    policy_date: car.policy_date || '',
    tech_inspection_date: car.tech_inspection_date || '',
    notes: car.notes || ''
  }
  instructorSearchText.value = car.instructor_name || ''
  instructorDropdownOpen.value = false
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function saveCar() {
  if (!form.value.car_name || !form.value.car_name.trim()) {
    modalError.value = "Avtomobil nomini kiriting."
    return
  }
  saving.value = true
  modalError.value = null

  try {
    const payload = {
      car_name: form.value.car_name.trim(),
      status: form.value.status || 'available',
      instructor: form.value.instructor || null,
      mileage: form.value.mileage !== null && form.value.mileage !== '' ? parseInt(form.value.mileage, 10) : null,
      oil_change_date: form.value.oil_change_date || null,
      oil_change_mileage: form.value.oil_change_mileage !== null && form.value.oil_change_mileage !== '' ? parseInt(form.value.oil_change_mileage, 10) : null,
      oil_change_interval_km: form.value.oil_change_interval_km !== null && form.value.oil_change_interval_km !== '' ? parseInt(form.value.oil_change_interval_km, 10) : 5000,
      manufact_year: form.value.manufact_year ? parseInt(form.value.manufact_year, 10) : null,
      policy_date: form.value.policy_date || null,
      tech_inspection_date: form.value.tech_inspection_date || null,
      notes: form.value.notes ? form.value.notes.trim() : '',
    }

    if (selectedCarFile.value) {
      const formData = new FormData()
      Object.keys(payload).forEach(k => {
        if (payload[k] !== null && payload[k] !== undefined) {
          formData.append(k, payload[k])
        }
      })
      formData.append('image', selectedCarFile.value)
      if (isEditing.value) {
        await api.patch(`/cars/${editingId.value}/`, formData)
      } else {
        await api.post('/cars/', formData)
      }
    } else {
      if (isEditing.value) {
        await api.patch(`/cars/${editingId.value}/`, payload)
      } else {
        await api.post('/cars/', payload)
      }
    }
    closeModal()
    fetchCars()
  } catch (err) {
    console.error("Avtomobilni saqlashda xatolik:", err)
    if (err.response?.data) {
      const data = err.response.data
      if (typeof data === 'object') {
        const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
        modalError.value = msgs.join(' | ')
      } else {
        modalError.value = String(data)
      }
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi."
    }
  } finally {
    saving.value = false
  }
}

function confirmDelete(car) {
  carToDelete.value = car
  showDeleteModal.value = true
}

async function deleteCar() {
  if (!carToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/cars/${carToDelete.value.id}/`)
    showDeleteModal.value = false
    carToDelete.value = null
    fetchCars()
  } catch (err) {
    console.error("Avtomobilni o'chirishda xatolik:", err)
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.page-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.page-main-title { font-size: 22px; font-weight: 800; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }

.btn-primary-action { display: flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #4F46E5, #4338CA); color: white; border: none; padding: 10px 18px; border-radius: 12px; font-weight: 600; font-size: 13.5px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25); }
.btn-primary-action:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35); }

.metrics-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-blue { color: #2563EB; font-weight: 800; }
.text-green { color: #10B981; font-weight: 800; }
.text-orange { color: #EA580C; font-weight: 800; }

.margin-top { margin-top: 24px; }
.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.toolbar-left-controls { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.search-box { display: flex; align-items: center; gap: 10px; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 9px 14px; width: 280px; }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; width: 100%; }

.filter-item { display: flex; align-items: center; gap: 8px; }
.flabel-inline { font-size: 13px; font-weight: 600; color: #4B5563; }
.select-wrap-relative { position: relative; display: inline-block; }
.fselect-field { appearance: none; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 9px 36px 9px 14px; font-size: 13px; font-weight: 600; color: #374151; outline: none; cursor: pointer; }
.fselect-modal-field { appearance: none; background: #FAFAFA; border: 1.5px solid #D1D5DB; border-radius: 10px; padding: 10px 36px 10px 14px; font-size: 13.5px; outline: none; width: 100% !important; box-sizing: border-box !important; }
.select-chevron-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; font-size: 10px; color: #6B7280; }
.total-count { font-size: 13px; color: #6B7280; }

.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }

.car-title { font-weight: 700; color: #1E293B; }
.status-badge-pill { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
.status-badge-pill.available { background: #DCFCE7; color: #15803D; }
.status-badge-pill.repairing { background: #FEF3C7; color: #D97706; }
.status-badge-pill.not_available { background: #FEE2E2; color: #DC2626; }

.year-inline { color: #64748B; font-weight: 600; }
.notes-text { font-size: 12.5px; color: #64748B; }
.instructor-badge { padding: 4px 10px; background: #EEF2FF; color: #4338CA; border-radius: 8px; font-size: 12px; font-weight: 700; white-space: nowrap; }
.link-value { cursor: pointer; }
.link-value:hover { text-decoration: underline; }
.text-muted { color: #9CA3AF; font-size: 12.5px; }

/* DATE STATUS BADGES */
.status-badge { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 12px; line-height: 1.3; }
.days-left-badge { white-space: nowrap; }
.chip-green { background: #DCFCE7; color: #15803D; }
.chip-yellow { background: #FEF3C7; color: #D97706; }
.chip-red { background: #FEE2E2; color: #DC2626; }
.chip-gray { background: #F1F5F9; color: #64748B; }


.row-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-action-edit, .btn-action-delete { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #E5E7EB; background: #F9FAFB; cursor: pointer; transition: all 0.15s ease; }
.btn-action-edit { color: #2563EB; &:hover { background: #EFF6FF; border-color: #BFDBFE; transform: translateY(-1px); } }
.btn-action-delete { color: #EF4444; &:hover { background: #FEE2E2; border-color: #FCA5A5; transform: translateY(-1px); } }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #4F46E5; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* MODAL STYLES & FULL INPUT WIDTH FIX */
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.55); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 520px; max-height: 90vh; overflow: hidden; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.18); display: flex; flex-direction: column; }
.modal-sm { max-width: 420px; }
.modal-header-banner { padding: 18px 24px; display: flex; align-items: center; justify-content: space-between; color: white; flex-shrink: 0; }
.primary-banner { background: linear-gradient(135deg, #4F46E5, #3730A3); }
.red-banner { background: linear-gradient(135deg, #EF4444, #DC2626); }
.header-left-info { display: flex; align-items: center; gap: 14px; }
.header-icon-box { font-size: 24px; }
.header-left-info h3 { font-size: 17px; font-weight: 700; margin: 0; }
.header-left-info p { font-size: 12px; opacity: 0.85; margin-top: 2px; }
.btn-modal-close { background: rgba(255, 255, 255, 0.2); border: none; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; transition: background 0.15s; }
.btn-modal-close:hover { background: rgba(255, 255, 255, 0.35); }

.modal-body { padding: 22px 24px; overflow-y: auto; flex: 1; }
.modal-body-pad { padding: 24px; }
.form-group { margin-bottom: 16px; width: 100%; }
.flabel { display: block; font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.required { &::after { content: " *"; color: #EF4444; } }
.finput { width: 100% !important; box-sizing: border-box !important; padding: 10px 14px; border: 1.5px solid #D1D5DB; border-radius: 10px; font-size: 13.5px; outline: none; transition: border-color 0.15s; background: #FAFAFA; line-height: 1.4; }
.finput:focus { border-color: #4F46E5; background: white; }
.textarea-field { resize: vertical; min-height: 70px; }
.status-select-fixed { height: 42px; }

/* Searchable instructor select */
.searchable-select { position: relative; }
.searchable-dropdown { position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: white; border: 1.5px solid #D1D5DB; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); max-height: 220px; overflow-y: auto; z-index: 20; }
.searchable-option { padding: 9px 14px; font-size: 13.5px; color: #374151; cursor: pointer; }
.searchable-option:hover { background: #F3F4F6; }
.searchable-option.selected { background: #EEF2FF; color: #4338CA; font-weight: 600; }
.searchable-empty { padding: 10px 14px; font-size: 12.5px; color: #9CA3AF; text-align: center; }

.alert-error { padding: 10px 14px; background: #FEE2E2; border-left: 4px solid #EF4444; color: #B91C1C; font-size: 13px; border-radius: 6px; margin-bottom: 16px; }
.modal-footer { display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-top: 22px; }
.btn-cancel { padding: 9px 16px; background: #F3F4F6; color: #4B5563; border-radius: 10px; font-size: 13px; font-weight: 600; border: none; cursor: pointer; }
.btn-save { padding: 9px 20px; background: #4F46E5; color: white; border-radius: 10px; font-size: 13px; font-weight: 600; border: none; cursor: pointer; box-shadow: 0 3px 10px rgba(79, 70, 229, 0.3); }
.btn-save:hover { background: #4338CA; }
.btn-delete-confirm { padding: 9px 20px; background: #DC2626; color: white; border-radius: 10px; font-size: 13px; font-weight: 600; border: none; cursor: pointer; }
.btn-delete-confirm:hover { background: #B91C1C; }
</style>
