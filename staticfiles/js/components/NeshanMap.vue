<template>
  <div class="neshan-map-container">
    <MapComponent 
      :options="{
        mapKey: 'web.ea06affc328a4934995818fed7a98b78',
        mapType: MapTypes.neshanVector,
        poi: true,
        traffic: false,
        center: [59.6067, 36.2972],
        zoom: 14
      }"
      :map-setter="onMapLoad"
    />
  </div>
</template>

<script setup>
import { MapComponent, MapTypes } from "@neshan-maps-platform/mapbox-gl-vue";
import "@neshan-maps-platform/mapbox-gl-vue/dist/style.css";
import { ref } from 'vue';

const map = ref(null);

const onMapLoad = (mapInstance) => {
  map.value = mapInstance;
  console.log('نقشه با موفقیت بارگذاری شد');
};
</script>

<style scoped>
.neshan-map-container {
  width: 100%;
  height: 500px;
}
</style>
