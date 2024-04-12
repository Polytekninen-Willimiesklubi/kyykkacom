import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { useNavBarStore } from "@/stores/navbar.store";

// const baseUrl = `${import.meta.env.VITE_API_URL}/api/teams/`;

const baseUrl = 'http://localhost:8000/api/teams/'; // TODO: change this to .env variable

export const useHomeStore = defineStore('home', () => {
    const allTeams = ref(JSON.parse(localStorage.getItem('allTeams')));
    const noBrackets = ref(0);
    const loading = ref(false);

    // Return in array of arrays. Each array contains one bracket teams 
    const bracketedTeams = computed(() => {
        if (noBrackets.value === 0 || allTeams.value.length === 0) {
            return []
        }
        const returnedTeams = []
        if (noBrackets.value > 1) {
            for (let i = 0; i < noBrackets; i++) {
                returnedTeams.push([]);
            }
            allTeams.forEach(ele => {
                returnedTeams[ele.bracket -1].push(ele);
            });
            return returnedTeams
        } else {
            return [allTeams]
        }
    })

    const superWeekendBrackets = computed( () => {
        if (noBrackets.value === 0 || allTeams.value.length === 0) {
            return []
        }
        const returnedTeams = []
        if (noBrackets.value > 1) {
            for (let i = 0; i < noBrackets; i++) {
                returnedTeams.push([]);
            }
            allTeams.forEach(ele => {
                returnedTeams[ele.super_weekend_bracket -1].push(ele);
            });
            return returnedTeams
        } else {
            return [allTeams]
        }
    }) 

    async function getTeams() {
        const navStore = useNavBarStore()
        const question = '?season=' + navStore.seasonId + '&post_season=0'
        try {
            loading.value = true;
            const response = await fetch(baseUrl + question, {method: 'GET'});
            const payload = await response.json();
            allTeams.value = payload;
            localStorage.setItem('allTeams', JSON.stringify(allTeams.value));
            loading.value = false;
        } catch (error) {
            console.log(error);
        }
    }

    return {
        allTeams,
        noBrackets,
        bracketedTeams,
        superWeekendBrackets,
        loading,
        getTeams,
    }
})