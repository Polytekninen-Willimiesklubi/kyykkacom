<!-- BUG isNaN sortting to bottom does not work -->
<template>
  <div class="flex-1-1-100">
    <v-card title="Kaikki Joukkueet">
      <v-row align="center">
        <v-col cols="2" class="mb-2 ml-2" justify="left">
          <v-text-field
            color="red"
            v-model="search"
            label="Etsi"
            single-line
            hide-details
          />
        </v-col>
        <v-spacer />
        <v-spacer />
        <!-- <v-col cols="2" align="center">
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
                />
              </template>
            </v-tooltip>
          </v-btn-toggle>
        </v-col> -->
        <v-col cols="3">
          <v-btn-toggle
            v-model="teamStore.filterSetting"
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
        <v-spacer />
        <v-col cols="2">
          <v-btn-toggle
            v-model="teamStore.aggregationSetting"
            variant="outlined"
            divided
            mandatory
            @update:model-value="tableHeaders = teamStore.aggregationSetting === 1 ? headersAllTeamsPerSeason : headersTeamsAllTime"
          >
            <v-tooltip
              location="top"
              :text="'Näytä kaikki pelaajan kaudet tiivistettynä.'"
            >
              <template #activator="{ props }">
                <v-btn v-bind="props" size="x-small" text="Kaikki kaudet" :value="2"/>
              </template>
            </v-tooltip>
            <v-tooltip
              location="top"
              :text="'Näytä pelaajat kausittain'"
            >
              <template #activator="{ props }">
                <v-btn v-bind="props" size="x-small" text="Per Kausi" :value="1"/>
              </template>
            </v-tooltip>
          </v-btn-toggle>
        </v-col>
        <v-spacer />
      </v-row>
      <v-data-table
        :mobile-breakpoint="0"
        :headers="tableHeaders"
        @click:row="handleRedirect"
        :sortBy="sortBy"
        :items="teamStore.filteredAllResults"
        :loading="teamStore.loading"
        no-data-text="Ei dataa :("
        :search="search"
        loading-text="Ladataan kaikkia pelaajia..."
        items-per-page="50"
        density="compact"
      >
        <template v-for="header in tableHeaders"
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
          <template v-else> <!-- No Tooltip -->
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
      </v-data-table>
    </v-card>
  </div>
</template>

<route lang="yaml">
  meta:
      layout: "withoutSidebar"
</route>

<script setup>
import { useTeamsStore } from '@/stores/teams.store'
import { headersTeamsAllTime, headersAllTeamsPerSeason } from '@/stores/headers';

const teamStore = useTeamsStore();
teamStore.aggregationSetting = 2;
teamStore.getTeamsAllSeasons();

// Setting sortBy stops the resetting after filtering is applied
const sortBy = ref([{key: 'season_count', order:'desc'}]);
const tableHeaders = ref(headersTeamsAllTime);
const search = ref('');

function handleRedirect (value, row) {
  location.href = '/joukkueet/' + row.item.team_id;
}

</script>
<style scoped>
tbody tr :hover {
  cursor: unset;
}
</style>
