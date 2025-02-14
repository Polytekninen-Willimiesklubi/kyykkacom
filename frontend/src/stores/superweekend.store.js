import { useNavBarStore } from "./navbar.store";
import { seasonsMappings } from '../tournament_templates/index'

const baseUrl = `${import.meta.env.VITE_API_URL}/superweekend/`;
const teamUrl = `${import.meta.env.VITE_API_URL}/teams/`;

export const useSuperStore = defineStore('superweekend', () => {
    const noBrackets = ref(0);
    const format = ref(null);
    const teams = ref(null);
    const dataLoaded = ref(false);
    const teamsLoaded = ref(false);
    const isBronze = ref(null);
    const superId = ref(null);

    const seededTeams = computed(() => {
        if (teams.value === null) return [];
        const seeded = [[]];
        teams.value.forEach((team) => {
            seeded[0].push([team.current_abbreviation, team.super_weekend_playoff_seed])
        })
        return seeded;
    })

    const loaded = computed(() => {
        return dataLoaded.value && teamsLoaded.value;
    });

    const bracketedTeams = computed(() => {
        if (teams.value === null || !teamsLoaded.value || !noBrackets.value) return [];
        const allBrackets = [];
        for (let i = 0; i < noBrackets.value; i++) {
            allBrackets.push([]);
        }
        teams.value.forEach((team) => {
            if (team.super_weekend_bracket && team.super_weekend_bracket > 0) {
                allBrackets[team.super_weekend_bracket - 1].push(team);
            }
        })
        allBrackets.forEach(
            bracket => bracket.sort((a, b) =>
                a.super_weekend_bracket_placement - b.super_weekend_bracket_placement
            )
        );
        allBrackets.forEach(
            bracket => bracket.forEach((ele, index) => { ele.order = index + 1 })
        );
        return allBrackets;
    });

    const bracket = computed(() => {
        if (format.value === null) return [];
        return seasonsMappings[format.value].one_bracket;
    })

    const playoffLines = computed(() => {
        if (!format.value) return [];
        return seasonsMappings[format.value].playoffLines
    })

    async function getData() {
        dataLoaded.value = false;
        const navStore = useNavBarStore();
        // const question = '?season=' + navStore.seasonId;
        const question = '?season=24&super_weekend=1';
        const response = await fetch(baseUrl + question, { method: 'GET' });
        const payload = await response.json();

        noBrackets.value = payload.super_weekend_no_brackets;
        superId.value = payload.id
        format.value = payload.super_weekend_playoff_format;
        if (!Object.keys(seasonsMappings).includes(format.value)) {
            dataLoaded.value = true;
            return
        }

        isBronze.value = seasonsMappings[format].bronze;

        dataLoaded.value = true;
    }

    async function getSuperTeams() {
        teamsLoaded.value = false;
        const navStore = useNavBarStore();
        const question = '?season=' + navStore.seasonId + '&super_weekend=1';
        const response = await fetch(teamUrl + question, { method: 'GET' });
        const payload = await response.json();

        teams.value = payload;

        teamsLoaded.value = true;
    }

    async function getAllData() {
        getSuperTeams();
        await getData();
        return true;
    }

    return {
        noBrackets,
        superId,
        format,
        teams,
        dataLoaded,
        teamsLoaded,
        isBronze,
        loaded,
        bracketedTeams,
        bracket,
        seededTeams,
        playoffLines,
        getData,
        getSuperTeams,
        getAllData,
    }
});