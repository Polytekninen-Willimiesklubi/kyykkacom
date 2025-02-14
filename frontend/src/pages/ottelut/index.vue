<template>
  <div class="flex-1-1-100">
    <v-card>
      <v-card-title>
          <v-row>
            <v-col>
              Ottelut
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="3">
              <v-select 
                v-model="matchStore.selection"
                color="red" 
                :items="selectionOptions" 
                @update:model-value="updateFilter"
              />
            </v-col>
            <v-col cols="3" v-if="(
                matchStore.selection === 'Runkosarja' || matchStore.selection === 'Kaikki ottelut'
              ) && navStore.noBrackets >= 2"
            > 
            <v-btn-toggle
              v-model="toggleMultiple"
              variant="outlined"
              divided
              multiple
            >
              <template v-for="(num, index) in navStore.noBrackets">
                <v-btn
                  :text="`Lohko ${String.fromCharCode(65+index)}`"
                  @click="matchStore.setSelectedBracket(index);"
                />
              </template>
            </v-btn-toggle>
          </v-col>
          <v-spacer v-else/>
            <v-col cols="3">
              <v-row>
                <v-col cols="12" align="center" class="pa-0">
                  <v-btn-toggle 
                    v-model="matchStore.timeFilterMode"
                    density="compact"
                    variant="outlined"
                    divided
                  >
                    <!-- There might be a bug in vuetify: if value is 0-1 it will higlight 
                        button from the other group as it's 
                    -->
                    <v-btn size="small" text="Tänään" :value="3"/>
                    <v-btn size="small" text="Viikolla" :value="4"/>
                  </v-btn-toggle>
                </v-col>
                <v-col cols="12" align="center" class="pa-0">
                  <v-btn-toggle 
                    v-model="matchStore.timeFilterMode"
                    density="compact"
                    variant="outlined"
                    divided
                  >
                    <v-btn size="small" text="Huomenna" :value="5"/>
                    <v-btn size="small" text="Ensi viikolla" :value="6"/>
                  </v-btn-toggle>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="3">
              <v-text-field 
                color="red" 
                v-model="search" 
                label="Search" 
                single-line 
                hide-details 
              />
            </v-col>
          </v-row>
      </v-card-title>
      <v-data-table
        :mobile-breakpoint=0
        :headers="matchHeaders"
        :items="matchStore.selectedMatches"
        :search="search"
        @click:row="handleRedirect"
        :loading="matchStore.loading"
        loading-text="Ladataan otteluita..."
        :no-data-text="!search || !matchStore.selectedMatches ? 'Ei dataa :(' : 'Ei hakutuloksia :('"
        :sort-by="[{key: 'match_time', order:'asc'}]"
        :group-by="groupBy"
        :row-props="itemRowBackground"
        density="compact"
        items-per-page="20"
      >
      <template #item.match_time = "{ item }">
        <v-row>
          <v-col>
            <span>{{ date.formatByString(date.date(item.match_time), 'yyyy-MM-dd HH:mm') }}</span> 
          </v-col>
          <v-col cols="1" v-if="!item.stream_link">
            <v-tooltip
              activator='parent'
              text="Striimin linkki"
              location="left"
            />
            <v-btn
              :href="item.stream_link"
              icon="mdi-access-point"
              size="xs-small"
              variant="plain"
            />
          </v-col>
          <v-col cols="1" v-if="!item.video_link">
            <v-tooltip
              activator='parent'
              text="Video linkki"
              location="left"
            />
            <v-btn
              :href="item.video_link"
              icon="mdi-youtube"
              size="xs-small"
              variant="plain"
            />
          </v-col>
          <v-col cols="2">
            <template v-if="!item.is_validated 
              && item.away_score_total !== null 
              && item.home_score_total !== null"
            >
              <v-tooltip
                activator='parent'
                text="Ottelu on validoimatta"
                location="right"
              />
              <v-icon
                color="grey"
                icon="mdi-information"
              />
            </template>
            <template v-else-if="(authStore.isCaptain || authStore.isSuperUser)
              && item.home_team.id === authStore.teamId 
              && (item.away_score_total === null || item.home_score_total === null)"
            >
              <v-tooltip
                activator='parent'
                text="Syötä ottelun tulos"
                location="right"
              />
              <v-icon
                color="grey"
                icon="mdi-alert"
              />
            </template>
            <template v-else-if="(authStore.isCaptain || authStore.isSuperUser)
              && new Date() > new Date(item.match_time)
              && item.away_team.id === authStore.teamId
              && (item.away_score_total === null || item.home_score_total === null)"
            >
              <v-tooltip
                activator='parent'
                text="Kotijoukkue ei ole syöttänyt lopputulosta"
                location="right"
              />
              <v-icon
                color="grey"
                icon="mdi-timer-sand"
              />
            </template>
          </v-col>
        </v-row>

      </template>
      <template #group-header="{item, columns, toggleGroup, isGroupOpen }">
        <tr>
          <td :colspan="columns.length">
            <v-row align="center" justify="center">
              <v-col cols="3" >
                <v-btn
                  :icon="isGroupOpen(item) ? '$expand' : '$next'"
                  size="small"
                  variant="text"
                  @click="toggleGroup(item)"
                />
                {{ item.items[0].raw.type_name }}
              </v-col>
              <v-spacer />
              <v-col cols="2" align="center">
                {{ item.items[0].raw.home_team.current_abbreviation }}
              </v-col>
              <v-col cols="1" align="center">
                vs.
              </v-col>
              <v-col cols="2" align="center">
                {{ item.items[0].raw.away_team.current_abbreviation }}
              </v-col>
              <v-spacer />
            </v-row>
          </td>
        </tr>
      </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.store';
import useMatchesStore from '@/stores/matches.store';
import { useNavBarStore } from '@/stores/navbar.store';
import { useDate } from 'vuetify';
import {
  headersMatches,
  headersMatchesPostSeason,
} from '@/stores/headers';
import { watch } from 'vue';

const search = ref('');
const matchHeaders = ref(null);
const groupBy = ref(null);
const toggleMultiple = ref([]);

const authStore = useAuthStore();
const matchStore = useMatchesStore();
const navStore = useNavBarStore();
const date = useDate();

const selectionOptions = ['Kaikki ottelut', 'Runkosarja', 'Jatkosarja', 'Pudotuspelit', 'SuperWeekend'];

/**
 * @description Checks match list rows if background needs to change to alert captain.
 * @param row Single row from datatable, should contain `match_time`, `home_team.id` and `away_team.id` attribute.
 * @returns {object} Object with class string. Should point scoped style in this file
 */
function itemRowBackground(row) {
  if (!authStore.teamId || !(authStore.isCaptain || authStore.isSuperUser)) {
    return {class: 'actions_not_needed'};
  }
  if (row.item.is_validated || new Date(row.item.match_time) > new Date()) {
    return {class: 'actions_not_needed'};
  }
  return row.item.home_team.id === authStore.teamId || row.item.away_team.id === authStore.teamId
    ? {class: 'captain_actions_needed'} : {class: 'actions_not_needed'};
}

function handleRedirect (value, row) {
  location.href = '/ottelut/' + row.item.id;
}

function updateFilter() {
  matchHeaders.value = matchStore.selection === 'Pudotuspelit'
    ? headersMatchesPostSeason : headersMatches;

  groupBy.value = matchStore.selection === 'Pudotuspelit'
    ? [{key: 'seriers'}] : [];
}

matchStore.getMatches();
updateFilter();

watch(() => navStore.seasonId, (newId) => {
  matchStore.getMatches();
})

</script>

<style>
.captain_actions_needed {
  background-color: #EF9A9A !important;
}

.actions_not_needed {
  background-color: white;
}
</style>
