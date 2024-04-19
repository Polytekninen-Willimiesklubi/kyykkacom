<template>
  <v-layout class="pt-5 mr-2">
    <div width="100px" class="pr-10">
      <v-btn class="mb-5"
          @click="showFormat = !showFormat"
          width="150px"
      >
          {{!showFormat ? "Vain Formaatti" : "Tulokset"}}
      </v-btn>
      <!-- <side-bar
          title="Alkulohko"
          :headers="headers"
          sortBy="super_weekend_bracket_placement"
          :sortDesc="false"
          :no_brackets="no_brackets"
          :super="true"
          :nonDefaultTeams="teams"
      /> -->
    </div>
    <div class="d-flex" width="100px">
      <tournament
        :played_games="matchesStore.superWeekendMatches"
        :rounds_parrent="superStore.bracket"
        :first_round="false"
        :first="0"
        :only_format="showFormat"
        :bracket_placements="superStore.bracketTeams"
        :non_default_seeds="superStore.seededTeams"
        :bronze="superStore.isBronze"
        :load_ended="superStore.loaded"
      />
    </div>
  </v-layout>
</template>

<script setup>
import { useMatchesStore } from '@/stores/matches.store';
import { useSuperStore } from '@/stores/superweeked.store';

const showFormat = ref(false);

const matchesStore = useMatchesStore();
const superStore = useSuperStore();

</script>

<style>
</style>
