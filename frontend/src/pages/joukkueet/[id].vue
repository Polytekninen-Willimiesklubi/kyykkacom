<template>
  <div class="flex-1-1-100 ml-20" style="max-width: 90%;">
    <v-card>
      <v-skeleton-loader
        class="ma-5"
        :loading="teamStore.singleLoading" 
        type="image, actions"
      >
        <v-card elevation=0 class="ma-2">
          <v-row class="pb-5">
            <v-col align="center" justify="center" cols="2">
              <img src="@/assets/kyykkalogo120px.png"/>
            </v-col>
            <v-col cols="10">
              <v-row>
                <v-col>
                  <v-card-title align="center">{{ teamStore.teamName }}</v-card-title>
                </v-col>
              </v-row>
              <v-row>
                <v-col>
                  <v-btn-toggle v-model="teamStore.selectedSeasonId" mandatory divided>
                    <v-slide-group show-arrows>
                      <v-slide-group-item>
                        <v-btn 
                          text="All-Time"
                          value="allTime"
                          @click="teamStore.selectedSeasonId = 'allTime'"
                        />
                      </v-slide-group-item>
                      <v-slide-group-item 
                        v-for="year in Object.keys(teamStore.seasonsStats).sort((a,b) => b-a)" 
                        :key="year"
                      >
                        <v-btn
                          :text="year"
                          :value="year"
                          @click="teamStore.selectedSeasonId = year"
                        />
                      </v-slide-group-item>
                    </v-slide-group>
                  </v-btn-toggle>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-divider />
          <v-data-iterator 
            :items="headersTeamSeasonStats"
            :loading="teamStore.singleLoading"
            items-per-page="-1"
            density="compact"
          >
            <template #default="{ items }">
              <v-row>
                <v-col cols="6" v-for="(item, i) in items">
                  <v-row>
                    <v-col cols="6">
                      {{ item.raw.title }}
                    </v-col>
                    <v-col cols="6" class="align-end">
                      {{ teamStore.seasonStats[`${item.raw.key}`] }}
                    </v-col>
                  </v-row>
                  <v-divider v-if="i % 2 == 0" />
                  <v-divider vertical v-if="i -1 != items.length" />
                </v-col>
              </v-row>
            </template>
          </v-data-iterator>
        </v-card>
      </v-skeleton-loader>
      <v-divider />
      <v-expansion-panels v-model="panel" multiple>
        <v-expansion-panel title="Pelaajat">
          <v-expansion-panel-text>
            <v-data-table 
              class="mt-5"
              :mobile-breakpoint="0"
              :headers="headersTeamPlayers"
              @click:row="handleRedirect"
              :items="teamStore.seasonPlayers"
              :loading="teamStore.singleLoading"
              loading-text="Ladataan Pelaajia..."
              no-data-text="Ei pelaajia :("
              hide-default-footer
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
                        <span> {{ column.title }} </span>
                        <v-tooltip v-if="column.tooltip"
                          activator="parent"
                          location="top"
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
            </v-data-table>
          </v-expansion-panel-text>
          <v-spacer />
          <v-expansion-panels>
            <v-expansion-panel
              title="Varaa pelaajia"
              v-if="teamStore.reserveLoading || teamStore.reserveAllowed"
            >
              <v-expansion-panel-text>
                <v-text-field 
                  class="mb-10 mt-0" 
                  style="width: 50%;"
                  color="red"
                  v-model="search"
                  label="Search"
                  single-line
                />
                <v-data-table 
                  :mobile-breakpoint="0"
                  :search="search"
                  :items="teamStore.unReservedPlayers"
                  :headers="headersTeamReserve"
                  :loading="teamStore.reserveLoading"
                  loading-text="Ladataan pelaajia..."
                  no-data-text="Ei dataa :("
                  items-per-page="-1"
                  density="compact"
                >
                  <template #item.actions="{ item }">
                    <v-icon
                      icon="mdi-plus"
                      color=green
                      @click="teamStore.reservePlayer(item)"
                    />
                  </template>
                  <!-- <template #bottom></template> -->
                </v-data-table>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-expansion-panel>
        <v-expansion-panel title="Ottelut">
          <v-expansion-panel-text>
            <v-text-field 
              class="mb-10 mt-0" 
              style="width: 50%;"
              color="red"
              v-model="matchSearch"
              label="Etsi Otteluja"
              single-line
            />
            <v-data-table 
              :mobile-breakpoint="0"
              @click:row="handleRedirectMatches"
              color='alert'
              :search="matchSearch"
              :headers="headersTeamMatch"
              :loading="teamStore.singleLoading"
              loading-text="Ladataan otteluita..."
              no-data-text="Ei pelattuja otteluita :("
              :sort-by="[{key: 'match_time', order:'desc'}]"
              :items="teamStore.matches"
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
                          location="top"
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
              <template #item.own_team_total="{ item }">
                <v-chip :color="getColor(item.own_team_total, item.opposite_team_total)">
                  <strong>{{ item.own_team_total }}</strong>
                </v-chip>
              </template>
              <template #item.opposite_team_total="{ item }">
                <v-chip :color="getColor(item.opposite_team_total, item.own_team_total)">
                  <strong>{{ item.opposite_team_total }}</strong>
                </v-chip>
              </template>
            </v-data-table>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card>
  </div>
</template>

<route lang="yaml">
  meta:
      layout: "withoutSidebar"
</route>

<script setup>
import { useTeamsStore } from '@/stores/teams.store';
import { useAuthStore } from '@/stores/auth.store';
import { useDate } from 'vuetify'
import { useRoute } from 'vue-router/auto';
import { 
  headersTeamPlayers,
  headersTeamMatch,
  headersTeamReserve,
  headersTeamSeasonStats
} from '@/stores/headers';

const teamStore = useTeamsStore();
const authStore = useAuthStore();

const route = useRoute('/joukkueet/[id]');
const date = useDate();

const search = ref('');
const matchSearch = ref('');
const panel = ref([0]);


function handleRedirect (value, row) {
  location.href = '/pelaajat/' + row.item.player
}

function handleRedirectMatches (value, row) {
  location.href = '/ottelut/' + row.item.id
}

function getColor(val1, val2) {
  if (val1 < val2) return 'green-accent-4'
  else if (val1 > val2) return 'red-accent-4'
  else return 'yellow-accent-4'
}

teamStore.getTeamPlayers(route.params.id)
if (authStore.loggedIn && (authStore.isCaptain || authStore.isSuperUser)) {
  teamStore.getReserve(route.params.id)
}

// Forcing reload of the page fixes a issue where if I am at some location '/page/15' and I have 
// a redirect button to location '/page/50' it would not load the new content.  
watch(() => route.params.id, () => {
  window.location.reload()
});

</script>
