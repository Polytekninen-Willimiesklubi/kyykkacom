import { fetchNewToken, getCookie, useAuthStore } from '@/stores/auth.store';

const baseUrl = 'http://localhost:8000/api/register/'; // TODO: change this to .env variable

export const useRegisterStore = defineStore('register', () => {
    const errors = ref([]);
    const response_errors = ref([]);
    const credentials = ref({});
    const loading = ref(false);

    async function register() {
      loading.value = true;
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
            response_errors.value = response.body;
            loading.value = false;
            return false;
          }

          const isJson = response.headers?.get('content-type')?.includes('application/json');
          const data = isJson ? await response.json() : null;

          if (data) {
              const authStore = useAuthStore();
              const payload = data.body;
              authStore.changeLogin(payload.user.id, payload.role, null, payload.player_name);
          }
          loading.value = false;
          return true;
      } catch (error) {
          console.log(error)
      } finally {
        loading.value = false;
      }
    }

    function validEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }

    return {
      credentials,
      errors,
      response_errors,
      credentials,
      loading,
      register,
      validEmail,
    }
})
