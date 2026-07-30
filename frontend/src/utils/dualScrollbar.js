// Every data table in the app wraps its <table> in one of these
// overflow-x:auto containers. The browser only ever draws that scrollbar at
// the bottom of the container, which is invisible on a tall table until the
// user scrolls all the way down. This adds a matching scrollbar strip above
// the table too, kept in sync with the real one.
const WRAP_SELECTOR = '.table-wrap, .table-container, .table-scroll'

const resizeObservers = new WeakMap()

function ensureTopBar(wrapEl) {
  let topBar = wrapEl.previousElementSibling
  if (topBar && topBar.classList && topBar.classList.contains('dual-scroll-top')) {
    return topBar
  }

  topBar = document.createElement('div')
  topBar.className = 'dual-scroll-top'
  const spacer = document.createElement('div')
  spacer.className = 'dual-scroll-top-spacer'
  topBar.appendChild(spacer)
  wrapEl.parentNode.insertBefore(topBar, wrapEl)

  // Mirror scrollLeft one way at a time, and only once per animation frame.
  // Writing scrollLeft synchronously from inside a 'scroll' handler (which can
  // fire far more often than 60/s during a trackpad fling) forces layout on
  // every event and is the classic cause of stuttery scrolling — batching the
  // write through rAF keeps it to at most one reflow per rendered frame.
  let pending = false
  let source = null
  function flush() {
    pending = false
    if (source === topBar) wrapEl.scrollLeft = topBar.scrollLeft
    else if (source === wrapEl) topBar.scrollLeft = wrapEl.scrollLeft
  }
  function onScroll(el) {
    source = el
    if (pending) return
    pending = true
    requestAnimationFrame(flush)
  }
  topBar.addEventListener('scroll', () => onScroll(topBar), { passive: true })
  wrapEl.addEventListener('scroll', () => onScroll(wrapEl), { passive: true })

  return topBar
}

function syncWidth(wrapEl, topBar) {
  const spacer = topBar.firstElementChild
  const scrollWidth = wrapEl.scrollWidth
  const needsScroll = scrollWidth > wrapEl.clientWidth + 1
  topBar.style.display = needsScroll ? 'block' : 'none'
  if (spacer) spacer.style.width = scrollWidth + 'px'
}

// Scans `root` for table-scroll wrappers and (re)attaches a synced top
// scrollbar to each. Safe to call repeatedly — already-wired wrappers are
// only re-measured, not duplicated.
export function initDualScrollbars(root = document) {
  const wraps = root.querySelectorAll(WRAP_SELECTOR)
  wraps.forEach((wrapEl) => {
    const topBar = ensureTopBar(wrapEl)
    syncWidth(wrapEl, topBar)

    if (!resizeObservers.has(wrapEl) && typeof ResizeObserver !== 'undefined') {
      const ro = new ResizeObserver(() => syncWidth(wrapEl, topBar))
      ro.observe(wrapEl)
      if (wrapEl.firstElementChild) ro.observe(wrapEl.firstElementChild)
      resizeObservers.set(wrapEl, ro)
    }
  })
}
