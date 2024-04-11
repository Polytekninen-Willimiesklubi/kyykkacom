import { ref } from "vue";
import { defineStore } from "pinia";
// import { router } from '@/router';

const baseUrl = `${import.meta.env.VITE_API_URL}/login/`;

function getCookie(name) {
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

async function fetchNewToken() {
    await fetch('api/csrf/', {withCredentials: true})
}

export const useAuthStore = defineStore('auth', () => {
    const userId = ref(JSON.parse(localStorage.getItem("userId")));
    const roleId = ref(JSON.parse(localStorage.getItem('roleId')));
    const teamId = ref(JSON.parse(localStorage.getItem('teamId')));
    const playerName = ref(JSON.parse(localStorage.getItem('playeName')));
    const loggedIn = ref(JSON.parse(localStorage.getItem('loggedIn')));

    async function logIn(username, password, again=false) {
        try {
            const requestOpt = {
                'method': 'POST',
                'headers': {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                'content-type': 'application/json',
                'body': JSON.stringify({
                    'username' : username,
                    'password' : password
                }),
                withCredentials: true,
            };
            
            const response = await fetch(baseUrl, requestOpt)
            
            const isJson = response.headers?.get('content-type')?.includes('application/json');
            const data = isJson ? await response.json() : null;
            
            if ([401, 403].includes(response.status) && user) {
                // auto logout if 401 Unauthorized or 403 Forbidden response returned from api
                if (again) {
                    return false
                }
                fetchNewToken();
                success = logIn(username, password, true);
                if (!success) {
                    logOut();
                    return false
                }
                loggedIn.value = true
                return true
            }

            userId.value = response.body.user_id
            roleId.value = response.body.role
            teamId.value = response.body.team_id
            playerName.value = response.body.player_name
            
            // store user details local storage to keep user logged in between page refreshes
            localStorage.setItem('user_id', JSON.stringify(response.body.user.id));
            localStorage.setItem('team_id', JSON.stringify(response.body.team_id));
            localStorage.setItem('role_id', JSON.stringify(response.body.role));
            localStorage.setItem('player_name', JSON.stringify(response.body.user.player_name));
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
        localStorage.removeItem('user')
        localStorage.removeItem('userId')
        localStorage.removeItem('teamId')
        localStorage.removeItem('roleId')
        localStorage.removeItem('playerName')
        localStorage.setItem('loggedIn', JSON.stringify(false))
    }
    return {
        userId,
        roleId,
        teamId,
        playerName,
        logIn,
        logOut
    }
})