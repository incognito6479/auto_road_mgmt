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
 * Format phone string cleanly
 * @param {string} phone 
 * @returns {string}
 */
export function formatPhone(phone) {
  if (!phone) return '-'
  const p = phone.toString().replace(/\D/g, '')
  if (p.length === 12 && p.startsWith('998')) {
    return `+${p.slice(0, 3)} (${p.slice(3, 5)}) ${p.slice(5, 8)}-${p.slice(8, 10)}-${p.slice(10, 12)}`
  }
  if (p.length === 9) {
    return `+998 (${p.slice(0, 2)}) ${p.slice(2, 5)}-${p.slice(5, 7)}-${p.slice(7, 9)}`
  }
  return phone
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
