import { ref } from 'vue'

/**
 * Shared arrow-key + Enter navigation for the app's searchable-select
 * dropdowns (agent/instructor/coordinator/student pickers). Keeps a
 * highlighted index and exposes a single keydown handler each dropdown
 * wires to its search <input>.
 */
export function useSearchSelectKeyboard() {
  const highlightedIndex = ref(-1)

  function reset() {
    highlightedIndex.value = -1
  }

  function onKeydown(e, items, onSelect, onClose) {
    if (e.key === 'Escape') {
      e.preventDefault()
      reset()
      onClose && onClose()
      return
    }
    if (!items || items.length === 0) return

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      highlightedIndex.value = highlightedIndex.value < items.length - 1 ? highlightedIndex.value + 1 : 0
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      highlightedIndex.value = highlightedIndex.value > 0 ? highlightedIndex.value - 1 : items.length - 1
    } else if (e.key === 'Enter') {
      e.preventDefault()
      const idx = highlightedIndex.value >= 0 ? highlightedIndex.value : 0
      if (items[idx]) onSelect(items[idx])
      reset()
    }
  }

  return { highlightedIndex, onKeydown, reset }
}
