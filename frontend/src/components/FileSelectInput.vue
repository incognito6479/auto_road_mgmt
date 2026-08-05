<template>
  <div class="file-select-wrap" :class="{ 'has-file': !!fileName }">
    <input
      type="file"
      :accept="accept"
      :required="required"
      class="file-select-native"
      @change="onChange"
    />
    <span class="file-select-btn">Fayl tanlash</span>
    <span class="file-select-name">{{ fileName || 'Fayl tanlanmagan' }}</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  accept: { type: String, default: '' },
  required: { type: Boolean, default: false },
})
const emit = defineEmits(['change'])

const fileName = ref('')

function onChange(e) {
  const file = e.target.files?.[0] || null
  fileName.value = file ? file.name : ''
  emit('change', e)
}

function reset() {
  fileName.value = ''
}

defineExpose({ reset })
</script>

<style scoped>
.file-select-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
  padding: 4px;
  border: 1.5px solid #D1D5DB;
  border-radius: 10px;
  background: #FAFAFA;
  min-height: 40px;
  transition: border-color 0.15s;
}
.file-select-wrap:hover { border-color: #9CA3AF; }

.file-select-native {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 1;
}

.file-select-btn {
  flex-shrink: 0;
  padding: 7px 14px;
  border-radius: 7px;
  background: #EEF2FF;
  color: #4338CA;
  font-size: 12.5px;
  font-weight: 700;
  white-space: nowrap;
}
.file-select-wrap:hover .file-select-btn { background: #E0E7FF; }

.file-select-name {
  font-size: 12.5px;
  color: #9CA3AF;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-select-wrap.has-file .file-select-name { color: #374151; font-weight: 600; }
</style>
