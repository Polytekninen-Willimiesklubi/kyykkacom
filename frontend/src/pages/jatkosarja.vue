<template>
  <v-layout class="pt-5">
    <div width="100px" class="pr-10">
      <v-btn 
        class="mb-5 ml-5"
        @click="showFormat = !showFormat"
        width="150px"
        :text="!showFormat ? 'Vain Formaatti' : 'Tulokset'"
      />
      <!-- <side-bar
          title="Runkosarja"
          :headers="headers"
          sort-by="bracket_placement"
          :sort-desc=false
          :no_brackets="no_brackets"
          :non-default-teams="teams"
      /> -->
    </div>
    <div class="d-flex" width="100px">
      <tournament
        :played_games="matchesStore.excludingSuperMatches"
        :rounds_parrent="rounds"
        :first_round="first_round"
        :first="first"
        :only_format="showFormat"
        :bracket_placements="teamStore.bracketedTeams"
        :load_ended="load_ended"
      />
    </div>
  </v-layout>
</template>

<script setup>
import { useMatchesStore } from '@/stores/matches.store';
import { useNavBarStore } from '@/stores/navbar.store';
import { useTeamsStore } from '@/stores/teams.store';

// import { definePage } from 'vue-router/auto';

import cup_22 from '../tournament_templates/cup_template_22_teams.json';
import cup_16 from '../tournament_templates/cup_template_16_teams.json';
import cup_12 from '../tournament_templates/cup_seeded_template_12_teams.json';
import cup_8 from '../tournament_templates/cup_template_8_teams.json';
import cup_6 from '../tournament_templates/cup_seeded_template_6_teams.json';
import cup_4 from '../tournament_templates/cup_template_4_teams.json';

// definePage({
//   meta: {
//     layout: '@/layouts/tournament.vue'
//   }
// })


const headers = [
  { text: 'Sij.', value: 'bracket_placement' },
  { text: 'Joukkue', value: 'current_abbreviation', sortable: false, width: '10%' },
  { text: 'O', value: 'matches_played', sortable: false, width: '3%' },
  { text: 'V', value: 'matches_won', sortable: false, width: '3%' },
  { text: 'T', value: 'matches_tie', sortable: false, width: '3%' },
  { text: 'H', value: 'matches_lost', sortable: false, width: '3%' },
  { text: 'P', value: 'points_total', sortable: false, width: '3%' },
  { text: 'OKA', value: 'match_average', sortable: false, width: '5%' }
];

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

const navbarStore = useNavBarStore();
const matchesStore = useMatchesStore();
const teamStore = useTeamsStore(); 

matchesStore.getMatches();
teamStore.getTeams();
navbarStore.getSeasons();

watch(() => [matchesStore.loaded, teamStore.loaded, navbarStore.loaded], ([matchesReady, teamsReady, seasonsReady]) => {
  if (!matchesReady || !teamsReady || !navbarStore.selectedSeason.playoff_format) return;

  const json = seasons_mapping[navbarStore.selectedSeason.playoff_format]
  rounds.value = navbarStore.selectedSeason.no_brackets === 1 ? json.one_bracket : json.two_bracket;
  first.value = json.first_round
  first_round.value = !!first.value
  load_ended.value = true;
})

</script>

<style>
</style>
