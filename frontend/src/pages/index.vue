<template>
  <v-layout>
    <div class="d-flex flex-column">
      <h1>Nationaali Kyykkä Liiga</h1>
      <lorem-ipsum />
    </div>
    <div class="d-flex right">
      <!-- <side-bar
          :no_brackets="no_brackets"
          :non-default-teams="teams"
        /> -->
    </div>
  </v-layout>
</template>

<script setup>
import { useHomeStore } from '@/stores/home.store';
import { useNavBarStore } from '@/stores/navbar.store';

const navStore = useNavBarStore(); 
const homeStore = useHomeStore();

const loadedSeason = localStorage.loadedSeason;
if (loadedSeason !== navStore.seasonId || !localStorage.allTeams) {
  homeStore.getTeams();
  localStorage.loadedSeason = navStore.seasonId;
}

</script>

<style>
.right {
    padding-right: 3em;
    padding-top: 6em;
}
.layout {
    margin-bottom: 1em;
}
</style>
