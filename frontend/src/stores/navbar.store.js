import { useTeamsStore } from "@/stores/teams.store";
import { seasonsMappings } from "@/tournament_templates";
// @ts-ignore TODO meta.env is vite/client special and should be in config file setup somehow
const baseUrl = `${import.meta.env.VITE_API_URL}/seasons`;

export const useNavBarStore = defineStore('navbar', () => {
    const selectedSeason = ref(JSON.parse(localStorage.getItem('selectedSeason')) ? JSON.parse(localStorage.getItem('selectedSeason')) : []);
    const seasons = ref(JSON.parse(localStorage.getItem('allSeasons')) ? JSON.parse(localStorage.getItem('allSeasons')) : []);
    const loaded = ref(true);

    const seasonId = computed(() => {
        if (selectedSeason.value === null || selectedSeason.value.id === null) return undefined;
        return selectedSeason.value.id;
    });

    const playoffFormat = computed(() => {
        return selectedSeason.value.playoff_format;
    });

    const noBrackets = computed(() => {
        return selectedSeason.value.no_brackets;
    });

    const playoffLines = computed(() => {
        if (playoffFormat.value === undefined) return [];
        if (seasonsMappings[playoffFormat.value] == undefined) return [];
        return seasonsMappings[playoffFormat.value].playoffLines
    });

    const secondStagePlayoffLines = computed(() => {
        if (playoffFormat.value === undefined) return [];
        if (seasonsMappings[playoffFormat.value] == undefined) return [];
        return seasonsMappings[playoffFormat.value].second_playofflines
    });

    async function setSelectedSeasonById(id) {
        const teamStore = useTeamsStore();
        if (seasons.value === null) {
            loaded.value = false;
            await getSeasons();

        }
        selectedSeason.value = seasons.value.find(element => element.id == id)
        localStorage.setItem('selectedSeason', JSON.stringify(selectedSeason.value))
        teamStore.getTeams();
        loaded.value = true;
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
                var response = await fetch(baseUrl, { method: 'GET' });
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
            seasons.value = { error };
        }
    }
    return {
        selectedSeason,
        seasons,
        loaded,
        seasonId,
        noBrackets,
        playoffFormat,
        playoffLines,
        secondStagePlayoffLines,
        setSelectedSeason,
        setSelectedSeasonById,
        getSeasons,
    }
})
