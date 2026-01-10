<template>
  <div class="flex-1-1-100">
    <v-card>
      <v-card-title>
        <v-row>
          <v-col>Ottelut</v-col>
        </v-row>
        <v-row>
          <v-col cols="2">
            <v-select 
              v-model="matchStore.selection"
              color="red" 
              :items="selectionOptions" 
              @update:model-value="updateFilter"
            >
              <template #append-item>
                <v-divider class="mt-2" color="red" opacity="100" thickness="2"/>
                <v-list-item
                  title="Videot"
                  @click="matchStore.selection = 'Videot'"
                >
                  <template v-slot:prepend>
                    <v-icon color="red" icon="mdi-youtube" />
                  </template>
                </v-list-item>
                <v-list-item
                  title="Striimit"
                  @click="matchStore.selection = 'Striimit'"
                >
                  <template v-slot:prepend>
                    <v-icon color="red" icon="mdi-access-point" />
                  </template>
                </v-list-item>
              </template>
            </v-select>
          </v-col>
          <v-spacer />
          <v-col cols="2" align="center" v-if="(
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
                  size="small"
                  :text="`Lohko ${String.fromCharCode(65+index)}`"
                  @click="matchStore.setSelectedBracket(index);"
                />
              </template>
            </v-btn-toggle>
          </v-col>
          <v-spacer v-else/>
          <v-spacer />
          <v-col cols="3">
            <v-select
              prepend-inner-icon="mdi-filter"
              v-model="matchStore.selectedTeamsFilter"
              :items="sortedTeams"
              item-title="current_abbreviation"
              item-value="id"
              color="red"
              label="Joukkuesuodatin"
              multiple
              clearable
            >
              <template #prepend-item v-if="
                authStore.teamSeasonId != null
                && teamStore.allTeams.map(obj => obj.id).includes(authStore.teamSeasonId)
              ">
                <v-list-item
                  title="Oma joukkue"
                  @click="selectOwnTeam"
                >
                  <template v-slot:prepend>
                    <v-checkbox-btn
                      :color="ownTeamSelected ? 'red' : undefined"
                      :model-value="ownTeamSelected"
                    />
                  </template>
                </v-list-item>
                <v-divider class="mt-2" color="red" opacity="100" thickness="2"/>
              </template>
              <template #selection="{ item, index }">
                <v-chip text-color="red" v-if="index < 2">
                  {{ item.title }}
                </v-chip>

                <span v-if="index === 2"
                  class="text-red text-caption align-self-center"
                >
                  (+{{ matchStore.selectedTeamsFilter.length - 2 }} muuta)
                </span>
              </template>
            </v-select>
          </v-col>
          <v-col cols="2" align="end">
            <v-select
              prepend-inner-icon="mdi-calendar-filter"
              v-model="matchStore.timeFilterMode"
              color="red"
              :items="dateFilterOptions" 
              item-title="text"
              label="Aikasuodatin"
            />
          </v-col>
          <v-col cols="2">
            <v-text-field 
              prepend-inner-icon="mdi-magnify"
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
        :mobile-breakpoint="0"
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
          <v-col cols="1" v-if="item.stream_link">
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
          <v-col cols="1" v-if="item.video_link">
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
import { useTeamsStore } from '@/stores/teams.store';

const search = ref('');
const matchHeaders = ref(null);
const groupBy = ref(null);
const toggleMultiple = ref([]);

const authStore = useAuthStore();
const matchStore = useMatchesStore();
const navStore = useNavBarStore();
const teamStore = useTeamsStore();
const date = useDate();

const selectionOptions = ['Kaikki ottelut', 'Runkosarja', 'Jatkosarja', 'Pudotuspelit', 'SuperWeekend'];

function selectOwnTeam() {
  const teamId = authStore.teamSeasonId;
  if (matchStore.selectedTeamsFilter.includes(teamId)) {
    // Remove own team from filter
    matchStore.selectedTeamsFilter = matchStore.selectedTeamsFilter.filter(id => id !== teamId);
  } else {
    // Add own team to filter
    matchStore.selectedTeamsFilter = [...matchStore.selectedTeamsFilter, teamId]
  }
}

const ownTeamSelected = computed(() => {
  return matchStore.selectedTeamsFilter.includes(authStore.teamSeasonId);
});

const sortedTeams = computed(() =>
  [...teamStore.allTeams].sort((a, b) =>
    a.current_abbreviation.localeCompare(b.current_abbreviation)
  )
)

const dateFilterOptions = [
  { text: 'Kaikki', value: 0 },
  { text: 'Eilen', value: 1 },
  { text: 'Tänään', value: 2 },
  { text: 'Huomenna', value: 3 },
  { text: 'Viime viikolla', value: 4 },
  { text: 'Tällä viikolla', value: 5 },
  { text: 'Ensi viikolla', value: 6 },
];

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
