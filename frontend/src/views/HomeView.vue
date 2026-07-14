<template>
  <AppLayout>

    <!-- ── Stat Cards ─────────────────────────────────── -->
    <div class="stats-row">
      <div class="stat-card" v-for="s in stats" :key="s.key">
        <div class="stat-top">
          <div class="stat-icon-wrap" :style="{ background: s.iconBg }">
            <span v-html="s.icon"></span>
          </div>
          <span class="stat-label">{{ s.label }}</span>
        </div>
        <div class="stat-value">{{ s.value }}</div>
        <div class="stat-bar-track">
          <div class="stat-bar-fill" :style="{ width: s.pct + '%', background: s.color }"></div>
        </div>
      </div>
    </div>

    <!-- ── Row 2: Lessons + Heatmap ─────────────────── -->
    <div class="two-col-row">

      <!-- Upcoming Lessons -->
      <div class="card">
        <div class="card-head">
          <h2>Kelayotgan darslar</h2>
          <button class="btn-outline">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            Taqvim
          </button>
        </div>
        <table class="dtable">
          <thead>
            <tr>
              <th>Talaba ismi</th>
              <th>Vaqt</th>
              <th>Avtomobil</th>
              <th>Holat</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lesson in upcomingLessons" :key="lesson.id">
              <td>
                <div class="cell-with-ava">
                  <div class="mini-ava" :style="{ background: lesson.color }">{{ lesson.initials }}</div>
                  <span>{{ lesson.name }}</span>
                </div>
              </td>
              <td class="td-muted">{{ lesson.time }}</td>
              <td class="td-muted">{{ lesson.vehicle }}</td>
              <td>
                <span class="badge" :class="lesson.status === 'Rejalashtirilgan' ? 'badge-green' : 'badge-amber'">
                  {{ lesson.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Instructor Heatmap -->
      <div class="card">
        <div class="card-head">
          <h2>Instruktor mavjudligi</h2>
          <button class="btn-dark-sm">+ Yangi instruktor</button>
        </div>
        <div class="heatmap-days-row">
          <div class="hday-spacer"></div>
          <div v-for="d in heatmapDays" :key="d" class="hday">{{ d }}</div>
        </div>
        <div class="heatmap-row" v-for="inst in instructors" :key="inst.name">
          <div class="inst-info">
            <div class="mini-ava" :style="{ background: inst.color }">{{ inst.initials }}</div>
            <span class="inst-name">{{ inst.name }}</span>
          </div>
          <div v-for="(slot, idx) in inst.slots" :key="idx" class="hcell" :class="slot ? 'hcell-active' : ''">
            <span v-if="slot" class="hcell-label">{{ slot }}</span>
          </div>
        </div>
      </div>

    </div>

    <!-- ── Row 3: Alerts + Vehicles ──────────────────── -->
    <div class="two-col-row">

      <!-- Student Alerts -->
      <div class="card">
        <div class="card-head">
          <h2>Talabalar jarayoni / Ogohlantirishlar</h2>
        </div>
        <div class="alert-list">
          <div class="alert-row" v-for="a in alerts" :key="a.id">
            <div class="alert-ico-wrap" :class="a.type === 'warn' ? 'aico-warn' : 'aico-info'">
              <svg v-if="a.type === 'warn'" viewBox="0 0 24 24" fill="currentColor" width="13" height="13">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor" width="13" height="13">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <span class="alert-label">{{ a.label }}</span>
            <span class="alert-desc">{{ a.desc }}</span>
            <span class="badge badge-green">{{ a.status }}</span>
            <span class="alert-arrow">›</span>
          </div>
        </div>
      </div>

      <!-- Vehicle Status -->
      <div class="card">
        <div class="card-head">
          <h2>Avtomobil holati</h2>
          <button class="btn-outline">Ko'rish</button>
        </div>
        <table class="dtable">
          <thead>
            <tr>
              <th>Avtomobil</th>
              <th>Holat</th>
              <th>Yoqilg'i</th>
              <th>Keyingi xizmat</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in vehicles" :key="v.id">
              <td>
                <div class="cell-with-ava">
                  <svg viewBox="0 0 24 24" fill="#9CA3AF" width="16" height="16">
                    <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
                  </svg>
                  <span>{{ v.name }}</span>
                </div>
              </td>
              <td>
                <span class="badge" :class="v.status === 'Mavjud' ? 'badge-green' : 'badge-amber'">{{ v.status }}</span>
              </td>
              <td>
                <div class="fuel-cell">
                  <span class="td-muted">{{ v.fuel }}</span>
                  <div class="fuel-track">
                    <div class="fuel-fill" :style="{ width: v.fuel, background: v.fuelColor }"></div>
                  </div>
                </div>
              </td>
              <td class="td-muted">{{ v.nextService }}</td>
              <td><button class="more-btn">···</button></td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'

// ── Stats data ────────────────────────────────────────────────
const stats = [
  {
    key: 'students', label: 'Faol talabalar', value: '202', pct: 70,
    color: '#2D6A4F', iconBg: '#d1fae5',
    icon: `<svg viewBox="0 0 24 24" fill="#2D6A4F" width="20" height="20"><path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v2h20v-2c0-3.3-6.7-5-10-5z"/></svg>`,
  },
  {
    key: 'lessons', label: 'Kutilayotgan darslar', value: '19', pct: 38,
    color: '#f59e0b', iconBg: '#fef3c7',
    icon: `<svg viewBox="0 0 24 24" fill="#f59e0b" width="20" height="20"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23L13 14.87V7z"/></svg>`,
  },
  {
    key: 'maintenance', label: "Texnik ko'rik", value: '13', pct: 28,
    color: '#3b82f6', iconBg: '#dbeafe',
    icon: `<svg viewBox="0 0 24 24" fill="#3b82f6" width="20" height="20"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>`,
  },
  {
    key: 'revenue', label: 'Oylik daromad', value: "45 000 000 so'm", pct: 82,
    color: '#2D6A4F', iconBg: '#d1fae5',
    icon: `<svg viewBox="0 0 24 24" fill="#2D6A4F" width="20" height="20"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>`,
  },
]

// ── Upcoming Lessons ──────────────────────────────────────────
const upcomingLessons = [
  { id: 1, name: 'Rahmatullo Qodirov', initials: 'RQ', color: '#4f46e5', time: '10:00 – 11:00', vehicle: 'Avto',   status: 'Rejalashtirilgan' },
  { id: 2, name: 'Sardor Mirzayev',    initials: 'SM', color: '#0891b2', time: '11:30 – 12:30', vehicle: "Qo'lda", status: 'Jarayonda' },
  { id: 3, name: 'Barno Holiqova',     initials: 'BH', color: '#7c3aed', time: '14:00 – 15:00', vehicle: 'Avto',   status: 'Rejalashtirilgan' },
  { id: 4, name: 'Jamshid Toshmatov',  initials: 'JT', color: '#db2777', time: '16:00 – 17:00', vehicle: "Qo'lda", status: 'Jarayonda' },
]

// ── Instructor Heatmap ────────────────────────────────────────
const heatmapDays = ['Du', 'Se', 'Ch', 'Pa', 'Ju']
const instructors = [
  { name: 'Admin',        initials: 'A',  color: '#2D6A4F', slots: ['', '10:00', '',      '13:00', '']      },
  { name: 'Instruktor 1', initials: 'I1', color: '#0891b2', slots: ['', '10:00', '14:00', '',      '10:00'] },
  { name: 'Instruktor 2', initials: 'I2', color: '#7c3aed', slots: ['', '',      '14:00', '14:00', '']      },
  { name: 'Blonanin',     initials: 'BL', color: '#db2777', slots: ['', '10:00', '',      '10:00', '']      },
  { name: 'Admin 2',      initials: 'A2', color: '#f59e0b', slots: ['19:00', '', '10:00', '',      '']      },
]

// ── Alerts ───────────────────────────────────────────────────
const alerts = [
  { id: 1, type: 'warn', label: 'Guvohnoma muddati',     desc: 'Guvohnoma muddati tugayapti',  status: 'Rejalashtirilgan' },
  { id: 2, type: 'warn', label: 'Nazariya imtihoni',     desc: 'Nazariya imtihoni zarur',       status: 'Rejalashtirilgan' },
  { id: 3, type: 'warn', label: 'Nazariya imtihoni',     desc: 'Nazariya imtihoni zarur',       status: 'Rejalashtirilgan' },
  { id: 4, type: 'info', label: 'Amaliy imtihon tayyor', desc: 'Guvohnoma muddati tugayapti',   status: 'Rejalashtirilgan' },
]

// ── Vehicles ─────────────────────────────────────────────────
const vehicles = [
  { id: 1, name: 'Avto-T167', status: 'Mavjud',   fuel: '60%', fuelColor: '#2D6A4F', nextService: '01.03.2023' },
  { id: 2, name: 'Avto-5320', status: "Ta'mirda", fuel: '50%', fuelColor: '#f59e0b', nextService: '01.03.2023' },
  { id: 3, name: 'Avto-BR3V', status: 'Mavjud',   fuel: '85%', fuelColor: '#2D6A4F', nextService: '01.03.2023' },
]
</script>

<style scoped>
/* ── Dashboard body layout ──────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 18px;
}

.two-col-row {
  display: grid;
  grid-template-columns: 3fr 2fr;
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
.stat-value { font-size: 26px; font-weight: 700; color: #111827; line-height: 1; }

.stat-bar-track { height: 4px; background: #F3F4F6; border-radius: 4px; overflow: hidden; }
.stat-bar-fill  { height: 100%; border-radius: 4px; }

/* ── Cards ──────────────────────────────────────────────── */
.card {
  background: white;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  min-width: 0;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.card-head h2 { font-size: 14.5px; font-weight: 600; color: #111827; }

.btn-outline {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 11px;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
  font-size: 12.5px;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-outline:hover { background: #F9FAFB; }

.btn-dark-sm {
  padding: 5px 11px;
  border-radius: 8px;
  background: #1B2430;
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-dark-sm:hover { background: #111827; }

/* ── Table ──────────────────────────────────────────────── */
.dtable { width: 100%; border-collapse: collapse; font-size: 13px; }

.dtable th {
  text-align: left;
  padding: 7px 10px;
  color: #6B7280;
  font-weight: 600;
  font-size: 11.5px;
  border-bottom: 1px solid #F3F4F6;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.dtable td {
  padding: 10px 10px;
  color: #374151;
  border-bottom: 1px solid #F9FAFB;
  vertical-align: middle;
}

.dtable tbody tr:last-child td { border-bottom: none; }
.dtable tbody tr:hover td { background: #FAFAFA; }
.td-muted { color: #6B7280; }

.cell-with-ava { display: flex; align-items: center; gap: 8px; }

.mini-ava {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11.5px;
  font-weight: 600;
  white-space: nowrap;
}
.badge-green { background: #d1fae5; color: #065f46; }
.badge-amber { background: #fef3c7; color: #92400e; }

/* ── Heatmap ────────────────────────────────────────────── */
.heatmap-days-row {
  display: grid;
  grid-template-columns: 110px repeat(5, 1fr);
  gap: 4px;
  margin-bottom: 6px;
}

.hday { text-align: center; font-size: 11.5px; font-weight: 600; color: #9CA3AF; }

.heatmap-row {
  display: grid;
  grid-template-columns: 110px repeat(5, 1fr);
  gap: 4px;
  align-items: center;
  margin-bottom: 5px;
}

.inst-info { display: flex; align-items: center; gap: 6px; overflow: hidden; }

.inst-name {
  font-size: 11.5px;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hcell {
  height: 28px;
  border-radius: 5px;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hcell-active { background: #2D6A4F; }
.hcell-label  { font-size: 9.5px; color: white; font-weight: 700; }

/* ── Alerts ─────────────────────────────────────────────── */
.alert-list { display: flex; flex-direction: column; }

.alert-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 4px;
  border-bottom: 1px solid #F9FAFB;
}
.alert-row:last-child { border-bottom: none; }

.alert-ico-wrap {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.aico-warn { background: #fef3c7; color: #f59e0b; }
.aico-info { background: #d1fae5; color: #2D6A4F; }

.alert-label {
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-desc {
  font-size: 12px;
  color: #9CA3AF;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-arrow { color: #9CA3AF; font-size: 18px; flex-shrink: 0; }

/* ── Fuel bar ───────────────────────────────────────────── */
.fuel-cell { display: flex; align-items: center; gap: 7px; }

.fuel-track {
  width: 55px;
  height: 5px;
  background: #F3F4F6;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}
.fuel-fill { height: 100%; border-radius: 4px; }

.more-btn {
  color: #9CA3AF;
  font-size: 14px;
  padding: 4px 6px;
  border-radius: 5px;
  letter-spacing: 1px;
  transition: background 0.15s;
}
.more-btn:hover { background: #F3F4F6; }
</style>
