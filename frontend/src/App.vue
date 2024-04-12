<template>
  <v-app>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
 </template>

<script setup>
import {useNavBarStore} from '@/stores/navbar.store';

const store = useNavBarStore() 

if (!store.seasonId) {
  // Index starts at 1 : 2000
  store.seasonId = new Date().getFullYear() - 2000 + 1;
}

</script>

<style>

#app {
    background: url('./src/assets/kyykka_background.jpg') no-repeat center center fixed;
    background-size: cover;
    --v-theme-background: rgba(0,0,0,0) !important;
  }
  
.v-application {
  --v-theme-background: rgba(0,0,0,0) !important;
}

</style>
