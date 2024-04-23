<template>
  <v-app>
    <NavBar/>
    <v-main class="content">
      <v-layout class="pa-10">
        <router-view class="pr-5"/>
        <div class="d-flex right">
          <side-bar 
            :no_brackets="navStore.selectedSeason.no_brackets"
            :teams="teamStore.bracketedTeams"
            :lines="navStore.playoffLines"
          />
        </div>
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
</style>
