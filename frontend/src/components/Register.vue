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
    >
      <v-alert 
        :value="store.alert" 
        type="error" 
        transition="scale-transition" 
        outlined
      >
        <b>Korjaa seuraava(t):</b>
        <ul>
          <li v-bind:key="error.id" v-for="error in store.errors.value">{{ error }}</li>
        </ul>
      </v-alert>
      <v-container grid-list-md>
        <v-layout wrap>
          <v-layout row>
            <div class="d-flex xs5 sm6 md4">
              <v-text-field 
                color="red darken-1" 
                v-model="store.credentials.first_name" 
                label="Etunimi*" 
                required
              ></v-text-field>
            </div>
            <div class="d-flex xs5 sm6 md4 mr-5">
              <v-text-field 
                color="red darken-1" 
                v-model="store.credentials.last_name" 
                label="Sukunimi*" 
                required
              ></v-text-field>
            </div>
            <div class="d-flex xs2 sm2 ml-5">
              <v-select 
                item-color="red" 
                color="red darken-1" 
                v-model="store.credentials.number" 
                required 
                :items="Array.from(Array(100).keys())"
              ></v-select>
            </div>
          </v-layout>
          <div class="d-flex xs12">
            <v-text-field 
              color="red darken-1" 
              v-model="store.credentials.username" 
              label="sähköposti*" 
              type="email" 
              required
            ></v-text-field>
          </div>
          <div class="d-flex xs12">
            <v-text-field
              color="red darken-1"
              v-model="store.credentials.password"
              label="salasana*"
              type="password"
              required
            ></v-text-field>
            <v-text-field
              color="red darken-1"
              v-model="store.credentials.password_check"
              label="salasana varmistus*"
              type="password"
              required
            ></v-text-field>
          </div>
        </v-layout>
      </v-container>
      <small>*pakollinen kenttä</small>
      <v-card-actions class=justify-center>
        <v-btn color="red darken-1" text="Register" @click="store.checkForm()" />
        <v-btn color="red darken-1" text="Close" @click="dialog = !dialog" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useRegisterStore } from '@/stores/register.store';

const store = useRegisterStore();

const dialog = ref(false)

</script>

<style scoped>
</style>
