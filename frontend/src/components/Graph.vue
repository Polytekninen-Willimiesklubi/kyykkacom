<template>
    <v-card>
        <canvas 
          :id="this.id_name" 
          :width="this.width_px" 
          :height="this.height_px"
        ></canvas>
    </v-card>
</template>

<script>
import Chart from 'chart.js/auto'

export default {
  name: 'graph',
  props: {
    id_name: String,
    width_px: String,
    height_px: String,
    title: String,
    labels: Array,
    reversed: Boolean,
    type: String,
    dataset: Array
  },
  mounted () {
    const canvas = document.getElementById(this.id_name)
    const config = {
      type: this.type,
      data: {
        labels: this.labels,
        datasets: this.dataset
      },
      options: {
        indexAxis: this.reversed ? 'y' : 'x',
        scales: {
          y: {
            beginAtZero: true
          }
        },
        plugins: {
          title: {
            text: this.title,
            display: true
          }
        }
      }
    }
    new Chart(canvas, config)
  },
  watch: {
    dataset () {
      const chart = Chart.getChart(this.id_name)
      chart.data.datasets = this.dataset
      chart.update()
    }
  }
}
</script>
