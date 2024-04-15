<template>
  <v-layout class="pt-5">
    <v-container grid-list-md>
      <v-row>
        <v-col>
          <v-card v-if="dataReady">
            <h3 class="text-md-left headline">
              {{matchData.type_name}} kenttä <span v-if="matchData.field">{{matchData.field}}</span><span v-else>TBD</span>
              <span style="float:right;">{{ date.formatByString(date.date(matchData.match_time), 'yyyy-MM-dd HH:mm') }}</span>
            </h3>
            <v-row>
              <v-col justify="center" align="center" class="ml-5">
                <figure>
                  <v-img src="@/assets/kyykkalogo120px.png"/>
                  <figcaption v-if="matchData.home_score_total">
                    <br>
                    <v-chip
                      :color="`${getColor(matchData.home_score_total, matchData.away_score_total)} lighten-2`"
                    >{{matchData.home_score_total}}</v-chip>
                  </figcaption>
                </figure>
              </v-col>
              <v-col justify="center" align="center">
                <a :href="'/joukkue/'+matchData.home_team.id">{{matchData.home_team.current_name}}</a>
              </v-col>
              <v-col justify="center" align="center">
                vs.
              </v-col>
              <v-col justify="center" align="center">
                <a :href="'/joukkue/'+matchData.away_team.id">{{matchData.away_team.current_name}}</a>
              </v-col>
              <v-col justify="center" align="center" class="mr-5">
                <figure>
                  <v-img src="@/assets/kyykkalogo120px.png"/>
                  <figcaption v-if="matchData.home_score_total">
                    <br>
                    <v-chip
                      :color="`${getColor(matchData.away_score_total, matchData.home_score_total)} lighten-2`"
                    >{{matchData.away_score_total}}</v-chip>
                  </figcaption>
                </figure>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card color="secondary">
            <round 
              v-if="dataReady" 
              :matchData="matchData" 
              roundNumber="1" 
              teamSide="home"
            />
          </v-card>
        </v-col>
        <v-col>
          <v-card color="secondary">
            <round 
              v-if="dataReady" 
              :matchData="matchData" 
              roundNumber="1" 
              teamSide="away"
            />
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card color="secondary">
            <round 
              v-if="dataReady" 
              :matchData="matchData" 
              roundNumber="2" 
              teamSide="home"
            />
          </v-card>
        </v-col>
        <v-col>
          <v-card color="secondary">
            <round 
              v-if="dataReady" 
              :matchData="matchData" 
              roundNumber="2" 
              teamSide="away"
            />
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="text-xs-center">
          <v-btn 
            v-if="dataReady && authStore.isCaptain" 
            @click="validateClick" 
            x-large
            color="error"
          >
            vahvista
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-layout>
</template>

<script setup>
import { useMatchStore } from '@/stores/match.store';
import { useAuthStore } from '@/stores/auth.store';
import { storeToRefs } from 'pinia';
import { useDate } from 'vuetify';

const authStore = useAuthStore();
const matchStore = useMatchStore();

const {matchData, dataReady, isAwayCaptain} = storeToRefs(matchStore);

const date = useDate();

matchStore.getMatchData();

/**
 * Returns red/yellow/green depending is it higher, lower or tie
 * @param {*} teamScore Team score that you want to get color
 * @param {*} team2Score The team score that you are comparing teamScore param
 * @returns {*} Color string: 'green' if lower, 'yellow' if tie and 'red' if higher
 */
function getColor(teamScore, team2Score) {
  if (teamScore < team2Score) {
    return 'green';
  } else if (teamScore > team2Score) {
    return 'red';
  } else {
    return 'yellow';
  }

}




</script>

<style scoped>
a {
  color: black;
  text-decoration: none;
}
</style>
