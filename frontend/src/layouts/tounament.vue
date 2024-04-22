<template>
  <v-app>
    <v-main>
      <NavBar/>
      <v-layout>
        <div class="d-flex left">
          <side-bar 
            :no_brackets="navStore.selectedSeason.no_brackets"
            :teams="teamStore.bracketedTeams"
            :lines="navStore.playoffLines"
          />
        </div>
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