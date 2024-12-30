import { fetchNewToken, getCookie, useAuthStore } from '@/stores/auth.store';

const baseUrl = `${import.meta.env.VITE_API_URL}/register/`;

export const useRegisterStore = defineStore('register', () => {
    // TODO Register alert and use it in register page
    const errors = ref([]);
    const response_errors = ref([]);
    const credentials = ref({});
    const loading = ref(false);

    async function register() {
      loading.value = true;
      credentials.value['number'] = 99;
      fetchNewToken();
      try {
          const requestOpt = {
              'method': 'POST',
              'headers': {
                  'X-CSRFToken': getCookie('csrftoken'),
                  'Content-Type': 'application/json',
              },
              'body': JSON.stringify(credentials.value),
              withCredentials: true,
          };
          
          const response = await fetch(baseUrl, requestOpt);

          if (!response.ok) {
            response_errors.value = response.body;
            loading.value = false;
            return false;
          }

          const isJson = response.headers?.get('Content-Type')?.includes('application/json');
          const data = isJson ? await response.json() : null;
          
          
          if (data) {
              console.log(data)
              const authStore = useAuthStore();
              authStore.changeLogin(data.user.id, data.role, null, data.user.player_name);
          }
          loading.value = false;
          return true;
      } catch (error) {
          console.log(error)
      } finally {
        loading.value = false;
        return false;
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
