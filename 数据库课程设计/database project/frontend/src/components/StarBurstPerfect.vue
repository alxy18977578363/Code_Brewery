<template>
  <div class="starburst-bg" @click="starBurst">
    <slot />
    <transition-group name="starburst-fade">
      <div
        v-for="star in stars"
        :key="star.id"
        class="starburst-star"
        :style="{
          left: star.x + 'px',
          top: star.y + 'px',
          opacity: star.opacity,
          transform: `scale(${star.scale}) rotate(${star.rotate}deg)`
        }"
      >
        <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
          <defs>
            <radialGradient id="starColor" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#fffbe6" />
              <stop offset="60%" stop-color="#FFD700" />
              <stop offset="100%" stop-color="#7f5fff" />
            </radialGradient>
          </defs>
          <path d="M16 2l4.09 8.26L29 11.27l-6.55 6.38L24.18 28 16 23.27 7.82 28l1.73-10.35L2 11.27l8.91-1.01L16 2z" fill="url(#starColor)"/>
        </svg>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref, defineExpose } from 'vue'
let id = 0
const stars = ref([])

function starBurst(e) {
  let baseX = 0, baseY = 0;
  if (e && e.clientX !== undefined && e.clientY !== undefined) {
    // 支持外部传入全局坐标
    const rect = (e.currentTarget && e.currentTarget.getBoundingClientRect) ? e.currentTarget.getBoundingClientRect() : document.body.getBoundingClientRect();
    baseX = e.clientX - rect.left;
    baseY = e.clientY - rect.top;
  } else {
    baseX = 200;
    baseY = 200;
  }
  const count = 12 + Math.floor(Math.random() * 5)
  for (let i = 0; i < count; i++) {
    const angle = (2 * Math.PI * i) / count + (Math.random() - 0.5) * 0.2
    const speed = 60 + Math.random() * 30
    const vx = Math.cos(angle) * speed
    const vy = Math.sin(angle) * speed - 10
    stars.value.push({
      id: id++,
      x: baseX,
      y: baseY,
      vx,
      vy,
      scale: 0.7 + Math.random() * 0.5,
      rotate: Math.random() * 360,
      opacity: 1
    })
  }
  animate()
}

function animate() {
  let frame = 0
  function step() {
    frame++
    stars.value.forEach(star => {
      // 粒子运动+重力
      star.x += star.vx * 0.04
      star.y += star.vy * 0.04 + 0.18 * frame * 0.04
      star.vy += 1.2 // 重力加速度
      star.opacity -= 0.018
      star.scale *= 0.985
    })
    // 移除消失的星星
    while (stars.value.length && stars.value[0].opacity <= 0) {
      stars.value.shift()
    }
    if (stars.value.length) {
      requestAnimationFrame(step)
    }
  }
  requestAnimationFrame(step)
}

defineExpose({ starBurst })
</script>

<style scoped>
.starburst-bg {
  position: relative;
  width: 100%;
  height: 100%;
}
.starburst-star {
  position: absolute;
  pointer-events: none;
  z-index: 10;
  transition: opacity 0.3s;
  will-change: left, top, transform, opacity;
}
.starburst-fade-enter-active, .starburst-fade-leave-active {
  transition: opacity 1s;
}
.starburst-fade-enter-from, .starburst-fade-leave-to {
  opacity: 0;
}
</style>
