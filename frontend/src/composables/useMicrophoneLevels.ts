import { ref } from 'vue'

export function useMicrophoneLevels(size = 18) {
  const levels = ref<number[]>(Array.from({ length: size }, () => 24))
  const isListening = ref(false)
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let stream: MediaStream | null = null
  let frameId = 0

  async function start() {
    if (isListening.value) return

    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioContext = new AudioContext()
    analyser = audioContext.createAnalyser()
    analyser.fftSize = 64
    audioContext.createMediaStreamSource(stream).connect(analyser)
    isListening.value = true

    const data = new Uint8Array(analyser.frequencyBinCount)
    const tick = () => {
      if (!analyser) return
      analyser.getByteFrequencyData(data)
      levels.value = Array.from({ length: size }, (_, index) => {
        const value = data[index % data.length] ?? 0
        return Math.max(12, Math.min(96, Math.round((value / 255) * 100)))
      })
      frameId = window.requestAnimationFrame(tick)
    }
    tick()
  }

  function stop() {
    window.cancelAnimationFrame(frameId)
    stream?.getTracks().forEach((track) => track.stop())
    audioContext?.close()
    stream = null
    audioContext = null
    analyser = null
    isListening.value = false
    levels.value = Array.from({ length: size }, () => 24)
  }

  return {
    isListening,
    levels,
    start,
    stop,
  }
}
