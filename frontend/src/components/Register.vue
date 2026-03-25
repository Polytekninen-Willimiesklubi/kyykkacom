<template>
  <v-dialog v-model="dialog" persistent max-width="600px">
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        @click="dialog = !dialog"
        text="Rekisteröidy"
        v-bind="activatorProps"
        class="hidden-lg-and-up ml-1" 
        width="100%"
      />
      <v-btn
        @click="dialog = !dialog"
        text="Rekisteröidy"
        class="hidden-md-and-down" 
        v-bind="activatorProps"
      />
    </template>
    <v-card
      title="Rekisteröityminen"
      subtitle="Kaikki kentät pakollisia"
    >
      <v-form
        validate-on="submit"
        @submit.prevent="awaitSubmitCheck()"
        ref="form"
      >
        <v-container>
          <v-row>
            <v-col>
              <v-alert 
                :model-value="alert" 
                type="error" 
                transition="scale-transition" 
                outlined
              >
                <b>Jotain meni pieleen. Mahdollisesti email on jo käytössä.</b>
              </v-alert>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field 
                color="red darken-1" 
                v-model="credentials.first_name" 
                :rules="[v => !!v || 'Etunimi puuttuu.']"
                label="Etunimi"
              />
            </v-col>
            <v-col cols="6">
              <!-- TODO api kysely onko username käytössä -->
              <v-text-field 
                color="red darken-1" 
                v-model="credentials.username" 
                :rules="[
                  v => !!v || 'Sähköposti puuttuu.',
                  v => validEmail(v) || 'Anna sähköposti mallia foo@bar.xyz'
                ]"
                label="Sähköposti"
                type="email"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field 
                color="red darken-1" 
                v-model="credentials.last_name" 
                :rules="[v => !!v || 'Sukunimi puuttuu.']"
                label="Sukunimi"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                color="red darken-1"
                v-model="credentials.password"
                :rules="[
                  v => !!v || 'Salasana puuttuu.',
                  v => v.length >= 6 || 'Salasana pitää olla vähintään 6 merkkiä pitkä.'
                ]"
                label="Salasana"
                type="password"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-spacer/>
            <v-col cols="6">
              <v-text-field
                color="red darken-1"
                v-model="credentials.password_check"
                :rules="[
                  v => !!v || 'Anna Salasana uudelleen.',
                  () => credentials.password === credentials.password_check 
                    || 'Salasanat eivät täsmää.',
                ]"
                label="Salasana uudelleen"
                type="password"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-spacer/>
            <v-col cols="3">
              <v-btn
                :loading="loading"
                class="mb-2"
                color="red darken-1"
                text="Register"
                type="submit"
                block
              />
            </v-col>
            <v-col cols="3">
              <v-btn 
                color="red darken-1" 
                text="Close" 
                @click="dialog = false; alert = false" 
              />
            </v-col>
            <v-spacer/>
          </v-row>
        </v-container>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { VForm } from 'vuetify/components';
import { fetchWrapper, getPayload } from '@/utils/fetchWrapper';
import { useAuthStore } from '@/stores/auth.store';
const registerAPIUrl = `${import.meta.env.VITE_API_URL}/register/`;

interface Credentials {
  first_name?: string;
  last_name?: string;
  username?: string;
  password?: string;
  password_check?: string;
  number: number;
  [key: string]: any;
}

const credentials = ref < Credentials > ({
  number: 0,
});
const loading = ref < boolean > (false);
const alert = ref < boolean > (false);

const form = ref < InstanceType < typeof VForm > | null > (null);
const dialog = ref(false);

async function register() {
  loading.value = true;
  try {
    const response = await fetchWrapper(registerAPIUrl, credentials.value, 'POST');
    if (response && response.ok) {
      alert.value = false;
      const data = await getPayload(response);
      if (data && data.user) {
        const authStore = useAuthStore();
        authStore.changeLogin(data.user.id, data.role, null, data.user.player_name);
      }
    } else {
      alert.value = true;
    }
  } catch (error) {
    alert.value = true;
  } finally {
    loading.value = false;
  }
}
async function awaitSubmitCheck() {
  (await form.value?.validate())?.valid && await register();
}

function validEmail(email: string): boolean {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}


</script>
