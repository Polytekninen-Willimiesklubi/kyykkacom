const teamPatchUrl = `${import.meta.env.VITE_API_URL}/kyykka_admin/team/update/`;
const superUrl = `${import.meta.env.VITE_API_URL}/kyykka_admin/superweekend/`;
const matchUrl = `${import.meta.env.VITE_API_URL}/kyykka_admin/match`;
import { getCookie, fetchNewToken } from '@/stores/auth.store';
import { useTeamsStore } from '@/stores/teams.store';
import { useSuperStore } from '@/stores/superweekend.store';

export const gameTypes = [
    { name: 'Alkulohko', value: 31 },
    { name: 'Finaali', value: 32 },
    { name: 'Pronssi', value: 33 },
    { name: 'Välierä', value: 34 },
    { name: 'Puolivälierä', value: 35 },
    { name: 'Neljännesvälierä', value: 36 },
    { name: 'Kahdeksannesvälierä', value: 37 }
];

export const checkScoreRules = [
    value => {
        return !isNaN(parseInt(value)) || value === '' ? true : 'Pitää olla numero!'
    },
    value => {
        return parseInt(value) <= 160 || value === '' ? true : 'Liian iso ottelutulos!'
    },
    value => {
        return parseInt(value) >= -13 || value === '' ? true : 'Liian pieni ottelutulos!'
    }
];


async function fetchWrapper(url, postData, method='PATCH') {
    const requestOpt = {
        'method': method,
        'headers': {
            'X-CSRFToken': getCookie('csrftoken'),
            'content-type': 'application/json',
        },
        'body': JSON.stringify(postData),
        withCredentials: true,
    }
    try {
        const response = await fetch(url, requestOpt);
        
        if (!response.ok && response.status === 403) {
            fetchNewToken();
            requestOpt.headers['X-CSRFToken'] = getCookie('csrftoken');
            const secondResponse = await fetch(url, requestOpt);
            if (!secondResponse.ok) {
                console.log("Post request was denied: " + secondResponse);
            }
        }
    } catch(error) {
        console.log(error)
    }
}

export const useAdminStore = defineStore('admin', () => {
    const regularSeasonTeams = ref({});
    const superWeekendTeams = ref({});
    const notInSuper = ref({});
    const flattenSuperTeams = ref({});

    function patchTeamData(postData, teamId) {
        const url = teamPatchUrl + teamId
        fetchWrapper(url, postData);
    }

    function patchSuperTeamWinner(postData, superId) {
        const url = superUrl + superId
        fetchWrapper(url, postData)
    }

    function postMatch(postData) {
        fetchWrapper(matchUrl, postData, 'POST')
    }

    /* 
    * Gets data from teamStore superStore getters and save it to writible variable 
    *    
    */
    async function getData() {
        const teamStore = useTeamsStore();
        const superStore = useSuperStore();
        const promise1 = superStore.getAllData()
        const promise2 = teamStore.getTeams();
        
        await Promise.all([promise1, promise2])
        regularSeasonTeams.value = structuredClone(toRaw(teamStore.bracketedTeams).map(ele => ele.map(toRaw)));
        superWeekendTeams.value = structuredClone(toRaw(superStore.bracketedTeams).map(ele => ele.map(toRaw)));
        flattenSuperTeams.value = structuredClone(toRaw(superWeekendTeams.value).flat())
        const jotain = teamStore.allTeams.filter(ele => !flattenSuperTeams.value.find(team => ele.id === team.id))
        notInSuper.value = structuredClone(jotain.map(toRaw));
    }

    return {
        regularSeasonTeams,
        superWeekendTeams,
        flattenSuperTeams,
        notInSuper,
        getData,
        patchTeamData,
        patchSuperTeamWinner,
        postMatch,
    }

});
