<template>
  <v-layout>
    <div class="flex-1-1-100">
      <v-card title="Pelaajat">
        <v-spacer />
        <v-text-field
          color="red"
          v-model="search"
          label="Search"
          single-line
          hide-details 
        />
        <!-- TODO loading -->
        <!-- :custom-sort="custSort()" -->
        <v-data-table 
          mobile-breakpoint="0"
          :headers="headers"
          @click:row="handleRedirect"
          :sortBy="sortBy"
          :items="playerStore.players"
          :search="search"
          no-data-text="Ei dataa :("
          items-per-page="25"
          density="compact"
        />
          <!-- <template
            bind:key="props.item.id"
            v-slot:item.team="props"
          >
            <td v-if="props.item.team !== null">
              Ei varausta
              {{ props.item.team.current_abbreviation }}
            </td>
            <td v-else>
            </td>
          </template> -->
      </v-card>
    </div>
  </v-layout>
</template>

<script setup>
import { usePlayerStore } from '@/stores/players.store';
import { useTeamsStore } from '@/stores/teams.store'

const teamStore = useTeamsStore();
const playerStore = usePlayerStore();

playerStore.getPlayers();
teamStore.getTeams();

const search = ref('')
const sortBy = ref([{key: 'rounds_total', order:'desc'}]);
const sortDesc = ref(false);

const headers = [
  { title: 'Nimi', key: 'player_name', align: 'left'},
  { title: 'Joukkue', key: 'team.current_abbreviation', align: 'left'},
  { title: 'E', key: 'rounds_total', align: 'center'},
  { title: 'P', key: 'score_total', width: '1%', align: 'center' },
  { title: 'PPH', key: 'score_per_throw', align: 'center' },
  { title: 'SP',key: 'scaled_points',align: 'center'},
  { title: 'SPH',key: 'scaled_points_per_throw',align: 'center'},
  { title: 'kHP', key: 'avg_throw_turn', align: 'center'},
  { title: 'H', key: 'pikes_total', align: 'center' },
  { title: 'H%', key: 'pike_percentage', align: 'center'},
  { title: 'VM', key: 'zeros_total', align: 'center'},
  { title: 'JK', key: 'gteSix_total', align: 'center'}
];

function handleRedirect (value, row) {
  location.href = '/pelaajat/' + row.item.id
}

function custSort(items, index, isDescending) {
  function d (p1) {
    switch (p1) {
      case 'NaN':
        return -2
        default:
          return p1
        }
  }
  items.sort((a, b) => {
    const a1 = d(a[index[0]])
    const b1 = d(b[index[0]])
    if (!isDescending[0]) {
      return a1 < b1 ? 1 : a1 === b1 ? 0 : -1
    } else {
      return a1 < b1 ? -1 : a1 === b1 ? 0 : 1
    }
  })
  return items
}

</script>

<style scoped>

tbody tr :hover {
  cursor: unset;
}

</style>
