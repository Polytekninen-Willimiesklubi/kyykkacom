<template>
    <v-layout>
      <div class="d-flex" auto>
        <pelaaja />
      </div>
      <div class="d-flex pl-3 xs4 hidden-md-and-down">
        <!-- <side-bar
          :no_brackets="no_brackets"
          :non-default-teams="teams"
        /> -->
      </div>
    </v-layout>
  </template>

<script>
import { useHomeStore } from '@/stores/home.store'

const homeStore = useHomeStore();
const teams = homeStore.getTeams();

</script>
