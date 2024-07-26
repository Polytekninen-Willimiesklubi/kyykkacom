<template>
  <v-app class="pt-10">
    <NavBar/>
    <v-main class="content">
      <v-layout class="pa-10">
        <router-view class="pr-5"/>
        <div class="d-flex right align-self-start">
          <side-bar
            title="Runkosarja"
            :headers="headersDefaultSideBar"
            sort-by="bracket_placement"
            :sort-desc="false"
            :teams="teamStore.bracketedTeams"
            :lines="navStore.playoffLines"
            :boldingKeys="['P', 'points_total']"
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
import { headersDefaultSideBar } from '@/stores/headers';

const navStore = useNavBarStore(); 
const teamStore = useTeamsStore();

</script>

<style>
</style>
