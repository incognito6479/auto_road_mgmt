/**
 * Delays invoking `fn` until `wait` ms have passed since the last call.
 * Used to avoid firing a network request on every keystroke in server-side
 * filter inputs (finance views' student/group name search boxes, etc.).
 */
export function debounce(fn, wait = 400) {
  let timeoutId = null
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), wait)
  }
}
