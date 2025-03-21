import { useNavBarStore } from "@/stores/navbar.store";
import { getCookie, fetchNewToken } from '@/stores/auth.store';

const baseUrl = `${import.meta.env.VITE_API_URL}/teams/`;
const reserveUrl = `${import.meta.env.VITE_API_URL}/reserve/`;

export const useTeamsStore = defineStore('joukkue', () => {
    const allTimeStats = ref({});
    const seasonsStats = ref({});
    const selectedSeasonId = ref(null);
    const unReservedPlayers = ref([]);
    const allTeams = ref(JSON.parse(localStorage.getItem('allTeams')) ? JSON.parse(localStorage.getItem('allTeams')) : []);
    const secondStage = ref(JSON.parse(localStorage.getItem('secondStage')) ? JSON.parse(localStorage.getItem('secondStage')) : []);
    const loading = ref(false);
    const loaded = ref(false);
    const singleLoading = ref(false);
    const reserveLoading = ref(false);

    const seasonStats = computed(() => {
        if (selectedSeasonId.value === 'allTime') {
            console.log(allTimeStats.value)
            return allTimeStats.value;
        }
        const returnValue = Object.keys(seasonsStats.value).length && selectedSeasonId.value
            ? seasonsStats.value[selectedSeasonId.value]
            : {};
        return returnValue;
    });

    const seasonPlayers = computed(() => {
        if (selectedSeasonId.value === 'allTime') {
            return allTimeStats.value.players
        }
        return Object.keys(seasonsStats.value).length && selectedSeasonId.value
            ? seasonsStats.value[selectedSeasonId.value].players
            : [];
    });

    const teamName = computed(() => {
        if (selectedSeasonId.value === 'allTime') {
            const latestIndex = Math.max(...Object.keys(seasonsStats.value).map(x => +x)) //str -> int conversion
            console.log(seasonsStats.value[latestIndex])
            return seasonsStats.value[latestIndex].current_name;
        }
        return Object.keys(seasonsStats.value).length && selectedSeasonId.value
            ? seasonsStats.value[selectedSeasonId.value].current_name
            : '';
    })

    const matches = computed(() => {
        if (selectedSeasonId.value === 'allTime') {
            return allTimeStats.value.matches;
        }
        return Object.keys(seasonsStats.value).length && selectedSeasonId.value
            ? seasonsStats.value[selectedSeasonId.value].matches
            : [];
    });

    const bracketedTeams = computed(() => {
        const navStore = useNavBarStore();
        if (navStore.selectedSeason.no_brackets === 0 || allTeams.value.length === 0) {
            return []
        }
        let returnedTeams = [];
        if (navStore.selectedSeason.no_brackets > 1) {
            for (let i = 0; i < navStore.selectedSeason.no_brackets; i++) {
                returnedTeams.push([]);
            }
            allTeams.value.forEach(ele => {
                returnedTeams[ele.bracket - 1].push(ele);
            });
        } else {
            returnedTeams = [allTeams.value]
        }
        returnedTeams.forEach(ele => {
            ele.forEach((e, i) => {
                e.order = i + 1
            })
        })
        return returnedTeams
    });

    const secondStageBrackets = computed(() => {
        const navStore = useNavBarStore();
        if (navStore.selectedSeason.playoff_format !== 8 || allTeams.value.length === 0) {
            return [[], [], []]
        }
        let returnedTeams = [[], [], []];
        secondStage.value.forEach(ele => {
            if (ele.second_stage_bracket !== null) {
                returnedTeams[ele.second_stage_bracket - 1].push(ele);
            }
        });
        returnedTeams.forEach((ele, i) => {
            ele.forEach((e, j) => {
                e.order = j + 1 + i * 12
            })
        })
        return returnedTeams
    });

    const onlyPlacements = computed(() => {
        const navStore = useNavBarStore();
        if (navStore.selectedSeason.no_brackets === 0 || allTeams.value.length === 0) {
            return []
        }
        const returnedTeams = []
        for (let i = 0; i < navStore.selectedSeason.no_brackets; i++) {
            returnedTeams.push([]);
        }
        allTeams.value.forEach(ele => {
            if (ele.bracket == undefined) {
                return;
            }
            const tmp = !ele.bracket_placement ? 1 : ele.bracket_placement
            returnedTeams[ele.bracket - 1].push([ele.current_abbreviation, tmp]);
        });
        return returnedTeams
    });


    // const superWeekendBrackets = computed( () => {
    //     const navStore = useNavBarStore();
    //     if (navStore.selectedSeason.no_brackets === 0 || allTeams.value.length === 0) {
    //         return []
    //     }
    //     const returnedTeams = []
    //     if (noBrackets.value > 1) {
    //         for (let i = 0; i < navStore.selectedSeason.no_brackets; i++) {
    //             returnedTeams.push([]);
    //         }
    //         allTeams.forEach(ele => {
    //             returnedTeams[ele.super_weekend_bracket -1].push(ele);
    //         });
    //         return returnedTeams
    //     } else {
    //         return [allTeams]
    //     }
    // });

    async function getTeams() {
        const navStore = useNavBarStore();
        const question = '?season=' + navStore.seasonId + '&post_season=0'
        try {
            loading.value = true;
            const response = await fetch(baseUrl + question, { method: 'GET' });
            const payload = await response.json();
            if (navStore.selectedSeason.playoff_format === 8) {
                allTeams.value = payload[0];
                secondStage.value = payload[1];
            } else {
                allTeams.value = payload;
                secondStage.value = []
            }
            localStorage.setItem('allTeams', JSON.stringify(allTeams.value));
            localStorage.setItem('secondStage', JSON.stringify(secondStage.value));
            loading.value = false;
            loaded.value = true;
        } catch (error) {
            console.log(error);
            return false
        }
        return true
    }

    async function getTeamPlayers(teamIndex) {
        singleLoading.value = true;
        const navStore = useNavBarStore();

        const question = teamIndex + '/?seasons=' + navStore.seasonId; // TODO this doesen't need season id?
        const response = await fetch(baseUrl + question, { method: 'GET' });
        const payload = await response.json();

        let recent_year = -1
        for (const [key, value] of Object.entries(payload)) {
            if (key === 'all_time') {
                allTimeStats.value = value;
            } else {
                seasonsStats.value[key] = value;
                recent_year = Number(key) > recent_year ? Number(key) : recent_year
            }
        }
        // Select the most recent year to single team page
        selectedSeasonId.value = recent_year != -1 ? String(recent_year) : 'allTime'

        singleLoading.value = false;
    }

    async function getReserve() {
        reserveLoading.value = true;
        try {
            const response = await fetch(reserveUrl, { method: 'GET' });
            const payload = await response.json();

            unReservedPlayers.value = payload.filter((ele) => { ele.team.current_name !== '' })
        } catch (error) {
            console.log(error)
        } finally {
            reserveLoading.value = false;
        }
    }

    async function reservePlayer(player) {

        const navStore = useNavBarStore();
        if (!confirm('Haluatko varmasti varata pelaajan "' + player.player_name + '"?')) {
            return
        }

        const question = '?season=' + navStore.seasonId;
        const requestOpt = {
            'method': 'POST',
            'headers': {
                'X-CSRFToken': getCookie('csrftoken')
            },
            'content-type': 'application/json',
            'body': JSON.stringify({ player: player.id }),
            withCredentials: true,
        };
        try {
            const response = await fetch(reserveUrl + question, requestOpt);

            if (!response.ok && response.status === 403) {
                fetchNewToken();
                requestOpt.headers['X-CSRFToken'] = getCookie('csrftoken');
                const secondResponse = await fetch(reserveUrl + question, requestOpt);
                if (!secondResponse.ok) {
                    console.log("Post request was denied: " + secondResponse);
                }
            }

            const index = unReservedPlayers.value.findIndex(item => player.id === item.id);
            const reservedPlayer = unReservedPlayers.value.splice(index, 1);
            seasonsStats[navStore.seasonId].players.push(reservedPlayer);

        } catch (error) {
            console.log(error)
        }
    }
    return {
        allTeams,
        loading,
        loaded,
        allTimeStats,
        seasonsStats,
        selectedSeasonId,
        unReservedPlayers,
        seasonStats,
        seasonPlayers,
        bracketedTeams,
        onlyPlacements,
        singleLoading,
        reserveLoading,
        secondStageBrackets,
        // superWeekendBrackets,
        teamName,
        matches,
        getTeams,
        getTeamPlayers,
        getReserve,
        reservePlayer,
    }
})