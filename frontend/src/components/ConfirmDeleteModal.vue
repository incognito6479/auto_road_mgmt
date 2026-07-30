<template>
  <dialog ref="dialogEl" class="modal-dialog modal-dialog-sm" closedby="any">
    <div class="modal-header">
      <h3 class="modal-title">{{ title }}</h3>
      <button type="button" class="btn-close" @click="close">✕</button>
    </div>

    <div class="modal-body">
      <div class="delete-warning-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" width="48" height="48">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </div>

      <p class="delete-confirm-text">
        <slot>Haqiqatan ham o'chirmoqchimisiz?</slot>
      </p>

      <div v-if="error" class="modal-alert modal-alert-error">{{ error }}</div>

      <div class="modal-actions">
        <button type="button" class="btn-cancel" @click="close">Bekor qilish</button>
        <button type="button" class="btn-delete-confirm" :disabled="deleting" @click="$emit('confirm')">
          <span v-if="deleting" class="btn-spinner"></span>
          {{ deleting ? "O'chirilmoqda..." : "Ha, O'chirish" }}
        </button>
      </div>
    </div>
  </dialog>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  title: { type: String, default: "O'chirish" },
  deleting: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
defineEmits(['confirm'])

const dialogEl = ref(null)
function show() { dialogEl.value?.showModal() }
function close() { dialogEl.value?.close() }
defineExpose({ show, close })
</script>

<style scoped>
.modal-dialog {
  border: none;
  border-radius: 20px;
  padding: 0;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  margin: auto;
}
.modal-dialog-sm { max-width: 440px; }
.modal-dialog::backdrop {
  background: rgba(17, 24, 39, 0.45);
  backdrop-filter: blur(6px);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 28px 18px 28px;
  border-bottom: 1px solid #F3F4F6;
}
.modal-title { font-size: 18px; font-weight: 700; color: #111827; margin: 0; }
.btn-close {
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
  flex-shrink: 0;
}

.modal-body { padding: 20px 24px; }

.delete-warning-icon { display: flex; justify-content: center; margin-bottom: 12px; }
.delete-confirm-text { text-align: center; font-size: 15px; color: #111827; }

.modal-alert {
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 13px;
  margin-top: 12px;
}
.modal-alert-error {
  background: #FEE2E2;
  color: #991B1B;
  border: 1px solid #FCA5A5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
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
}
.btn-delete-confirm {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  background: #DC2626;
  color: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
  cursor: pointer;
}
.btn-delete-confirm:disabled { opacity: 0.7; cursor: not-allowed; }

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
