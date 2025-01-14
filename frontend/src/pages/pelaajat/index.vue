<template>
  <div class="flex-1-1-100">
    <v-card title="Pelaajat">
      <v-row>
        <v-col cols="4" class="mb-2 ml-2">
          <v-text-field
            color="red"
            v-model="search"
            label="Search"
            single-line
            hide-details
          />
        </v-col>
        <v-spacer />
      </v-row>
      <!-- :custom-key-sort="customSorts" -->
      <v-data-table
        mobile-breakpoint="0"
        :headers="headerPlayers"
        @click:row="handleRedirect"
        :sortBy="[{key: 'rounds_total', order:'desc'}]"
        :items="playerStore.players"
        :loading="playerStore.loading"
        :search="search"
        no-data-text="Ei dataa :("
        loading-text="Ladataan pelaajia..."
        items-per-page="-1"
        density="compact"
        >
        <!-- Header Tooltip -->
        <template #headers="{ columns, isSorted, getSortIcon, toggleSort }">
          <tr>
            <template v-for="column in columns" :key="column.key">
              <th
                class="v-data-table__td v-data-table__th cursor-pointer player-header"
                @click="() => toggleSort(column)"
              >
                <div class="v-data-table-header__content justify-center" align="center">
                  {{ column.title }}
                  <v-tooltip v-if="column.tooltip"
                    activator="parent"
                    location="bottom"
                    :text="column.tooltip"
                  />
                  <template v-if="isSorted(column)">
                    <v-icon :icon="getSortIcon(column)" />
                  </template>
                </div>
              </th>
            </template>
          </tr>
        </template>
        <template #bottom></template> <!-- This hides the pagination controls-->
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup>
import { usePlayerStore } from '@/stores/players.store';
import { useTeamsStore } from '@/stores/teams.store'
import { useNavBarStore } from '@/stores/navbar.store';

import { headerPlayers } from '@/stores/headers'

const teamStore = useTeamsStore();
const playerStore = usePlayerStore();
const navStore = useNavBarStore();

playerStore.getPlayers();
teamStore.getTeams();

const search = ref('')

function handleRedirect (value, row) {
  location.href = '/pelaajat/' + row.item.id
}

// TODO 
// Inverses the order of which is first: desc or asc
// const customSorts = {
//   score_per_throw: (item1, item2, isDesc) => {
//     console.log(isDesc)
//     a = item1 == "NaN" ? -1 : item1
//     b = item2 == "NaN" ? -1 : item2
//     return b - a
//   }
// }

watch(() => navStore.seasonId, (newId) => {
  playerStore.getPlayers();
})

</script>

<style scoped>

tbody tr :hover {
  cursor: unset;
}

</style>
