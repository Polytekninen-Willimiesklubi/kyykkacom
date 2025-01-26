<template>
  <div class="pr-10">
    <v-btn
      class="mb-5"
      @click="showFormat = !showFormat"
      :text="!showFormat ? 'Vain Formaatti' : 'Tulokset'"
    />
    <side-bar
      :title="!isTwoStage ? 'Runkosarja' : 'Jatkosarja'"
      :headers="headersPlayoff"
      :sortBy="[{key: 'bracket_placement', order: 'asc'}]"
      :teams="!isTwoStage ? teamStore.bracketedTeams : teamStore.secondStageBrackets"
      :lines="navStore.playoffLines"
      :boldingKeys="['P', 'points_total']"
      :second_stage="isTwoStage"
      :disable_close="true"
    />
  </div>
  <div class="d-flex">
    <tournament
      :played_games="matchesStore.excludingSuperMatches"
      :rounds_parrent="rounds"
      :first_round="first_round"
      :first="first"
      :only_format="showFormat"
      :bracket_placements="!isTwoStage ? teamStore.onlyPlacements : teamStore.secondStageBrackets"
      :load_ended="load_ended"
      :format_2025="isTwoStage"
    />
  </div>
</template>

<route lang="yaml">
  meta:
    layout: "withoutSidebar"
</route>

<script setup>
import useMatchesStore from '@/stores/matches.store';
import { useNavBarStore } from '@/stores/navbar.store';
import { useTeamsStore } from '@/stores/teams.store';

import { headersPlayoff } from '@/stores/headers';
import { seasonsMappings } from '../tournament_templates/index.js';

const rounds = ref([]);
const first_round = ref(false);
const first = ref(0);
const showFormat = ref(false);
const load_ended = ref(false);
const isTwoStage = ref(false); // If true, show the last stage of braket stages  

const navStore = useNavBarStore();
const matchesStore = useMatchesStore();
const teamStore = useTeamsStore();

if (!navStore.selectedSeason) {
  navStore.getSeasons();
}
matchesStore.getMatches();
teamStore.getTeams();


watch(() => [matchesStore.loaded, teamStore.loaded, navStore.loaded], ([matchesReady, teamsReady, seasonsReady]) => {
  if (!matchesReady || !teamsReady || !navStore.selectedSeason.playoff_format) return;

  if (navStore.selectedSeason.playoff_format === 8) {
    isTwoStage.value = true;
  }

  const json = seasonsMappings[navStore.selectedSeason.playoff_format]
  rounds.value = navStore.selectedSeason.no_brackets === 1 ? json.one_bracket : json.two_bracket;
  first.value = json.first_round;
  first_round.value = !!first.value;
  load_ended.value = true;
})

</script>

<style>
</style>
