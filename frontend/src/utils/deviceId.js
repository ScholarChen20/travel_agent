import { ref } from 'vue'

const STORAGE_KEY = 'travel_agent_device_id'

export const deviceId = ref('')

export async function initDeviceId() {
  try {
    let storedId = localStorage.getItem(STORAGE_KEY)

    if (!storedId) {
      const fingerprint = generateFingerprint()
      storedId = await sha256(fingerprint)
      localStorage.setItem(STORAGE_KEY, storedId)
    }

    deviceId.value = storedId
    console.log('设备ID已生成:', storedId)
    return storedId
  } catch (error) {
    console.error('生成设备ID失败:', error)
    return generateFallbackDeviceId()
  }
}

function generateFingerprint() {
  const components = [
    navigator.userAgent,
    navigator.language,
    screen.colorDepth,
    screen.width + 'x' + screen.height,
    new Date().getTimezoneOffset(),
    !!window.sessionStorage,
    !!window.localStorage,
    navigator.hardwareConcurrency || 'unknown',
    navigator.platform,
    navigator.doNotTrack,
    JSON.stringify(navigator.plugins)
  ]

  return components.join('###')
}

async function sha256(message) {
  try {
    const msgBuffer = new TextEncoder().encode(message)
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
    return hashHex
  } catch (error) {
    console.error('SHA256加密失败:', error)
    return generateFallbackHash(message)
  }
}

function generateFallbackHash(message) {
  let hash = 0
  for (let i = 0; i < message.length; i++) {
    const char = message.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash).toString(16)
}

function generateFallbackDeviceId() {
  const timestamp = Date.now().toString(36)
  const random = Math.random().toString(36).substring(2, 15)
  const fallbackId = `fallback_${timestamp}_${random}`
  localStorage.setItem(STORAGE_KEY, fallbackId)
  return fallbackId
}

export function getDeviceId() {
  return deviceId.value || localStorage.getItem(STORAGE_KEY) || ''
}

export function getDeviceIdInfo() {
  const id = getDeviceId()
  return {
    deviceId: id,
    isGenerated: !!id,
    timestamp: Date.now()
  }
}

export function resetDeviceId() {
  localStorage.removeItem(STORAGE_KEY)
  deviceId.value = ''
}
