import { ref } from "vue";
import { defineStore } from "pinia";
import { computed } from "vue";
// import { router } from "@/router";

const baseUrl = 'http://localhost:8000/api/seasons' // TODO: change this to .env variable

export const useNavBarStore = defineStore('navbar', () => {
    const selectedSeason = ref({});
    const seasons = ref([]);

    function setSelectedSeason(val) {
        localStorage.setItem('seasonId', val)
        // router.push('/').catch(() => {
        //     window.location.reload()
        // })
    }

    async function getSeasons() {
        try {
            const response = await fetch(baseUrl, {method: 'GET'})
            const payload = await response.json()
            const allSeasons = payload[0]

            // There is two values in body and second one is current year
            selectedSeason.value = payload[1] 
            allSeasons.sort((x, y) => { // This makes the current year top most
                if (x.name < y.name) { 
                    return 1 
                } else if (x.name > y.name) { 
                    return -1 
                } else { 
                    return 0 
                }
            })
            sessionStorage.setItem('allSeasons', JSON.stringify(allSeasons))
            seasons.value = allSeasons

        } catch (error) {
            console.log(error)
            seasons.value = {error}
        }
    }
    return {
        selectedSeason,
        seasons,
        setSelectedSeason,
        getSeasons,
    }
})
