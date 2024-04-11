import { ref } from "vue";
import { defineStore } from "pinia";

const baseUrl = `${import.meta.env.VITE_API_URL}/api/teams/`;

export const useHomeStore = defineStore('home', () => {
    const teams = ref([]);
    const noBrackets = ref(0);

    async function getTeams() {
        const sessionId = localStorage.sessionId
        const question = '?season=' + sessionId + '"post_season=0'

        try {
            const response = await fetch(baseUrl + question, {method: 'GET'});
            teams.value = response.data.body;
            localStorage.setItem('allTeams', JSON.stringify(allTeams));
        } catch (error) {
            console.log(error.statusText);
        }
        splitToBrackets();
    }

    function splitToBrackets() {
        if (localStorage.allSeasons) {
            const allSeasons = JSON.parse(localStorage.getItem('allSeasons'));
            const tmpIdx = allSeasons.map(ele => String(ele.id).indexOf(sessionId))
            noBrackets.value = allSeasons[tmpIdx].no_brackets
        } else {
            noBrackets.value = 1
        }
    }

    return {
        teams,
        noBrackets,
        getTeams,
    }
})