<template>
  <div align="center">
    <side-bar
      title="Runkosarjatilanne"
      :headers="headersDefaultSideBar"
      :sort-by="[{key:'bracket_placement', order: 'asc'}, {key:'points_total', order: 'desc'}]"
      :teams="teamStore.bracketedTeams"
      :lines="navStore.playoffLines"
      :boldingKeys="['P', 'points_total']"
    />
  </div>
</template>

<route lang="yaml">
    meta:
        layout: "withoutSidebar"
</route>

<script setup>
import { useTeamsStore } from '@/stores/teams.store';
import { useNavBarStore } from '@/stores/navbar.store';
import { headersDefaultSideBar } from '@/stores/headers';

const navStore = useNavBarStore(); 
const teamStore = useTeamsStore();

</script>