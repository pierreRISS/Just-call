import { ref } from 'vue'
import { Device, type Call } from '@twilio/voice-sdk'
import { getVoiceToken } from '../api/client'

export type VoiceStatus = 'idle' | 'ready' | 'connecting' | 'live' | 'ended' | 'error'

export function useTwilioVoice() {
  const status = ref<VoiceStatus>('idle')
  const errorMessage = ref('')
  const isMuted = ref(false)
  let device: Device | null = null
  let activeCall: Call | null = null

  async function ensureDevice() {
    if (device) return device

    const { token } = await getVoiceToken()
    device = new Device(token, {
      logLevel: 1,
    })

    device.on('registered', () => {
      status.value = 'ready'
    })
    device.on('error', (error) => {
      errorMessage.value = error.message || 'Twilio Voice error.'
      status.value = 'error'
    })
    await device.register()
    return device
  }

  async function connect(params: { to: string; callId: number; recordConsent: boolean }) {
    const currentDevice = await ensureDevice()
    status.value = 'connecting'
    errorMessage.value = ''

    activeCall = await currentDevice.connect({
      params: {
        To: params.to,
        CallId: String(params.callId),
        RecordConsent: params.recordConsent ? 'true' : 'false',
      },
    })

    activeCall.on('accept', () => {
      status.value = 'live'
    })
    activeCall.on('disconnect', () => {
      status.value = 'ended'
      activeCall = null
      isMuted.value = false
    })
    activeCall.on('cancel', () => {
      status.value = 'ended'
      activeCall = null
      isMuted.value = false
    })
    activeCall.on('reject', () => {
      status.value = 'ended'
      activeCall = null
      isMuted.value = false
    })
    activeCall.on('error', (error) => {
      errorMessage.value = error.message || 'Call failed.'
      status.value = 'error'
    })
  }

  function setMuted(nextMuted: boolean) {
    activeCall?.mute(nextMuted)
    isMuted.value = nextMuted
  }

  function hangup() {
    activeCall?.disconnect()
    activeCall = null
    status.value = 'ended'
    isMuted.value = false
  }

  function destroy() {
    activeCall?.disconnect()
    device?.destroy()
    activeCall = null
    device = null
    status.value = 'idle'
    isMuted.value = false
  }

  return {
    errorMessage,
    isMuted,
    status,
    connect,
    destroy,
    hangup,
    setMuted,
  }
}
