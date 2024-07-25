<template>
  <v-app>
    <NavBar/>
    <v-main class="content">
      <v-layout class="pa-10">
        <router-view class="pr-5"/>
        <div class="d-flex right">
          <side-bar
            title="Runkosarja"
            :headers="headers"
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

const navStore = useNavBarStore(); 
const teamStore = useTeamsStore();

const headers = [
  { title: 'Joukkue', key: 'current_abbreviation',  sortable: false },
  { title: 'O',       key: 'matches_played',        sortable: false,  tooltip: "Pelatut Ottelut"},
  { title: 'V',       key: 'matches_won',           sortable: false,  tooltip: "Voitot"},
  { title: 'T',       key: 'matches_tie',           sortable: false,  tooltip: "Tasapelit"},
  { title: 'H',       key: 'matches_lost',          sortable: false,  tooltip: "Häviöt"},
  { title: 'P',       key: 'points_total',          sortable: false,  tooltip: "Pisteet"},
  { title: 'P/O',     key: 'points_average',        sortable: false,  tooltip: "Pistettä per Ottelu "},
  { title: 'OKA',     key: 'match_average',         sortable: false,  tooltip: "Ottelu keskiarvo"}
];

</script>

<style>
</style>
