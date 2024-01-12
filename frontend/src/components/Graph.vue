<template>
    <v-card>
        <canvas :id="this.id_name" :width="this.width_px" :height="this.height_px"/>
    </v-card>
</template>

<script>
import Chart, { _adapters } from "chart.js/auto"

export default {
    name: 'graph',
    data: function () {
        return {
            old: []
        }
    },
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
    mounted: function() {
        const canvas = document.getElementById(this.id_name)
        var config = {
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
        dataset: function(new_val) {
            const chart = Chart.getChart(this.id_name)
            chart.data.datasets = this.dataset
            chart.update()
        }
    }
};
</script>
