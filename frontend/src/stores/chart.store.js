export const useChartStore = defineStore('chart', () => {
    const datasets = ref([]);
    const labels = ref([]);
    
    return {
        datasets,
        labels,
    }
})
