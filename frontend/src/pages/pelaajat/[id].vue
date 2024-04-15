<template>
    <v-layout>
      <v-flex auto>
        <pelaaja />
      </v-flex>
      <v-flex xs4 class="pl-3 hidden-md-and-down">
        <!-- <side-bar
          :no_brackets="no_brackets"
          :non-default-teams="teams"
        /> -->
      </v-flex>
    </v-layout>
  </template>

<script>
import { useHomeStore } from '@/stores/home.store'

const homeStore = useHomeStore();
const teams = homeStore.getTeams();

</script>
