import { ref } from "vue";
import { defineStore } from "pinia";
// import { router } from "@/router";

const baseUrl = 'api/seasons'

export const useNavBarStore = defineStore('navbar', () => {
    const selectedSeason = ref({});
    const seasons = ref([]);

    function setSelectedSeason() {
        localStorage.setItem('seasonId', selectedSeason)
        // router.push('/').catch(() => {
        //     window.location.reload()
        // })
    }

    async function getSeasons() {
        try {
            const response = await fetch(baseUrl, {method: 'GET'})
            const payload = response.data.body
            const allSeasons = []
            payload[0].forEach(ele => {
                allSeasons.push(ele)
            })
            // There is two values in body and second one is current year
            selectedSeason.value = {
                value: payload[1].value   
            }
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
        seasons,
        selectedSeason,
        setSelectedSeason,
        getSeasons,
    }
})
