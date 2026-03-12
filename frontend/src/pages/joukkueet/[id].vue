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
        <v-expansion-panel title="Saavutukset" v-if="teamStore.selectedSeasonId === 'allTime'">
          <v-expansion-panel-text>
            <v-row class="pl-5 pb-10">
              <v-col cols="12">
                <div class="accolades-header">
                  <span class="accolades-title">Joukkue Palkinnot</span>
                  <span class="accolades-title">Pelaaja Palkinnot</span>
                </div>
                <v-list 
                  class="w-100"
                  style="overflow: hidden" 
                  v-for="[season, achievements] in Object.entries(
                    hofStore.teamAccoladesBySeason
                  ).sort((a, b) => b[0] - a[0])" 
                  :key="season"
                >
                  <div class="season-header">
                    <v-list-item-title class="season-title">Kausi {{ season }}</v-list-item-title>
                  </div>
                  <v-row style="overflow: hidden">
                    <v-col cols="6">
                      <template v-for="accolade in achievements['team_accolades']" :key="accolade.id">
                        <div class="achievement-badge">
                          <v-row>
                            <v-col cols="1">
                              <accolade-icon :filename="accolade.accolade.icon" />
                            </v-col>
                            <v-col cols="11">
                              <span style="font-weight: 600;">{{ accolade.accolade.name }}</span>
                            </v-col>
                          </v-row>
                        </div>
                      </template>
                    </v-col>
                    <v-divider vertical inset :thickness="1" style="border-color: #000000 !important; color: #000000" />
                    <v-col cols="6" class="pr-8">
                      <template v-for="accolade in achievements['player_accolades']" :key="accolade.id">
                        <div class="achievement-badge">
                          <v-row>
                            <v-col cols="1">
                              <accolade-icon :filename="accolade.accolade.icon" />
                            </v-col>
                            <v-col cols="3">
                              <span style="font-weight: 600;">{{ accolade.accolade.name }}</span>
                            </v-col>
                            <v-col cols="8">
                              <span style="font-weight: 600;">{{ accolade.player_name }}</span>
                            </v-col>
                          </v-row>
                        </div>
                      </template>
                    </v-col>
                  </v-row>
                </v-list>
              </v-col>
            </v-row>
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
import { useHofStore } from '@/stores/hof.store';
import { useRoute } from 'vue-router/auto';
import {
  headersTeamPlayers,
  headersTeamMatch,
  headersTeamReserve,
  headersTeamSeasonStats
} from '@/stores/headers';

const teamStore = useTeamsStore();
const authStore = useAuthStore();
const hofStore = useHofStore();

const route = useRoute('/joukkueet/[id]');

const search = ref('');
const matchSearch = ref('');
const panel = ref([0]);


function handleRedirect(value, row) {
  location.href = '/pelaajat/' + row.item.player
}

function handleRedirectMatches(value, row) {
  location.href = '/ottelut/' + row.item.id
}

function getColor(val1, val2) {
  if (val1 < val2) return 'green-accent-4'
  else if (val1 > val2) return 'red-accent-4'
  else return 'yellow-accent-4'
}


hofStore.getTeamAccolades(route.params.id)
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

<style scoped>
.achievements-item {
  /* flex-direction: column !important; */
  align-items: stretch !important;
  padding: 16px 0 !important;
}

.season-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding-left: 16px;
}

.season-title {
  font-size: 1.1rem;
  font-weight: 600;
  padding-right: 12px;
  white-space: nowrap;
}

.season-header::before {
  content: '';
  flex: 1;
  height: 2px;
  background: linear-gradient(to right, currentColor 100%, transparent 50%);
  margin-left: 12px;
  margin-right: 12px;
}

.season-header::after {
  content: '';
  flex: 1;
  height: 2px;
  background: linear-gradient(to right, currentColor 100%, transparent 50%);
  margin-left: 12px;
  margin-right: 12px;
}

.accolades-header {
  position: relative;
  height: 2.5rem;
  margin-bottom: 12px;
  padding-left: 16px;
  padding-right: 16px;
}

.accolades-title {
  position: absolute;
  font-size: 1.1rem;
  font-weight: 600;
  white-space: nowrap;
  top: 50%;
}

.accolades-title:nth-child(1) {
  left: 25%;
  transform: translate(-50%, -50%);
}

.accolades-title:nth-child(2) {
  left: 75%;
  transform: translate(-50%, -50%);
}

.accolades-header::before {
  content: '';
  position: absolute;
  height: 2px;
  /* background: linear-gradient(to right, currentColor 100%, transparent 0%); */
  top: 50%;
  left: 16px;
  right: 50%;
  margin-right: 8px;
}

.accolades-header::after {
  content: '';
  position: absolute;
  height: 2px;
  /* background: linear-gradient(to left, currentColor 100%, transparent 0%); */
  top: 50%;
  left: 50%;
  right: 16px;
  margin-left: 8px;
}

.achievements-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding-left: 16px;
  padding-bottom: 4px;
}

.achievement-badge {
  padding: 6px 12px;
  margin: 3px 6px;
  margin-bottom: 6px;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 0.9rem;
}
</style>