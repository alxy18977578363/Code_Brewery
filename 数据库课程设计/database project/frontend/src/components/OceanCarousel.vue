<template>
  <div class="ocean-carousel">
    <el-carousel :interval="4000" trigger="click" height="260px" type="card" autoplay>
      <el-carousel-item v-for="(img, idx) in images" :key="idx">
        <div class="slide" :style="{ backgroundImage: `url(${img.url})` }">
          <div class="slide-overlay">
            <h3>{{ img.title }}</h3>
            <p>{{ img.caption }}</p>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const images = ref([
  {
    url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&auto=format&fit=crop&q=80',
    title: '深海采样',
    caption: '探索海洋放射性样本'
  },
  {
    url: 'https://images.unsplash.com/photo-1508672019048-805c876b67e2?w=1200&auto=format&fit=crop&q=80',
    title: '全球覆盖',
    caption: '多站点采样与监测'
  },
  {
    url: 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=1200&auto=format&fit=crop&q=80',
    title: '科研协作',
    caption: '数据驱动科学发现'
  }
])
</script>

<style scoped>
.ocean-carousel {
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(6, 24, 44, 0.12);
}
.slide {
  height: 260px;
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: flex-end;
}
.slide-overlay {
  width: 100%;
  padding: 18px 20px;
  background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(2,6,23,0.55) 60%, rgba(2,6,23,0.85) 100%);
  color: #fff;
}
.slide-overlay h3 {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 700;
}
.slide-overlay p {
  margin: 0;
  font-size: 13px;
  opacity: 0.9;
}
</style>