<template>
  <v-dialog v-model="dialog" persistent width="600px">
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        @click="dialog = !dialog"
        v-bind="activatorProps"
        class="hidden-lg-and-up mb-5 ml-1" 
        width="100%"
      >
        Log In
      </v-btn>
      <v-btn
        @click="dialog = !dialog"
        class="hidden-md-and-down" 
        v-bind="activatorProps"
      >
        Log in
      </v-btn>
    </template>
    <v-card
      title="Log In"
    >
      <v-alert
        :value="authStore.alert"
        type="info"
        transition="scale-transition"
        outlined
      >
        Invalid user credentials.
      </v-alert>
      <v-container>
        <v-layout>
          <v-row>
            <v-col cols="7">
              <v-text-field 
                v-model="authStore.credentials.username" 
                color="red darken-1" 
                label="Email*" 
                required
              />
            </v-col>
            <v-spacer />
            <v-col cols="5">
              <v-text-field
                v-model="authStore.credentials.password"
                label="Password*"
                type="password"
                color="red darken-1"
                required
              />
            </v-col>
          </v-row>
        </v-layout>
      </v-container>
      <small class="ml-2">*indicates required field</small>
      <template v-slot:actions>
        <v-btn color="red darken-1" text @click="authStore.logIn()">Log in</v-btn>
        <v-btn color="red darken-1" text @click="dialog = !dialog, authStore.alert = !authStore.alert">Close</v-btn>
      </template>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.store';

const dialog = ref(false);

const authStore = useAuthStore();

// if (localStorage.role_id && localStorage.user_id) {
//   this.$session.set('role_id', localStorage.role_id)
//   this.$session.set('user_id', localStorage.user_id)
//   this.changeLogin(localStorage.player_name)
// }
// if (localStorage.csrfToken) {
//   this.$session.set('csrf', localStorage.csrfToken)
// }
</script>
