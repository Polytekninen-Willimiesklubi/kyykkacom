import { ref } from "vue";
import { defineStore } from "pinia";
import { fetchNewToken, getCookie, useAuthStore } from '@/stores/auth.store';

const baseUrl = 'http://localhost:8000/api/register'; // TODO: change this to .env variable


export const useRegisterStore = defineStore('register', () => {
    const alert = ref(false);
    const errors = ref([]);
    const response_errors = ref([]);
    const credentials = ref({});

    async function register(again=false) {
        fetchNewToken();
        try {
            const requestOpt = {
                'method': 'POST',
                'headers': {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                'content-type': 'application/json',
                'body': JSON.stringify(credentials),
                withCredentials: true,
            };
            
            const response = await fetch(baseUrl, requestOpt);

            if (!response.ok) {
                if (again) {
                    return false;
                }
                response_errors.value = response.body;
                success = checkFrom(true);
                if (!success) {
                    return false;
                }
            }

            const isJson = response.headers?.get('content-type')?.includes('application/json');
            const data = isJson ? await response.json() : null;

            if (data) {
                const authStore = useAuthStore();
                const payload = data.body 
                authStore.changeLogin(payload.user.id, payload.role, null, payload.player_name)
            }

            return true;
        } catch (error) {
            console.log(error)
        }
    }

    function checkFrom() {
        errors.value = [];

        if (!alertState.value) {
          alertState.value = !alertState.value;
        }
        if (response_errors.value.username == 'This field must be unique.') {
          errors.value.push('Sähköposti on jo käytössä.');
        }
        if (!credentials.value.first_name) {
          errors.value.push('Etunimi puuttuu.');
        }
        if (!credentials.value.last_name) {
          errors.value.push('Sukunimi puuttuu.');
        }
        if (!credentials.value.username) {
          errors.value.push('Sähköposti puuttuu.');
        } else if (!validEmail()) {
          errors.value.push('Anna sähköposti mallia foo@bar.xyz.');
        }
        if (!credentials.value.password) {
          errors.value.push('Salasana puuttuu.');
        }
        if (!credentials.value.number && credentials.value.number != 0) {
          errors.value.push('Pelaajanumero puuttuu.');
        }
        if (credentials.value.password !== credentials.value.password_check) {
          errors.value.push('Salasanat eivät täsmää.');
        }
        if (errors.value.length == 0) {
          register();
        }
    }

    function validEmail() {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }
    return {
        credentials,
        errors,
        response_errors,
        credentials,
        alert,
        register,
        checkFrom,
        validEmail,
    }
})
