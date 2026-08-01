import { onMounted, onUnmounted } from 'vue'

// Sizes `elRef` to fill exactly from its own top edge to the bottom of the
// viewport (minus `bottomPadding`), measured directly via
// getBoundingClientRect rather than assumed from hardcoded topbar/padding
// constants — those constants drift out of sync with what's actually
// rendered (observed as StudentsView and GroupsView, despite identical
// `height: calc(100vh - Npx)` rules, leaving different amounts of empty
// space below the table). Measuring the real layout can't drift.
export function useFillViewportHeight(elRef, bottomPadding = 24) {
  function update() {
    if (!elRef.value) return
    const top = elRef.value.getBoundingClientRect().top
    const height = window.innerHeight - top - bottomPadding
    elRef.value.style.height = Math.max(height, 0) + 'px'
  }

  onMounted(() => {
    update()
    window.addEventListener('resize', update)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', update)
  })

  return { update }
}
