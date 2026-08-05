<template>
  <AppLayout>

    <!-- ── Quick Navigation ───────────────────────────── -->
    <div class="quick-card">
      <h3 class="quick-title">Tezkor o'tish</h3>
      <div class="quick-nav-grid">
        <button v-for="q in quickNavLinks" :key="q.label" class="quick-nav-btn" @click="goTo(q)">
          <span class="quick-nav-icon" v-html="q.icon"></span>
          <span>{{ q.label }}</span>
        </button>
      </div>
    </div>

    <!-- ── Quick Actions ──────────────────────────────── -->
    <div v-if="authStore.isAdminOrSuperuser" class="quick-card">
      <h3 class="quick-title">Tezkor amallar</h3>
      <div class="quick-actions-grid">
        <button class="quick-action-btn action-violet" @click="goStartGroup">
          <span class="qa-icon">+</span> Guruhni boshlash
        </button>
        <button class="quick-action-btn action-blue" @click="goEnrollStudent">
          <span class="qa-icon">+</span> O'quvchini qabul qilish
        </button>
        <button class="quick-action-btn action-green" @click="openAcceptPaymentModal">
          <span class="qa-icon">+</span> To'lov qabul qilish
        </button>
        <button class="quick-action-btn action-amber" @click="openPayAgentModal">
          <span class="qa-icon">+</span> Agentga to'lov
        </button>
        <button class="quick-action-btn action-indigo" @click="openPayTeacherModal">
          <span class="qa-icon">+</span> O'qituvchiga to'lov
        </button>
        <button class="quick-action-btn action-amber" @click="openAddCertModal">
          <span class="qa-icon">+</span> Sertifikat qo'shish
        </button>
        <button v-if="authStore.isSuperuser" class="quick-action-btn action-teal" @click="openImportExcelModal">
          <span class="qa-icon">+</span> Excel orqali guruh yuklash
        </button>
      </div>
    </div>

    <!-- ── Count Stat Cards ────────────────────────────── -->
    <div class="stats-row">
      <div class="stat-card" v-for="s in countStatCards" :key="s.key">
        <div class="stat-top">
          <div class="stat-icon-wrap" :style="{ background: s.iconBg }">
            <span v-html="s.icon"></span>
          </div>
          <span class="stat-label">{{ s.label }}</span>
        </div>
        <div class="stat-value">
          <span v-if="loadingStats" class="stat-spinner"></span>
          <template v-else>{{ s.value }}</template>
        </div>
      </div>
    </div>

    <!-- ── Money Stat Cards ─────────────────────────────── -->
    <div class="quick-card money-stats-card">
      <div class="money-stats-header">
        <h3 class="quick-title">Moliyaviy ko'rsatkichlar</h3>
        <div class="money-date-filter">
          <label class="money-date-label">Sanadan:</label>
          <input v-model="moneyDateFrom" type="date" class="money-date-input" />
          <label class="money-date-label">Sanagacha:</label>
          <input v-model="moneyDateTo" type="date" class="money-date-input" />
        </div>
      </div>
      <div class="stats-row">
        <div class="stat-card" v-for="s in moneyStatCards" :key="s.key">
          <div class="stat-top">
            <div class="stat-icon-wrap" :style="{ background: s.iconBg }">
              <span v-html="s.icon"></span>
            </div>
            <span class="stat-label">{{ s.label }}</span>
          </div>
          <div class="stat-value">
            <span v-if="loadingMoneyStats" class="stat-spinner"></span>
            <template v-else>{{ s.value }}</template>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Accept Payment Modal ───────────────────────── -->
    <Transition name="modal">
      <div v-if="showAcceptPaymentModal" class="modal-overlay" @click.self="closeAcceptPaymentModal">
        <div class="modal-card">
          <div class="modal-header-banner green-banner">
            <div class="header-left-info">
              <div class="header-icon-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <rect x="2" y="5" width="20" height="14" rx="2"></rect>
                  <line x1="2" y1="10" x2="22" y2="10"></line>
                </svg>
              </div>
              <div>
                <h3>To'lov Qabul Qilish</h3>
                <p>O'quvchi to'lovini tizimga kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeAcceptPaymentModal">✕</button>
          </div>

          <form @submit.prevent="submitAcceptPayment" class="modal-body">
            <div v-if="payModalError" class="alert-error">{{ payModalError }}</div>

            <div class="form-group">
              <label class="flabel required">Guruhni Tanlang *</label>
              <div class="searchable-select-wrap" ref="payGroupSelectRef">
                <input
                  v-model="payGroupQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="Guruh nomi bo'yicha qidiring..."
                  @click="showPayGroupDropdown = !showPayGroupDropdown"
                  @input="showPayGroupDropdown = true"
                  @keydown="onPayGroupKeydown"
                />
                <button v-if="selectedPayGroupId" type="button" class="input-clear-btn" title="Guruhni bekor qilish" @click="clearPayGroupSelection">✕</button>
                <div v-if="showPayGroupDropdown" class="dropdown-options-list">
                  <div
                    v-for="(g, idx) in filteredPayGroups"
                    :key="g.id"
                    class="dropdown-option-item"
                    :class="{ selected: selectedPayGroupId === g.id, highlighted: payGroupKb.highlightedIndex.value === idx }"
                    @click="selectPayGroup(g)"
                  >
                    <div class="opt-name">{{ g.name }}</div>
                  </div>
                  <div v-if="filteredPayGroups.length === 0" class="dropdown-empty">
                    Mos guruh topilmadi
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">O'quvchini Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap" ref="studentSelectRef">
                <input
                  v-model="studentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  :placeholder="selectedPayGroupId ? 'Ism bo\'yicha qidiring...' : 'Avval guruhni tanlang'"
                  :disabled="!selectedPayGroupId"
                  @click="showStudentDropdown = !showStudentDropdown"
                  @input="showStudentDropdown = true"
                  @keydown="onStudentPayKeydown"
                />
                <button v-if="payForm.enrollment" type="button" class="input-clear-btn" title="O'quvchini bekor qilish" @click="clearPayStudentSelection">✕</button>
                <div v-if="showStudentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(e, idx) in filteredEnrollments"
                    :key="e.id"
                    class="dropdown-option-item"
                    :class="{ selected: payForm.enrollment === e.id, highlighted: studentPayKb.highlightedIndex.value === idx }"
                    @click="selectPayEnrollment(e)"
                  >
                    <div class="opt-name">{{ e.student_name }}</div>
                    <div class="opt-sub">{{ e.category_name }} {{ e.group_name ? `(${e.group_name})` : '' }}</div>
                  </div>
                  <div v-if="filteredEnrollments.length === 0" class="dropdown-empty">
                    Mos o'quvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedStudentLabel" class="selected-chip">
                Tanlandi: <strong>{{ selectedStudentLabel }}</strong>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">To'lanayotgan Summa *</label>
              <input
                v-model="payForm.amountFormatted"
                type="text"
                class="finput amount-input"
                placeholder="0"
                required
                @input="onPayAmountInput"
              />
            </div>

            <div class="form-group">
              <label class="flabel required">To'lov Usuli *</label>
              <div class="select-wrap-relative">
                <select v-model="payForm.method" class="fselect-field">
                  <option value="cash">Naqd</option>
                  <option value="card">Karta</option>
                  <option value="qr_code">QR code</option>
                  <option value="click">Click</option>
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <div class="form-group" v-if="payForm.method === 'click'">
              <label class="flabel">Click cheki rasmi (ixtiyoriy)</label>
              <FileSelectInput ref="payCheckFileInputRef" accept="image/*" @change="onPayCheckFileChange" />
            </div>

            <div class="form-group">
              <label class="flabel">Izoh / Eslatma</label>
              <input v-model="payForm.notes" type="text" class="finput" placeholder="Ixtiyoriy izoh..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeAcceptPaymentModal">Bekor qilish</button>
              <button type="submit" class="btn-save" :disabled="paySaving">
                {{ paySaving ? "Saqlanmoqda..." : "To'lovni Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ── Pay Agent Modal ────────────────────────────── -->
    <Transition name="modal">
      <div v-if="showPayAgentModal" class="modal-overlay" @click.self="closePayAgentModal">
        <div class="modal-card">
          <div class="modal-header-banner gold-banner">
            <div class="header-left-info">
              <div class="header-icon-box gold-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                </svg>
              </div>
              <div>
                <h3>Agentga To'lov</h3>
                <p>Hamkor agentga bonus/to'lov summasini kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closePayAgentModal">✕</button>
          </div>

          <form @submit.prevent="submitPayAgent" class="modal-body">
            <div v-if="agentPayModalError" class="alert-error">{{ agentPayModalError }}</div>

            <div class="form-group">
              <label class="flabel required">Agentni Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap" ref="agentSelectRef">
                <input
                  v-model="agentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="Agent ismini kiriting..."
                  @click="showAgentDropdown = !showAgentDropdown"
                  @input="showAgentDropdown = true"
                  @keydown="onAgentPayKeydown"
                />
                <div v-if="showAgentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(ag, idx) in filteredAgentsForPay"
                    :key="ag.id"
                    class="dropdown-option-item"
                    :class="{ selected: agentPayForm.agent === ag.id, highlighted: agentPayKb.highlightedIndex.value === idx }"
                    @click="selectPayAgent(ag)"
                  >
                    <div class="opt-name">
                      👤 {{ ag.full_name }}
                      <span v-if="ag.user" class="opt-teacher-badge">{{ ag.user_role === 'instructor' ? 'Instruktor' : "O'qituvchi" }}</span>
                    </div>
                    <div class="opt-sub">{{ ag.phone || 'Telefon ko\'rsatilmagan' }}</div>
                  </div>
                  <div v-if="filteredAgentsForPay.length === 0" class="dropdown-empty">
                    Mos agent topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedAgentLabel" class="selected-chip gold-chip">
                Tanlandi: <strong>{{ selectedAgentLabel }}</strong>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel">O'quvchini Ism bo'yicha Qidirish (Ixtiyoriy)</label>
              <div class="searchable-select-wrap" ref="agentPayStudentSelectRef">
                <input
                  v-model="agentPayStudentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  :placeholder="agentPayForm.agent ? 'O\'quvchi ismini kiriting...' : 'Barcha o\'quvchilar (avval agentni tanlang)'"
                  @click="showAgentPayStudentDropdown = !showAgentPayStudentDropdown"
                  @input="showAgentPayStudentDropdown = true"
                  @keydown="onAgentPayStudentKeydown"
                />
                <button v-if="agentPayForm.enrollment" type="button" class="input-clear-btn" title="O'quvchini bekor qilish" @click="clearAgentPayStudentSelection">✕</button>
                <div v-if="showAgentPayStudentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(e, idx) in filteredEnrollmentsForAgentPay"
                    :key="e.id"
                    class="dropdown-option-item"
                    :class="{ selected: agentPayForm.enrollment === e.id, highlighted: agentPayStudentKb.highlightedIndex.value === idx }"
                    @click="selectAgentPayStudent(e)"
                  >
                    <div class="opt-name">{{ e.student_name }}</div>
                    <div class="opt-sub">{{ e.category_name }} {{ e.group_name ? `(${e.group_name})` : '' }}</div>
                  </div>
                  <div v-if="filteredEnrollmentsForAgentPay.length === 0" class="dropdown-empty">
                    Mos o'quvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedAgentPayStudentLabel" class="selected-chip gold-chip">
                Tanlandi: <strong>{{ selectedAgentPayStudentLabel }}</strong>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">To'lov Summasi *</label>
              <input
                v-model="agentPayForm.amountFormatted"
                type="text"
                class="finput amount-input gold-text"
                placeholder="0"
                required
                @input="onAgentPayAmountInput"
              />
            </div>

            <div class="form-group">
              <label class="flabel required">To'lov Usuli *</label>
              <div class="select-wrap-relative">
                <select v-model="agentPayForm.method" class="fselect-field">
                  <option value="cash">Naqd</option>
                  <option value="card">Karta</option>
                  <option value="qr_code">QR code</option>
                  <option value="click">Click</option>
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel">Izoh / Eslatma</label>
              <input v-model="agentPayForm.notes" type="text" class="finput" placeholder="Ixtiyoriy izoh..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closePayAgentModal">Bekor qilish</button>
              <button type="submit" class="btn-save btn-gold-save" :disabled="agentPaySaving">
                {{ agentPaySaving ? "Saqlanmoqda..." : "To'lovni Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ── Pay Teacher Modal ──────────────────────────── -->
    <Transition name="modal">
      <div v-if="showPayTeacherModal" class="modal-overlay" @click.self="closePayTeacherModal">
        <div class="modal-card">
          <div class="modal-header-banner indigo-banner">
            <div class="header-left-info">
              <div class="header-icon-box indigo-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
              <div>
                <h3>O'qituvchiga To'lov</h3>
                <p>O'qituvchi yoki instruktorga to'lov summasini kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closePayTeacherModal">✕</button>
          </div>

          <form @submit.prevent="submitPayTeacher" class="modal-body">
            <div v-if="teacherPayModalError" class="alert-error">{{ teacherPayModalError }}</div>

            <div class="form-group">
              <label class="flabel required">O'qituvchini Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap" ref="teacherSelectRef">
                <input
                  v-model="teacherSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="O'qituvchi/Instruktor ismini kiriting..."
                  @click="showTeacherDropdown = !showTeacherDropdown"
                  @input="showTeacherDropdown = true"
                  @keydown="onTeacherPayKeydown"
                />
                <div v-if="showTeacherDropdown" class="dropdown-options-list">
                  <div
                    v-for="(t, idx) in filteredTeachersForPay"
                    :key="t.id"
                    class="dropdown-option-item"
                    :class="{ selected: teacherPayForm.teacher === t.id, highlighted: teacherPayKb.highlightedIndex.value === idx }"
                    @click="selectPayTeacher(t)"
                  >
                    <div class="opt-name">👨‍🏫 {{ t.full_name }}</div>
                    <div class="opt-sub">{{ t.role === 'instructor' ? 'Instruktor' : "O'qituvchi" }} ({{ t.phone }})</div>
                  </div>
                  <div v-if="filteredTeachersForPay.length === 0" class="dropdown-empty">
                    Mos o'qituvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedTeacherLabel" class="selected-chip indigo-chip">
                Tanlandi: <strong>{{ selectedTeacherLabel }}</strong>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">To'lov Summasi *</label>
              <input
                v-model="teacherPayForm.amountFormatted"
                type="text"
                class="finput amount-input indigo-text"
                placeholder="0"
                required
                @input="onTeacherPayAmountInput"
              />
            </div>

            <div class="form-group">
              <label class="flabel required">To'lov Turi *</label>
              <div class="select-wrap-relative">
                <select v-model="teacherPayForm.status" class="fselect-field">
                  <option value="paid">Oylik to'lov</option>
                  <option value="bonus_teacher">Sertifikat bonusi</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">To'lov Usuli *</label>
              <div class="select-wrap-relative">
                <select v-model="teacherPayForm.method" class="fselect-field">
                  <option value="cash">Naqd</option>
                  <option value="card">Karta</option>
                  <option value="qr_code">QR code</option>
                  <option value="click">Click</option>
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel">Izoh / Eslatma</label>
              <input v-model="teacherPayForm.notes" type="text" class="finput" placeholder="Ixtiyoriy izoh..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closePayTeacherModal">Bekor qilish</button>
              <button type="submit" class="btn-save btn-indigo-save" :disabled="teacherPaySaving">
                {{ teacherPaySaving ? "Saqlanmoqda..." : "To'lovni Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ── Add Certificate Modal ──────────────────────── -->
    <Transition name="modal">
      <div v-if="showAddCertModal" class="modal-overlay" @click.self="closeAddCertModal">
        <div class="modal-card">
          <div class="modal-header-banner amber-banner">
            <div class="header-left-info">
              <div class="header-icon-box amber-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <circle cx="12" cy="8" r="6"></circle><path d="M8.21 13.89L7 23l5-3 5 3-1.21-9.12"></path>
                </svg>
              </div>
              <div>
                <h3>Sertifikat Qo'shish</h3>
                <p>O'quvchining kursni tugatganlik sertifikatini kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeAddCertModal">✕</button>
          </div>

          <form @submit.prevent="submitAddCert" class="modal-body">
            <div v-if="addCertModalError" class="alert-error">{{ addCertModalError }}</div>

            <div class="form-group">
              <label class="flabel required">Guruhni Tanlang *</label>
              <div class="searchable-select-wrap" ref="certGroupSelectRef">
                <input
                  v-model="certGroupQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="Guruh nomi bo'yicha qidiring..."
                  @click="showCertGroupDropdown = !showCertGroupDropdown"
                  @input="showCertGroupDropdown = true"
                  @keydown="onCertGroupKeydown"
                />
                <button v-if="selectedCertGroupId" type="button" class="input-clear-btn" title="Guruhni bekor qilish" @click="clearCertGroupSelection">✕</button>
                <div v-if="showCertGroupDropdown" class="dropdown-options-list">
                  <div
                    v-for="(g, idx) in filteredCertGroups"
                    :key="g.id"
                    class="dropdown-option-item"
                    :class="{ selected: selectedCertGroupId === g.id, highlighted: certGroupKb.highlightedIndex.value === idx }"
                    @click="selectCertGroup(g)"
                  >
                    <div class="opt-name">{{ g.name }}</div>
                  </div>
                  <div v-if="filteredCertGroups.length === 0" class="dropdown-empty">
                    Mos guruh topilmadi
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">O'quvchini Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap" ref="certStudentSelectRef">
                <input
                  v-model="certStudentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  :placeholder="selectedCertGroupId ? 'Ism bo\'yicha qidiring...' : 'Avval guruhni tanlang'"
                  :disabled="!selectedCertGroupId"
                  @click="showCertStudentDropdown = !showCertStudentDropdown"
                  @input="showCertStudentDropdown = true"
                  @keydown="onCertStudentKeydown"
                />
                <button v-if="addCertForm.student" type="button" class="input-clear-btn" title="O'quvchini bekor qilish" @click="clearCertStudentSelection">✕</button>
                <div v-if="showCertStudentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(s, idx) in filteredCertStudents"
                    :key="s.id"
                    class="dropdown-option-item"
                    :class="{ selected: addCertForm.student === s.id, highlighted: certStudentKb.highlightedIndex.value === idx }"
                    @click="selectCertStudent(s)"
                  >
                    <div class="opt-name">{{ s.student_name }}</div>
                  </div>
                  <div v-if="filteredCertStudents.length === 0" class="dropdown-empty">
                    Mos o'quvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedCertStudentLabel" class="selected-chip">
                Tanlandi: <strong>{{ selectedCertStudentLabel }}</strong>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">Seriya *</label>
              <input v-model="addCertForm.certificate_series" type="text" maxlength="2" class="finput text-upper" placeholder="AB" />
            </div>

            <div class="form-group">
              <label class="flabel required">Raqami *</label>
              <input v-model="addCertForm.certificate_number" type="text" maxlength="9" class="finput" placeholder="9 ta raqam" />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeAddCertModal">Bekor qilish</button>
              <button type="submit" class="btn-save btn-amber-save" :disabled="addCertSaving">
                {{ addCertSaving ? "Saqlanmoqda..." : "Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ── Import Excel Modal ─────────────────────────── -->
    <Transition name="modal">
      <div v-if="showImportModal" class="modal-overlay" @click.self="closeImportModal">
        <div class="modal-card">
          <div class="modal-header-banner teal-banner">
            <div class="header-left-info">
              <div class="header-icon-box teal-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="12" y1="18" x2="12" y2="12"></line>
                  <polyline points="9 15 12 12 15 15"></polyline>
                </svg>
              </div>
              <div>
                <h3>Excel Orqali Guruh Yuklash</h3>
                <p>Eski tizimdagi guruh, o'quvchi va to'lov ma'lumotlarini import qilish</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeImportModal">✕</button>
          </div>

          <div class="modal-body">
            <div v-if="importError" class="alert-error">{{ importError }}</div>

            <template v-if="!importTaskId">
              <div class="form-group">
                <label class="flabel required">Excel fayl (.xlsx, .xlsm, .xls) *</label>
                <FileSelectInput ref="importFileInputRef" accept=".xlsx,.xlsm,.xls" @change="onImportFileChange" />
              </div>
              <p class="import-hint">Fayldagi "Гурух" varag'idan guruhlar, o'quvchilar, to'lovlar va agent bonuslari import qilinadi. Bu amalni faqat bir marta bajarish tavsiya etiladi.</p>
            </template>

            <template v-else-if="importPolling">
              <div class="import-progress">
                <div class="spinner"></div>
                <p>Import bajarilmoqda, bu bir necha daqiqa vaqt olishi mumkin...</p>
              </div>
            </template>

            <template v-else-if="importSummary">
              <div class="import-summary">
                <p class="import-summary-title">Import muvaffaqiyatli yakunlandi:</p>
                <ul>
                  <li>Yangi kategoriyalar: <strong>{{ importSummary.created.categories }}</strong></li>
                  <li>Yangi guruhlar: <strong>{{ importSummary.created.groups }}</strong></li>
                  <li>Yangi agentlar: <strong>{{ importSummary.created.agents }}</strong></li>
                  <li>Yangi o'quvchilar: <strong>{{ importSummary.created.students }}</strong></li>
                  <li>Yangi ro'yxatga olishlar: <strong>{{ importSummary.created.enrollments }}</strong></li>
                  <li>Yangi to'lovlar: <strong>{{ importSummary.created.payments }}</strong></li>
                  <li>Agent bonus to'lovlari: <strong>{{ importSummary.created.bonus_payments }}</strong></li>
                </ul>
                <template v-if="importSummary.warnings.length > 0">
                  <p class="import-summary-title">Ogohlantirishlar ({{ importSummary.warnings.length }}):</p>
                  <ul class="import-warnings-list">
                    <li v-for="(w, idx) in importSummary.warnings" :key="idx">{{ w }}</li>
                  </ul>
                </template>
              </div>
            </template>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeImportModal">{{ importSummary ? 'Yopish' : 'Bekor qilish' }}</button>
              <button v-if="!importTaskId" type="button" class="btn-save btn-teal-save" :disabled="importSaving || !importSelectedFile" @click="submitImportExcel">
                {{ importSaving ? "Yuklanmoqda..." : "Yuklash" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import FileSelectInput from '@/components/FileSelectInput.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatMoney, formatNumber } from '@/utils/formatters'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'
import { useGroupSelect } from '@/composables/useGroupSelect'

const router = useRouter()
const authStore = useAuthStore()

// ── Icons (inline, monochrome, reused across quick nav + stat cards) ──
const icoStudents = `<svg viewBox="0 0 24 24" fill="#2D6A4F" width="20" height="20"><path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v2h20v-2c0-3.3-6.7-5-10-5z"/></svg>`
const icoStaff = `<svg viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2" width="20" height="20"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`
const icoMoney = `<svg viewBox="0 0 24 24" fill="#2D6A4F" width="20" height="20"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>`
const icoOutcome = `<svg viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" width="20" height="20"><path d="M17 7 7 17"/><path d="M17 17H7V7"/></svg>`
const icoDebt = `<svg viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" width="20" height="20"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`
const icoGroups = `<svg viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="1.8" width="20" height="20"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`
const icoCars = `<svg viewBox="0 0 24 24" fill="#3b82f6" width="20" height="20"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>`
const icoDebtNav = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>`
const icoAgentNav = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`

// ── Quick Navigation ───────────────────────────────────
const quickNavLinks = [
  { label: 'Avtomobillar', path: '/vehicles', icon: icoCars },
  { label: "O'quvchilar", path: '/students', icon: icoStudents },
  { label: 'Qarzdorlar', path: '/finances/debts', icon: icoDebtNav },
  { label: 'Guruhlar', path: '/groups', icon: icoGroups },
  { label: "O'qituvchilar", path: '/users', query: { role: 'coordinator' }, icon: icoStaff },
  { label: 'Instruktorlar', path: '/users', query: { role: 'instructor' }, icon: icoStaff },
  { label: 'Agentlar', path: '/agents', icon: icoAgentNav },
]

function goTo(q) {
  router.push({ path: q.path, query: q.query })
}

function goStartGroup() {
  router.push({ path: '/groups', query: { action: 'create' } })
}
function goEnrollStudent() {
  router.push({ path: '/students', query: { action: 'create' } })
}

// ── Real dashboard stats ──────────────────────────────
const loadingStats = ref(true)
const loadingMoneyStats = ref(true)
const enrolledStudentsCount = ref(0)
const activeStaffCount = ref(0)
const activeGroupsCount = ref(0)
const activeCarsCount = ref(0)
const monthIncome = ref(0)
const monthOutcomeAgents = ref(0)
const monthOutcomeTeachers = ref(0)
const monthOutcomeOther = ref(0)
const monthReturned = ref(0)
const monthBank = ref(0)
const totalDebt = ref(0)
// Clean/net accepted income: gross "accepted" collections minus everything
// paid back out (returned, paid to instructors, agent/teacher bonuses, bank
// transfers) — for the same date-range filter as the raw figures above.
const netIncome = computed(() => Math.max(
  0,
  monthIncome.value - monthReturned.value - monthOutcomeOther.value -
  monthOutcomeAgents.value - monthOutcomeTeachers.value - monthBank.value
))

const enrollments = ref([])
const agents = ref([])
const teachers = ref([])
const groups = ref([])

function listOf(data) {
  return data && data.results ? data.results : (data || [])
}

function countOf(data) {
  if (data && typeof data.count === 'number') return data.count
  return listOf(data).length
}

function getDebt(e) {
  if (!e || e.enrolled_free) return 0
  const contract = Number(e.enrolled_amount) || 0
  const paid = Number(e.paid_amount) || 0
  return Math.max(0, contract - paid)
}

const now = new Date()
const defaultMoneyFrom = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
const defaultMoneyTo = now.toISOString().split('T')[0]
const moneyDateFrom = ref(defaultMoneyFrom)
const moneyDateTo = ref(defaultMoneyTo)

async function fetchCountStats() {
  loadingStats.value = true
  try {
    const [studentsRes, coordinatorsRes, instructorsRes, groupsRes, carsRes] = await Promise.all([
      api.get('/students/', { params: { status: 'Faol', page_size: 1 } }),
      api.get('/users/', { params: { role: 'coordinator', page_size: 1 } }),
      api.get('/users/', { params: { role: 'instructor', page_size: 1 } }),
      api.get('/groups/', { params: { page_size: 1000 } }),
      api.get('/cars/', { params: { status: 'available', page_size: 1 } }),
    ])

    enrolledStudentsCount.value = countOf(studentsRes.data)
    activeStaffCount.value = countOf(coordinatorsRes.data) + countOf(instructorsRes.data)
    groups.value = listOf(groupsRes.data)
    activeGroupsCount.value = groups.value.filter(g => g.status === 'started').length
    activeCarsCount.value = countOf(carsRes.data)
  } catch (err) {
    console.error('Failed to load dashboard stats:', err)
  } finally {
    loadingStats.value = false
  }
}

async function fetchMoneyStats() {
  loadingMoneyStats.value = true
  try {
    const [paymentsRes, enrollmentsRes, agentsRes, teachersRes] = await Promise.all([
      api.get('/payments/', {
        params: {
          status: 'accepted,bonus,bonus_teacher,paid,returned,bank',
          date_from: moneyDateFrom.value,
          date_to: moneyDateTo.value,
          page_size: 1000,
        },
      }),
      api.get('/enrollments/', { params: { page_size: 1000 } }),
      api.get('/agents/', { params: { page_size: 1000 } }),
      api.get('/users/', { params: { page_size: 1000 } }),
    ])

    const periodPayments = listOf(paymentsRes.data)
    monthIncome.value = periodPayments.filter(p => p.status === 'accepted').reduce((s, p) => s + (Number(p.amount) || 0), 0)
    monthOutcomeAgents.value = periodPayments.filter(p => p.status === 'bonus').reduce((s, p) => s + (Number(p.amount) || 0), 0)
    monthOutcomeTeachers.value = periodPayments.filter(p => p.status === 'bonus_teacher').reduce((s, p) => s + (Number(p.amount) || 0), 0)
    monthOutcomeOther.value = periodPayments.filter(p => p.status === 'paid').reduce((s, p) => s + (Number(p.amount) || 0), 0)
    monthReturned.value = periodPayments.filter(p => p.status === 'returned').reduce((s, p) => s + (Number(p.amount) || 0), 0)
    monthBank.value = periodPayments.filter(p => p.status === 'bank').reduce((s, p) => s + (Number(p.amount) || 0), 0)

    enrollments.value = listOf(enrollmentsRes.data)
    totalDebt.value = enrollments.value.reduce((s, e) => s + getDebt(e), 0)

    agents.value = listOf(agentsRes.data)
    teachers.value = listOf(teachersRes.data).filter(u => u.role === 'coordinator' || u.role === 'instructor')
  } catch (err) {
    console.error('Failed to load money stats:', err)
  } finally {
    loadingMoneyStats.value = false
  }
}

async function fetchDashboardStats() {
  await Promise.all([fetchCountStats(), fetchMoneyStats()])
}

watch([moneyDateFrom, moneyDateTo], () => { fetchMoneyStats() })

const countStatCards = computed(() => [
  { key: 'students', label: "Faol o'quvchilar", value: formatNumber(enrolledStudentsCount.value), iconBg: '#d1fae5', icon: icoStudents },
  { key: 'staff', label: "Faol o'qituvchi + instruktor", value: formatNumber(activeStaffCount.value), iconBg: '#cffafe', icon: icoStaff },
  { key: 'groups', label: 'Faol guruhlar', value: formatNumber(activeGroupsCount.value), iconBg: '#ede9fe', icon: icoGroups },
  { key: 'cars', label: 'Faol avtomobillar', value: formatNumber(activeCarsCount.value), iconBg: '#dbeafe', icon: icoCars },
])

const moneyStatCards = computed(() => [
  { key: 'income', label: 'Davr sof daromadi', value: formatMoney(netIncome.value), iconBg: '#d1fae5', icon: icoMoney },
  { key: 'outcome-agents', label: 'Davr chiqimi (Agentlar)', value: formatMoney(monthOutcomeAgents.value), iconBg: '#fef3c7', icon: icoOutcome },
  { key: 'outcome-teachers', label: "Davr chiqimi (O'qituvchilar)", value: formatMoney(monthOutcomeTeachers.value), iconBg: '#fef3c7', icon: icoOutcome },
  { key: 'outcome-other', label: 'Davr chiqimi (Boshqa)', value: formatMoney(monthOutcomeOther.value), iconBg: '#fef3c7', icon: icoOutcome },
  { key: 'debt', label: 'Joriy qarzdorlik', value: formatMoney(totalDebt.value), iconBg: '#fee2e2', icon: icoDebt },
])

// ── Accept Payment Modal ──────────────────────────────
const showAcceptPaymentModal = ref(false)
const paySaving = ref(false)
const payModalError = ref(null)
const studentSearchQuery = ref('')
const showStudentDropdown = ref(false)
const selectedStudentLabel = ref('')
const studentSelectRef = ref(null)
const payForm = ref({ enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' })

// Group-first cascade: pick a group, then the student list narrows to that group.
const {
  query: payGroupQuery,
  showDropdown: showPayGroupDropdown,
  selectedId: selectedPayGroupId,
  selectRef: payGroupSelectRef,
  filtered: filteredPayGroups,
  select: selectPayGroupRaw,
  reset: resetPayGroupSelect,
  isOutside: isPayGroupOutside,
} = useGroupSelect(groups)

function selectPayGroup(g) {
  selectPayGroupRaw(g)
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  payForm.value.enrollment = ''
}

function clearPayGroupSelection() {
  resetPayGroupSelect()
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  payForm.value.enrollment = ''
}

function clearPayStudentSelection() {
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  payForm.value.enrollment = ''
}

const payGroupKb = useSearchSelectKeyboard()
function onPayGroupKeydown(e) {
  payGroupKb.onKeydown(e, filteredPayGroups.value, selectPayGroup, () => { showPayGroupDropdown.value = false })
}

const filteredEnrollments = computed(() => {
  if (!selectedPayGroupId.value) return []
  const q = studentSearchQuery.value.toLowerCase().trim()
  return enrollments.value.filter(e => {
    if (e.group !== selectedPayGroupId.value) return false
    return !q || (e.student_name || '').toLowerCase().includes(q)
  })
})

function openAcceptPaymentModal() {
  payModalError.value = null
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  showStudentDropdown.value = false
  resetPayGroupSelect()
  payForm.value = { enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' }
  payCheckFile.value = null
  payCheckFileInputRef.value?.reset()
  showAcceptPaymentModal.value = true
}
function closeAcceptPaymentModal() { showAcceptPaymentModal.value = false }
const payCheckFile = ref(null)
const payCheckFileInputRef = ref(null)
function onPayCheckFileChange(e) {
  payCheckFile.value = e.target.files?.[0] || null
}

function selectPayEnrollment(e) {
  payForm.value.enrollment = e.id
  selectedStudentLabel.value = `${e.student_name} (${e.category_name})`
  studentSearchQuery.value = e.student_name
  showStudentDropdown.value = false
}
const studentPayKb = useSearchSelectKeyboard()
function onStudentPayKeydown(e) {
  studentPayKb.onKeydown(e, filteredEnrollments.value, selectPayEnrollment, () => { showStudentDropdown.value = false })
}

function onPayAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { payForm.value.amount = 0; payForm.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  payForm.value.amount = num
  payForm.value.amountFormatted = formatMoney(num, false)
}

async function submitAcceptPayment() {
  if (!payForm.value.enrollment) { payModalError.value = "O'quvchini tanlang."; return }
  if (!payForm.value.amount || payForm.value.amount <= 0) { payModalError.value = "To'g'ri summani kiriting."; return }
  paySaving.value = true
  payModalError.value = null
  try {
    if (payCheckFile.value) {
      const formData = new FormData()
      formData.append('user', authStore.user?.id)
      formData.append('enrollment', payForm.value.enrollment)
      formData.append('amount', payForm.value.amount)
      formData.append('status', 'accepted')
      formData.append('method', payForm.value.method)
      if (payForm.value.notes) formData.append('notes', payForm.value.notes)
      formData.append('click_check_image', payCheckFile.value)
      await api.post('/payments/', formData)
    } else {
      await api.post('/payments/', {
        user: authStore.user?.id,
        enrollment: payForm.value.enrollment,
        amount: payForm.value.amount,
        status: 'accepted',
        method: payForm.value.method,
        notes: payForm.value.notes,
      })
    }
    closeAcceptPaymentModal()
    fetchDashboardStats()
  } catch (err) {
    payModalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    paySaving.value = false
  }
}

// ── Pay Agent Modal ────────────────────────────────────
const showPayAgentModal = ref(false)
const agentPaySaving = ref(false)
const agentPayModalError = ref(null)
const agentSearchQuery = ref('')
const showAgentDropdown = ref(false)
const selectedAgentLabel = ref('')
const agentSelectRef = ref(null)
const agentPayForm = ref({ agent: '', enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' })

const filteredAgentsForPay = computed(() => {
  const q = agentSearchQuery.value.toLowerCase().trim()
  if (!q) return agents.value
  return agents.value.filter(a => (a.full_name || '').toLowerCase().includes(q))
})

// Student cascade — narrows to the selected agent's own students, just like
// the Bonus (agent) payment create modal in the finance section.
const agentPayStudentSearchQuery = ref('')
const showAgentPayStudentDropdown = ref(false)
const selectedAgentPayStudentLabel = ref('')
const agentPayStudentSelectRef = ref(null)

const filteredEnrollmentsForAgentPay = computed(() => {
  const q = agentPayStudentSearchQuery.value.toLowerCase().trim()
  return enrollments.value.filter(e => {
    if (agentPayForm.value.agent && e.agent !== agentPayForm.value.agent) return false
    return !q || (e.student_name || '').toLowerCase().includes(q)
  })
})

function openPayAgentModal() {
  agentPayModalError.value = null
  agentSearchQuery.value = ''
  selectedAgentLabel.value = ''
  showAgentDropdown.value = false
  agentPayStudentSearchQuery.value = ''
  selectedAgentPayStudentLabel.value = ''
  showAgentPayStudentDropdown.value = false
  agentPayForm.value = { agent: '', enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' }
  showPayAgentModal.value = true
}
function closePayAgentModal() { showPayAgentModal.value = false }

function selectPayAgent(a) {
  agentPayForm.value.agent = a.id
  selectedAgentLabel.value = `${a.full_name} (${a.phone || 'No phone'})`
  agentSearchQuery.value = a.full_name
  showAgentDropdown.value = false
  agentPayStudentSearchQuery.value = ''
  selectedAgentPayStudentLabel.value = ''
  agentPayForm.value.enrollment = ''
}
const agentPayKb = useSearchSelectKeyboard()
function onAgentPayKeydown(e) {
  agentPayKb.onKeydown(e, filteredAgentsForPay.value, selectPayAgent, () => { showAgentDropdown.value = false })
}

function selectAgentPayStudent(e) {
  agentPayForm.value.enrollment = e.id
  selectedAgentPayStudentLabel.value = `${e.student_name} (${e.category_name})`
  agentPayStudentSearchQuery.value = e.student_name
  showAgentPayStudentDropdown.value = false
}
function clearAgentPayStudentSelection() {
  agentPayStudentSearchQuery.value = ''
  selectedAgentPayStudentLabel.value = ''
  agentPayForm.value.enrollment = ''
}
const agentPayStudentKb = useSearchSelectKeyboard()
function onAgentPayStudentKeydown(e) {
  agentPayStudentKb.onKeydown(e, filteredEnrollmentsForAgentPay.value, selectAgentPayStudent, () => { showAgentPayStudentDropdown.value = false })
}

function onAgentPayAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { agentPayForm.value.amount = 0; agentPayForm.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  agentPayForm.value.amount = num
  agentPayForm.value.amountFormatted = formatMoney(num, false)
}

async function submitPayAgent() {
  if (!agentPayForm.value.agent) { agentPayModalError.value = "Agentni tanlang."; return }
  if (!agentPayForm.value.amount || agentPayForm.value.amount <= 0) { agentPayModalError.value = "To'g'ri summani kiriting."; return }
  agentPaySaving.value = true
  agentPayModalError.value = null
  try {
    await api.post('/payments/', {
      user: authStore.user?.id,
      agent: agentPayForm.value.agent,
      enrollment: agentPayForm.value.enrollment || null,
      amount: agentPayForm.value.amount,
      status: 'bonus',
      method: agentPayForm.value.method,
      notes: agentPayForm.value.notes,
    })
    closePayAgentModal()
    fetchDashboardStats()
  } catch (err) {
    agentPayModalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    agentPaySaving.value = false
  }
}

// ── Pay Teacher Modal ──────────────────────────────────
const showPayTeacherModal = ref(false)
const teacherPaySaving = ref(false)
const teacherPayModalError = ref(null)
const teacherSearchQuery = ref('')
const showTeacherDropdown = ref(false)
const selectedTeacherLabel = ref('')
const teacherSelectRef = ref(null)
const teacherPayForm = ref({ teacher: '', amountFormatted: '', amount: 0, status: 'paid', method: 'cash', notes: '' })

const filteredTeachersForPay = computed(() => {
  const q = teacherSearchQuery.value.toLowerCase().trim()
  if (!q) return teachers.value
  return teachers.value.filter(t => (t.full_name || '').toLowerCase().includes(q))
})

function openPayTeacherModal() {
  teacherPayModalError.value = null
  teacherSearchQuery.value = ''
  selectedTeacherLabel.value = ''
  showTeacherDropdown.value = false
  teacherPayForm.value = { teacher: '', amountFormatted: '', amount: 0, status: 'paid', method: 'cash', notes: '' }
  showPayTeacherModal.value = true
}
function closePayTeacherModal() { showPayTeacherModal.value = false }

function selectPayTeacher(t) {
  teacherPayForm.value.teacher = t.id
  selectedTeacherLabel.value = `${t.full_name} (${t.role === 'instructor' ? 'Instruktor' : "O'qituvchi"})`
  teacherSearchQuery.value = t.full_name
  showTeacherDropdown.value = false
}
const teacherPayKb = useSearchSelectKeyboard()
function onTeacherPayKeydown(e) {
  teacherPayKb.onKeydown(e, filteredTeachersForPay.value, selectPayTeacher, () => { showTeacherDropdown.value = false })
}

function onTeacherPayAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { teacherPayForm.value.amount = 0; teacherPayForm.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  teacherPayForm.value.amount = num
  teacherPayForm.value.amountFormatted = formatMoney(num, false)
}

async function submitPayTeacher() {
  if (!teacherPayForm.value.teacher) { teacherPayModalError.value = "O'qituvchini tanlang."; return }
  if (!teacherPayForm.value.amount || teacherPayForm.value.amount <= 0) { teacherPayModalError.value = "To'g'ri summani kiriting."; return }
  teacherPaySaving.value = true
  teacherPayModalError.value = null
  try {
    await api.post('/payments/', {
      user: teacherPayForm.value.teacher,
      amount: teacherPayForm.value.amount,
      status: teacherPayForm.value.status,
      method: teacherPayForm.value.method,
      notes: teacherPayForm.value.notes,
    })
    closePayTeacherModal()
    fetchDashboardStats()
  } catch (err) {
    teacherPayModalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    teacherPaySaving.value = false
  }
}

// ── Add Certificate Modal ───────────────────────────────
const showAddCertModal = ref(false)
const addCertSaving = ref(false)
const addCertModalError = ref(null)
const certEnrollments = ref([])
const certStudentSearchQuery = ref('')
const showCertStudentDropdown = ref(false)
const selectedCertStudentLabel = ref('')
const certStudentSelectRef = ref(null)
const addCertForm = ref({ student: '', certificate_series: '', certificate_number: '' })

// Group-first cascade: pick a group, then the student list narrows to that group.
const {
  query: certGroupQuery,
  showDropdown: showCertGroupDropdown,
  selectedId: selectedCertGroupId,
  selectRef: certGroupSelectRef,
  filtered: filteredCertGroups,
  select: selectCertGroupRaw,
  reset: resetCertGroupSelect,
  isOutside: isCertGroupOutside,
} = useGroupSelect(groups)

function selectCertGroup(g) {
  selectCertGroupRaw(g)
  certStudentSearchQuery.value = ''
  selectedCertStudentLabel.value = ''
  addCertForm.value.student = ''
}

function clearCertGroupSelection() {
  resetCertGroupSelect()
  certStudentSearchQuery.value = ''
  selectedCertStudentLabel.value = ''
  addCertForm.value.student = ''
}

function clearCertStudentSelection() {
  certStudentSearchQuery.value = ''
  selectedCertStudentLabel.value = ''
  addCertForm.value.student = ''
}

const certGroupKb = useSearchSelectKeyboard()
function onCertGroupKeydown(e) {
  certGroupKb.onKeydown(e, filteredCertGroups.value, selectCertGroup, () => { showCertGroupDropdown.value = false })
}

const filteredCertStudents = computed(() => {
  if (!selectedCertGroupId.value) return []
  const q = certStudentSearchQuery.value.toLowerCase().trim()
  return certEnrollments.value.filter(e => {
    if (e.group !== selectedCertGroupId.value) return false
    return !q || (e.student_name || '').toLowerCase().includes(q)
  })
})

async function fetchCertEnrollments() {
  if (certEnrollments.value.length > 0) return
  try {
    const res = await api.get('/enrollments/', { params: { page_size: 1000 } })
    certEnrollments.value = listOf(res.data)
  } catch (err) {
    console.error('Failed to load enrollments:', err)
  }
}

function openAddCertModal() {
  addCertModalError.value = null
  certStudentSearchQuery.value = ''
  selectedCertStudentLabel.value = ''
  showCertStudentDropdown.value = false
  resetCertGroupSelect()
  addCertForm.value = { student: '', certificate_series: '', certificate_number: '' }
  showAddCertModal.value = true
  fetchCertEnrollments()
}
function closeAddCertModal() { showAddCertModal.value = false }

function selectCertStudent(s) {
  addCertForm.value.student = s.student
  selectedCertStudentLabel.value = s.student_name
  certStudentSearchQuery.value = s.student_name
  showCertStudentDropdown.value = false
}
const certStudentKb = useSearchSelectKeyboard()
function onCertStudentKeydown(e) {
  certStudentKb.onKeydown(e, filteredCertStudents.value, selectCertStudent, () => { showCertStudentDropdown.value = false })
}

async function submitAddCert() {
  if (!addCertForm.value.student) { addCertModalError.value = "O'quvchini tanlang."; return }
  const series = addCertForm.value.certificate_series.trim().toUpperCase()
  const number = addCertForm.value.certificate_number.trim()
  if (!/^[A-Z]{2}$/.test(series)) { addCertModalError.value = "Seriya 2 ta harfdan iborat bo'lishi kerak (masalan: AB)."; return }
  if (!/^\d{9}$/.test(number)) { addCertModalError.value = "Raqam 9 ta raqamdan iborat bo'lishi kerak."; return }
  addCertSaving.value = true
  addCertModalError.value = null
  try {
    await api.patch(`/students/${addCertForm.value.student}/`, {
      certificate_series: series,
      certificate_number: number,
    })
    closeAddCertModal()
  } catch (err) {
    addCertModalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    addCertSaving.value = false
  }
}

// ── Excel Import Modal ──────────────────────────────────
const showImportModal = ref(false)
const importFileInputRef = ref(null)
const importSelectedFile = ref(null)
const importSaving = ref(false)
const importError = ref('')
const importTaskId = ref(null)
const importPolling = ref(false)
const importSummary = ref(null)
let importPollTimer = null

function openImportExcelModal() {
  importError.value = ''
  importSelectedFile.value = null
  importFileInputRef.value?.reset()
  importTaskId.value = null
  importPolling.value = false
  importSummary.value = null
  showImportModal.value = true
}

function closeImportModal() {
  showImportModal.value = false
  clearInterval(importPollTimer)
}

function onImportFileChange(e) {
  importSelectedFile.value = e.target.files?.[0] || null
}

async function submitImportExcel() {
  if (!importSelectedFile.value) {
    importError.value = "Excel faylni tanlang."
    return
  }
  importSaving.value = true
  importError.value = ''
  try {
    const formData = new FormData()
    formData.append('file', importSelectedFile.value)
    const res = await api.post('/import-excel/', formData)
    importTaskId.value = res.data.task_id
    pollImportStatus()
  } catch (err) {
    importError.value = err.response?.data?.detail || "Yuklashda xatolik yuz berdi."
  } finally {
    importSaving.value = false
  }
}

function pollImportStatus() {
  importPolling.value = true
  importPollTimer = setInterval(async () => {
    try {
      const res = await api.get(`/import-excel/status/${importTaskId.value}/`)
      if (res.data.state === 'SUCCESS') {
        importSummary.value = res.data.result
        importPolling.value = false
        clearInterval(importPollTimer)
      } else if (res.data.state === 'FAILURE') {
        importError.value = res.data.error || "Import bajarilishida xatolik yuz berdi."
        importTaskId.value = null
        importPolling.value = false
        clearInterval(importPollTimer)
      }
    } catch (err) {
      console.error(err)
    }
  }, 3000)
}

// Both searchable selects close when the click lands outside their own wrapper.
// Clicking the input itself is handled by its own @click toggle, and since the
// input sits inside the wrapper this handler leaves that toggle alone.
function handleSelectOutsideClick(e) {
  if (studentSelectRef.value && !studentSelectRef.value.contains(e.target)) {
    showStudentDropdown.value = false
  }
  if (agentSelectRef.value && !agentSelectRef.value.contains(e.target)) {
    showAgentDropdown.value = false
  }
  if (agentPayStudentSelectRef.value && !agentPayStudentSelectRef.value.contains(e.target)) {
    showAgentPayStudentDropdown.value = false
  }
  if (teacherSelectRef.value && !teacherSelectRef.value.contains(e.target)) {
    showTeacherDropdown.value = false
  }
  if (certStudentSelectRef.value && !certStudentSelectRef.value.contains(e.target)) {
    showCertStudentDropdown.value = false
  }
  if (isPayGroupOutside(e.target)) {
    showPayGroupDropdown.value = false
  }
  if (isCertGroupOutside(e.target)) {
    showCertGroupDropdown.value = false
  }
}

onMounted(() => {
  fetchDashboardStats()
  document.addEventListener('click', handleSelectOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleSelectOutsideClick)
  clearInterval(importPollTimer)
})
</script>

<style scoped>
/* ── Quick nav / actions ────────────────────────────────── */
.quick-card {
  background: white;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  margin-bottom: 18px;
}

.quick-title { font-size: 14.5px; font-weight: 600; color: #111827; margin-bottom: 14px; }

.money-stats-card .stats-row { margin-bottom: 0; }
.money-stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 14px;
}
.money-stats-header .quick-title { margin-bottom: 0; }
.money-date-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.money-date-label { font-size: 12.5px; font-weight: 600; color: #6B7280; }
.money-date-input {
  padding: 7px 10px;
  border: 1.5px solid #E5E7EB;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  background: #F9FAFB;
  outline: none;
}
.money-date-input:focus { border-color: #2D6A4F; }

.quick-nav-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 10px;
  border: 1.5px solid #E5E7EB;
  background: #F9FAFB;
  color: #374151;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.quick-nav-btn:hover {
  background: white;
  border-color: #2D6A4F;
  color: #2D6A4F;
  transform: translateY(-1px);
}
.quick-nav-icon { display: inline-flex; align-items: center; }

.quick-actions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.quick-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 20px;
  border-radius: 12px;
  border: none;
  color: white;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(0,0,0,0.12);
}
.quick-action-btn:hover { transform: translateY(-2px); }
.qa-icon { font-size: 15px; font-weight: 800; }

.action-violet { background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); }
.action-blue   { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); }
.action-green  { background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); }
.action-amber  { background: linear-gradient(135deg, #D97706 0%, #B45309 100%); }
.action-indigo { background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); }
.action-teal   { background: linear-gradient(135deg, #0D9488 0%, #115E59 100%); }

/* ── Dashboard body layout ──────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

/* ── Stat cards ─────────────────────────────────────────── */
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 18px 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stat-top { display: flex; align-items: center; gap: 10px; }

.stat-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-label { font-size: 12.5px; color: #6B7280; font-weight: 500; line-height: 1.3; }
.stat-value { font-size: 22px; font-weight: 700; color: #111827; line-height: 1.2; }
.stat-spinner { display: inline-block; width: 18px; height: 18px; border: 2.5px solid #E5E7EB; border-top-color: #0D9488; border-radius: 50%; animation: spin 0.8s linear infinite; }

/* ── Shared modal styles (Accept payment / Pay agent) ───── */
.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 500px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.modal-header-banner { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F3F4F6; }
.modal-header-banner.green-banner { background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%); }
.modal-header-banner.gold-banner { background: linear-gradient(180deg, #FEF3C7 0%, #FFFFFF 100%); }
.modal-header-banner.indigo-banner { background: linear-gradient(180deg, #EEF2FF 0%, #FFFFFF 100%); }
.modal-header-banner.amber-banner { background: linear-gradient(180deg, #FFFBEB 0%, #FFFFFF 100%); }
.header-left-info { display: flex; align-items: center; gap: 12px; }
.header-left-info h3 { font-size: 17px; font-weight: 700; color: #111827; }
.header-left-info p { font-size: 12px; color: #6B7280; margin-top: 2px; }
.header-icon-box { width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white; display: flex; align-items: center; justify-content: center; }
.header-icon-box.gold-box { background: linear-gradient(135deg, #D97706 0%, #B45309 100%); }
.header-icon-box.indigo-box { background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); }
.header-icon-box.amber-box { background: linear-gradient(135deg, #D97706 0%, #92400E 100%); }
.modal-header-banner.teal-banner { background: linear-gradient(180deg, #F0FDFA 0%, #FFFFFF 100%); }
.header-icon-box.teal-box { background: linear-gradient(135deg, #0D9488 0%, #115E59 100%); }
.btn-modal-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.modal-body { padding: 24px; }

.form-group { margin-bottom: 18px; width: 100%; }
.flabel { display: block; font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.finput, .fselect-field {
  width: 100%; box-sizing: border-box; padding: 11px 14px;
  border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 14px;
  background-color: #FAFAFA; color: #111827; outline: none;
  transition: all 0.2s ease; appearance: none; -webkit-appearance: none;
}
.finput:focus, .fselect-field:focus { border-color: #2D6A4F; background-color: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(45, 106, 79, 0.12); }

.select-wrap-relative { position: relative; width: 100%; }
.select-chevron-icon { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9CA3AF; font-size: 10px; }

.searchable-select-wrap { position: relative; width: 100%; }
.input-clear-btn {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 22px; height: 22px; border-radius: 50%; border: none;
  background: #E5E7EB; color: #4B5563; font-size: 11px; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.input-clear-btn:hover { background: #D1D5DB; color: #111827; }
.searchable-select-wrap .finput { padding-right: 34px; }
.dropdown-options-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 200px; overflow-y: auto; background: white; border: 1.5px solid #2D6A4F; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 50; margin-top: 4px; }
.dropdown-option-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #F3F4F6; }
.dropdown-option-item:hover { background: #F0FDF4; }
.dropdown-option-item.selected { background: #E8F5E9; font-weight: 700; }
.dropdown-option-item.highlighted { background: #F0FDF4; }
.opt-name { font-size: 13.5px; font-weight: 600; color: #111827; }
.opt-sub { font-size: 11.5px; color: #6B7280; margin-top: 1px; }
.opt-teacher-badge { margin-left: 6px; padding: 2px 7px; font-size: 10px; font-weight: 700; color: #4338CA; background: #E0E7FF; border-radius: 6px; vertical-align: middle; }
.dropdown-empty { padding: 12px; text-align: center; color: #9CA3AF; font-size: 13px; }
.selected-chip { font-size: 12.5px; color: #2D6A4F; margin-top: 6px; }
.selected-chip.gold-chip { color: #D97706; }
.selected-chip.indigo-chip { color: #4F46E5; }

.amount-input { font-size: 16.5px; font-weight: 800; color: #2D6A4F; }
.amount-input.gold-text { color: #B45309; }
.amount-input.indigo-text { color: #3730A3; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-save { padding: 10px 22px; background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.btn-gold-save { background: linear-gradient(135deg, #D97706 0%, #B45309 100%); }
.btn-indigo-save { background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); }
.btn-amber-save { background: linear-gradient(135deg, #D97706 0%, #92400E 100%); }
.btn-teal-save { background: linear-gradient(135deg, #0D9488 0%, #115E59 100%); }
.finput.text-upper { text-transform: uppercase; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }

.import-hint { font-size: 12.5px; color: #6B7280; margin-top: 10px; line-height: 1.5; }
.import-progress { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 30px 0; color: #4B5563; font-size: 13.5px; }
.spinner { width: 30px; height: 30px; border: 3px solid #E5E7EB; border-top-color: #0D9488; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.import-summary-title { font-weight: 700; color: #111827; font-size: 13.5px; margin: 14px 0 6px; }
.import-summary-title:first-child { margin-top: 0; }
.import-summary ul { margin: 0; padding-left: 18px; font-size: 13px; color: #374151; }
.import-summary li { margin-bottom: 4px; }
.import-warnings-list { max-height: 220px; overflow-y: auto; background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 10px 10px 10px 26px; color: #92400E; font-size: 12.5px; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
