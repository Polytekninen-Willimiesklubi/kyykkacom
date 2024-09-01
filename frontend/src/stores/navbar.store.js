import { useTeamsStore } from "@/stores/teams.store";
import { seasonsMappings } from "@/tournament_templates";

const baseUrl = `${import.meta.env.VITE_API_URL}/api/seasons/`;

export const useNavBarStore = defineStore('navbar', () => {
    const selectedSeason = ref(JSON.parse(localStorage.getItem('selectedSeason')));
    const seasons = ref(JSON.parse(localStorage.getItem('allSeasons')));

    const seasonId = computed(() => {
        console.log(selectedSeason.value);
        if (selectedSeason.value === null || selectedSeason.value.id === null) return undefined;
        return selectedSeason.value.id;
    })

    const playoffFormat = computed(() => {
        return selectedSeason.value.playoff_format;
    })

    const playoffLines = computed(() => {
        if (playoffFormat.value === undefined) return [];
        if (seasonsMappings[playoffFormat.value] == undefined) return [];
        return seasonsMappings[playoffFormat.value].playoffLines
    })

    function setSelectedSeasonById(id) {
        const teamStore = useTeamsStore();
        selectedSeason.value = seasons.value.find(element => element.id == id)
        localStorage.setItem('selectedSeason', JSON.stringify(selectedSeason.value))
        teamStore.getTeams();
    }

    function setSelectedSeason(season) {
        const teamStore = useTeamsStore();
        selectedSeason.value = season
        localStorage.setItem('selectedSeason', JSON.stringify(selectedSeason.value))
        teamStore.getTeams();
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
            selectedSeason.value = payload !== null ? payload[1] : allSeasons[1]
            localStorage.setItem('selectedSeason', JSON.stringify(selectedSeason.value))
            seasons.value = allSeasons;
            localStorage.setItem('allSeasons', JSON.stringify(allSeasons));
            

        } catch (error) {
            console.log(error);
            seasons.value = {error};
        }
    }
    return {
        selectedSeason,
        seasons,
        seasonId,
        playoffFormat,
        playoffLines,
        setSelectedSeason,
        setSelectedSeasonById,
        getSeasons,
    }
})
