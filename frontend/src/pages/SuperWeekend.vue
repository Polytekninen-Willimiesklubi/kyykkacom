<template>
  <v-layout class="pt-5 mr-2">
    <div class="pr-10">
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
        :no_brackets="superStore.noBrackets"
        :super="true"
        :teams="superStore.bracketTeams"
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
        :bracket_placements="superStore.bracketTeams"
        :non_default_seeds="superStore.seededTeams"
        :bronze="superStore.isBronze"
        :load_ended="superStore.loaded"
      />
    </div>
  </v-layout>
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
import { useSuperStore } from '@/stores/superweeked.store';
import { superSidebarHeaders } from '@/stores/superweeked.store';

const showFormat = ref(false);

const matchesStore = useMatchesStore();
const superStore = useSuperStore();

superStore.getAllData();
setTimeout(() => {

  console.log(superStore.teams);
}, 1000)

</script>

<style>
</style>
