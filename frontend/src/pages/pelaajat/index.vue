<template>
  <v-layout>
    <div class="d-flex" auto>
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
          :sortDesc="sortDesc"
          :sortBy="sortBy"
          :items="playerStore.players"
          :search="search"
          no-data-text="Ei dataa :("
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
import { useHomeStore } from '@/stores/home.store'

const homeStore = useHomeStore();
const playerStore = usePlayerStore();

const search = ref('')
const sortBy = ref(['rounds_total']);
const sortDesc = ref(false);

playerStore.getPlayers();
const teams = homeStore.getTeams();

const headers = [
  { title: 'Nimi', value: 'player_name', align: 'left'},
  { title: 'Joukkue', value: 'team.current_abbreviation', align: 'left'},
  { title: 'E', value: 'rounds_total', align: 'center'},
  { title: 'P', value: 'score_total', width: '1%', align: 'center' },
  { title: 'PPH', value: 'score_per_throw', align: 'center' },
  { title: 'SP',value: 'scaled_points',align: 'center'},
  { title: 'SPH',value: 'scaled_points_per_throw',align: 'center'},
  { title: 'kHP', value: 'avg_throw_turn', align: 'center'},
  { title: 'H', value: 'pikes_total', align: 'center' },
  { title: 'H%', value: 'pike_percentage', align: 'center'},
  { title: 'VM', value: 'zeros_total', align: 'center'},
  { title: 'JK', value: 'gteSix_total', align: 'center'}
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
