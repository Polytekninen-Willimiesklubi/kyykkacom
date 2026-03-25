import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth.store';
import { fetchNewToken, getCookie } from '@/utils/cookies';

const baseUrl = `${import.meta.env.VITE_API_URL}/register/`;

interface Credentials {
    first_name?: string;
    last_name?: string;
    username?: string;
    password?: string;
    password_check?: string;
    number: number;
    [key: string]: any;
}

export const useRegisterStore = defineStore('register', () => {
    const credentials = ref<Credentials>({
        number: 99, // Default number, can't be changed by user for now
    });
    const loading = ref<boolean>(false);
    const alert = ref<boolean>(false);

    async function register(): Promise<void> {
        loading.value = true;
        fetchNewToken();
        try {
            const headers: Record<string, string> = {
                'X-CSRFToken': getCookie('csrftoken') || '',
                'Content-Type': 'application/json',
            };
            const requestOpt: RequestInit = {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(credentials.value),
                credentials: 'include',
            };

            const response = await fetch(baseUrl, requestOpt);

            if (!response.ok) {
                // response_errors.value = response.body;
                alert.value = true;
            }

            const isJson = response.headers?.get('Content-Type')?.includes('application/json');
            const data = isJson ? await response.json() : null;

            if (data) {
                const authStore = useAuthStore();
                authStore.changeLogin(data.user.id, data.role, null, data.user.player_name);
            }
            alert.value = false;
        } catch (error) {
            console.log(error)
            alert.value = true;
        } finally {
            loading.value = false;
        }
    }



    return {
        credentials,
        loading,
        alert,
        register,
    }
})
