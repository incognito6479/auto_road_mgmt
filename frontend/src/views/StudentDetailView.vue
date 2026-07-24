<template>
  <AppLayout>

    <!-- ───────────────────── HEADER ───────────────────── -->
    <div class="detail-header">
      <button class="btn-back" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        Orqaga
      </button>

      <div v-if="student" class="header-info">
        <div class="header-avatar">{{ initials }}</div>
        <div>
          <h1 class="header-name">{{ student.full_name || student.phone }}</h1>
          <div class="header-meta">
            <span class="status-badge" :class="statusClass(activeStatus)">{{ statusText(activeStatus) }}</span>
            <span class="meta-sep">·</span>
            <span class="meta-phone">{{ formatPhone(student.phone) }}</span>
            <template v-if="enrollment?.category_name">
              <span class="meta-sep">·</span>
              <span class="meta-cat">{{ enrollment.category_name }}</span>
            </template>
          </div>
        </div>
      </div>

      <div class="header-actions" v-if="student">
        <button class="btn-payment" v-if="!enrollment?.enrolled_free" @click="openPaymentModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
            <rect x="2" y="5" width="20" height="14" rx="2"/>
            <line x1="2" y1="10" x2="22" y2="10"/>
          </svg>
          To'lov qabul qilish
        </button>
        <button class="btn-edit-main" @click="openEditModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          Tahrirlash
        </button>
      </div>
    </div>

    <!-- LOADING / ERROR -->
    <div v-if="loading" class="state-box">
      <div class="spinner"></div>
      <p>Yuklanmoqda...</p>
    </div>
    <div v-else-if="error" class="state-box state-error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchAll">Qayta urinish</button>
    </div>

    <!-- CONTENT GRID -->
    <div v-else-if="student" class="content-grid">

      <!-- LEFT COLUMN -->
      <div class="col-left">

        <!-- Student Info Card -->
        <div class="detail-card">
          <div class="card-header">
            <span class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </span>
            <h2 class="card-title">Shaxsiy Ma'lumotlar</h2>
          </div>
          <div class="info-grid">
            <div class="info-row"><span class="info-label">To'liq Ismi</span><span class="info-value fw">{{ student.full_name || '-' }}</span></div>
            <div class="info-row"><span class="info-label">Telefon</span><span class="info-value">{{ formatPhone(student.phone) || '-' }}</span></div>
            <div class="info-row" v-if="student.phone2"><span class="info-label">Qo'shimcha tel.</span><span class="info-value">{{ formatPhone(student.phone2) }}</span></div>
            <div class="info-row"><span class="info-label">JSHSHR</span><span class="info-value mono">{{ student.jshshr || '-' }}</span></div>
            <div class="info-row"><span class="info-label">Pasport</span><span class="info-value mono">{{ student.passport_serie || '' }} {{ student.passport_number || '' }}</span></div>
            <div class="info-row"><span class="info-label">Ro'yxatdan o'tgan</span><span class="info-value">{{ formatDate(student.date_joined) }}</span></div>
            <div class="info-row" v-if="student.notes"><span class="info-label">Eslatma</span><span class="info-value">{{ student.notes }}</span></div>
          </div>
        </div>

        <!-- Enrollment Card -->
        <div class="detail-card" v-if="enrollment">
          <div class="card-header">
            <span class="card-icon card-icon-blue">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
            </span>
            <h2 class="card-title">O'quv Ma'lumotlari</h2>
          </div>
          <div class="info-grid">
            <div class="info-row"><span class="info-label">Kategoriya</span><span class="info-value"><span class="cat-badge">{{ enrollment.category_name || '-' }}</span></span></div>
            <div class="info-row"><span class="info-label">Holat</span><span class="info-value"><span class="status-badge" :class="statusClass(activeStatus)">{{ statusText(activeStatus) }}</span></span></div>
            <div class="info-row" v-if="enrollment.instructor_name"><span class="info-label">Instruktor</span><span class="info-value">{{ enrollment.instructor_name }}</span></div>
            <div class="info-row" v-if="enrollment.coordinator_name"><span class="info-label">O'qituvchi</span><span class="info-value">{{ enrollment.coordinator_name }}</span></div>
            <div class="info-row" v-if="enrollment.learning_place_name"><span class="info-label">O'quv joyi</span><span class="info-value">{{ enrollment.learning_place_name }}</span></div>
            <div class="info-row" v-if="enrollment.learning_time"><span class="info-label">O'quv vaqti</span><span class="info-value">{{ enrollment.learning_time }}</span></div>
            <div class="info-row" v-if="enrollment.learning_days"><span class="info-label">O'quv kunlari</span><span class="info-value">{{ formatLearningDays(enrollment.learning_days) }}</span></div>
            <div class="info-row" v-if="enrollment.agent_name"><span class="info-label">Agent</span><span class="info-value">{{ enrollment.agent_name }}</span></div>
            <div class="info-row"><span class="info-label">Shartnoma summasi</span><span class="info-value fw"><span v-if="enrollment.enrolled_free" class="badge-free">Tekin (Bonus)</span><span v-else>{{ formatMoney(enrollment.enrolled_amount) }}</span></span></div>
          </div>
        </div>

        <!-- Group Card -->
        <div class="detail-card">
          <div class="card-header">
            <span class="card-icon card-icon-purple">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </span>
            <h2 class="card-title">Guruh Ma'lumotlari</h2>
          </div>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Guruh nomi</span>
              <span class="info-value fw">{{ group ? group.name : "Biriktirilmagan" }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Kategoriya</span>
              <span class="info-value">{{ group?.category_name || enrollment?.category_name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Boshlanish sanasi</span>
              <span class="info-value">{{ group?.started_at ? formatDate(group.started_at) : '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Davomiylik</span>
              <span class="info-value">{{ group?.duration ? (group.duration + ' oy') : '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Guruh holati</span>
              <span class="info-value">
                <span class="status-badge" :class="group ? groupStatusClass(group.status) : 'badge-notstarted'">
                  {{ group ? groupStatusText(group.status) : 'Boshlanmagan' }}
                </span>
              </span>
            </div>
          </div>
        </div>

      </div>

      <!-- RIGHT COLUMN -->
      <div class="col-right">

        <!-- Payment Summary -->
        <div class="detail-card" v-if="enrollment">
          <div class="card-header">
            <span class="card-icon card-icon-green">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            </span>
            <h2 class="card-title">To'lov Holati</h2>
            <button class="btn-add-payment" v-if="!enrollment?.enrolled_free" @click="openPaymentModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              To'lov
            </button>
          </div>
          <div class="payment-stats">
            <div class="pay-stat"><div class="pay-stat-label">Shartnoma</div><div class="pay-stat-value">{{ enrollment.enrolled_free ? 'Tekin' : formatMoney(enrollment.enrolled_amount) }}</div></div>
            <div class="pay-stat"><div class="pay-stat-label">To'langan</div><div class="pay-stat-value green">{{ formatMoney(paidTotal) }}</div></div>
            <div class="pay-stat"><div class="pay-stat-label">Qoldiq</div><div class="pay-stat-value" :class="remaining > 0 ? 'red' : 'green'">{{ enrollment.enrolled_free ? '—' : formatMoney(remaining) }}</div></div>
          </div>
          <div class="progress-wrap" v-if="!enrollment.enrolled_free && enrollment.enrolled_amount > 0">
            <div class="progress-bar"><div class="progress-fill" :style="{ width: progressPct + '%' }"></div></div>
            <span class="progress-label">{{ progressPct }}%</span>
          </div>
        </div>

        <!-- Payment History -->
        <div class="detail-card">
          <div class="card-header">
            <span class="card-icon card-icon-orange">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </span>
            <h2 class="card-title">To'lovlar Tarixi</h2>
          </div>
          <div v-if="loadingPayments" class="mini-state"><div class="spinner spinner-sm"></div><span>Yuklanmoqda...</span></div>
          <div v-else-if="payments.length === 0" class="mini-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="#D1D5DB" stroke-width="1.5" width="32" height="32"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
            <span>To'lovlar mavjud emas</span>
          </div>
          <div v-else class="pay-table-wrap">
            <table class="pay-table">
              <thead><tr><th>Sana</th><th>Summa</th><th>Usul</th><th>Holat</th><th>Eslatma</th></tr></thead>
              <tbody>
                <tr v-for="p in payments" :key="p.id" class="pay-row">
                  <td class="td-date">{{ formatDateTime(p.created_at) }}</td>
                  <td class="td-amount">{{ formatMoney(p.amount) }}</td>
                  <td><span class="method-badge">{{ methodText(p.method) }}</span></td>
                  <td><span class="pay-status-badge" :class="payStatusClass(p.status)">{{ payStatusText(p.status) }}</span></td>
                  <td class="td-notes">{{ p.notes || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- EDIT MODAL -->
    <dialog ref="editModal" class="modal-dialog" closedby="any">
      <form class="modal-form" @submit.prevent="saveStudent">
        <div class="modal-head">
          <h3 class="modal-title">O'quvchini Tahrirlash</h3>
          <button type="button" class="btn-close" @click="editModal?.close()">✕</button>
        </div>
        <div v-if="editError" class="modal-error">{{ editError }}</div>
        <div class="form-section">
          <div class="section-tag">Shaxsiy Ma'lumotlar</div>
          <div class="form-grid-2">
            <div class="form-group fg-full"><label class="form-label">To'liq Ismi <span class="req">*</span></label><input v-model="editForm.full_name" type="text" class="form-input" placeholder="Ali Valiyev" required/></div>
            <div class="form-group"><label class="form-label">Telefon <span class="req">*</span></label><input v-model="editForm.phone" type="text" class="form-input" placeholder="+998 90 123 45 67" @input="onEditPhoneInput" required/></div>
            <div class="form-group"><label class="form-label">Qo'shimcha Telefon</label><input v-model="editForm.phone2" type="text" class="form-input" placeholder="+998 90 123 45 67" @input="onEditPhone2Input"/></div>
            <div class="form-group"><label class="form-label">JSHSHR</label><input v-model="editForm.jshshr" type="text" maxlength="14" class="form-input mono" placeholder="14 ta raqam"/></div>
            <div class="form-group"><label class="form-label">Pasport Seriyasi</label><input v-model="editForm.passport_serie" type="text" maxlength="2" class="form-input text-upper" placeholder="AA"/></div>
            <div class="form-group"><label class="form-label">Pasport Raqami</label><input v-model="editForm.passport_number" type="text" maxlength="7" class="form-input mono" placeholder="1234567"/></div>
          </div>
        </div>
        <div class="form-section">
          <div class="section-tag">Holat va Eslatmalar</div>
          <div class="form-grid-2">
            <div class="form-group">
              <label class="form-label">Holat</label>
              <div class="select-wrap">
                <select v-model="editForm.status" class="form-input form-select">
                  <option value="new">Yangi</option>
                  <option value="enrolled">Qabul qilingan</option>
                  <option value="finished">Tugatgan</option>
                  <option value="canceled">Bekor qilingan</option>
                </select>
                <svg class="sel-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
              </div>
            </div>
            <div class="form-group fg-full"><label class="form-label">Eslatma</label><textarea v-model="editForm.notes" class="form-input" rows="3" placeholder="Qo'shimcha eslatmalar..."></textarea></div>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="editModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="editSaving"><span v-if="editSaving" class="btn-spinner"></span>{{ editSaving ? 'Saqlanmoqda...' : 'Saqlash' }}</button>
        </div>
      </form>
    </dialog>

    <!-- PAYMENT MODAL -->
    <dialog ref="paymentModal" class="modal-dialog modal-sm" closedby="any">
      <form class="modal-form" @submit.prevent="savePayment">
        <div class="modal-head">
          <h3 class="modal-title">To'lov Qabul Qilish</h3>
          <button type="button" class="btn-close" @click="paymentModal?.close()">✕</button>
        </div>
        <div v-if="payError" class="modal-error">{{ payError }}</div>
        <div class="form-section">
          <div class="pay-remaining-hint" v-if="!enrollment?.enrolled_free">
            Qoldiq: <strong>{{ formatMoney(remaining) }}</strong>
          </div>
          <div class="form-grid-2">
            <div class="form-group fg-full"><label class="form-label">Summa <span class="req">*</span></label><input v-model="payForm.amountFormatted" type="text" class="form-input" placeholder="0" required @input="onPayAmountInput"/></div>
            <div class="form-group">
              <label class="form-label">To'lov usuli</label>
              <div class="select-wrap">
                <select v-model="payForm.method" class="form-input form-select"><option value="cash">Naqd</option><option value="card">Karta</option><option value="qr_code">QR Code</option><option value="transfer">O'tkazma</option></select>
                <svg class="sel-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">To'lov holati</label>
              <div class="select-wrap">
                <select v-model="payForm.status" class="form-input form-select"><option value="accepted">Qabul qilingan</option><option value="paid">To'langan</option><option value="bank">Bank</option></select>
                <svg class="sel-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
              </div>
            </div>
            <div class="form-group fg-full"><label class="form-label">Eslatma</label><input v-model="payForm.notes" type="text" class="form-input" placeholder="Ixtiyoriy..."/></div>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="paymentModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="paySaving"><span v-if="paySaving" class="btn-spinner"></span>{{ paySaving ? 'Saqlanmoqda...' : "To'lovni Saqlash" }}</button>
        </div>
      </form>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const student    = ref(null)
const enrollment = ref(null)
const payments   = ref([])
const group      = ref(null)
const loading    = ref(false)
const loadingPayments = ref(false)
const error      = ref('')

const editModal    = ref(null)
const paymentModal = ref(null)
const editError    = ref('')
const editSaving   = ref(false)
const payError     = ref('')
const paySaving    = ref(false)

const editForm = ref({ full_name: '', phone: '', phone2: '', jshshr: '', passport_serie: '', passport_number: '', status: 'enrolled', notes: '' })
const payForm  = ref({ amountFormatted: '', amount: 0, method: 'cash', status: 'accepted', notes: '' })

const initials = computed(() => {
  const name = student.value?.full_name || ''
  const parts = name.trim().split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  if (parts[0]) return parts[0][0].toUpperCase()
  return '?'
})

const activeStatus = computed(() => {
  return enrollment.value?.status || student.value?.status || 'new'
})

const paidTotal = computed(() =>
  payments.value.filter(p => p.is_active && p.status === 'accepted').reduce((s, p) => s + (p.amount || 0), 0)
)
const remaining = computed(() => {
  if (!enrollment.value || enrollment.value.enrolled_free) return 0
  return Math.max(0, (enrollment.value.enrolled_amount || 0) - paidTotal.value)
})
const progressPct = computed(() => {
  const amt = enrollment.value?.enrolled_amount
  if (!amt) return 0
  return Math.min(100, Math.round((paidTotal.value / amt) * 100))
})

const fetchAll = async () => {
  loading.value = true; error.value = ''
  try {
    const id = route.params.id
    const [sRes, eRes] = await Promise.all([
      api.get(`/students/${id}/`),
      api.get('/enrollments/', { params: { student: id } }),
    ])
    student.value = sRes.data
    const list = Array.isArray(eRes.data) ? eRes.data : (eRes.data.results || [])
    enrollment.value = list.find(e => e.is_active) || list[0] || null
    if (enrollment.value?.group) {
      const gRes = await api.get(`/groups/${enrollment.value.group}/`)
      group.value = gRes.data
    } else {
      group.value = null
    }
    await fetchPayments()
  } catch (err) {
    console.error(err); error.value = "Ma'lumotlarni yuklashda xatolik yuz berdi."
  } finally { loading.value = false }
}

const fetchPayments = async () => {
  if (!student.value) return
  loadingPayments.value = true
  try {
    const studentId = Number(student.value.id)
    const currentEnrollmentId = enrollment.value?.id

    const res = await api.get('/payments/', { params: { student: studentId, page_size: 100 } })
    const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
    
    payments.value = list.filter(p => {
      if (p.status === 'bonus') return false
      if (currentEnrollmentId && (p.enrollment === currentEnrollmentId || p.enrollment_id === currentEnrollmentId)) return true
      if (p.student === studentId || p.student_id === studentId) return true
      return true
    }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (err) { console.error(err) }
  finally { loadingPayments.value = false }
}

const openEditModal = () => {
  const s = student.value
  editForm.value = {
    full_name: s.full_name || '', phone: formatPhone(s.phone),
    phone2: s.phone2 ? formatPhone(s.phone2) : '',
    jshshr: s.jshshr ? String(s.jshshr) : '',
    passport_serie: s.passport_serie || '',
    passport_number: s.passport_number ? String(s.passport_number) : '',
    status: activeStatus.value, notes: s.notes || '',
  }
  editError.value = ''; editModal.value?.showModal()
}

const maskPhone = (val) => {
  let d = val.replace(/\D/g, '')
  if (!d.startsWith('998')) d = d.length === 0 ? '998' : '998' + d
  d = d.slice(0, 12)
  let f = '+' + d.slice(0, 3)
  if (d.length > 3) f += ' ' + d.slice(3, 5)
  if (d.length > 5) f += ' ' + d.slice(5, 8)
  if (d.length > 8) f += ' ' + d.slice(8, 10)
  if (d.length > 10) f += ' ' + d.slice(10, 12)
  return f
}
const onEditPhoneInput  = (e) => { editForm.value.phone  = maskPhone(e.target.value) }
const onEditPhone2Input = (e) => { editForm.value.phone2 = maskPhone(e.target.value) }

const saveStudent = async () => {
  editError.value = ''
  const f = editForm.value
  const phoneCleaned = f.phone.replace(/\D/g, '')
  if (!f.full_name.trim())      { editError.value = "Ism kiritilishi shart."; return }
  if (phoneCleaned.length < 12) { editError.value = "Telefon raqami noto'g'ri."; return }
  editSaving.value = true
  try {
    await api.patch(`/students/${student.value.id}/`, {
      full_name: f.full_name.trim(), phone: phoneCleaned,
      phone2: f.phone2 ? f.phone2.replace(/\D/g, '') : null,
      jshshr: f.jshshr ? parseInt(f.jshshr, 10) : null,
      passport_serie: f.passport_serie ? f.passport_serie.trim().toUpperCase() : null,
      passport_number: f.passport_number ? parseInt(f.passport_number, 10) : null,
      status: f.status, notes: f.notes,
    })
    editModal.value?.close(); await fetchAll()
  } catch (err) { console.error(err); editError.value = "Saqlashda xatolik yuz berdi." }
  finally { editSaving.value = false }
}

const openPaymentModal = () => {
  payForm.value = { amountFormatted: '', amount: 0, method: 'cash', status: 'accepted', notes: '' }
  payError.value = ''; paymentModal.value?.showModal()
}

const onPayAmountInput = (e) => {
  const digits = e.target.value.replace(/\D/g, '')
  payForm.value.amount = digits ? parseInt(digits, 10) : 0
  payForm.value.amountFormatted = digits ? Number(digits).toLocaleString('uz-UZ').replace(/,/g, ' ') : ''
}

const savePayment = async () => {
  payError.value = ''
  if (!payForm.value.amount || payForm.value.amount <= 0) { payError.value = "Summa kiritilishi shart."; return }
  if (!enrollment.value) { payError.value = "O'quvchining aktiv qabuli mavjud emas."; return }
  paySaving.value = true
  try {
    await api.post('/payments/', {
      enrollment: enrollment.value.id, user: authStore.user?.id,
      amount: payForm.value.amount, method: payForm.value.method,
      status: payForm.value.status, notes: payForm.value.notes || null,
    })
    paymentModal.value?.close(); await fetchPayments()
  } catch (err) { console.error(err); payError.value = "To'lovni saqlashda xatolik yuz berdi." }
  finally { paySaving.value = false }
}

const formatPhone = (p) => {
  if (!p) return ''; const d = String(p).replace(/\D/g, '')
  if (d.length === 12) return `+${d.slice(0,3)} ${d.slice(3,5)} ${d.slice(5,8)} ${d.slice(8,10)} ${d.slice(10,12)}`
  return p
}
const formatDate = (d) => {
  if (!d) return '-'; const dt = new Date(d); if (isNaN(dt)) return d
  return `${String(dt.getDate()).padStart(2,'0')}.${String(dt.getMonth()+1).padStart(2,'0')}.${dt.getFullYear()}`
}
const formatDateTime = (d) => {
  if (!d) return '-'; const dt = new Date(d); if (isNaN(dt)) return d
  return `${String(dt.getDate()).padStart(2,'0')}.${String(dt.getMonth()+1).padStart(2,'0')}.${dt.getFullYear()} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
}
const formatMoney = (n) => {
  if (n == null) return "0 so'm"
  return Number(n).toLocaleString('uz-UZ').replace(/,/g, ' ') + " so'm"
}
const formatLearningDays = (d) => {
  if (d === 'Mo-Wed-Fri') return 'Dush – Chor – Juma'
  if (d === 'Tue-Thu-Sat') return 'Sesh – Pay – Shan'
  if (d === 'everyday') return "Har kuni"
  return d || '-'
}
const statusText  = (s) => ({ new: 'Yangi', enrolled: 'Qabul qilingan', finished: 'Tugatgan', canceled: 'Bekor qilingan' }[s] || s || '-')
const statusClass = (s) => ({ new: 'badge-new', enrolled: 'badge-enrolled', finished: 'badge-done', canceled: 'badge-canceled' }[s] || '')
const groupStatusText  = (s) => ({ started: 'Boshlangan', finished: 'Tugatgan', canceled: 'Bekor qilingan' }[s] || s || '-')
const groupStatusClass = (s) => ({ started: 'badge-enrolled', finished: 'badge-done', canceled: 'badge-canceled' }[s] || '')
const payStatusText  = (s) => ({ accepted: 'Qabul qilingan', paid: "To'langan", returned: 'Qaytarilgan', bonus: 'Bonus', bank: 'Bank' }[s] || s || '-')
const payStatusClass = (s) => ({ accepted: 'pstatus-accepted', paid: 'pstatus-paid', returned: 'pstatus-returned', bonus: 'pstatus-bonus', bank: 'pstatus-bank' }[s] || '')
const methodText = (m) => ({ cash: 'Naqd', card: 'Karta', qr_code: 'QR', transfer: "O'tkazma" }[m] || m || '-')

onMounted(async () => {
  if (!authStore.user) await authStore.fetchCurrentUser()
  await fetchAll()

  // Setup light dismiss for dialogs
  const dialogs = [editModal.value, paymentModal.value]
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
        if (!isInside) dialog.close()
      })
    }
  })
})
</script>

<style scoped>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
button{cursor:pointer;background:none;border:none;font-family:inherit}

.btn-back{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:8px;font-size:13.5px;font-weight:500;color:#374151;background:white;border:1px solid #E5E7EB;transition:background 0.15s,border-color 0.15s}
.btn-back:hover{background:#F9FAFB;border-color:#D1D5DB}

.detail-header{display:flex;align-items:center;gap:16px;margin-bottom:24px;flex-wrap:wrap}
.header-info{display:flex;align-items:center;gap:14px;flex:1}
.header-avatar{width:48px;height:48px;border-radius:14px;background:linear-gradient(135deg,#2D6A4F,#52B788);color:white;font-weight:800;font-size:17px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 4px 12px rgba(45,106,79,0.25)}
.header-name{font-size:20px;font-weight:700;color:#111827;line-height:1.2}
.header-meta{display:flex;align-items:center;gap:8px;margin-top:4px;flex-wrap:wrap}
.meta-sep{color:#D1D5DB;font-size:12px}
.meta-phone{font-size:13px;color:#6B7280;font-weight:500}
.meta-cat{font-size:13px;color:#374151;font-weight:600}
.header-actions{display:flex;gap:10px;flex-shrink:0}

.btn-edit-main{display:inline-flex;align-items:center;gap:6px;padding:10px 16px;border-radius:8px;font-size:13.5px;font-weight:600;color:#374151;background:white;border:1px solid #E5E7EB;transition:background 0.15s,border-color 0.15s}
.btn-edit-main:hover{background:#F9FAFB;border-color:#D1D5DB}
.btn-payment{display:inline-flex;align-items:center;gap:6px;padding:10px 18px;border-radius:8px;font-size:13.5px;font-weight:600;color:white;background:#2D6A4F;transition:background 0.15s;box-shadow:0 2px 8px rgba(45,106,79,0.25)}
.btn-payment:hover{background:#1B4332}

.state-box{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:60px 20px;color:#6B7280;font-size:14px}
.state-error{color:#EF4444}
.btn-retry{padding:8px 16px;border-radius:8px;background:#EF4444;color:white;font-size:13.5px;font-weight:600;cursor:pointer}

.content-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
@media(max-width:900px){.content-grid{grid-template-columns:1fr}}
.col-left,.col-right{display:flex;flex-direction:column;gap:20px}

.detail-card{background:white;border-radius:14px;border:1px solid #E5E7EB;box-shadow:0 1px 4px rgba(0,0,0,0.05);overflow:hidden}
.card-header{display:flex;align-items:center;gap:10px;padding:16px 20px 14px;border-bottom:1px solid #F3F4F6}
.card-icon{width:30px;height:30px;border-radius:8px;background:#ECFDF5;color:#2D6A4F;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.card-icon-blue{background:#EFF6FF;color:#3B82F6}
.card-icon-green{background:#ECFDF5;color:#2D6A4F}
.card-icon-purple{background:#F5F3FF;color:#7C3AED}
.card-icon-orange{background:#FFF7ED;color:#EA580C}
.card-title{font-size:14px;font-weight:700;color:#111827;flex:1}
.btn-add-payment{display:inline-flex;align-items:center;gap:4px;padding:5px 12px;border-radius:6px;font-size:12.5px;font-weight:600;color:#2D6A4F;background:#ECFDF5;border:1px solid #A7F3D0;transition:background 0.15s}
.btn-add-payment:hover{background:#D1FAE5}

.info-grid{padding:4px 0 8px}
.info-row{display:flex;align-items:flex-start;gap:12px;padding:10px 20px;border-bottom:1px solid #F9FAFB}
.info-row:last-child{border-bottom:none}
.info-label{font-size:12.5px;font-weight:600;color:#6B7280;width:150px;flex-shrink:0;padding-top:1px}
.info-value{font-size:13.5px;color:#1F2937;flex:1;line-height:1.5}
.info-value.fw{font-weight:600}
.info-value.mono{font-family:monospace}

.status-badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;letter-spacing:.02em}
.badge-new{background:#FEF9C3;color:#92400E}
.badge-enrolled{background:#D1FAE5;color:#065F46}
.badge-done{background:#E0E7FF;color:#3730A3}
.badge-canceled{background:#FEE2E2;color:#991B1B}
.badge-notstarted{background:#F3F4F6;color:#6B7280}
.badge-free{background:#D1FAE5;color:#065F46;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600}
.cat-badge{display:inline-block;padding:3px 10px;background:#1B2430;color:white;border-radius:20px;font-size:12px;font-weight:700;letter-spacing:.04em}

.payment-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#F3F4F6;border-bottom:1px solid #F3F4F6}
.pay-stat{background:white;padding:16px 18px;text-align:center}
.pay-stat-label{font-size:11.5px;color:#9CA3AF;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}
.pay-stat-value{font-size:16px;font-weight:700;color:#111827}
.pay-stat-value.green{color:#2D6A4F}
.pay-stat-value.red{color:#EF4444}
.progress-wrap{display:flex;align-items:center;gap:10px;padding:14px 20px}
.progress-bar{flex:1;height:8px;background:#F3F4F6;border-radius:99px;overflow:hidden}
.progress-fill{height:100%;background:linear-gradient(90deg,#52B788,#2D6A4F);border-radius:99px;transition:width 0.5s ease}
.progress-label{font-size:12px;font-weight:700;color:#2D6A4F;width:36px;text-align:right}

.mini-state{display:flex;align-items:center;justify-content:center;gap:10px;padding:32px;color:#9CA3AF;font-size:13.5px;flex-direction:column}
.pay-table-wrap{overflow-x:auto}
.pay-table{width:100%;border-collapse:collapse;font-size:13px}
.pay-table th{padding:10px 16px;background:#F9FAFB;color:#6B7280;font-weight:600;font-size:12px;text-align:left;border-bottom:1px solid #E5E7EB;white-space:nowrap}
.pay-table td{padding:11px 16px;border-bottom:1px solid #F3F4F6;color:#1F2937;vertical-align:middle}
.pay-row:last-child td{border-bottom:none}
.pay-row:hover td{background:#FAFAFA}
.td-date{color:#6B7280;font-size:12.5px;white-space:nowrap}
.td-amount{font-weight:700;color:#2D6A4F;white-space:nowrap}
.td-notes{color:#6B7280;font-size:12.5px;max-width:120px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.method-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11.5px;font-weight:600;background:#F3F4F6;color:#374151}
.pay-status-badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11.5px;font-weight:600}
.pstatus-accepted{background:#D1FAE5;color:#065F46}
.pstatus-paid{background:#DBEAFE;color:#1D4ED8}
.pstatus-returned{background:#FEE2E2;color:#991B1B}
.pstatus-bonus{background:#FEF9C3;color:#92400E}
.pstatus-bank{background:#F5F3FF;color:#5B21B6}

.spinner{width:32px;height:32px;border:3px solid #E5E7EB;border-top-color:#2D6A4F;border-radius:50%;animation:spin 0.7s linear infinite}
.spinner-sm{width:16px;height:16px;border-width:2px}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── Perfectly Centered Dialogs ── */
.modal-dialog{
  border:none;
  border-radius:16px;
  padding:0;
  width:90%;
  max-width:640px;
  box-shadow:0 20px 60px rgba(0,0,0,0.22);
  overflow:hidden;
  position:fixed;
  top:50%;
  left:50%;
  transform:translate(-50%, -50%);
  margin:0;
}
.modal-dialog.modal-sm{max-width:480px}
.modal-dialog::backdrop{background:rgba(17,24,39,0.5);backdrop-filter:blur(3px)}
.modal-form{display:flex;flex-direction:column}
.modal-head{display:flex;align-items:center;justify-content:space-between;padding:20px 24px 16px;border-bottom:1px solid #F3F4F6}
.modal-title{font-size:17px;font-weight:700;color:#111827}
.btn-close{width:30px;height:30px;border-radius:50%;background:#F3F4F6;color:#6B7280;font-size:13px;display:flex;align-items:center;justify-content:center;transition:background 0.15s}
.btn-close:hover{background:#E5E7EB}
.modal-error{margin:12px 24px 0;padding:10px 14px;background:#FEE2E2;border-radius:8px;color:#991B1B;font-size:13px;font-weight:500}
.form-section{padding:18px 24px 4px}
.section-tag{font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#2D6A4F;display:flex;align-items:center;gap:8px;margin-bottom:14px}
.section-tag::after{content:'';flex:1;height:1px;background:#E5E7EB}
.form-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.form-group{display:flex;flex-direction:column;gap:6px}
.fg-full{grid-column:span 2}
.form-label{font-size:12.5px;font-weight:600;color:#374151}
.req{color:#EF4444}
.form-input{width:100%;padding:9px 12px;font-size:13.5px;border:1.5px solid #D1D5DB;border-radius:10px;outline:none;background:#F9FAFB;color:#111827;font-family:inherit;transition:border-color 0.2s,background 0.2s,box-shadow 0.2s}
.form-input:focus{border-color:#2D6A4F;background:white;box-shadow:0 0 0 3px rgba(45,106,79,0.1)}
.form-input.mono{font-family:monospace}
.form-input.text-upper{text-transform:uppercase}
.form-select{appearance:none;-webkit-appearance:none;padding-right:32px}
.select-wrap{position:relative}
.sel-arrow{position:absolute;right:10px;top:50%;transform:translateY(-50%);pointer-events:none;color:#6B7280}
textarea.form-input{resize:vertical;min-height:80px}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;padding:16px 24px 20px;border-top:1px solid #F3F4F6;margin-top:8px}
.btn-cancel{padding:10px 18px;border-radius:8px;font-size:13.5px;font-weight:600;color:#374151;background:#F9FAFB;border:1px solid #E5E7EB;transition:background 0.15s}
.btn-cancel:hover{background:#F3F4F6}
.btn-save{display:inline-flex;align-items:center;gap:6px;padding:10px 22px;border-radius:8px;font-size:13.5px;font-weight:600;color:white;background:#2D6A4F;transition:background 0.15s;box-shadow:0 2px 6px rgba(45,106,79,0.25)}
.btn-save:hover:not(:disabled){background:#1B4332}
.btn-save:disabled{opacity:.6;cursor:not-allowed}
.btn-spinner{display:inline-block;width:13px;height:13px;border:2px solid rgba(255,255,255,0.4);border-top-color:white;border-radius:50%;animation:spin 0.7s linear infinite}
.pay-remaining-hint{padding:10px 14px;background:#ECFDF5;border-radius:8px;color:#065F46;font-size:13px;font-weight:500;margin-bottom:14px}
</style>
