import { useTeamsStore } from "@/stores/teams.store";

import cup_22 from '../tournament_templates/cup_template_22_teams.json';
import cup_16 from '../tournament_templates/cup_template_16_teams.json';
import cup_12 from '../tournament_templates/cup_seeded_template_12_teams.json';
import cup_8 from '../tournament_templates/cup_template_8_teams.json';
import cup_6 from '../tournament_templates/cup_seeded_template_6_teams.json';
import cup_4 from '../tournament_templates/cup_template_4_teams.json';
import super_cup_15 from '../tournament_templates/super_cup_template_15_teams.json';

const seasons_mapping = {
    1: cup_16,
    2: cup_8,
    3: cup_4,
    4: cup_22,
    5: cup_6,
    6: cup_12,
    7: super_cup_15
}

const baseUrl = 'http://localhost:8000/api/seasons' // TODO: change this to .env variable

export const useNavBarStore = defineStore('navbar', () => {
    const selectedSeason = ref({});
    const seasonId = ref(null);
    const seasons = ref([]);
    const currentSeasonId = ref(null);
    const loaded = ref(false);

    const playoffFormat = computed( () => {
        return selectedSeason.value.playoff_format;
    })

    const playoffLines = computed(() => {
        if (playoffFormat.value === undefined) return [];
        return seasons_mapping[playoffFormat.value].playoffLines
    })

    function setSelectedSeason(season) {
        const teamStore = useTeamsStore();

        selectedSeason.value = season
        seasonId.value = season.value
        localStorage.setItem('seasonId', seasonId)

        teamStore.getTeams();

        // router.push('/').catch(() => { // TODO
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
            selectedSeason.value = payload !== null ? payload[1] : allSeasons[1]
            seasonId.value = selectedSeason.value.value;
            currentSeasonId.value = seasonId.value
            localStorage.setItem('allSeasons', JSON.stringify(allSeasons));
            seasons.value = allSeasons;
            loaded.value = true;

        } catch (error) {
            console.log(error);
            seasons.value = {error};
        }
    }
    return {
        selectedSeason,
        seasons,
        loaded,
        seasonId,
        currentSeasonId,
        playoffFormat,
        playoffLines,
        setSelectedSeason,
        getSeasons,
    }
})
