<template>
  <v-dialog v-model="dialog" persistent width="600px">
    <template #activator="{ props: activatorProps }">
      <v-btn
        @click="dialog = !dialog"
        v-bind="activatorProps"
        text="Kirjaudu"
        class="hidden-lg-and-up mb-5 ml-1" 
        width="100%"
      />
      <v-btn
        @click="dialog = !dialog"
        v-bind="activatorProps"
        class="hidden-md-and-down"
        text="Kirjaudu"
      />
    </template>
    <v-card title="Kirjaudu sisään">
      <v-container>
        <v-row>
          <v-col>
            <v-alert 
              :model-value="authStore.alert" 
              type="error" 
              transition="scale-transition" 
              outlined
            >
              <b>Kirjautuminen epäonnistui</b>
            </v-alert>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="7">
            <v-text-field 
              v-model="authStore.credentials.username" 
              color="red darken-1" 
              label="Sähköposti" 
              required
            />
          </v-col>
          <v-spacer />
          <v-col cols="5">
            <v-text-field
              v-model="authStore.credentials.password"
              label="Salasana"
              type="password"
              color="red darken-1"
              required
            />
          </v-col>
        </v-row>
      </v-container>
      <template #actions>
        <v-container>  
          <v-btn
            color="red darken-1" 
            text="Kirjaudu" 
            @click="authStore.logIn()"
          />
          <v-btn
            color="red darken-1"
            text="Sulje"
            @click="dialog = !dialog, authStore.alert = false"
          />
        </v-container>
      </template>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.store';

const dialog = ref(false);

const authStore = useAuthStore();

</script>
