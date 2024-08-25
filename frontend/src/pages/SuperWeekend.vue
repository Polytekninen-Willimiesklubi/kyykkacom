<template>
  <div class="pr-10 pt-5 mr-2">
    <v-btn
      class="mb-5"
      @click="showFormat = !showFormat"
      :text="!showFormat ? 'Vain Formaatti' : 'Tulokset'"
    />
    <side-bar
      title="Alkulohko"
      :headers="superSidebarHeaders"
      sortBy="super_weekend_bracket_placement"
      :sortDesc="false"
      :teams="superStore.bracketedTeams"
      :lines="superStore.playoffLines"
    />
  </div>
  <div class="d-flex">
    <tournament
      :played_games="matchesStore.superWeekendMatches"
      :rounds_parrent="superStore.bracket"
      :first_round="false"
      :first="0"
      :only_format="showFormat"
      :bracket_placements="superStore.seededTeams"
      :bronze="superStore.isBronze"
      :load_ended="superStore.loaded"
    />
  </div>
</template>

<route lang="yaml">
  meta:
    layout: "withoutSidebar"
</route>

<script setup>
import { useMatchesStore } from '@/stores/matches.store';
import { useSuperStore } from '@/stores/superweekend.store';
import { superSidebarHeaders } from '@/stores/headers'

const showFormat = ref(false);

const matchesStore = useMatchesStore();
const superStore = useSuperStore();

superStore.getAllData();

</script>

<style>
</style>
