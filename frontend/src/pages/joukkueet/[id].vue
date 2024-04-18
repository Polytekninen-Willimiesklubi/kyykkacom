<template>
  <v-layout>
    <div class="d-flex auto mt-10 ml-20" style="max-width: 80%;">
      <v-card>
        <v-card elevation=0>
          <v-row style="height:130px margin-bottom:3px">
            <v-col align="center" justify="center" cols="2">
              <v-img src="@/assets/kyykkalogo120px.png"/>
            </v-col>
            <v-col>
              <v-row>
                <v-col>
                  <v-card-title align="center">{{ teamStore.teamName }}</v-card-title>
                </v-col>
              </v-row>
              <v-row>
                <v-col>
                  <v-btn-toggle v-model="teamStore.selectedSeasonId" mandatory>
                    <v-slide-group show-arrows>
                      <v-slide-group-item>
                        <v-btn 
                          text
                          value="all_time"
                          @click="teamStore.selectedSeasonId = 'allTime'"
                        >
                          All-Time
                        </v-btn>
                      </v-slide-group-item>
                      <v-slide-group-item 
                        v-for="year in Object.keys(teamStore.seasonsStats).sort((a,b) => b-a)" 
                        :key="year"
                      >
                        <v-btn 
                          text
                          :value="year"
                          @click="teamStore.selectedSeasonId = year"
                        >
                          {{ year }}
                        </v-btn>
                      </v-slide-group-item>
                    </v-slide-group>
                  </v-btn-toggle>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-divider />
          <v-row style="height:220px">
            <v-col class="pt-0">
              <v-data-iterator
                :items="teamStore.seasonStats"
                hide-default-footer
              >
                <template v-slot:item="props">
                  <v-list dense>
                    <div v-for="(stat, index) in leftStats">
                      <v-list-item>
                        <div>{{ stat.text }}:</div>
                        <div class="align-end">{{ props.item[stat.value] }}</div>
                      </v-list-item>
                      <v-divider v-if="index -1 != leftStats.length" />
                    </div>
                  </v-list>
                </template>
              </v-data-iterator>
            </v-col>
            <v-divider vertical />
            <v-col class="pt-0">
              <v-data-iterator
                :items="teamStore.seasonStats"
                hide-default-footer
                row 
                wrap
              >
                <template v-slot:item="props">
                  <v-list dense>
                    <div v-for="(stat, index) in rightStats">
                      <v-list-item>
                        <div>{{ stat.text }}:</div>
                        <div class="align-end">{{ props.item[stat.value] }}</div>
                      </v-list-item>
                      <v-divider v-if="index -1 != rightStats.length" />
                    </div>
                  </v-list>
                </template>
              </v-data-iterator>
            </v-col>
          </v-row>
        </v-card>
        <v-divider />
        <v-expansion-panels v-model="panel" multiple>
          <v-expansion-panel title="Pelaajat">
            <v-expansion-panel-text>
              <v-data-table mobile-breakpoint="0" class="mt-5"
                disable-pagination
                :headers="headers"
                @click:row="handleRedirect"
                :items="teamStore.seasonPlayers"
                no-data-text="Ei dataa :("
                hide-default-footer
              />
            </v-expansion-panel-text>
          <!-- TODO: loading -->
            <v-spacer />
            <v-expansion-panels>
              <v-expansion-panel
                title="Varaa pelaajia"
                v-if="authStore.isCaptain"
              >
                <v-expansion-panel-text>
                  <v-text-field 
                    class="mb-10 mt-0" 
                    style="width: 50%;"
                    color="red"
                    v-model="search"
                    label="Search"
                    single-line
                    hide-details
                  />
                  <!-- TODO: loading -->
                  <v-data-table 
                    mobile-breakpoint="0"
                    disable-pagination
                    :search="search"
                    :items="teamStore.unReservedPlayers"
                    :headers="reserveHeaders"
                    no-data-text="Ei dataa :("
                    dense
                    hide-default-footer
                  >
                    <template v-slot:[`item.actions`]="{ item }">
                      <v-icon
                        v-if="!item.team.current_name"
                        color=green
                        @click="teamStore.reservePlayer(item)"
                      >
                        mdi-plus
                      </v-icon>
                      <v-icon
                        v-else
                        color=gray
                      >
                        mdi-lock
                      </v-icon>
                    </template>
                  </v-data-table>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-expansion-panel>
          <v-expansion-panel title="Ottelut">
            <!-- TODO: loading -->
            <v-expansion-panel-text>
              <v-data-table mobile-breakpoint="0"
                @click:row="handleRedirectMatches"
                color='alert'
                :search="search"
                :headers="matchHeaders"
                no-data-text="Ei dataa :("
                :items="teamStore.matches"
              >
                <!-- TODO can't I use :headers value here?  -->
                <template v-for="h in matchHeaders" v-slot:[`header.${h.value}`]="{ header }"> 
                  <span>
                    {{ h.text }}
                    <v-tooltip
                      activator="parent"
                      location="bottom"
                    >
                      {{ h.tooltip }}
                    </v-tooltip>
                  </span>
                </template>
                <template #item.match_time="{ item }">
                  <span>{{ date.formatByString(date.date(item.match_time), 'yyyy-MM-dd HH:mm') }}</span>
                </template>
                <template #item.own_team_total="{ item }">
                  <v-chip :color="getColor(item.own_team_total, item.opposite_team_total)">
                    {{ item.own_team_total }}
                  </v-chip>
                </template>
                <template #item.opposite_team_total="{ item }">
                  <v-chip :color="getColor(item.opposite_team_total, item.own_team_total)">
                    {{ item.opposite_team_total }}
                  </v-chip>
                </template>
              </v-data-table>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card>
    </div>
    <div class="d-flex hidden-md-and-down pl-2">
      <!-- <side-bar
          :no_brackets="no_brackets"
          :non-default-teams="teams"
        /> -->
    </div>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue';

import { useTeamStore } from '@/stores/team.store';
import { useAuthStore } from '@/stores/auth.store';
import { useDate } from 'vuetify'

const date = useDate();

const search = ref('');
const panel = ref([0]);

const teamStore = useTeamStore();
const authStore = useAuthStore();

const reserveHeaders = [
  { text: '#', value: 'player_number' },
  { text: 'Pelaajan nimi', value: 'player_name' },
  {
    text: 'Varaa',
    value: 'actions',
    align: 'left',
    sortable: false
  }
]

const headers = [
  { text: '#', value: 'player_number', width: '1%' },
  {
    text: 'Nimi',
    value: 'player_name',
    width: '20%',
    align: 'left'
  },
  {
    text: 'E',
    value: 'rounds_total',
    width: '1%',
    align: 'left'
  },
  { text: 'P', value: 'score_total', width: '1%', align: 'left' },
  {
    text: 'PPH',
    value: 'score_per_throw',
    width: '1%',
    align: 'left'
  },
  {
    text: 'SP',
    value: 'scaled_points',
    width: '1%',
    alignt: 'left'
  },
  {
    text: 'SPPH',
    value: 'scaled_points_per_throw',
    width: '1%',
    alignt: 'left'
  },
  {
    text: 'kHP',
    value: 'avg_throw_turn',
    width: '1%',
    align: 'left'
  },
  { text: 'H', value: 'pikes_total', width: '1%', align: 'left' },
  {
    text: 'H%',
    value: 'pike_percentage',
    width: '1%',
    align: 'left'
  },
  {
    text: 'VM',
    value: 'zeros_total',
    width: '1%',
    align: 'left'
  },
  {
    text: 'JK',
    value: 'gteSix_total',
    width: '1%',
    alignt: 'left'
  }
]

const matchHeaders = [
  { text: 'Aika', value: 'match_time', align: 'center', tooltip: 'Pelausaika' },
  { text: 'Tyyppi', value: 'match_type', align: 'center', tooltip: 'Peli Tyyppi' },
  { text: 'Vastustaja', value: 'opposite_team', align: 'center', tooltip: 'Vastustaja joukkue' },
  { text: 'OJ 1', value: 'own_first', align: 'center', tooltip: 'Oman Joukkueen 1. Erä', width: '2%' },
  { text: 'OJ 2', value: 'own_second', align: 'center', tooltip: 'Oman Joukkueen 2. Erä', width: '2%' },
  { text: 'V 1', value: 'opp_first', align: 'center', tooltip: 'Vastustaja Joukkueen 1. Erä', width: '2%' },
  { text: 'V 2', value: 'opp_second', align: 'center', tooltip: 'Vastustaja Joukkueen 2. Erä', width: '2%' },
  // { text: 'H+VM', value: 'jotain', align: 'center', tooltip: 'Yhteensä pelissä oman joukkueen heittämät nolla heitot'},
  // { text: 'JK', value: 'jotain', align: 'center', tooltip: '(Joulukuusi) Yhteensä pelissä oman joukkueen heittämät "6 kyykkää tai enemmän"- heitot'},
  { text: 'OJ pis.', value: 'own_team_total', align: 'center', tooltip: 'Oman joukkueen pisteet' },
  { text: 'V pis.', value: 'opposite_team_total', align: 'center', tooltip: 'Vastustaja joukkueen pisteet' }
]

const leftStats = [
  { text: 'Poistetut Kyykät', value: 'score_total' },
  { text: 'Ottelut', value: 'match_count' },
  { text: 'Hauet', value: 'pikes_total' },
  { text: 'Nolla heitot', value: 'zeros_total' },
  { text: 'Nolla aloitukset', value: 'zero_or_pike_first_throw_total' }
]

const rightStats = [
  { text: 'Heitot', value: 'throws_total' },
  { text: 'Ottelu keskiarvo', value: 'match_average' },
  { text: 'Haukiprosentti', value: 'pike_percentage' },
  { text: 'Nollaprosentti', value: 'zero_percentage' },
  { text: 'Joulukuuset', value: 'gteSix_total' }
]

function handleRedirect (value, row) {
  location.href = '/pelaajat/' + row.item.id
}

function handleRedirectMatches (value, row) {
  location.href = '/ottelut/' + row.item.id
}

function getColor(val1, val2) {
  if (val1 < val2) return '#C8E6C9' // green-lighten-4
  else if (val1 > val2) return '#EF9A9A' // red-lighten-4
  else return '#F0F4C3' // yellow-lighten-4
}

const splittedURL = location.href.split('/')
teamStore.teamId = +splittedURL[splittedURL.length-1]

teamStore.getPlayers()
if (authStore.loggedIn && authStore.isCaptain) {
  teamStore.getReserve()
}

</script>


<style>

tbody tr :hover {
    cursor: unset;
}

</style>
