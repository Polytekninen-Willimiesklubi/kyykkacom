<template>
  <div class="flex-1-1-100">
    <v-card title="Pelaajat">
      <v-row align="center">
        <v-col cols="3" class="mb-2 ml-2" justify="left">
          <v-text-field
            color="red"
            v-model="search"
            label="Etsi"
            single-line
            hide-details
          />
        </v-col>
        <v-col cols="2" align="center">
          <v-btn-toggle
            v-model="filtterEmpty"
            variant="outlined"
          >
            <v-tooltip
              location="top"
              text="Suodata pelaamattomat pelaajat"
            >
              <template #activator="{ props }">
                <v-btn
                  size="small"
                  v-bind="props"
                  :value="1" 
                  icon="mdi-filter-variant" 
                  @click="playerStore.emptyFiltter = !playerStore.emptyFiltter"
                />
              </template>
            </v-tooltip>
          </v-btn-toggle>
        </v-col>
        <v-col cols="3">
          <v-btn-toggle
            v-model="playerStore.playersPositionsToggle"
            variant="outlined"
            divided
            multiple
          >
            <template v-for="i in 4">
              <v-tooltip
                location="top"
                :text="'Näytä vain heittopaikan '+ i +' statsit'"
              >
                <template #activator="{ props }">
                  <v-btn v-bind="props" size="x-small" :text="i+'.'" :value="i"/>
                </template>
              </v-tooltip>
            </template>
          </v-btn-toggle>
        </v-col>
        <v-col cols="3">
          <v-btn-toggle
            v-model="playerStore.playoffFiltter"
            variant="outlined"
            divided
            mandatory
          >
            <template v-for="(list, i) in [
                ['Kaikki', 'kaikkien pelien'],
                ['Runko', 'runkosarjapelien'],
                ['Pudotus', 'pudotuspelien']
              ]"
            >
              <v-tooltip
                  location="top"
                  :text="'Näytä '+ list[1] +' statsit'"
                >
                  <template #activator="{ props }">
                    <v-btn v-bind="props" size="x-small" :text="list[0]" :value="i"/>
                  </template>
                </v-tooltip>
            </template>
          </v-btn-toggle>
        </v-col>
      </v-row>
      <!-- :custom-key-sort="customSorts" -->
      <v-data-table
        :mobile-breakpoint=0
        :headers="headerPlayers"
        @click:row="handleRedirect"
        :sortBy="sortBy"
        :items="playerStore.playersPostionFilttered"
        :loading="playerStore.loading"
        :search="search"
        no-data-text="Ei dataa :("
        loading-text="Ladataan pelaajia..."
        items-per-page="-1"
        density="compact"
      >
        <template v-for="header in headerPlayers"
          #[`header.${header.key}`]="{ column, toggleSort, getSortIcon }"
        >
          <v-tooltip :text="column.tooltip" v-if="column.tooltip" location="top">
            <template #activator="{ props }">
              <div class="v-data-table-header__content" v-bind="props">
                <!-- HACK To properly center column header with the sort icon
                          just add another span to other side -->
                <span v-if="column.align !== 'left'" style="width:14px"></span>
                <span @click="() => toggleSort(column)">{{ column.title }}</span>
                <v-icon v-if="column.sortable" 
                  class="v-data-table-header__sort-icon" 
                  :icon="getSortIcon(column)"
                  size="x-small"
                />
              </div>
            </template>
          </v-tooltip>
          <template v-else>
            <div class="v-data-table-header__content">
              <!-- HACK To properly center column header with the sort icon
                        just add another span to other side -->
              <span v-if="column.align !== 'left'" style="width:14px"></span>
              <span @click="() => toggleSort(column)">{{ column.title }}</span>
              <v-icon v-if="column.sortable" 
                class="v-data-table-header__sort-icon" 
                :icon="getSortIcon(column)"
                size="x-small"
              />
            </div>
          </template>
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

import { headerPlayers } from '@/stores/headers';

const teamStore = useTeamsStore();
const playerStore = usePlayerStore();
const navStore = useNavBarStore();

playerStore.getPlayers(navStore.seasonId);
teamStore.getTeams();

const search = ref('');
const filtterEmpty = ref(undefined);
// Setting sortBy stops the resetting after filtering is applied
const sortBy = ref([{key: 'rounds_total', order:'desc'}])

function handleRedirect (value, row) {
  location.href = '/pelaajat/' + row.item.player_id;
}

watch(() => navStore.seasonId, (newId) => {
  playerStore.getPlayers(navStore.seasonId);
})

</script>
<style scoped>
tbody tr :hover {
  cursor: unset;
}
</style>
