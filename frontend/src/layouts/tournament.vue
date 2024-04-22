<!-- Only removes the sidebar. Sidebar is reused as differently in 
  these pages and shoud be rendered in the "page"- file -->
<template>
  <v-app>
    <v-main>
      <NavBar/>
      <v-layout>
        <router-view />
      </v-layout>
    </v-main>

    <!-- <AppFooter /> -->
  </v-app>
</template>

<script setup>
import { useTeamsStore } from '@/stores/teams.store';
import { useNavBarStore } from '@/stores/navbar.store';

const navStore = useNavBarStore(); 
const teamStore = useTeamsStore();

const loadedSeason = localStorage.loadedSeason;
if (loadedSeason !== navStore.seasonId || !localStorage.allTeams) {
  teamStore.getTeams();
  localStorage.loadedSeason = navStore.seasonId;
}

</script>

<style>
.left {
    padding-left: 3em;
    padding-top: 6em;
}
</style>