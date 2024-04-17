<template>
  <v-card>
    <Bar v-if="props.type === 'bar'"
      :id="props.id"
      :data="{ 
        labels: props.labels,
        datasets: props.datasets
      }"
      :options="{
        responsive: true,
        indexAxis: horizontal,
        scales: {
          y: {
            beginAtZero: true
          }
        },
        plugins:{
          title: {
            text: props.title,
            display: true
          }
        }
      }"
    />
    <Line v-else 
      :id="props.id_name"
      :data="{ 
        labels: props.labels,
        datasets: props.datasets,
      }"
      :options="{
        responsive: true,
        scales: {
          y: {
            beginAtZero: true
          }
        },
        plugins:{
          title: {
            text: props.title,
            display: true
          }
        }
      }"
    />
  </v-card>
</template>

<script setup>
import { Bar, Line } from 'vue-chartjs';
import { 
  Chart as ChartJS, Title, Tooltip,
  Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement)

import { useChartStore } from "@/stores/chart.store";
import { computed } from 'vue';

const chartStore = useChartStore();

const props = defineProps({
  id: String,
  width_px: String,
  height_px: String,
  title: String,
  labels: Array,
  horizontal: {
    type: Boolean,
    default: false,
  },
  type: String,
  datasets: Array
})

const horizontal = computed(() => {
  return props.horizontal ? 'y' : 'x';
})


</script>
