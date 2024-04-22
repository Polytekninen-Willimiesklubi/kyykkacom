import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { useNavBarStore } from "./navbar.store";
import { getCookie, fetchNewToken } from '@/stores/auth.store';


const baseUrl = 'http://localhost:8000/api/teams/'; // TODO: change this to .env variable
const reserveUrl = 'http://localhost:8000/api/reserve/';

export const useTeamStore = defineStore('joukkue', () => {
    const teamId = ref(null);
    const allTimeStats = ref({});
    const seasonsStats = ref({});
    const selectedSeasonId = ref(null);
    const unReservedPlayers = ref([]);

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

    const seasonPlayers = computed( () => {
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
    })

    async function getPlayers() {
        const navStore = useNavBarStore();

        const question = teamId.value + '/?seasons=' + navStore.seasonId; // TODO this doesen't need season id?
        const response = await fetch(baseUrl + question, {method: 'GET'});
        const payload = await response.json();

        for (const [key, value] of Object.entries(payload)) {
            if (key === 'all_time') {
              allTimeStats.value = value;
            } else {
              seasonsStats.value[key] = value;
            }
        }
    }

    async function getReserve() {
        try {
            const response = await fetch(reserveUrl, {method: 'GET'});
            const payload = await response.json();
    
            unReservedPlayers.value = payload.filte((ele) => {ele.team.current_name !== ''}) 
        } catch (error) {
            console.log(error)
        }
    }

    async function reservePlayer(player)  {
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
            'body': JSON.stringify({ player : player.id }),
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
            
            const index = unReservedPlayers.value.findIndex(player => player.id === item.id);
            const player = unReservedPlayers.value.splice(index, 1);
            seasonsStats[navStore.currentSeasonId].players.push(player);

        } catch(error) {
            console.log(error)
        }
    }
    return {
        teamId,
        allTimeStats,
        seasonsStats,
        selectedSeasonId,
        unReservedPlayers,
        seasonStats,
        seasonPlayers,
        teamName,
        matches,
        getPlayers,
        getReserve,
        reservePlayer,
    }
})