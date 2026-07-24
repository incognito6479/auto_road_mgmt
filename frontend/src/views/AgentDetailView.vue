<template>
  <AppLayout>

    <!-- Top Navigation & Action Bar -->
    <div class="page-top">
      <div class="top-left">
        <button class="btn-back" @click="goBack" title="Orqaga">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          <span>Agentlar ro'yxatiga qaytish</span>
        </button>
        <h2 class="page-main-title">{{ agent?.full_name || 'Agent Ma\'lumotlari' }}</h2>
      </div>

      <button v-if="authStore.isStaff && agent" class="btn-edit-profile" @click="openEditAgentModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" style="margin-right: 6px;">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
        <span>Agentni Tahrirlash</span>
      </button>
    </div>

    <!-- Loading / Error States -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Agent ma'lumotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchAll">Qayta urinish</button>
    </div>

    <div v-else-if="agent" class="detail-container">

      <!-- Profile Overview Card -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-large">
            {{ agentInitials }}
          </div>
          <div class="profile-identity">
            <h3 class="profile-name">{{ agent.full_name }}</h3>
            <span class="agent-chip">Agent / Hamkor</span>
          </div>
        </div>

        <div class="profile-grid">
          <div class="info-item">
            <span class="info-label">Telefon Raqami</span>
            <span class="info-value font-semibold">{{ formatPhone(agent.phone) }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Qo'shimcha Telefon</span>
            <span class="info-value">{{ formatPhone(agent.phone2) || '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Ro'yxatdan o'tgan sana</span>
            <span class="info-value">{{ formatDate(agent.created_at) }}</span>
          </div>
        </div>

        <div v-if="agent.notes" class="notes-block">
          <span class="info-label">Izoh / Eslatma:</span>
          <p class="notes-text">{{ agent.notes }}</p>
        </div>
      </div>

      <!-- Bonus Metrics Cards Grid -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
            </svg>
          </div>
          <div>
            <span class="metric-label">Jalb Etilgan O'quvchilar</span>
            <h4 class="metric-value">{{ enrollments.length }} ta qabul</h4>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon gold">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
          <div>
            <span class="metric-label">Bonus Berilgan Qabullar</span>
            <h4 class="metric-value bonus-val">{{ bonusPaidCount }} ta qabul</h4>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
          <div>
            <span class="metric-label">Bonus Kutilmoqda</span>
            <h4 class="metric-value warning-text">{{ bonusPendingCount }} ta qabul</h4>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
          </div>
          <div>
            <span class="metric-label">Jami Berilgan Bonuslar Summasi</span>
            <h4 class="metric-value font-bold text-amber">{{ formatMoney(totalBonusSum) }} so'm</h4>
          </div>
        </div>
      </div>

      <!-- ATTRACTED STUDENTS & BONUS PAYMENTS TABLE -->
      <div class="section-container">
        <div class="section-title-wrap">
          <h3 class="section-title">👥 Jalb Qilingan O'quvchilar va Bonus To'lovlari</h3>
          <span class="section-badge">{{ enrollmentsWithBonus.length }} ta qabul</span>
        </div>

        <div v-if="loadingEnrollments" class="state-container">
          <div class="spinner"></div>
          <p class="state-text">O'quvchilar ro'yxati va bonus to'lovlari yuklanmoqda...</p>
        </div>

        <div v-else-if="enrollmentsWithBonus.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="36" height="36">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
            </svg>
          </div>
          <p class="empty-title">O'quvchilar topilmadi</p>
          <p class="empty-sub">Ushbu agent orqali biriktirilgan o'quvchilar mavjud emas.</p>
        </div>

        <div v-else class="table-card">
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>O'quvchi F.I.SH.</th>
                  <th>Telefon & JSHSHR</th>
                  <th>Kategoriya & Guruh</th>
                  <th>Shartnoma Summasi</th>
                  <th>Qabul Sanasi</th>
                  <th style="min-width: 240px;">Bonus Holati & To'lov</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in enrollmentsWithBonus" :key="item.id" class="table-row">
                  <td class="td-name">
                    <router-link :to="`/students/${item.student}`" class="student-link">
                      {{ item.student_name || 'Noma\'lum' }}
                    </router-link>
                  </td>
                  <td class="td-contact">
                    <div class="phone-val">{{ formatPhone(item.student_phone) }}</div>
                    <div v-if="item.student_jshshr" class="jshshr-val">JSHSHR: {{ item.student_jshshr }}</div>
                  </td>
                  <td class="td-cat">
                    <div class="cat-pill-wrap">
                      <span class="cat-badge">{{ item.category_name || '-' }}</span>
                      <span v-if="item.group_name" class="group-pill">{{ item.group_name }}</span>
                    </div>
                  </td>
                  <td class="td-amount">
                    <span v-if="item.enrolled_free" class="grant-pill">Bepul (Grant)</span>
                    <span v-else class="amount-val">{{ formatMoney(item.enrolled_amount) }} so'm</span>
                  </td>
                  <td class="td-date">{{ formatDate(item.created_at) }}</td>

                  <!-- BONUS PAYMENT STATUS & ACTION -->
                  <td class="td-bonus-action">
                    <!-- IF BONUS PAYMENT EXISTS -->
                    <div v-if="item.bonusPayment" class="bonus-paid-box">
                      <div class="bonus-badge-paid">
                        <span class="bonus-icon">🎁</span>
                        <span class="bonus-amount-text">{{ formatMoney(item.bonusPayment.amount) }} so'm</span>
                        <span class="bonus-chip-tag">Bonus to'langan</span>
                      </div>
                      <div class="bonus-meta">
                        <span>{{ methodText(item.bonusPayment.method) }}</span>
                        <span>•</span>
                        <span>{{ formatDate(item.bonusPayment.created_at) }}</span>
                        <span v-if="item.bonusPayment.cashier_name">• {{ item.bonusPayment.cashier_name }}</span>
                      </div>
                    </div>

                    <!-- IF NO BONUS PAYMENT EXISTS -->
                    <div v-else class="bonus-pending-box">
                      <span class="bonus-chip-unpaid">Bonus to'lanmagan</span>
                      <button 
                        v-if="authStore.isStaff"
                        class="btn-pay-bonus" 
                        @click="openPayBonusModal(item)"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                          <line x1="12" y1="5" x2="12" y2="19"></line>
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        <span>To'lov qilish</span>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    <!-- PAY BONUS MODAL -->
    <Transition name="modal">
      <div v-if="showPayModal" class="modal-overlay" @click.self="closePayModal">
        <div class="modal-card">
          <div class="modal-header-banner bonus-banner">
            <div class="modal-header-left">
              <div class="header-icon-box gold-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
              </div>
              <div>
                <h3 class="modal-title-text">Agentga Bonus To'lovini Amalga Oshirish</h3>
                <p class="modal-subtitle-text">Tanlangan o'quvchi uchun agentga bonus summasi to'lanadi</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closePayModal" title="Yopish">✕</button>
          </div>

          <form @submit.prevent="submitBonusPayment" class="modal-form-body">
            <div v-if="payModalError" class="modal-error-alert">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="flex-shrink: 0;">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{{ payModalError }}</span>
            </div>

            <!-- Target Student & Enrollment Info Card -->
            <div v-if="selectedEnrollment" class="target-info-card">
              <div class="target-card-header">
                <div class="target-avatar">
                  {{ selectedEnrollment.student_name?.[0] || 'O' }}
                </div>
                <div class="target-student-meta">
                  <h4 class="target-student-name">{{ selectedEnrollment.student_name }}</h4>
                  <span class="target-cat-tag">{{ selectedEnrollment.category_name }} {{ selectedEnrollment.group_name ? `(${selectedEnrollment.group_name})` : '' }}</span>
                </div>
              </div>
              <div class="target-card-footer">
                <span class="target-label">Hamkor Agent:</span>
                <span class="target-agent-name">👤 {{ agent?.full_name }}</span>
              </div>
            </div>

            <!-- Bonus Amount Input -->
            <div class="form-field-group">
              <label class="field-label required">Bonus Summasi *</label>
              <div class="input-with-addon">
                <div class="input-icon-left">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" width="18" height="18">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                  </svg>
                </div>
                <input 
                  v-model="payForm.amountFormatted" 
                  type="text" 
                  class="field-input amount-field input-has-icon" 
                  placeholder="0" 
                  required 
                  @input="onBonusAmountInput"
                />
                <span class="input-addon-right">so'm</span>
              </div>
            </div>

            <!-- Payment Method Select -->
            <div class="form-field-group">
              <label class="field-label required">To'lov Usuli *</label>
              <div class="select-field-wrap">
                <div class="input-icon-left">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" width="18" height="18">
                    <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                    <line x1="1" y1="10" x2="23" y2="10"></line>
                  </svg>
                </div>
                <select v-model="payForm.method" class="field-input field-select select-has-icon">
                  <option value="cash">💵 Naqd pulli to'lov</option>
                  <option value="card">💳 Plastik karta</option>
                  <option value="transfer">🏦 Bank o'tkazmasi</option>
                  <option value="qr_code">📱 QR Code to'lovi</option>
                </select>
                <div class="select-chevron">
                  <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
            </div>

            <!-- Notes Input -->
            <div class="form-field-group">
              <label class="field-label">Izoh / Eslatma</label>
              <div class="input-with-addon">
                <div class="input-icon-left">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" width="18" height="18">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </div>
                <input v-model="payForm.notes" type="text" class="field-input input-has-icon" placeholder="Masalan: Ushbu o'quvchi uchun berilgan bonus..." />
              </div>
            </div>

            <div class="modal-footer-actions">
              <button type="button" class="btn-modal-cancel" @click="closePayModal">Bekor qilish</button>
              <button type="submit" class="btn-modal-submit gold-btn" :disabled="paySaving">
                <div v-if="paySaving" class="btn-spinner"></div>
                <span>{{ paySaving ? "To'lov saqlanmoqda..." : "🎁 Bonusni To'lash" }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- EDIT AGENT MODAL -->
    <Transition name="modal">
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditAgentModal">
        <div class="modal-card">
          <div class="modal-header-banner">
            <div class="modal-header-left">
              <div class="header-icon-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                </svg>
              </div>
              <div>
                <h3 class="modal-title-text">Agent Ma'lumotlarini Tahrirlash</h3>
                <p class="modal-subtitle-text">Hamkor agent ma'lumotlarini yangilang</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeEditAgentModal" title="Yopish">✕</button>
          </div>

          <form @submit.prevent="saveAgent" class="modal-form-body">
            <div v-if="editModalError" class="modal-error-alert">
              <span>{{ editModalError }}</span>
            </div>

            <div class="form-field-group">
              <label class="field-label required">Agent F.I.SH.</label>
              <input v-model="editForm.full_name" type="text" class="field-input" required />
            </div>

            <div class="form-two-cols">
              <div class="form-field-group">
                <label class="field-label required">Telefon raqami</label>
                <input v-model="editForm.phone" type="text" class="field-input" required />
              </div>

              <div class="form-field-group">
                <label class="field-label">Qo'shimcha telefon</label>
                <input v-model="editForm.phone2" type="text" class="field-input" />
              </div>
            </div>

            <div class="form-field-group">
              <label class="field-label">Izoh / Eslatma</label>
              <textarea v-model="editForm.notes" rows="3" class="field-input field-textarea"></textarea>
            </div>

            <div class="modal-footer-actions">
              <button type="button" class="btn-modal-cancel" @click="closeEditAgentModal">Bekor qilish</button>
              <button type="submit" class="btn-modal-submit" :disabled="editSaving">
                <div v-if="editSaving" class="btn-spinner"></div>
                <span>{{ editSaving ? 'Saqlanmoqda...' : 'Saqlash' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatMoney, formatPhone, formatDate } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const agent = ref(null)
const loading = ref(true)
const error = ref(null)

const enrollments = ref([])
const bonusPayments = ref([])
const loadingEnrollments = ref(false)

// Pay Bonus Modal state
const showPayModal = ref(false)
const selectedEnrollment = ref(null)
const payModalError = ref(null)
const paySaving = ref(false)
const payForm = ref({
  amountFormatted: '',
  amount: 0,
  method: 'cash',
  notes: ''
})

// Edit Agent Modal state
const showEditModal = ref(false)
const editSaving = ref(false)
const editModalError = ref(null)
const editForm = ref({
  full_name: '',
  phone: '',
  phone2: '',
  notes: ''
})

const agentInitials = computed(() => {
  if (!agent.value || !agent.value.full_name) return 'A'
  const parts = agent.value.full_name.trim().split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return agent.value.full_name.slice(0, 2).toUpperCase()
})

const totalBonusSum = computed(() => {
  return bonusPayments.value.reduce((acc, p) => acc + (Number(p.amount) || 0), 0)
})

const enrollmentsWithBonus = computed(() => {
  return enrollments.value.map(e => {
    // Find matching bonus payment for this enrollment or student
    const bp = bonusPayments.value.find(p => 
      p.enrollment === e.id || p.enrollment_id === e.id || p.student === e.student || p.student_id === e.student
    )
    return {
      ...e,
      bonusPayment: bp || null
    }
  })
})

const bonusPaidCount = computed(() => {
  return enrollmentsWithBonus.value.filter(e => e.bonusPayment != null).length
})

const bonusPendingCount = computed(() => {
  return enrollmentsWithBonus.value.filter(e => e.bonusPayment == null).length
})

function goBack() {
  router.push('/agents')
}

async function fetchAll() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/agents/${route.params.id}/`)
    agent.value = res.data
    await fetchAgentEnrollmentsAndPayments()
  } catch (err) {
    console.error(err)
    error.value = "Agent ma'lumotlarini yuklashda xatolik"
  } finally {
    loading.value = false
  }
}

async function fetchAgentEnrollmentsAndPayments() {
  loadingEnrollments.value = true
  try {
    const [eRes, pRes] = await Promise.all([
      api.get('/enrollments/', { params: { agent: route.params.id, page_size: 200 } }),
      api.get('/payments/', { params: { agent: route.params.id, status: 'bonus', page_size: 200 } })
    ])
    enrollments.value = eRes.data.results ? eRes.data.results : eRes.data
    bonusPayments.value = pRes.data.results ? pRes.data.results : pRes.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingEnrollments.value = false
  }
}

function methodText(m) {
  switch (m) {
    case 'cash': return 'Naqd pulli'
    case 'card': return 'Karta orqali'
    case 'qr_code': return 'QR Code'
    case 'transfer': return 'Bank o\'tkazmasi'
    default: return m
  }
}

// Bonus amount formatting on input
function onBonusAmountInput(e) {
  const val = e.target.value
  const digits = val.replace(/\D/g, '')
  if (!digits) {
    payForm.value.amount = 0
    payForm.value.amountFormatted = ''
    return
  }
  const num = parseInt(digits, 10)
  payForm.value.amount = num
  payForm.value.amountFormatted = formatMoney(num)
}

// Open Pay Bonus Modal for specific student enrollment
function openPayBonusModal(item) {
  selectedEnrollment.value = item
  payModalError.value = null
  payForm.value = {
    amountFormatted: '',
    amount: 0,
    method: 'cash',
    notes: ''
  }
  showPayModal.value = true
}

function closePayModal() {
  showPayModal.value = false
  selectedEnrollment.value = null
}

async function submitBonusPayment() {
  if (!payForm.value.amount || payForm.value.amount <= 0) {
    payModalError.value = "Iltimos, to'g'ri bonus summasini kiriting."
    return
  }

  paySaving.value = true
  payModalError.value = null
  try {
    await api.post('/payments/', {
      enrollment: selectedEnrollment.value.id,
      agent: agent.value.id,
      amount: payForm.value.amount,
      method: payForm.value.method,
      status: 'bonus',
      notes: payForm.value.notes || `Bonus payment for ${selectedEnrollment.value.student_name}`
    })

    closePayModal()
    await fetchAgentEnrollmentsAndPayments()
  } catch (err) {
    console.error(err)
    payModalError.value = err.response?.data?.detail || "Bonus to'lovini saqlashda xatolik yuz berdi."
  } finally {
    paySaving.value = false
  }
}

function openEditAgentModal() {
  editModalError.value = null
  editForm.value = {
    full_name: agent.value.full_name || '',
    phone: agent.value.phone || '',
    phone2: agent.value.phone2 || '',
    notes: agent.value.notes || ''
  }
  showEditModal.value = true
}

function closeEditAgentModal() {
  showEditModal.value = false
}

async function saveAgent() {
  if (!editForm.value.full_name.trim() || !editForm.value.phone.trim()) {
    editModalError.value = "Barcha majburiy maydonlarni to'ldiring."
    return
  }

  editSaving.value = true
  editModalError.value = null
  try {
    const res = await api.patch(`/agents/${agent.value.id}/`, editForm.value)
    agent.value = res.data
    closeEditAgentModal()
  } catch (err) {
    editModalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    editSaving.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchAll()
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
  color: #6B7280;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;

  &:hover {
    color: #2D6A4F;
  }
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
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.25);
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(45, 106, 79, 0.35);
  }
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 0;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #E5E7EB;
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F3F4F6;
}

.avatar-large {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(45, 106, 79, 0.25);
}

.profile-name {
  font-size: 19px;
  font-weight: 700;
  color: #111827;
}

.agent-chip {
  display: inline-block;
  padding: 3px 10px;
  background: #F0FDF4;
  color: #2D6A4F;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
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
  color: #111827;
}

.notes-block {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #F3F4F6;
}

.notes-text {
  font-size: 13.5px;
  color: #4B5563;
  background: #F9FAFB;
  padding: 10px 14px;
  border-radius: 8px;
  border-left: 3px solid #2D6A4F;
  margin-top: 6px;
}

/* Bonus Metrics Cards */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.green { background: #E8F5E9; color: #2D6A4F; }
  &.gold { background: #FEF3C7; color: #D97706; }
  &.orange { background: #FFF7ED; color: #EA580C; }
  &.purple { background: #F3E8FF; color: #9333EA; }
}

.metric-label {
  font-size: 12px;
  color: #6B7280;
  font-weight: 500;
  display: block;
}

.metric-value {
  font-size: 19px;
  font-weight: 700;
  color: #111827;
  margin-top: 2px;

  &.bonus-val { color: #D97706; }
  &.warning-text { color: #EA580C; }
  &.text-amber { color: #B45309; }
}

/* Table Section */
.section-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 17px;
  font-weight: 700;
  color: #111827;
}

.section-badge {
  font-size: 12.5px;
  font-weight: 600;
  color: #2D6A4F;
  background: #E8F5E9;
  padding: 4px 12px;
  border-radius: 20px;
}

.table-card {
  background: white;
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;

  th {
    background: #F9FAFB;
    padding: 12px 18px;
    font-size: 12px;
    font-weight: 600;
    color: #4B5563;
    text-align: left;
    border-bottom: 1px solid #E5E7EB;
  }

  td {
    padding: 14px 18px;
    font-size: 13.5px;
    color: #1F2937;
    border-bottom: 1px solid #F3F4F6;
    vertical-align: middle;
  }

  tr:last-child td {
    border-bottom: none;
  }
}

.student-link {
  color: #2D6A4F;
  font-weight: 700;
  text-decoration: none;

  &:hover { text-decoration: underline; }
}

.phone-val { font-size: 13.5px; font-weight: 600; color: #374151; }
.jshshr-val { font-size: 11.5px; color: #6B7280; margin-top: 2px; }

.cat-pill-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.cat-badge {
  padding: 3px 8px;
  background: #E8F5E9;
  color: #2D6A4F;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
}

.group-pill {
  padding: 3px 8px;
  background: #EFF6FF;
  color: #2563EB;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.grant-pill {
  padding: 3px 8px;
  background: #F3E8FF;
  color: #9333EA;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.amount-val { font-weight: 600; color: #111827; }

/* Bonus Status Action Column */
.bonus-paid-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bonus-badge-paid {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #FEF3C7;
  border: 1px solid #FDE68A;
  padding: 6px 12px;
  border-radius: 10px;
}

.bonus-icon { font-size: 15px; }

.bonus-amount-text {
  font-weight: 800;
  color: #92400E;
  font-size: 14px;
}

.bonus-chip-tag {
  font-size: 11px;
  font-weight: 700;
  color: #B45309;
  background: white;
  padding: 2px 6px;
  border-radius: 6px;
}

.bonus-meta {
  font-size: 11.5px;
  color: #78350F;
  display: flex;
  gap: 6px;
  margin-left: 2px;
}

.bonus-pending-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bonus-chip-unpaid {
  display: inline-block;
  padding: 4px 10px;
  background: #FFF7ED;
  color: #C2410C;
  border: 1px dashed #FDBA74;
  border-radius: 20px;
  font-size: 11.5px;
  font-weight: 600;
}

.btn-pay-bonus {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.25);
  transition: all 0.15s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(217, 119, 6, 0.35);
  }
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  background: white;
  border-radius: 14px;
  border: 1px dashed #D1D5DB;
}

.empty-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.empty-title { font-size: 15px; font-weight: 700; color: #111827; }
.empty-sub { font-size: 13px; color: #6B7280; margin-top: 4px; }

/* Modal Overlay & Card Styling */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header-banner {
  padding: 20px 24px;
  background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: space-between;

  &.bonus-banner {
    background: linear-gradient(180deg, #FEF3C7 0%, #FFFFFF 100%);
  }
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;

  &.gold-box {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
  }
}

.modal-title-text { font-size: 16.5px; font-weight: 700; color: #111827; }
.modal-subtitle-text { font-size: 12px; color: #6B7280; }

.btn-modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #9CA3AF;
  cursor: pointer;
}

.modal-form-body { padding: 24px; }

.target-info-card {
  background: linear-gradient(135deg, #FEF3C7 0%, #FFFBEB 100%);
  border: 1px solid #FDE68A;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 22px;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.08);
}

.target-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.target-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
  color: white;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 8px rgba(217, 119, 6, 0.25);
}

.target-student-meta {
  display: flex;
  flex-direction: column;
}

.target-student-name {
  font-size: 15px;
  font-weight: 700;
  color: #78350F;
}

.target-cat-tag {
  font-size: 12px;
  font-weight: 600;
  color: #92400E;
}

.target-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px dashed #FCD34D;
  font-size: 12.5px;
}

.target-label {
  color: #92400E;
  font-weight: 500;
}

.target-agent-name {
  color: #2D6A4F;
  font-weight: 700;
}

.input-with-addon {
  position: relative;
  display: flex;
  align-items: center;
}

.select-field-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon-left {
  position: absolute;
  left: 12px;
  display: flex;
  align-items: center;
  pointer-events: none;
  z-index: 2;
}

.input-has-icon {
  padding-left: 40px !important;
}

.select-has-icon {
  padding-left: 40px !important;
  appearance: none;
  -webkit-appearance: none;
}

.input-addon-right {
  position: absolute;
  right: 14px;
  font-size: 13px;
  font-weight: 700;
  color: #D97706;
  pointer-events: none;
}

.select-chevron {
  position: absolute;
  right: 12px;
  color: #6B7280;
  pointer-events: none;
}

.form-field-group { margin-bottom: 18px; }
.form-two-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.field-label {
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

.field-input {
  width: 100%;
  padding: 11px 14px;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  font-size: 14px;
  background-color: #FAFAFA;
  transition: all 0.2s ease;

  &:focus {
    border-color: #D97706;
    background-color: white;
    outline: none;
    box-shadow: 0 0 0 3.5px rgba(217, 119, 6, 0.15);
  }

  &.amount-field {
    font-size: 17px;
    font-weight: 800;
    color: #B45309;
    padding-right: 50px !important;
  }
}

.field-select {
  background-color: #FAFAFA;
  cursor: pointer;
}

.field-textarea { resize: vertical; }

.modal-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 26px;
}

.btn-modal-cancel {
  padding: 10px 18px;
  border: 1px solid #D1D5DB;
  background: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  color: #374151;
  cursor: pointer;

  &:hover {
    background: #F9FAFB;
  }
}

.btn-modal-submit {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13.5px;
  cursor: pointer;
  transition: all 0.15s ease;

  &.gold-btn {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
    box-shadow: 0 4px 14px rgba(217, 119, 6, 0.3);

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(217, 119, 6, 0.4);
    }
  }
}
</style>
