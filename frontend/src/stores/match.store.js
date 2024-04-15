import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { useAuthStore } from '@/stores/auth.store';

// const baseUrl = `${import.meta.env.VITE_API_URL}/api/teams/`;

const baseUrl = 'http://localhost:8000/api/matches/'; // TODO: change this to .env variable

export const useMatchStore = defineStore('match', () => {
    const matchData = ref({'jotain' : 'moi'});
    const dataReady = ref(false);
    
    const isAwayCaptain = computed(() => {
        const authStore = useAuthStore();
        return authStore.isCaptain && authStore.teamId === matchData.value.away_team.id;
    })

    async function getMatchData() {
        try {
            const splittedUrl = location.href.split('/')
            const index = splittedUrl[splittedUrl.length - 1]
            const response = await fetch(baseUrl + index, {method: 'GET'});
            const payload = await response.json();

            matchData.value = payload;
            dataReady.value = true;

        } catch(error) {
            console.log(error)
        }
    }

    return {
        matchData,
        dataReady,
        isAwayCaptain,
        getMatchData,
    }
});