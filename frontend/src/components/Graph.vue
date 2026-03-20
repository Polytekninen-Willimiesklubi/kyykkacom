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
            beginAtZero: true,
            title: {
              display: (props.yLabel !== undefined),
              text: props.yLabel,
            }
          }
        },
        plugins:{
          title: {
            text: props.title,
            display: true
          },
          tooltip: {
            callbacks: {
              label(context) {
                const dataset = context.dataset;
                const rawValue = context.parsed?.x ?? context.parsed?.y;
                const value = Number.isFinite(rawValue) ? rawValue.toFixed(2) : rawValue;

                if (Array.isArray(dataset.throwCounts)) {
                  const throwCount = dataset.throwCounts[context.dataIndex];
                  return `${dataset.label}: KPH ${value}, Heitot ${throwCount}`;
                }

                return `${dataset.label}: ${value}`;
              },
            },
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
  Chart as ChartJS, Title, Tooltip, Legend, BarElement,
  CategoryScale, LinearScale, PointElement, LineElement,
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement)

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
  datasets: Array,
  yLabel: String,
})

const horizontal = computed(() => {
  return props.horizontal ? 'y' : 'x';
})


</script>
