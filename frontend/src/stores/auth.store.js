const baseUrl = `${import.meta.env.VITE_API_URL}/login/`;

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
    await fetch('api/csrf/', { credentials: 'include' })
}

export const useAuthStore = defineStore('auth', () => {
    const userId = ref(JSON.parse(localStorage.getItem("userId")));
    const roleId = ref(JSON.parse(localStorage.getItem('roleId')));
    const teamId = ref(JSON.parse(localStorage.getItem('teamId')));
    const playerName = ref(JSON.parse(localStorage.getItem('playerName')));
    const loggedIn = ref(JSON.parse(localStorage.getItem('loggedIn')));

    const alert = ref(false);
    // const valid = ref(true);
    // const loading = ref(false);
    const credentials = ref({});

    const isCaptain = computed(() => {
        return roleId.value === 1;
    });

    const isSuperUser = computed(() => {
        return roleId.value === 2;
    })

    async function logIn(again = false) {
        alert.value = false;
        try {
            const response = await fetch(
                baseUrl,
                {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(credentials.value),
                    credentials: 'include',
                },
            );

            const isJson = response.headers?.get('content-type')?.includes('application/json');
            const data = isJson ? await response.json() : null;

            if ([401, 403].includes(response.status)) {
                // auto logout if 401 Unauthorized or 403 Forbidden response returned from api
                if (again) {
                    alert.value = true;
                    return false;
                }
                fetchNewToken();
                let success = logIn(true);
                if (!success) {
                    logOut();
                    alert.value = true;
                    return false;
                }
                alert.value = false;
                loggedIn.value = true;

                return true;
            } else if (response.status === 400) {
                alert.value = true;
                return false;
            }

            alert.value = false;
            if (data) {
                userId.value = data.user.id;
                roleId.value = data.role;
                teamId.value = data.team_id;
                playerName.value = data.user.player_name;
                // store user details local storage to keep user logged in between page refreshes
                localStorage.setItem('userId', JSON.stringify(data.user.id));
                localStorage.setItem('teamId', JSON.stringify(data.team_id));
                localStorage.setItem('roleId', JSON.stringify(data.role));
                localStorage.setItem('playerName', JSON.stringify(data.user.player_name));
                localStorage.setItem('loggedIn', JSON.stringify(true));
            }


            loggedIn.value = true;
            return true;

        } catch (error) {
            console.log(error);
            return false;
        }
    }

    function logOut() {
        userId.value = null;
        roleId.value = null;
        teamId.value = null;
        playerName.value = null;
        loggedIn.value = false;
        localStorage.removeItem('userId');
        localStorage.removeItem('teamId');
        localStorage.removeItem('roleId');
        localStorage.removeItem('playerName');
        localStorage.setItem('loggedIn', JSON.stringify(false));
    }

    /**
     * @param {number} userIndex
     * @param {number} role
     * @param {number | null} teamIndex
     * @param {string} name
     * @param {boolean} loginStatus
     */
    function changeLogin(userIndex, role = 0, teamIndex = null, name, loginStatus = true) {
        userId.value = userIndex;
        roleId.value = role;
        teamId.value = teamIndex;
        playerName.value = name;
        loggedIn.value = loginStatus;
        localStorage.setItem('userId', JSON.stringify(userIndex));
        localStorage.setItem('teamId', JSON.stringify(teamIndex));
        localStorage.setItem('roleId', JSON.stringify(role));
        localStorage.setItem('playerName', JSON.stringify(name));
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
        isSuperUser,
        logIn,
        logOut,
        changeLogin,
    }
})