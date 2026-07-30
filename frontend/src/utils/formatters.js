/**
 * Utility functions for formatting money, dates, numbers, and phone numbers.
 */

/**
 * Format currency with space separators: e.g. 4500000 -> "4 500 000 so'm"
 * @param {number|string} val 
 * @param {boolean} withSymbol 
 * @returns {string}
 */
export function formatMoney(val, withSymbol = true) {
  if (val === null || val === undefined || val === '') return '0' + (withSymbol ? " so'm" : '')
  const num = Math.round(Number(val))
  if (isNaN(num)) return '0' + (withSymbol ? " so'm" : '')
  const formatted = num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  return formatted + (withSymbol ? " so'm" : '')
}

/**
 * Format raw number with space separators: e.g. 4500000 -> "4 500 000"
 * @param {number|string} val 
 * @returns {string}
 */
export function formatNumber(val) {
  if (val === null || val === undefined || val === '') return '0'
  const num = Math.round(Number(val))
  if (isNaN(num)) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

/**
 * Format phone string cleanly. Numbers may carry free-form trailing text
 * (e.g. "+998 90 900 90 90 uncle" for a relative's contact) — that text is
 * preserved as-is, only the leading phone-looking portion gets formatted.
 * @param {string} phone
 * @returns {string}
 */
export function formatPhone(phone) {
  if (!phone) return '-'
  const str = phone.toString().trim()
  const match = str.match(/^(\+?[\d\s()-]+)(.*)$/)
  const phonePart = match ? match[1] : str
  const textPart = match ? match[2].trim() : ''

  const p = phonePart.replace(/\D/g, '')
  let formattedPhone
  if (p.length === 12 && p.startsWith('998')) {
    formattedPhone = `+${p.slice(0, 3)} (${p.slice(3, 5)}) ${p.slice(5, 8)}-${p.slice(8, 10)}-${p.slice(10, 12)}`
  } else if (p.length === 9) {
    formattedPhone = `+998 (${p.slice(0, 2)}) ${p.slice(2, 5)}-${p.slice(5, 7)}-${p.slice(7, 9)}`
  } else {
    formattedPhone = phonePart.trim() || str
  }

  return textPart ? `${formattedPhone} ${textPart}` : formattedPhone
}

/**
 * Format a phone number the way it should look *while being typed into an
 * input*: "+998 90 900 90 90". Unlike `formatPhone` (which is for display and
 * uses parens/dashes), this keeps the grouping edit-friendly. Always returns
 * a 998-prefixed string; strip non-digits before sending to the API.
 * @param {string} raw
 * @returns {string}
 */
export function formatPhoneInput(raw) {
  let digits = (raw || '').toString().replace(/\D/g, '')
  if (digits.length > 0 && !digits.startsWith('998')) digits = '998' + digits
  digits = digits.substring(0, 12)

  let out = ''
  if (digits.length > 0) out += '+' + digits.substring(0, 3)
  if (digits.length > 3) out += ' ' + digits.substring(3, 5)
  if (digits.length > 5) out += ' ' + digits.substring(5, 8)
  if (digits.length > 8) out += ' ' + digits.substring(8, 10)
  if (digits.length > 10) out += ' ' + digits.substring(10, 12)
  return out
}

/**
 * Format passport
 */
export function formatPassport(serie, number) {
  if (!serie && !number) return '-'
  return `${serie || ''} ${number || ''}`.trim()
}

/**
 * Format date string into YYYY-MM-DD or DD.MM.YYYY
 */
export function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return dateStr
    const day = String(d.getDate()).padStart(2, '0')
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const year = d.getFullYear()
    return `${day}.${month}.${year}`
  } catch (e) {
    return dateStr
  }
}

/**
 * Format a datetime string into DD.MM.YYYY HH:MM
 */
export function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  return `${formatDate(dateStr)} ${d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}`
}

const WEEKDAY_SHORT_NAMES = ['Dush', 'Sesh', 'Chor', 'Pay', 'Juma', 'Shan']

/**
 * Format enrollment.learning_days — a JSONField list of weekday indices
 * (0=Dushanba..5=Shanba) — or a legacy string code, into readable text.
 */
export function formatLearningDays(d) {
  if (Array.isArray(d)) {
    if (d.length === 0) return '-'
    if (d.length === 6) return 'Har kuni'
    return [...d].sort((a, b) => a - b).map(v => WEEKDAY_SHORT_NAMES[v] || v).join(' – ')
  }
  if (d === 'Mo-Wed-Fri') return 'Dush – Chor – Juma'
  if (d === 'Tue-Thu-Sat') return 'Sesh – Pay – Shan'
  if (d === 'everyday') return 'Har kuni'
  return d || '-'
}
