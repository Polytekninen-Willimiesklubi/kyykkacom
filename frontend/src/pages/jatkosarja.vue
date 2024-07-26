<template>
  <div class="pr-10">
    <v-btn
      class="mb-5"
      @click="showFormat = !showFormat"
      :text="!showFormat ? 'Vain Formaatti' : 'Tulokset'"
    />
    <side-bar
      title="Runkosarja"
      :headers="headersPlayoff"
      sort-by="bracket_placement"
      :sort-desc=false
      :teams="teamStore.bracketedTeams"
      :lines="navStore.playoffLines"
      :boldingKeys="['P', 'points_total']"
    />
  </div>
  <div class="d-flex">
    <tournament
      :played_games="matchesStore.excludingSuperMatches"
      :rounds_parrent="rounds"
      :first_round="first_round"
      :first="first"
      :only_format="showFormat"
      :bracket_placements="teamStore.onlyPlacements"
      :load_ended="load_ended"
    />
  </div>
</template>
<route>
{
  meta: {
    layout: "withoutSidebar"
  }
}
</route>
<script setup>
import { useMatchesStore } from '@/stores/matches.store';
import { useNavBarStore } from '@/stores/navbar.store';
import { useTeamsStore } from '@/stores/teams.store';

import { headersPlayoff } from '@/stores/headers'

import cup_22 from '../tournament_templates/cup_template_22_teams.json';
import cup_16 from '../tournament_templates/cup_template_16_teams.json';
import cup_12 from '../tournament_templates/cup_seeded_template_12_teams.json';
import cup_8 from '../tournament_templates/cup_template_8_teams.json';
import cup_6 from '../tournament_templates/cup_seeded_template_6_teams.json';
import cup_4 from '../tournament_templates/cup_template_4_teams.json';


const seasons_mapping = {
  1: cup_16,
  2: cup_8,
  3: cup_4,
  4: cup_22,
  5: cup_6,
  6: cup_12
};

const rounds = ref([]);
const first_round = ref(false);
const first = ref(0);
const showFormat = ref(false);
const load_ended = ref(false);

const navStore = useNavBarStore();
const matchesStore = useMatchesStore();
const teamStore = useTeamsStore(); 

matchesStore.getMatches();
teamStore.getTeams();
navStore.getSeasons();

watch(() => [matchesStore.loaded, teamStore.loaded, navStore.loaded], ([matchesReady, teamsReady, seasonsReady]) => {
  if (!matchesReady || !teamsReady || !navStore.selectedSeason.playoff_format) return;

  const json = seasons_mapping[navStore.selectedSeason.playoff_format]
  rounds.value = navStore.selectedSeason.no_brackets === 1 ? json.one_bracket : json.two_bracket;
  first.value = json.first_round
  first_round.value = !!first.value
  load_ended.value = true;
})

</script>

<style>
</style>
