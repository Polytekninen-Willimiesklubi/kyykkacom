import { useNavBarStore } from "@/stores/navbar.store";
import { useTeamsStore } from "@/stores/teams.store";
const baseUrl = `${import.meta.env.VITE_API_URL}/matches/`;


export const useMatchesStore = defineStore('matches', () => {
    const matches = ref([]);
    const selection = ref('Kaikki ottelut');
    const loaded = ref(false);
    const loading = ref(false);
    const selectedBrackets = ref([]);

    const superWeekendMatches = computed(() => {
        return matches.value.filter((match) => match.match_type >= 31);
    });

    const regularSeasonMatches = computed(() => {
        let regularSeason = matches.value.filter((match) => !match.post_season && match.match_type < 31)
        console.log("jotain2")
        if (!bracketSelected.value) {
            return regularSeason
        }
        const teamStore = useTeamsStore();
        const accetableTeamIds = teamStore.bracketedTeams.value.filter((_, i) => selectedBrackets.value.includes(i)).map(innerList => innerList.map(obj => obj.id));
        console.log("jotain4")
        console.log(teamStore.bracketedTeams)
        console.log(accetableTeamIds)
        return regularSeason.filter((match) => accetableTeamIds.includes(match.home_team.id) || accetableTeamIds.includes(match.away_team.id))
    });

    const excludingSuperMatches = computed(() => {
        return matches.value.filter((match) => match.match_type < 31);
    });

    const postSeasonMatches = computed(() => {
        return matches.value.filter((match) => match.post_season);
    });

    const selectedMatches = computed(() => {
        if (selection.value === 'Runkosarja') {
            return regularSeasonMatches.value;
        } else if (selection.value === 'Jatkosarja') {
            return postSeasonMatches.value;
        } else if (selection.value === 'SuperWeekend') {
            return superWeekendMatches.value;
        } else {
            return matches.value;
        }
    });

    async function getMatches() {
        loading.value = true;
        const navStore = useNavBarStore();

        const pelit = { // FIXME move this away
            1: 'Runkosarja',
            2: 'Finaali',
            3: 'Pronssi',
            4: 'Välierä',
            5: 'Puolivälierä',
            6: 'Neljännesvälierä',
            7: 'Kahdeksannesvälierä',
            10: 'Runkosarjafinaali',
            20: 'Jumbofinaali',
            31: 'SuperWeekend: Alkulohko',
            32: 'SuperWeekend: Finaali',
            33: 'SuperWeekend: Pronssi',
            34: 'SuperWeekend: Välierä',
            35: 'SuperWeekend: Puolivälierä',
            36: 'SuperWeekend: Neljännesvälierä',
            37: 'SuperWeekend: Kahdeksannesvälierä'
        };
        const question = '?season=' + navStore.seasonId;
        const response = await fetch(baseUrl + question, { method: "GET" });
        const payload = await response.json();

        payload.forEach(ele => {
            ele.type_name = pelit[ele.match_type];
            ele.dash = '-';
        });
        matches.value = payload;
        loaded.value = true;
        loading.value = false;
    }

    function setSelectedBracket(bracket) {
        console.log(bracket)
        if (selectedBrackets.value.includes(bracket)) {
            selectedBrackets.value = selectedBrackets.value.filter(b => b !== bracket)
        } else {
            selectedBrackets.value.push(bracket)
        }
        console.log(selectedBrackets.value)
    }

    return {
        matches,
        selection,
        loading,
        loaded,
        superWeekendMatches,
        postSeasonMatches,
        excludingSuperMatches,
        regularSeasonMatches,
        selectedMatches,
        getMatches,
        setSelectedBracket,
    };

})