import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { useNavBarStore } from "@/stores/navbar.store";

// const baseUrl = `${import.meta.env.VITE_API_URL}/api/teams/`;

const baseUrl = 'http://localhost:8000/api/matches/'; // TODO: change this to .env variable

export const useMatchesStore = defineStore('matches', () => {
    const matches = ref([]);
    const selection = ref('Kaikki ottelut');
    const loaded = ref(false);

    const superWeekendMatches = computed(() => {
        return matches.value.filter((match) => match.match_type >= 31);
    })

    const regularSeasonMatches = computed(() => {
        return matches.value.filter((match) => !match.post_season && match.match_type < 31);
    })

    const excludingSuperMatches = computed(() => {
        return matches.value.filter((match) => match.match_type < 31);
    })

    const postSeasonMatches = computed(() => {
        return matches.value.filter((match) => match.post_season);
    })

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
        const navStore = useNavBarStore();

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
        const response = await fetch(baseUrl + question, {method: "GET"});
        const payload = await response.json();

        payload.forEach(ele => {
            ele.type_name = pelit[ele.match_type]
            ele.dash = '-'
        });
        matches.value = payload;
        loaded.value = true;
    }

    return {
        matches,
        selection,
        loaded,
        superWeekendMatches,
        postSeasonMatches,
        excludingSuperMatches,
        regularSeasonMatches,
        selectedMatches,
        getMatches
    };

})