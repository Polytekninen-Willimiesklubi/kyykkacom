import { useNavBarStore } from "@/stores/navbar.store";
import { useTeamsStore } from "@/stores/teams.store";
// @ts-ignore TODO meta.env is vite/client special and should be in config file setup somehow
const baseUrl = `${import.meta.env.VITE_API_URL}/matches/`;

export default defineStore('matches', () => {
    const matches = ref([]);
    const selection = ref('Kaikki ottelut');
    const loaded = ref(false);
    const loading = ref(false);
    const selectedBrackets = ref([]);
    const timeFilterMode = ref(null);

    const superWeekendMatches = computed(() => {
        return matches.value.filter((match) => match.match_type >= 31);
    });

    const regularSeasonMatches = computed(() => {
        return matches.value.filter((match) => !match.post_season && match.match_type < 31);
    });

    const excludingSuperMatches = computed(() => {
        return matches.value.filter((match) => match.match_type < 31);
    });

    const postSeasonMatches = computed(() => {
        return matches.value.filter((match) => match.post_season);
    });

    const selectedMatches = computed(() => {
        if (selection.value === 'Runkosarja') {
            return selectionFilttering(regularSeasonMatches.value);
        } else if (selection.value === 'Pudotuspelit') {
            return postSeasonMatches.value;
        } else if (selection.value === 'SuperWeekend') {
            return superWeekendMatches.value;
        } else {
            return selectionFilttering(matches.value);
        }
    });

    async function getMatches() {
        loading.value = true;
        const navStore = useNavBarStore();

        // TODO Move this away
        const pelit = {
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
    };

    function setSelectedBracket(bracket) {
        if (selectedBrackets.value.includes(bracket)) {
            selectedBrackets.value = selectedBrackets.value.filter(b => b !== bracket);
        } else {
            selectedBrackets.value.push(bracket);
        }
    };

    // Internal function. No need to export
    function selectionFilttering(matches) {
        if (!selectedBrackets.value.length && !timeFilterMode.value) {
            return matches;
        }
        const teamStore = useTeamsStore();
        const accetableTeamIds = teamStore.bracketedTeams
            .filter((_, i) => selectedBrackets.value.includes(i) || !selectedBrackets.value.length)
            .flatMap(innerList => innerList.map(obj => obj.id));
        const filtteredTeamsByBracket = matches
            .filter((match) =>
                accetableTeamIds.includes(match.home_team.id) || accetableTeamIds.includes(match.away_team.id)
            );
        const today = new Date();
        let startTime;
        let endTime;
        if (!timeFilterMode.value) {
            return filtteredTeamsByBracket;
        } else if (timeFilterMode.value === 3) { // today
            startTime = today.getDate();
            endTime = startTime + 1;
        } else if (timeFilterMode.value === 4 || timeFilterMode.value === 6) { // this week and next
            // Find out what day is monday relative to this day
            const dayOfWeek = today.getDay();
            const diffToMonday = (dayOfWeek === 0 ? -6 : 1) - dayOfWeek; // Siirry maanantaihin
            startTime = today.getDate() + diffToMonday;
            if (timeFilterMode.value === 6) {
                startTime += 7;
            }
            endTime = startTime + 7;
        } else if (timeFilterMode.value === 5) { // tomorrow
            startTime = today.getDate() + 1;
            endTime = startTime + 1;
        } else {
            throw new Error("Something went wrong");
        }
        const timeStart = new Date(today.getFullYear(), today.getMonth(), startTime);
        const timeEnd = new Date(today.getFullYear(), today.getMonth(), endTime);
        return filtteredTeamsByBracket.filter(match => {
            const timestampDate = new Date(match.match_time);
            return timestampDate >= timeStart && timestampDate < timeEnd;
        });
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
        selectedBrackets,
        timeFilterMode,
        getMatches,
        setSelectedBracket,
    };

});