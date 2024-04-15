import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { useAuthStore } from '@/stores/auth.store';
import { getCookie, fetchNewToken } from '@/stores/auth.store';
import { useNavBarStore } from "./navbar.store";


// const baseUrl = `${import.meta.env.VITE_API_URL}/api/teams/`;

const baseUrl = 'http://localhost:8000/api/players/'; // TODO: change this to .env variable

export const usePlayerStore = defineStore('players', () => {
    const loading = ref(false);
    const players = ref([]);

    async function getPlayers() {
        loading.value = true; 
        const navStore = useNavBarStore();
        const question = '?season=' + navStore.seasonId;
        const response = await fetch(baseUrl + question, {method : 'GET'});
        const payload = await response.json();
        
        players.value = payload;
        loading.value = false;
    } 
    return {
        loading,
        players,
        getPlayers,
    }
})