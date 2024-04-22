import { getCookie, fetchNewToken } from '@/stores/auth.store';
import { useNavBarStore } from "./navbar.store";

import cup_22 from '../tournament_templates/cup_template_22_teams.json'
import cup_16 from '../tournament_templates/cup_template_16_teams.json'
import cup_12 from '../tournament_templates/cup_seeded_template_12_teams.json'
import cup_8 from '../tournament_templates/cup_template_8_teams.json'
import cup_6 from '../tournament_templates/cup_seeded_template_6_teams.json'
import cup_4 from '../tournament_templates/cup_template_4_teams.json'
import super_cup_15 from '../tournament_templates/super_cup_template_15_teams.json'

const baseUrl = 'http://localhost:8000/api/superweekend/'; // TODO: change this to .env variable
const teamUrl = 'http://localhost:8000/api/teams/';

const seasons_mapping = {
    1: cup_16,
    2: cup_8,
    3: cup_4,
    4: cup_22,
    5: cup_6,
    6: cup_12,
    7: super_cup_15
}

export const superSidebarHeaders = [
    { title: 'Sij.', key: 'super_weekend_bracket_placement' },
    { title: 'Joukkue', key: 'current_abbreviation', sortable: false, width: '10%' },
    { title: 'V', key: 'matches_won', sortable: false, width: '3%' },
    { title: 'T', key: 'matches_tie', sortable: false, width: '3%' },
    { title: 'H', key: 'matches_lost', sortable: false, width: '3%' },
    { title: 'OKA', key: 'match_average', sortable: false, width: '5%' }
];

export const useSuperStore = defineStore('superweekend', () => {
    const noBrackets = ref(0);
    const format = ref(null);
    const teams = ref(null);
    const dataLoaded = ref(false);
    const teamsLoaded = ref(false);
    const isBronze = ref(null);

    const seededTeams = computed(() => {
        if (teams.value === null) return [];
        const seeded = [];
        teams.value.forEach((team) => {
            seeded.push([team.current_abbreviation, team.super_weekend_playoff_seed])
        })
        return seeded;
    })

    const loaded = computed(() => {
        return dataLoaded.value && teamsLoaded.value;
    });

    const bracketTeams = computed(() => {
        if (teams.value === null || !teamsLoaded.value || !noBrackets.value) return [];
        const allBrackets = [];
        for (let i = 0; i < noBrackets.value; i++) {
            allBrackets.push([]);
        }
        teams.value.forEach((team) => {
            if(team.super_weekend_bracket && team.super_weekend_bracket > 0) {
                allBrackets[team.super_weekend_bracket - 1].push(team);
            }
        })
        allBrackets.forEach(
            bracket => bracket.sort((a, b) => 
                a.super_weekend_bracket_placement - b.super_weekend_bracket_placement
            )
        );
        return allBrackets;
    });

    const bracket = computed(() => {
        if (format.value === null) return [];
        return seasons_mapping[format.value].one_bracket;
    })

    const playoffLines = computed(() => {
        if (!format.value) return [];
        return seasons_mapping[format.value].playoffLines
    })

    async function getData() {
        dataLoaded.value = false;
        const navStore = useNavBarStore();
        const question = '?season=' + navStore.seasonId;
        const response = await fetch(baseUrl + question, {method : 'GET'});
        const payload = await response.json();

        noBrackets.value = payload.super_weekend_no_brackets;
        format.value = payload.super_weekend_playoff_format;
        if (!Object.keys(seasons_mapping).includes(format.value)) {
            dataLoaded.value = true;
            return
        }

        isBronze.value = seasons_mapping[format].bronze;

        dataLoaded.value = true;
    }

    async function getSuperTeams() {
        teamsLoaded.value = false;
        const navStore = useNavBarStore();
        const question = '?season=' + navStore.seasonId + '&super_weekend=1';
        const response = await fetch(teamUrl + question, {method : 'GET'});
        const payload = await response.json();

        teams.value = payload;

        teamsLoaded.value = true;
    }

    async function getAllData() {
        getSuperTeams();
        getData();
    }

    return {
        noBrackets,
        format,
        teams,
        dataLoaded,
        teamsLoaded,
        isBronze,
        loaded,
        bracketTeams,
        bracket,
        seededTeams,
        playoffLines,
        getData,
        getSuperTeams,
        getAllData,
    }
});