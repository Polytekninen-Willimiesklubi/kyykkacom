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
                          text="All-Time"
                          value="all_time"
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
            :items="middleStats"
            items-per-page="-1"
            density="compact"
          >
            <template #default="{ items }">
              <v-row>
                <v-col 
                  cols="6"
                  v-for="(item, i) in items"
                >
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
                  />
                  <!-- TODO: loading -->
                  <v-data-table 
                    mobile-breakpoint="0"
                    :search="search"
                    :items="teamStore.unReservedPlayers"
                    :headers="reserveHeaders"
                    no-data-text="Ei dataa :("
                    density="compact"
                  >
                    <template #item.actions="{ item }">
                      <v-icon
                        v-if="!item.team.current_name"
                        icon="mdi-plus"
                        color=green
                        @click="teamStore.reservePlayer(item)"
                      />
                      <v-icon v-else 
                        icon="mdi-lock"
                        color=gray
                      />
                    </template>
                    <template #bottom></template>
                  </v-data-table>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-expansion-panel>
          <v-expansion-panel title="Ottelut">
            <!-- TODO: loading -->
            <v-expansion-panel-text>
              <v-data-table 
                mobile-breakpoint="0"
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
                      :text="h.tooltip"
                      activator="parent"
                      location="bottom"
                    />
                  </span>
                </template>
                <template #item.match_time="{ item }">
                  <span>{{ date.formatByString(date.date(item.match_time), 'yyyy-MM-dd HH:mm') }}</span>
                </template>
                <template #item.own_team_total="{ item }">
                  <v-chip 
                    :color="getColor(item.own_team_total, item.opposite_team_total)"
                    :text="item.own_team_total"
                  />
                </template>
                <template #item.opposite_team_total="{ item }">
                  <v-chip
                    :color="getColor(item.opposite_team_total, item.own_team_total)"
                    :text="item.opposite_team_total"
                  />
                </template>
              </v-data-table>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card>
    </div>
  </v-layout>
</template>

<script setup>
import { useTeamsStore } from '@/stores/teams.store';
import { useAuthStore } from '@/stores/auth.store';
import { useDate } from 'vuetify'
import { useRoute } from 'vue-router/auto';

const teamStore = useTeamsStore();
const authStore = useAuthStore();

const route = useRoute('/joukkueet/[id]');
const date = useDate();

const search = ref('');
const panel = ref([0]);

const reserveHeaders = [
  { title: '#', key: 'player_number' },
  { title: 'Pelaajan nimi', key: 'player_name' },
  { title: 'Varaa', key: 'actions', align: 'left', sortable: false}
];

const headers = [
  { title: '#', key: 'player_number', width: '1%' },
  { title: 'Nimi', key: 'player_name', width: '20%',align: 'left'},
  { title: 'E', key: 'rounds_total', width: '1%', align: 'left'},
  { title: 'P', key: 'score_total', width: '1%', align: 'left' },
  { title: 'PPH', key: 'score_per_throw', width: '1%', align: 'left'},
  { title: 'SP', key: 'scaled_points', width: '1%', align: 'left'},
  { title: 'SPPH', key: 'scaled_points_per_throw', width: '1%',align: 'left'},
  { title: 'kHP', key: 'avg_throw_turn', width: '1%', align: 'left'},
  { title: 'H', key: 'pikes_total', width: '1%', align: 'left' },
  { title: 'H%', key: 'pike_percentage', width: '1%', align: 'left'},
  { title: 'VM', key: 'zeros_total', width: '1%', align: 'left'},
  { title: 'JK', key: 'gteSix_total', width: '1%', align: 'left'}
];

const matchHeaders = [
  { title: 'Aika', key: 'match_time', align: 'center', tooltip: 'Pelausaika' },
  { title: 'Tyyppi', key: 'match_type', align: 'center', tooltip: 'Peli Tyyppi' },
  { title: 'Vastustaja', key: 'opposite_team', align: 'center', tooltip: 'Vastustaja joukkue' },
  { title: 'OJ 1', key: 'own_first', align: 'center', tooltip: 'Oman Joukkueen 1. Erä', width: '2%' },
  { title: 'OJ 2', key: 'own_second', align: 'center', tooltip: 'Oman Joukkueen 2. Erä', width: '2%' },
  { title: 'V 1', key: 'opp_first', align: 'center', tooltip: 'Vastustaja Joukkueen 1. Erä', width: '2%' },
  { title: 'V 2', key: 'opp_second', align: 'center', tooltip: 'Vastustaja Joukkueen 2. Erä', width: '2%' },
  // { title: 'H+VM', key: 'jotain', align: 'center', tooltip: 'Yhteensä pelissä oman joukkueen heittämät nolla heitot'},
  // { title: 'JK', key: 'jotain', align: 'center', tooltip: '(Joulukuusi) Yhteensä pelissä oman joukkueen heittämät "6 kyykkää tai enemmän"- heitot'},
  { title: 'OJ pis.', key: 'own_team_total', align: 'center', tooltip: 'Oman joukkueen pisteet' },
  { title: 'V pis.', key: 'opposite_team_total', align: 'center', tooltip: 'Vastustaja joukkueen pisteet' }
]

const middleStats = [
  { title: 'Poistetut Kyykät', key: 'score_total' },
  { title: 'Heitot', key: 'throws_total' },
  { title: 'Ottelut', key: 'match_count' },
  { title: 'Ottelu keskiarvo', key: 'match_average' },
  { title: 'Hauet', key: 'pikes_total' },
  { title: 'Haukiprosentti', key: 'pike_percentage' },
  { title: 'Nolla heitot', key: 'zeros_total' },
  { title: 'Nollaprosentti', key: 'zero_percentage' },
  { title: 'Nolla aloitukset', key: 'zero_or_pike_first_throw_total' },
  { title: 'Joulukuuset', key: 'gteSix_total' } ,
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

teamStore.getTeamPlayers(route.params.id)
if (authStore.loggedIn && authStore.isCaptain) {
  teamStore.getReserve()
}

</script>

<style>
tbody tr :hover {
    cursor: unset;
}
</style>
