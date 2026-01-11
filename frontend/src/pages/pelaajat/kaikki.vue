<!-- BUG isNaN sortting to bottom does not work -->
<template>
  <div class="flex-1-1-100">
    <v-card title="Kaikki Pelaajat">
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
        <v-spacer/>
        <v-col cols="2">
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
        <v-spacer/>
        <v-col cols="2">
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
        <v-spacer/>
        <v-col cols="2">
          <v-btn-toggle
            v-model="playerStore.aggregationSetting"
            variant="outlined"
            divided
            mandatory
            @update:model-value="updateHeaders"
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
        <v-spacer/>
        <v-col cols="1">
          <v-menu
            v-model="showMenu"
            :close-on-content-click="false"
            location="bottom"
            max-width="300px"
          >
            <template #activator="{ props: menu }">
              <v-tooltip
                location="top"
                text="Suodatus asetuksia"
              >
                <template #activator="{ props: tooltip }">
                  <v-btn
                    v-bind="mergeProps(menu, tooltip)"
                    size="small"
                    class="square-btn"
                    variant="outlined"
                    icon="mdi-settings"
                    :active="settingsActive"
                  />
                </template>
              </v-tooltip>
            </template>
            <v-list>
              <v-list-item>
                <v-switch
                  v-model="clearenceOption"
                  color="red"
                  :label="'Vaihda tyhjennys (' + (clearenceOption ? 'TH' : 'Tyh.') + ')'"
                  @update:model-value="updateHeaders();checkActive()"
                />
              </v-list-item>
              <v-list-item>
                <v-radio-group 
                  color="red" 
                  v-model="percentOption"
                  @update:model-value="updateHeaders();checkActive()"
                  inline
                >
                  <v-radio label="H%" value="H%"/>
                  <v-radio label="VM%" value="VM%"/>
                  <v-radio label="H+VM%" value="H+VM%"/>
                </v-radio-group>
              </v-list-item>
              <v-list-item>
                <v-row>
                  <v-col cols="9">
                    <v-switch
                      v-model="playerStore.emptyFiltter"
                      color="red"
                      :label="'Näytä >' + playerStore.emptyFilterThreshold + ' erää pelanneet'"
                      @update:model-value="updateHeaders();checkActive()"
                    />
                  </v-col>
                  <v-col cols="3">
                    <v-text-field 
                      v-model="playerStore.emptyFilterThreshold"
                      type="number"
                      min="0"
                      max="99"
                      maxlength="2"
                      hide-spin-buttons
                    />
                  </v-col>
                </v-row>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-col>
      </v-row>
      <v-data-table
        :mobile-breakpoint="0"
        :headers="tableHeaders"
        @click:row="handleRedirect"
        :sortBy="sortBy"
        :items="playerStore.playersPostionFilttered"
        :loading="playerStore.loading"
        :search="search"
        no-data-text="Ei dataa :("
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

<script setup>
import { usePlayerStore } from '@/stores/players.store';
import { useTeamsStore } from '@/stores/teams.store'
import { headerAllPlayersTemplate } from '@/stores/headers';
import { mergeProps } from 'vue';

const teamStore = useTeamsStore();
const playerStore = usePlayerStore();

playerStore.getPlayers();
playerStore.aggregationSetting = 1;
teamStore.getTeams();

// Setting sortBy stops the resetting after filtering is applied
const sortBy = ref([{key: 'rounds_total', order:'desc'}]);
const tableHeaders = ref(headerAllPlayersTemplate);
const search = ref('');

// Filter options
const showMenu = ref(false);
const clearenceOption = ref(false);
const settingsActive = ref(false);
const percentOption = ref("H%");

function handleRedirect (value, row) {
  location.href = '/pelaajat/' + row.item.player_id;
}

function updateHeaders() {
  // Filter headers from template: first by season settings
  const seasonFilteredHeaders = headerAllPlayersTemplate.filter(header => {
    if (playerStore.aggregationSetting === 1) {
      return header.key !== 'season_count';
    } else if (playerStore.aggregationSetting === 2) {
      return header.key !== 'season' && header.key !== 'team_name';
    }
    return true;
  });
  // Then by percent option
  const precentFilteredHeaders = seasonFilteredHeaders.filter(header => {
    if (percentOption.value === "H%") {
      return header.key !== 'zero_percentage' && header.key !== 'combined_percentage' && header.key !== 'combined_total';
    } else if (percentOption.value === "VM%") {
      return header.key !== 'pike_percentage' && header.key !== 'combined_percentage' && header.key !== 'combined_total';
    } else if (percentOption.value === "H+VM%") {
      return header.key !== 'pike_percentage' && header.key !== 'zero_percentage' && header.key !== 'pikes_total' && header.key !== 'zeros_total';
    }
    return true;
  });
  // Finally by clearence option
  const headerAllPlayersPerSeason = precentFilteredHeaders.filter(header => {
    if (clearenceOption.value) {
      return header.key !== 'clearence_count';
    } else {
      return header.key !== 'clearence_throws_total';
    }
  });
  
  tableHeaders.value = headerAllPlayersPerSeason;
}

function checkActive() {
  settingsActive.value = (clearenceOption.value || percentOption.value !== "H%" || playerStore.emptyFiltter);
}


updateHeaders();
</script>
<style scoped>
tbody tr :hover {
  cursor: unset;
}

.square-btn {
  min-width: 48px;
  width: 48px;
  height: 48px;
  padding: 0;
  border-color: #e5e7eb;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}
</style>
