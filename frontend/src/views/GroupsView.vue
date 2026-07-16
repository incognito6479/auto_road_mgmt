<template>
  <AppLayout>

    <!-- Loading, error, or empty states -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Guruhlar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchGroups">Qayta urinish</button>
    </div>

    <div v-else-if="groups.length === 0" class="state-container">
      <p class="state-text">Hech qanday guruh topilmadi. O'quvchilar ro'yxatidan yangi guruh boshlang.</p>
    </div>

    <!-- Groups cards grid -->
    <div v-else class="cards-grid">
      <div class="group-card" v-for="g in groups" :key="g.id">

        <!-- Card Header -->
        <div class="group-header" style="justify-content: space-between; align-items: flex-start; width: 100%;">
          <div style="display: flex; align-items: center; gap: 14px;">
            <div class="group-icon-wrap">
              <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.8" width="28" height="28">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <div class="group-title-block">
              <h3 class="group-name">{{ g.name }}</h3>
              <span class="group-cat-badge">{{ g.category_name }} kategoriyasi</span>
            </div>
          </div>
          <button class="btn-edit-group" @click.stop="openEditModal(g)" title="Tahrirlash">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </button>
        </div>

        <!-- Card Stats / Info -->
        <div class="group-details">
          <div class="detail-row">
            <span class="detail-label">Boshlanish sanasi:</span>
            <span class="detail-value">{{ formatDate(g.started_at) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Davomiyligi:</span>
            <span class="detail-value">{{ g.duration ? g.duration + ' oy' : '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">O'quvchilar soni:</span>
            <span class="detail-value highlight">{{ g.student_count }} ta o'quvchi</span>
          </div>
        </div>

        <!-- Card Footer status badge & View Button -->
        <div class="group-footer" style="justify-content: space-between; align-items: center; width: 100%;">
          <span class="status-badge" :class="statusClass(g.status)">
            {{ statusText(g.status) }}
          </span>
          <button class="btn-view" @click="router.push({ name: 'group-detail', params: { id: g.id } })" style="padding: 6px 14px; background: #2D6A4F; color: white; border: none; border-radius: 8px; font-size: 12.5px; font-weight: 600; cursor: pointer; transition: background 0.15s;">
            Ko'rish
          </button>
        </div>

      </div>
    </div>

    <!-- Edit Group Dialog -->
    <dialog ref="editGroupModal" class="modal-dialog" closedby="any" aria-labelledby="edit-modal-title">
      <form class="modal-form" @submit.prevent="updateGroup">
        <h3 id="edit-modal-title" class="modal-title">Guruhni tahrirlash</h3>
        
        <div v-if="editModalError" class="modal-error">
          {{ editModalError }}
        </div>
        
        <div class="form-group">
          <label for="edit-grp-name" class="form-label">Guruh nomi</label>
          <input
            id="edit-grp-name"
            v-model="editingGroup.name"
            type="text"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="edit-grp-start" class="form-label">Boshlanish sanasi</label>
          <input
            id="edit-grp-start"
            v-model="editingGroup.started_at"
            type="date"
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="edit-grp-duration" class="form-label">Davomiyligi (oylar)</label>
          <input
            id="edit-grp-duration"
            v-model="editingGroup.duration"
            type="number"
            step="0.1"
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="edit-grp-status" class="form-label">Holati</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select id="edit-grp-status" v-model="editingGroup.status" required class="form-input select-input" style="width: 100%; appearance: none; -webkit-appearance: none;">
              <option value="started">Boshlangan</option>
              <option value="finished">Tugatgan</option>
              <option value="canceled">Bekor qilingan</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
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

  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'

const router = useRouter()

const groups = ref([])
const loading = ref(false)
const error = ref('')

// ── Edit Group state ──────────────────────────────────
const editGroupModal = ref(null)
const editingGroup = ref({
  id: null,
  name: '',
  started_at: '',
  duration: null,
  status: 'started',
})
const editSaving = ref(false)
const editModalError = ref('')

const fetchGroups = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/groups/')
    groups.value = response.data
  } catch (err) {
    console.error(err)
    error.value = "Guruhlarni yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('uz-UZ')
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

// ── Edit actions ───────────────────────────────────
const openEditModal = (g) => {
  editingGroup.value = {
    id: g.id,
    name: g.name,
    started_at: g.started_at || '',
    duration: g.duration,
    status: g.status,
  }
  editModalError.value = ''
  if (editGroupModal.value) {
    editGroupModal.value.showModal()
  }
}

const closeEditModal = () => {
  if (editGroupModal.value) {
    editGroupModal.value.close()
  }
}

const updateGroup = async () => {
  if (!editingGroup.value.name.trim() || !editingGroup.value.started_at || editingGroup.value.duration === null || editingGroup.value.duration === undefined) {
    editModalError.value = "Barcha maydonlarni to'ldiring."
    return
  }

  editSaving.value = true
  editModalError.value = ''
  try {
    const payload = {
      name: editingGroup.value.name.trim(),
      started_at: editingGroup.value.started_at,
      duration: parseFloat(editingGroup.value.duration),
      status: editingGroup.value.status,
    }
    await api.patch(`/groups/${editingGroup.value.id}/`, payload)
    closeEditModal()
    await fetchGroups()
  } catch (err) {
    console.error(err)
    editModalError.value = "Saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    editSaving.value = false
  }
}

// Light dismiss listener fallback
onMounted(() => {
  fetchGroups()
  
  if (editGroupModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    editGroupModal.value.addEventListener('click', (event) => {
      if (event.target !== editGroupModal.value) return
      const rect = editGroupModal.value.getBoundingClientRect()
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      )
      if (!isInside) {
        closeEditModal()
      }
    })
  }
})
</script>

<style scoped>
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

/* ── Cards grid ─────────────────────────────────────── */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

@media (max-width: 1024px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}

/* ── Group Card ─────────────────────────────────────── */
.group-card {
  background: white;
  border-radius: 14px;
  padding: 24px 22px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  gap: 18px;
  transition: box-shadow 0.2s, transform 0.2s;
}
.group-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.10), 0 8px 32px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}

.group-header {
  display: flex;
  align-items: center;
  gap: 14px;
}

.group-icon-wrap {
  width: 48px;
  height: 48px;
  background: #d1fae5;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.group-title-block {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.group-name {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0;
  line-height: 1.3;
}

.group-cat-badge {
  font-size: 11px;
  font-weight: 600;
  color: #047857;
  background: #ecfdf5;
  padding: 2px 8px;
  border-radius: 6px;
  align-self: flex-start;
}

/* Details list */
.group-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid #F3F4F6;
  padding-top: 14px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.detail-label {
  color: #6B7280;
  font-weight: 500;
}

.detail-value {
  color: #374151;
  font-weight: 600;
}

.detail-value.highlight {
  color: #2D6A4F;
  font-weight: 700;
}

/* Footer & Status Badge */
.group-footer {
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #F3F4F6;
  padding-top: 12px;
}

.status-badge {
  font-size: 11.5px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
}

.badge-started {
  background: #eff6ff;
  color: #1d4ed8;
}

.badge-finished {
  background: #f3f4f6;
  color: #4b5563;
}

.badge-canceled {
  background: #fef2f2;
  color: #b91c1c;
}
.btn-view:hover {
  background: #245C43 !important;
}

.btn-edit-group {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: #F3F4F6;
  border: 1px solid #E5E7EB;
  color: #4B5563;
  cursor: pointer;
  transition: all 0.15s ease;
  margin-top: 4px;
}

.btn-edit-group:hover {
  background: #E5E7EB;
  color: #111827;
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
}

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
</style>
