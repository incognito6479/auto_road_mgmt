<template>
  <div class="login-page">
    <!-- Real map background (Leaflet + OpenStreetMap) -->
    <div id="map-bg" ref="mapRef" aria-hidden="true"></div>
    <!-- Frosted blur overlay -->
    <div class="map-overlay" aria-hidden="true"></div>

    <!-- Main card -->
    <div class="card" role="main">

      <!-- Left panel: branding -->
      <div class="card-left">
        <div class="car-icon" aria-hidden="true">
          <img src="/car-icon.jpg" alt="Autoroad School car icon" />
        </div>
        <h2 class="brand-title">AUTOROAD<br>SCHOOL</h2>
        <p class="brand-welcome">Xush kelibsiz!</p>
        <p class="brand-desc">
          O'quvchilar va darslarni boshqarish uchun<br>administrator paneliga kiring.
        </p>
      </div>

      <!-- Right panel: login form -->
      <div class="card-right">
        <h1 class="form-title">Kirish</h1>

        <transition name="shake">
          <div v-if="errorMsg" class="error-banner" role="alert">
            {{ errorMsg }}
          </div>
        </transition>

        <form id="login-form" @submit.prevent="handleLogin" novalidate>

          <!-- Phone field -->
          <div class="field-group">
            <label for="phone-input">Telefon raqami</label>
            <div class="input-wrapper" :class="{ 'input-error': fieldError.phone }">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.4 2 2 0 0 1 3.6 1.21h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 8.82a16 16 0 0 0 6.29 6.29l.94-.94a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
              </span>
              <input
                id="phone-input"
                v-model="phone"
                type="tel"
                placeholder="+998 90 900 90 90"
                autocomplete="username"
                @input="clearFieldError('phone')"
              />

            </div>
            <span v-if="fieldError.phone" class="field-error-msg">{{ fieldError.phone }}</span>
          </div>

          <!-- Password field -->
          <div class="field-group">
            <label for="password-input">Parol</label>
            <div class="input-wrapper" :class="{ 'input-error': fieldError.password }">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              <input
                id="password-input"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Parolni kiriting"
                autocomplete="current-password"
                @input="clearFieldError('password')"
              />
              <button
                type="button"
                class="toggle-password"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Parolni yashirish' : 'Parolni ko\'rsatish'"
              >
                <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
            <span v-if="fieldError.password" class="field-error-msg">{{ fieldError.password }}</span>
          </div>

          <!-- Submit button -->
          <button
            id="login-btn"
            type="submit"
            class="btn-login"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner" aria-hidden="true"></span>
            {{ loading ? 'Yuklanmoqda...' : 'KIRISH' }}
          </button>

          <!-- Bottom row -->
          <div class="bottom-row">
            <label class="remember-label" for="remember-check">
              <input
                id="remember-check"
                type="checkbox"
                v-model="remember"
              />
              <span class="custom-check"></span>
              Eslab qolish
            </label>
          </div>

        </form>
      </div>
    </div>

    <!-- Footer -->
    <footer class="page-footer">
      <a href="#" @click.prevent="showHelpModal = true">Yordam markazi</a>
      <a href="#" @click.prevent="showContactModal = true">Biz bilan bog'laning</a>
    </footer>

    <!-- Help Modal -->
    <div v-if="showHelpModal" class="modal-backdrop" @click.self="showHelpModal = false">
      <div class="modal-content">
        <h2>Yordam markazi</h2>
        <p>Texnik yordam va qo'llab-quvvatlash uchun quyidagi raqamlarga murojaat qiling:</p>
        <div class="contact-numbers">
          <p><strong>Yordam telefoni:</strong> +998 (71) 200-11-22</p>
          <p><strong>Qo'shimcha raqam:</strong> +998 (71) 200-11-23</p>
          <p><strong>Ish vaqti:</strong> Dush - Shan, 9:00 - 18:00</p>
        </div>
        <button class="btn-close" @click="showHelpModal = false">Yopish</button>
      </div>
    </div>

    <!-- Contact Modal -->
    <div v-if="showContactModal" class="modal-backdrop" @click.self="showContactModal = false">
      <div class="modal-content">
        <h2>Biz bilan bog'laning</h2>
        <p>Haydovchilik maktabi ma'muriyati bilan bog'lanish:</p>
        <div class="contact-numbers">
          <p><strong>Ma'muriyat:</strong> +998 (90) 123-45-67</p>
          <p><strong>Qabulxona:</strong> +998 (90) 987-65-43</p>
          <p><strong>E-mail:</strong> info@autoroadschool.uz</p>
        </div>
        <button class="btn-close" @click="showContactModal = false">Yopish</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()
const authStore = useAuthStore()

// Map
const mapRef = ref(null)
let mapInstance = null

onMounted(() => {
  mapInstance = L.map(mapRef.value, {
    center: [41.2995, 69.2401], // Tashkent
    zoom: 15,
    zoomControl: false,
    attributionControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
    tap: false,
    touchZoom: false,
  })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
  }).addTo(mapInstance)
})

onUnmounted(() => {
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }
})

const phone = ref('')
const password = ref('')
const remember = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const fieldError = reactive({ phone: '', password: '' })

// Modal visibility states
const showHelpModal = ref(false)
const showContactModal = ref(false)

// Watch phone for formatting: +998 90 900 90 90
watch(phone, (newValue) => {
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
    phone.value = formatted
  }
})

function clearFieldError(field) {
  fieldError[field] = ''
  errorMsg.value = ''
}

function validate() {
  let ok = true
  const cleaned = phone.value.replace(/\D/g, '')
  if (!cleaned) {
    fieldError.phone = 'Telefon raqamini kiriting.'
    ok = false
  } else if (cleaned.length < 12) {
    fieldError.phone = 'Telefon raqami to\'liq emas.'
    ok = false
  }
  if (!password.value) {
    fieldError.password = 'Parolni kiriting.'
    ok = false
  }
  return ok
}

async function handleLogin() {
  if (!validate()) return
  loading.value = true
  errorMsg.value = ''
  const cleanedPhone = phone.value.replace(/\D/g, '')
  try {
    await authStore.login(cleanedPhone, password.value, remember.value)
    router.push({ name: 'home' })
  } catch (err) {
    if (err.response?.status === 401) {
      errorMsg.value = 'Telefon raqami yoki parol noto\'g\'ri.'
    } else {
      errorMsg.value = 'Xatolik yuz berdi. Qaytadan urinib ko\'ring.'
    }
  } finally {
    loading.value = false
  }
}

</script>

<style scoped>
/* ── Page layout ──────────────────────────────────────────── */
.login-page {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  position: relative;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
  box-sizing: border-box;
}

/* ── Real map background (Leaflet) ───────────────────────── */
#map-bg {
  position: fixed;
  inset: -10px; /* slightly larger to hide blur edges */
  z-index: 0;
  filter: brightness(0.92) saturate(1.1);
}

/* Frosted glass blur overlay */
.map-overlay {
  position: fixed;
  inset: 0;
  z-index: 1;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  background: rgba(240, 238, 232, 0.18);
  pointer-events: none;
}

/* ── Card ─────────────────────────────────────────────────── */
.card {
  position: relative;
  z-index: 2;
  display: flex;
  width: 100%;
  max-width: 820px;
  min-height: 420px;
  border-radius: 20px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.18),
    0 4px 16px rgba(0, 0, 0, 0.10);
  overflow: hidden;
}

/* ── Left panel ───────────────────────────────────────────── */
.card-left {
  width: 42%;
  background: linear-gradient(160deg, #f5f3ee 0%, #eae7df 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  gap: 12px;
  text-align: center;
  border-right: 1px solid rgba(0,0,0,0.06);
}

.car-icon {
  width: 110px;
  height: 110px;
  margin-bottom: 4px;
  filter: drop-shadow(0 4px 10px rgba(45,106,79,0.22));
}

.car-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
  mix-blend-mode: multiply;
}

.brand-title {
  font-size: 1.55rem;
  font-weight: 800;
  color: #1a3c2e;
  letter-spacing: 0.04em;
  line-height: 1.2;
  margin: 0;
}

.brand-welcome {
  font-size: 1rem;
  font-weight: 700;
  color: #2D6A4F;
  margin: 4px 0 0;
}

.brand-desc {
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.55;
  margin: 0;
}

/* ── Right panel ──────────────────────────────────────────── */
.card-right {
  flex: 1;
  background: #ffffff;
  padding: 48px 40px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 24px;
}

/* ── Error banner ─────────────────────────────────────────── */
.error-banner {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  color: #dc2626;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.82rem;
  margin-bottom: 16px;
}

/* ── Field group ──────────────────────────────────────────── */
.field-group {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-group label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #374151;
}

.input-wrapper {
  display: flex;
  align-items: center;
  border: 1.5px solid #d1d5db;
  border-radius: 10px;
  background: #f9fafb;
  transition: border-color 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.input-wrapper:focus-within {
  border-color: #2D6A4F;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
  background: #ffffff;
}

.input-wrapper.input-error {
  border-color: #ef4444;
}

.input-icon {
  padding: 0 12px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 11px 12px 11px 0;
  font-size: 0.9rem;
  color: #111827;
  font-family: inherit;
}

.input-wrapper input::placeholder {
  color: #9ca3af;
}

.toggle-password {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0 12px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.toggle-password:hover {
  color: #2D6A4F;
}

.field-error-msg {
  font-size: 0.75rem;
  color: #ef4444;
}

/* ── Submit button ────────────────────────────────────────── */
.btn-login {
  width: 100%;
  padding: 13px;
  background: #2D6A4F;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  font-family: inherit;
}

.btn-login:hover:not(:disabled) {
  background: #1B4332;
  box-shadow: 0 4px 16px rgba(45, 106, 79, 0.35);
  transform: translateY(-1px);
}

.btn-login:active:not(:disabled) {
  transform: translateY(0);
}

.btn-login:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* loading spinner */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Bottom row: remember + forgot ───────────────────────── */
.bottom-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
}

.remember-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: #374151;
  cursor: pointer;
  user-select: none;
}

.remember-label input[type='checkbox'] {
  display: none;
}

.custom-check {
  width: 16px;
  height: 16px;
  border: 1.5px solid #d1d5db;
  border-radius: 4px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s;
  flex-shrink: 0;
}

.remember-label input[type='checkbox']:checked + .custom-check {
  background: #2D6A4F;
  border-color: #2D6A4F;
}

.remember-label input[type='checkbox']:checked + .custom-check::after {
  content: '';
  width: 8px;
  height: 5px;
  border-left: 2px solid #fff;
  border-bottom: 2px solid #fff;
  transform: rotate(-45deg) translate(1px, -1px);
}

.forgot-link {
  font-size: 0.82rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.18s;
}

.forgot-link:hover {
  color: #2D6A4F;
  text-decoration: underline;
}

/* ── Page footer ──────────────────────────────────────────── */
.page-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 48px;
  padding: 18px;
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(6px);
  z-index: 10;
}

.page-footer a {
  font-size: 0.82rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.18s;
}

.page-footer a:hover {
  color: #2D6A4F;
}

/* ── Shake animation for error ────────────────────────────── */
.shake-enter-active {
  animation: shake 0.4s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%       { transform: translateX(-6px); }
  40%       { transform: translateX(6px); }
  60%       { transform: translateX(-4px); }
  80%       { transform: translateX(4px); }
}

/* ── Responsive ───────────────────────────────────────────── */
@media (max-width: 640px) {
  .card { flex-direction: column; max-width: 400px; }
  .card-left { width: 100%; padding: 32px 24px 24px; border-right: none; border-bottom: 1px solid rgba(0,0,0,0.06); }
  .card-right { padding: 32px 24px; }
}

/* ── Modal Styles ─────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  background: #ffffff;
  padding: 32px;
  border-radius: 16px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  text-align: center;
  font-family: inherit;
}

.modal-content h2 {
  font-size: 1.4rem;
  color: #1a3c2e;
  margin-top: 0;
  margin-bottom: 12px;
}

.modal-content p {
  font-size: 0.9rem;
  color: #4b5563;
  margin-bottom: 16px;
  line-height: 1.5;
}

.contact-numbers {
  background: #f3f4f6;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: left;
}

.contact-numbers p {
  margin: 6px 0;
  font-size: 0.85rem;
  color: #374151;
}

.btn-close {
  padding: 10px 24px;
  background: #2D6A4F;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-close:hover {
  background: #1B4332;
}
</style>

<style>
/* Unscoped style to disable body scrolling */
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden !important;
  height: 100% !important;
}
</style>
