<template>
  <AppLayout>
    <div class="agents-page">
      <!-- Top header bar -->
      <div class="page-header">
        <div>
          <h2 class="page-title">Agentlar boshqaruvi</h2>
          <p class="page-subtitle">Talabalarni jalb etuvchi agentlar ro'yxati va ma'lumotlari</p>
        </div>
        <button v-if="authStore.isAdminOrSuperuser" class="btn-primary" @click="openCreateModal">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
            <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
          </svg>
          Yangi agent qo'shish
        </button>
      </div>

      <!-- Filters and Search -->
      <div class="table-toolbar">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="13" y1="13" x2="18" y2="18"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Agent ismi yoki telefon raqami bo'yicha qidirish..."
            class="search-input"
            @input="onSearchInput"
          />
        </div>
        <div class="total-count">
          Jami: <strong>{{ totalAgents }}</strong> ta agent
        </div>
      </div>

      <!-- Data Table -->
      <div class="table-container">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <span>Yuklanmoqda...</span>
        </div>

        <div v-else-if="agents.length === 0" class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="48" height="48">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <p>Agentlar topilmadi</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th style="width: 50px;">#</th>
              <th>Agent F.I.SH.</th>
              <th>Telefon raqami</th>
              <th>Qo'shimcha telefon</th>
              <th>Yaratilgan sana</th>
              <th v-if="authStore.isAdminOrSuperuser" style="width: 100px; text-align: right;">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(agent, index) in agents" :key="agent.id" class="table-row clickable" @click="goToAgentDetail(agent.id)">
              <td class="td-muted">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td>
                <div class="agent-user-cell">
                  <div class="agent-avatar">
                    {{ agent.full_name?.[0]?.toUpperCase() || 'A' }}
                  </div>
                  <div class="agent-info">
                    <span class="agent-name agent-link-title">{{ agent.full_name }}</span>
                    <span v-if="agent.notes" class="agent-notes">{{ agent.notes }}</span>
                  </div>
                </div>
              </td>
              <td class="td-phone">{{ formatPhoneDisplay(agent.phone) }}</td>
              <td class="td-phone">{{ formatPhoneDisplay(agent.phone2) || '-' }}</td>
              <td class="td-muted">{{ formatDate(agent.created_at) }}</td>
              <td v-if="authStore.isAdminOrSuperuser" style="text-align: right;" @click.stop>
                <div class="action-btns">
                  <button class="btn-icon btn-edit" @click.stop="openEditModal(agent)" title="Tahrirlash">
                    <svg viewBox="0 0 20 20" fill="currentColor" width="15" height="15">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </button>
                  <button class="btn-icon btn-delete" @click.stop="confirmDelete(agent)" title="O'chirish">
                    <svg viewBox="0 0 20 20" fill="currentColor" width="15" height="15">
                      <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination-bar">
        <button class="page-btn" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">
          ‹ Oldingi
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">
          Keyingi ›
        </button>
      </div>

      <!-- Add/Edit Modal -->
      <dialog ref="agentModal" class="modal-dialog">
        <form @submit.prevent="saveAgent" class="modal-form">
          <h3 class="modal-title">{{ isEditing ? "Agent ma'lumotlarini tahrirlash" : "Yangi agent qo'shish" }}</h3>

          <div v-if="modalError" class="modal-error">
            {{ modalError }}
          </div>

          <div class="form-group">
            <label for="ag-name" class="form-label">F.I.SH. (To'liq ism) *</label>
            <input
              id="ag-name"
              v-model="form.full_name"
              type="text"
              placeholder="Masalan: Qodirov Samandar"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="ag-phone" class="form-label">Telefon raqami *</label>
            <input
              id="ag-phone"
              v-model="form.phone"
              type="tel"
              placeholder="+998 90 900 90 90"
              required
              class="form-input"
              @input="handlePhoneInput($event, 'phone')"
            />
          </div>

          <div class="form-group">
            <label for="ag-phone2" class="form-label">Qo'shimcha telefon raqami</label>
            <input
              id="ag-phone2"
              v-model="form.phone2"
              type="tel"
              placeholder="+998 90 900 90 90 (ixtiyoriy)"
              class="form-input"
              @input="handlePhoneInput($event, 'phone2')"
            />
          </div>

          <div class="form-group">
            <label for="ag-notes" class="form-label">Eslatmalar</label>
            <textarea
              id="ag-notes"
              v-model="form.notes"
              placeholder="Qo'shimcha eslatmalar..."
              class="form-input"
              rows="3"
              style="resize: vertical; font-family: inherit;"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
            <button type="submit" class="btn-save" :disabled="saving">
              <span v-if="saving" class="btn-spinner"></span>
              <span>{{ isEditing ? 'Saqlash' : "Qo'shish" }}</span>
            </button>
          </div>
        </form>
      </dialog>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

function goToAgentDetail(id) {
  if (id) router.push(`/agents/${id}`)
}

const agents = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalAgents = ref(0)
const pageSize = 50

const agentModal = ref(null)
const isEditing = ref(false)
const editingId = ref(null)
const modalError = ref('')

const form = ref({
  full_name: '',
  phone: '',
  phone2: '',
  notes: '',
})

let searchTimeout = null

const fetchAgents = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: pageSize,
    }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    const res = await api.get('/agents/', { params })
    if (Array.isArray(res.data)) {
      agents.value = res.data
      totalAgents.value = res.data.length
      totalPages.value = 1
    } else {
      agents.value = res.data.results || []
      totalAgents.value = res.data.count || 0
      totalPages.value = Math.ceil((res.data.count || 0) / pageSize) || 1
    }
    currentPage.value = page
  } catch (err) {
    console.error('Failed to fetch agents:', err)
  } finally {
    loading.value = false
  }
}

const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchAgents(1)
  }, 300)
}

const changePage = (p) => {
  if (p < 1 || p > totalPages.value) return
  fetchAgents(p)
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    full_name: '',
    phone: '',
    phone2: '',
    notes: '',
  }
  modalError.value = ''
  if (agentModal.value) agentModal.value.showModal()
  router.replace({ query: { ...route.query, action: 'add' } })
}

const openEditModal = (agent) => {
  isEditing.value = true
  editingId.value = agent.id
  form.value = {
    full_name: agent.full_name || '',
    phone: agent.phone || '',
    phone2: agent.phone2 || '',
    notes: agent.notes || '',
  }
  modalError.value = ''
  if (agentModal.value) agentModal.value.showModal()
}

const closeModal = () => {
  if (agentModal.value) agentModal.value.close()
  if (route.query.action) {
    const q = { ...route.query }
    delete q.action
    router.replace({ query: q })
  }
}

const saveAgent = async () => {
  const name = form.value.full_name.trim()
  const phoneCleaned = form.value.phone.replace(/\D/g, '')

  if (!name || !phoneCleaned) {
    modalError.value = "F.I.SH. va telefon raqamini kiriting."
    return
  }

  if (phoneCleaned.length < 12) {
    modalError.value = "Telefon raqami noto'g'ri kiritilgan (+998 ...)."
    return
  }

  const phone2Cleaned = form.value.phone2 ? form.value.phone2.replace(/\D/g, '') : null

  saving.value = true
  modalError.value = ''

  try {
    const payload = {
      full_name: name,
      phone: phoneCleaned,
      phone2: phone2Cleaned,
      notes: form.value.notes?.trim() || '',
    }

    if (isEditing.value) {
      await api.patch(`/agents/${editingId.value}/`, payload)
    } else {
      await api.post('/agents/', payload)
    }
    closeModal()
    fetchAgents(currentPage.value)
  } catch (err) {
    console.error(err)
    if (err.response?.data?.phone) {
      modalError.value = "Ushbu telefon raqamli agent allaqachon mavjud."
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi."
    }
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (agent) => {
  if (!confirm(`Haqiqatan ham "${agent.full_name}" agentini o'chirmoqchimisiz?`)) return
  try {
    await api.delete(`/agents/${agent.id}/`)
    fetchAgents(currentPage.value)
  } catch (err) {
    console.error('Failed to delete agent:', err)
    alert("Agentni o'chirishda xatolik yuz berdi.")
  }
}

const formatPhoneDisplay = (p) => {
  if (!p) return ''
  let digits = p.replace(/\D/g, '')
  if (!digits) return p
  if (!digits.startsWith('998') && digits.length <= 9) {
    digits = '998' + digits
  }
  digits = digits.substring(0, 12)
  let formatted = '+' + digits.substring(0, 3)
  if (digits.length > 3) formatted += ' ' + digits.substring(3, 5)
  if (digits.length > 5) formatted += ' ' + digits.substring(5, 8)
  if (digits.length > 8) formatted += ' ' + digits.substring(8, 10)
  if (digits.length > 10) formatted += ' ' + digits.substring(10, 12)
  return formatted
}

const handlePhoneInput = (event, key) => {
  const val = event.target.value
  if (!val) {
    form.value[key] = ''
    return
  }
  form.value[key] = formatPhoneDisplay(val)
}

const formatDate = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}.${month}.${year}`
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  await fetchAgents()

  if (route.query.action === 'add' && authStore.isAdminOrSuperuser) {
    openCreateModal()
  }

  // Light dismiss fallback
  if (agentModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    agentModal.value.addEventListener('click', (event) => {
      if (event.target !== agentModal.value) return
      const rect = agentModal.value.getBoundingClientRect()
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
</script>

<style scoped>
.agents-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 13.5px;
  color: #6B7280;
  margin: 0;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(45, 106, 79, 0.2);
  transition: background 0.15s;
}
.btn-primary:hover {
  background: #1B4332;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  padding: 9px 14px;
  width: 360px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-box:focus-within {
  border-color: #2D6A4F;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
}

.search-input {
  border: none;
  outline: none;
  font-size: 13.5px;
  width: 100%;
  color: #111827;
}

.total-count {
  font-size: 13.5px;
  color: #4B5563;
}

.table-container {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th {
  background: #F9FAFB;
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #E5E7EB;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #F3F4F6;
  font-size: 13.5px;
  color: #111827;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table tbody tr.clickable {
  cursor: pointer;
  transition: background 0.15s ease;
}

.data-table tbody tr.clickable:hover {
  background: #F0FDF4;
}

.agent-link-title {
  color: #2D6A4F;
  font-weight: 600;
}

.agent-link-title:hover {
  text-decoration: underline;
}

.agent-user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #E0E7FF;
  color: #4338CA;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  flex-shrink: 0;
}

.agent-info {
  display: flex;
  flex-direction: column;
}

.agent-name {
  font-weight: 600;
  color: #111827;
}

.agent-notes {
  font-size: 11.5px;
  color: #6B7280;
}

.td-muted {
  color: #6B7280;
  font-size: 13px;
}

.td-phone {
  font-weight: 500;
  color: #374151;
}

.action-btns {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-edit {
  color: #2563EB;
}
.btn-edit:hover {
  background: #EFF6FF;
  border-color: #BFDBFE;
}

.btn-delete {
  color: #DC2626;
}
.btn-delete:hover {
  background: #FEF2F2;
  border-color: #FCA5A5;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 12px;
  color: #6B7280;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #E5E7EB;
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.page-btn {
  padding: 6px 14px;
  background: white;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  transition: background 0.15s;
}
.page-btn:hover:not(:disabled) {
  background: #F3F4F6;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #4B5563;
  font-weight: 500;
}

/* Modal Dialog */
.modal-dialog {
  border: none;
  border-radius: 16px;
  padding: 0;
  max-width: 480px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  background: white;
}
.modal-dialog::backdrop {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
}

.modal-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  border-bottom: 1px solid #E5E7EB;
  padding-bottom: 12px;
}

.modal-error {
  padding: 10px 12px;
  background: #FEE2E2;
  border-left: 4px solid #EF4444;
  color: #991B1B;
  border-radius: 6px;
  font-size: 13px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
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
  transition: border-color 0.15s, box-shadow 0.15s;
}
.form-input:focus {
  border-color: #2D6A4F;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
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
}
.btn-cancel:hover { background: #E5E7EB; }

.btn-save {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 20px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
}
.btn-save:hover { background: #1B4332; }
</style>
