<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Html5Qrcode } from 'html5-qrcode'
import BaseModal from './BaseModal.vue'

const { t } = useI18n()

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['close', 'scanned'])

const cameraError = ref(false)
let scanner = null

watch(() => props.show, async (visible) => {
  if (visible) {
    cameraError.value = false
    // Wait for DOM to render the reader div
    await new Promise(r => setTimeout(r, 100))
    try {
      scanner = new Html5Qrcode('qr-reader')
      await scanner.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        (decodedText) => {
          emit('scanned', decodedText)
          stopScanner()
        },
        () => {}
      )
    } catch {
      cameraError.value = true
    }
  } else {
    stopScanner()
  }
})

async function stopScanner() {
  if (scanner) {
    try {
      await scanner.stop()
    } catch {
      // already stopped
    }
    scanner.clear()
    scanner = null
  }
}

function handleClose() {
  stopScanner()
  emit('close')
}
</script>

<template>
  <BaseModal :show="show" :title="t('login.scanQr')" @close="handleClose">
    <div v-if="cameraError" class="text-center text-danger py-8">
      {{ t('login.cameraError') }}
    </div>
    <div v-else id="qr-reader" class="w-full"></div>
    <template #footer />
  </BaseModal>
</template>
