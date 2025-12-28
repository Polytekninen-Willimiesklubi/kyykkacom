import { useNavBarStore } from "@/stores/navbar.store";
import { getCookie, fetchNewToken } from '@/stores/auth.store';

const baseUrl = `${import.meta.env.VITE_API_URL}/teams/`;
const reserveUrl = `${import.meta.env.VITE_API_URL}/reserve/`;

export const useTeamsStore = defineStore('joukkue', () => {
    const allTimeStats = ref({});
    const seasonsStats = ref({});
    const allTeamsAllSeasonsStats = ref([]);
    const allTeamsAllTimeStats = ref([])
    const selectedSeasonId = ref(null);
    const unReservedPlayers = ref([]);
    const allTeams = ref(JSON.parse(localStorage.getItem('allTeams')) ? JSON.parse(localStorage.getItem('allTeams')) : []);
    const secondStage = ref(JSON.parse(localStorage.getItem('secondStage')) ? JSON.parse(localStorage.getItem('secondStage')) : []);
    const loading = ref(false);
    const loaded = ref(false);
    const singleLoading = ref(false);
    const reserveLoading = ref(false);
    const reserveAllowed = ref(true);
    const filterSetting = ref(0); // 0: All, 1: Bracket, 2: Playoff
    const aggregationSetting = ref(1); // 1: Per Season, 2: All Time

    const seasonStats = computed(() => {
        if (selectedSeasonId.value === 'allTime') {
            return allTimeStats.value;
        }
        const returnValue = Object.keys(seasonsStats.value).length && selectedSeasonId.value
            ? seasonsStats.value[selectedSeasonId.value]
            : {};
        return returnValue;
    });

    const seasonPlayers = computed(() => {
        if (selectedSeasonId.value === 'allTime') {
            return allTimeStats.value.players;
        }
        return Object.keys(seasonsStats.value).length && selectedSeasonId.value
            ? seasonsStats.value[selectedSeasonId.value].players
            : [];
    });

    const teamName = computed(() => {
        if (selectedSeasonId.value === 'allTime') {
            const latestIndex = Math.max(...Object.keys(seasonsStats.value).map(x => +x)) //str -> int conversion
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
            returnedTeams = [allTeams.value];
        }
        returnedTeams.forEach(ele => {
            ele.forEach((e, i) => {
                e.order = i + 1;
            })
        })
        return returnedTeams;
    });

    const secondStageBrackets = computed(() => {
        const navStore = useNavBarStore();
        if (navStore.selectedSeason.playoff_format !== 8 || allTeams.value.length === 0) {
            return [[], [], []];
        }
        let returnedTeams = [[], [], []];
        secondStage.value.forEach(ele => {
            if (ele.second_stage_bracket !== null) {
                returnedTeams[ele.second_stage_bracket - 1].push(ele);
            }
        });
        returnedTeams.forEach((ele, i) => {
            ele.forEach((e, j) => {
                e.order = j + 1 + i * 12;
            })
        })
        return returnedTeams;
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

    const filteredAllResults = computed(() => {
        const values = aggregationSetting.value === 1 ? allTeamsAllSeasonsStats : allTeamsAllTimeStats;
        if (filterSetting.value === 0) {
            return values.value["all"];
        }
        else if (filterSetting.value === 1) {
            return values.value["bracket"];
        } else if (filterSetting.value === 2) {
            return values.value["playoff"];
        }
        console.log("Incorrect filter setting: " + filterSetting.value);
        return [];
    })


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
        if (navStore.seasonId === undefined || navStore.seasonId === null) {
            console.log("Season Id was undefined");
            return false;
        }
        const question = '?season=' + navStore.seasonId + '&post_season=0'
        try {
            loading.value = true;
            const response = await fetch(baseUrl + question, { method: 'GET' });
            const payload = await response.json();
            if (navStore.selectedSeason.playoff_format === 8) {
                allTeams.value = payload["first_stage"];
                secondStage.value = payload["bracket"];
            } else {
                allTeams.value = payload["bracket"];
                secondStage.value = [];
            }
            localStorage.setItem('allTeams', JSON.stringify(allTeams.value));
            localStorage.setItem('secondStage', JSON.stringify(secondStage.value));
            loading.value = false;
            loaded.value = true;
        } catch (error) {
            console.log(error);
            return false;
        } finally {
            loading.value = false;
        }
        return true;
    }

    async function getTeamsAllSeasons() {
        loading.value = true;
        loaded.value = false;
        try {
            const response = await fetch(baseUrl + "all/", { method: 'GET' });
            const payload = await response.json();

            allTeamsAllSeasonsStats.value = payload[0];
            allTeamsAllTimeStats.value = payload[1];

        } catch (error) {
            console.log(error);
            loaded.value = false;
            return false;
        } finally {
            loading.value = false;
        }
        loaded.value = true
        return true;
    }

    /**
     * Calls teams API to get one team all seasons statistics. Saves those to store attributes
     * @async
     * @param {number} teamIndex 
     * @returns {Promise<void>} 
     */
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

    async function getReserve(teamIndex) {
        reserveLoading.value = true;
        reserveAllowed.value = false;
        const requestOpt = {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include'
        };
        try {
            const question = reserveUrl + "?team=" + teamIndex
            let response = await fetch(question, requestOpt);
            if (!response.ok && response.status === 403) {
                // Make another request if token was too old
                fetchNewToken();
                requestOpt.headers['X-CSRFToken'] = getCookie('csrftoken');
                response = await fetch(question, requestOpt);
                if (!response.ok) {
                    console.log("Getting unreserved players request was denied.")
                    reserveAllowed.value = false;
                    return;
                }
            }

            const payload = await response.json();
            unReservedPlayers.value = payload.length ? payload : [];
            reserveAllowed.value = true;
        } catch (error) {
            console.log(error);
            reserveAllowed.value = false;
        } finally {
            reserveLoading.value = false;
        }
    }

    async function reservePlayer(player) {
        const navStore = useNavBarStore();
        if (!confirm('Haluatko varmasti varata pelaajan "' + player.player_name + '"?')) {
            return;
        }
        const question = '?season=' + navStore.seasonId;
        const requestOpt = {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'content-type': 'application/json',
            },
            body: JSON.stringify({ player: player.id }),
            credentials: 'include'
        };

        try {
            let response = await fetch(reserveUrl + question, requestOpt);
            if (!response.ok && response.status === 403) {
                fetchNewToken();
                requestOpt.headers['X-CSRFToken'] = getCookie('csrftoken');
                response = await fetch(reserveUrl + question, requestOpt);
                if (!response.ok) {
                    console.log("Post request to reserve player was denied: " + response);
                }
            }
            if (response.ok) {
                const index = unReservedPlayers.value.findIndex(item => player.id === item.id);
                unReservedPlayers.value.splice(index, 1);
            }
        } catch (error) {
            console.log(error);
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
        reserveAllowed,
        secondStageBrackets,
        // superWeekendBrackets,
        teamName,
        matches,
        allTeamsAllTimeStats,
        allTeamsAllSeasonsStats,
        filterSetting,
        aggregationSetting,
        filteredAllResults,
        getTeams,
        getTeamPlayers,
        getTeamsAllSeasons,
        getReserve,
        reservePlayer,
    }
})