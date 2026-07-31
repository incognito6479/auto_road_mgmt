import { ref, computed } from 'vue'

// Shared "search-select a group" state, used as the first step of the
// group -> student cascade in payment/certificate modals (pick a group
// first, then the student list narrows to that group's enrollments).
export function useGroupSelect(groupsRef) {
  const query = ref('')
  const showDropdown = ref(false)
  const selectedId = ref(null)
  const selectedLabel = ref('')
  const selectRef = ref(null)

  const filtered = computed(() => {
    const q = query.value.toLowerCase().trim()
    if (!q) return groupsRef.value
    return groupsRef.value.filter(g => (g.name || '').toLowerCase().includes(q))
  })

  function select(g) {
    selectedId.value = g.id
    selectedLabel.value = g.name
    query.value = g.name
    showDropdown.value = false
  }

  function reset() {
    query.value = ''
    showDropdown.value = false
    selectedId.value = null
    selectedLabel.value = ''
  }

  function isOutside(target) {
    return selectRef.value && !selectRef.value.contains(target)
  }

  return { query, showDropdown, selectedId, selectedLabel, selectRef, filtered, select, reset, isOutside }
}
