import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LoginCredentials, LoginResponse } from '@/types/api'
import { fetchWrapper } from '@/utils/fetchWrapper'
import { getLocal, setLocalWithRef, removeLocalAndNullRef } from '@/utils/localUtils'

const baseUrl = `${import.meta.env.VITE_API_URL}/login/`;

export const useAuthStore = defineStore('auth', () => {
    // Store user details local storage to keep user logged in between page refreshes
    const userId = ref<number | null>(getLocal('userId'));
    const roleId = ref<number | null>(getLocal('roleId'));
    const teamId = ref<number | null>(getLocal('teamId'));
    const teamSeasonId = ref<number | null>(getLocal('teamSeasonId'));
    const playerName = ref<string | null>(getLocal('playerName'));
    const loggedIn = ref<boolean>(getLocal('loggedIn') || false);
    const alert = ref<boolean>(false);
    const credentials = ref<LoginCredentials>({ username: '', password: '' });

    const isCaptain = computed<boolean>(() => roleId.value === 1);
    const isSuperUser = computed<boolean>(() => roleId.value === 2);

    async function logIn(): Promise<void> {
        alert.value = false;
        try {
            const payload = await fetchWrapper(baseUrl, credentials.value, 'POST', true);
            if (payload === undefined || payload === null) {
                alert.value = true;
                changeLogin();
                return;
            }

            const data = payload as LoginResponse;
            if (data) {
                changeLogin(
                    true,
                    data.user.id,
                    data.role,
                    data.team_id,
                    data.user.player_name,
                    data.team_season_id,
                );
            } else {
                console.error("Login data is null or undefined:", data);
                alert.value = true;
                changeLogin();
                return;
            }
        } catch (error) {
            changeLogin();
            alert.value = true;
            console.error(error);
        }
    }

    /** Alias to `changeLogin()` */
    function logOut(): void {
        changeLogin();
    }

    /** Change login status and update user details. Defaults to logging out.*/
    function changeLogin(
        loginStatus: boolean = false,
        userIndex: number | null = null,
        role: number | null = null,
        teamIndex: number | null = null,
        name: string | null = null,
        teamSeasonIdValue: number | null = null,
    ): void {
        if (loginStatus) {
            setLocalWithRef('userId', userIndex, userId);
            setLocalWithRef('teamId', teamIndex, teamId);
            setLocalWithRef('teamSeasonId', teamSeasonIdValue, teamSeasonId);
            setLocalWithRef('roleId', role, roleId);
            setLocalWithRef('playerName', name, playerName);
            setLocalWithRef('loggedIn', loginStatus, loggedIn);
        } else {
            removeLocalAndNullRef('userId', userId);
            removeLocalAndNullRef('roleId', roleId);
            removeLocalAndNullRef('teamId', teamId);
            removeLocalAndNullRef('teamSeasonId', teamSeasonId);
            removeLocalAndNullRef('playerName', playerName);
            setLocalWithRef('loggedIn', false, loggedIn);
        }
    }

    return {
        userId,
        roleId,
        teamId,
        teamSeasonId,
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
