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

const teamPatchUrl = 'api/kyykka_admin/team/update/';
const superUrl = 'api/kyykka_admin/superweekend/';
const matchUrl = 'api/kyykka_admin/match';
import { getCookie, fetchNewToken } from '@/stores/auth.store';

async function fetchWrapper(url, postData, method='PATCH') {
    const requestOpt = {
        'method': method,
        'headers': {
            'X-CSRFToken': getCookie('csrftoken')
        },
        'content-type': 'application/json',
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

    return {
        patchTeamData,
        patchSuperTeamWinner,
        postMatch,
    }

});
