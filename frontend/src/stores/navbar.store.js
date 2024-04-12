import { ref, computed } from "vue";
import { defineStore } from "pinia";
// import { router } from "@/router";

const baseUrl = 'http://localhost:8000/api/seasons' // TODO: change this to .env variable

export const useNavBarStore = defineStore('navbar', () => {
    const selectedSeason = ref({});
    const seasonId = ref(null)
    const seasons = ref([]);

    function setSelectedSeason(val) {
        localStorage.setItem('seasonId', val)
        // router.push('/').catch(() => {
        //     window.location.reload()
        // })
    }

    async function getSeasons() {
        try {
            let payload = null;
            if (!localStorage.allSeasons) {
                var response = await fetch(baseUrl, {method: 'GET'});
                payload = await response.json();
            }
            const allSeasons = payload !== null 
                ? payload[0] 
                : JSON.parse(localStorage.getItem('allSeasons'));

            allSeasons.sort((x, y) => { // This makes the current year top most
                if (x.name < y.name) { 
                    return 1;
                } else if (x.name > y.name) { 
                    return -1;
                } else { 
                    return 0;
                }
            })
            // There is two values in body and second one is current year
            selectedSeason.value = payload !== null ? payload[1] : allSeasons[0]
            seasonId.value = selectedSeason.value.value;
            localStorage.setItem('allSeasons', JSON.stringify(allSeasons));
            seasons.value = allSeasons;

        } catch (error) {
            console.log(error);
            seasons.value = {error};
        }
    }
    return {
        selectedSeason,
        seasons,
        seasonId,
        setSelectedSeason,
        getSeasons,
    }
})
