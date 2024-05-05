<template>
  <v-dialog v-model="dialog" persistent max-width="600px">
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        @click="dialog = !dialog"
        text="Register"
        v-bind="activatorProps"
        class="hidden-lg-and-up ml-1" 
        width="100%"
      />
      <v-btn
        @click="dialog = !dialog"
        text="Register"
        class="hidden-md-and-down" 
        v-bind="activatorProps"
      />
    </template>
    <v-card
      title="Rekisteröityminen"
      subtitle="Kaikki kentät pakollisia"
    >
    <!-- :model-value="registerForm" -->
    <!-- TODO JATKA TÄSTÄ register lähetys -->
      <v-form
        validate-on="submit"
        :model-value="j"
        ref="jotain"
      >
        <v-container>
          <v-row>
            <v-col cols="6">
              <v-text-field 
                color="red darken-1" 
                v-model="store.credentials.first_name" 
                :rules="[v => !!v || 'Etunimi puuttuu.']"
                label="Etunimi"
              />
            </v-col>
            <v-col cols="6">
              <!-- TODO api kysely onko username käytössä -->
              <v-text-field 
                color="red darken-1" 
                v-model="store.credentials.username" 
                :rules="[
                  v => !!v || 'Sähköposti puuttuu.',
                  v => store.validEmail(v) || 'Anna sähköposti mallia foo@bar.xyz.'
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
                v-model="store.credentials.last_name" 
                :rules="[v => !!v || 'Sukunimi puuttuu.']"
                label="Sukunimi"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                color="red darken-1"
                v-model="store.credentials.password"
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
                v-model="store.credentials.password_check"
                :rules="[
                  v => !!v || 'Anna Salasana uudelleen.',
                  () => store.credentials.password === store.credentials.password_check 
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
                :loading="store.loading"
                class="mb-2"
                color="red darken-1" 
                text="Register"
                type="submit"
                @click="jotain.isValid && store.register"
                block
              />
            </v-col>
            <v-col cols="3">
              <v-btn color="red darken-1" text="Close" @click="dialog = false" />
            </v-col>
            <v-spacer/>
          </v-row>
        </v-container>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useRegisterStore } from '@/stores/register.store';

const store = useRegisterStore();

const j = ref(null);
const jotain = ref();
const dialog = ref(false);

</script>

<style scoped>
</style>
