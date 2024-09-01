import { useAuthStore } from '@/stores/auth.store';
const baseUrl = `${import.meta.env.VITE_API_URL}/api/teams/`;

export const useMatchStore = defineStore('match', () => {
    const matchData = ref({'jotain' : 'moi'});
    const dataReady = ref(false);
    
    const isAwayCaptain = computed(() => {
        const authStore = useAuthStore();
        return authStore.isCaptain && authStore.teamId === matchData.value.away_team.id;
    })

    async function getMatchData(matchIndex) {
        try {
            const response = await fetch(baseUrl + matchIndex, {method: 'GET'});
            const payload = await response.json();

            matchData.value = payload;
            dataReady.value = true;

        } catch(error) {
            console.log(error)
        }
    }

    async function validateClick() {
        if (!confirm('Oletko tyytyväinen ottelun tuloksiin?')) {
            return
        }
        
        const splittedUrl = location.href.split('/')
        const index = splittedUrl[splittedUrl.length - 1]

        const requestOpt = {
            'method': 'POST',
            'headers': {
                'X-CSRFToken': getCookie('csrftoken'),
                'content-type': 'application/json',
            },
            'body': JSON.stringify({ is_validated : true }),
            withCredentials: true,
        };
        try {
            const response = await fetch(baseUrl + index, requestOpt);
            
            if (!response.ok && response.status === 403) {
                fetchNewToken();
                requestOpt.headers['X-CSRFToken'] = getCookie('csrftoken');
                const secondResponse = await fetch(reserveUrl + question, requestOpt);
                if (!secondResponse.ok) {
                    console.log("Patch request was denied: " + secondResponse);
                }
            }
            
            matchData.value.is_validated = true;
            window.location.reload();
            location.reload();
        } catch (error) {
            console.log(error)
        }
    }

    return {
        matchData,
        dataReady,
        isAwayCaptain,
        getMatchData,
        validateClick,
    }
});