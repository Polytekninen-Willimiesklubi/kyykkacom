// const baseUrl = `${import.meta.env.VITE_API_URL}/login/`;
const baseUrl = 'http://localhost:8000/api/login/'; // TODO: change this to .env variable

export function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim()
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
        }
        }
    }
    return cookieValue
}

export async function fetchNewToken() {
    await fetch('api/csrf/', {withCredentials: true})
}

export const useAuthStore = defineStore('auth', () => {
    const userId = ref(JSON.parse(localStorage.getItem("userId")));
    const roleId = ref(JSON.parse(localStorage.getItem('roleId')));
    const teamId = ref(JSON.parse(localStorage.getItem('teamId')));
    const playerName = ref(JSON.parse(localStorage.getItem('playerName')) );
    const loggedIn = ref(JSON.parse(localStorage.getItem('loggedIn')));

    const alert = ref(false);
    // const valid = ref(true);
    // const loading = ref(false);
    const credentials = ref({});

    const isCaptain = computed(() => {
        return roleId.value === 1;
    });

    async function logIn(again=false) {
        try {
            const requestOpt = {
                'method': 'POST',
                'headers': {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                'body' : JSON.stringify(credentials.value),
                'withCredentials': true,
            };
            
            const response = await fetch(baseUrl, requestOpt)
            
            const isJson = response.headers?.get('content-type')?.includes('application/json');
            const data = isJson ? await response.json() : null;
            
            if ([401, 403].includes(response.status) && user) {
                // auto logout if 401 Unauthorized or 403 Forbidden response returned from api
                if (again) {
                    alert.value = true
                    return false
                }
                fetchNewToken();
                success = logIn(username, password, true);
                if (!success) {
                    logOut();
                    alert.value = true
                    return false
                }
                alert.value = false
                loggedIn.value = true

                return true
            } else if (response.status === 400) {
                return false
            }
            
            alert.value = false

            userId.value = data.user.id
            roleId.value = data.role
            teamId.value = data.team_id
            playerName.value = data.user.player_name
            
            // store user details local storage to keep user logged in between page refreshes
            localStorage.setItem('userId', JSON.stringify(data.user.id));
            localStorage.setItem('teamId', JSON.stringify(data.team_id));
            localStorage.setItem('roleId', JSON.stringify(data.role));
            localStorage.setItem('playerName', JSON.stringify(data.user.player_name));
            localStorage.setItem('loggedIn', JSON.stringify(true));

            loggedIn.value = true
            return true

        } catch (error) {
            console.log(error)
            return false
        }
    }

    function logOut() {
        userId.value = null
        roleId.value = null
        teamId.value = null
        playerName.value = null
        loggedIn.value = true
        localStorage.removeItem('userId')
        localStorage.removeItem('teamId')
        localStorage.removeItem('roleId')
        localStorage.removeItem('playerName')
        localStorage.setItem('loggedIn', JSON.stringify(false))
    }

    function changeLogin(userId, roleId, teamId, playeName, loginStatus=true) {
        userId.value = userId
        roleId.value = roleId
        teamId.value = teamId
        playerName.value = playeName
        loggedIn.value = loginStatus
        localStorage.setItem('userId', JSON.stringify(userId));
        localStorage.setItem('teamId', JSON.stringify(teamId));
        localStorage.setItem('roleId', JSON.stringify(roleId));
        localStorage.setItem('playerName', JSON.stringify(playeName));
        localStorage.setItem('loggedIn', JSON.stringify(loginStatus));
    }

    return {
        userId,
        roleId,
        teamId,
        playerName,
        loggedIn,
        alert,
        credentials,
        isCaptain,
        logIn,
        logOut,
    }
})