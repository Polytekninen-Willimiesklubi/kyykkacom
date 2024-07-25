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
        if (seasons_mapping[playoffFormat.value] == undefined) return [];
        return seasons_mapping[playoffFormat.value].playoffLines
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
