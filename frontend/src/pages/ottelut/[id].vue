<template>
  <v-container class='pt-0' grid-list-md>
    <v-row>
      <v-col>
        <v-card v-if="dataReady">
          <v-row>
            <v-col>
              <h3 class="text-md-left headline mt-1 ml-1 mr-1">
                {{matchData.type_name}} kenttä 
                <span v-if="matchData.field">
                    {{matchData.field}}
                </span>
                <span v-else>TBD</span>
                <span style="float:right;">
                  {{ date.formatByString(date.date(matchData.match_time), 'yyyy-MM-dd HH:mm') }}
                </span>
              </h3>
              <v-icon v-if="showEdit" @click="showInput = !showInput" icon="mdi-pencil">
                <v-tooltip
                  activator='parent'
                  location="right"
                  text="Muokkaa tulosta"
                />
              </v-icon>
            </v-col>
          </v-row>
          <v-row justify="center" align="center">
            <v-col class="ml-5">
              <figure>
                <v-img 
                  src="@/assets/kyykkalogo120px.png"
                  height="120px"
                />
                <figcaption 
                  class="d-flex justify-center ma-2"
                  v-if="matchData.home_score_total"
                >
                  <v-chip :color="getColor(matchData.home_score_total, matchData.away_score_total)"
                  >
                    <strong>{{matchData.home_score_total}}</strong>
                  </v-chip>
                </figcaption>
              </figure>
            </v-col>
            <v-col class=''>
              <a :href="'/joukkueet/'+matchData.home_team.team_id">
                {{matchData.home_team.current_name}}
              </a>
            </v-col>
            <v-col>
              vs.
            </v-col>
            <v-col>
              <a :href="'/joukkueet/'+matchData.away_team.team_id">
                {{matchData.away_team.current_name}}
              </a>
            </v-col>
            <v-col class="mr-5">
              <figure>
                <v-img 
                  src="@/assets/kyykkalogo120px.png"
                  height="120px"
                />
                <figcaption 
                  class="d-flex justify-center ma-2"
                  v-if="matchData.home_score_total"
                >
                  <v-chip :color="getColor(matchData.away_score_total, matchData.home_score_total)">
                    <strong>{{matchData.away_score_total}}</strong>
                  </v-chip>
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
          <round v-if="dataReady"
            :roundScore="matchData.home_first_round_score"
            :players="matchData.home_team.players"
            :teamName="matchData.home_team.current_abbreviation"
            :roundData="matchData.first_round.home"
            :matchData="matchData" 
            roundNumber="1"
            :showInput="showInput"
            teamSide="home"
            :color="getColor(matchData.home_first_round_score,
              matchData.away_first_round_score)"
          />
        </v-card>
      </v-col>
      <v-col>
        <v-card color="secondary">
          <round v-if="dataReady" 
            :roundScore="matchData.away_first_round_score"
            roundNumber="1"
            :showInput="showInput"
            :players="matchData.away_team.players"
            :teamName="matchData.away_team.current_abbreviation"
            :roundData="matchData.first_round.away"
            teamSide="away"
            :color="getColor(matchData.away_first_round_score,
              matchData.home_first_round_score)"
          />
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card color="secondary">
          <round v-if="dataReady" 
            :matchData="matchData" 
            roundNumber="2"
            :showInput="showInput"
            :players="matchData.home_team.players"
            :teamName="matchData.home_team.current_abbreviation"
            :roundData="matchData.second_round.home"
            teamSide="home"
            :color="getColor(matchData.home_second_round_score,
              matchData.away_second_round_score)"
          />
        </v-card>
      </v-col>
      <v-col>
        <v-card color="secondary">
          <round v-if="dataReady" 
            :matchData="matchData" 
            roundNumber="2"
            :showInput="showInput"
            :players="matchData.away_team.players"
            :teamName="matchData.away_team.current_abbreviation"
            :roundData="matchData.second_round.away"
            teamSide="away"
            :color="getColor(matchData.away_second_round_score,
              matchData.home_second_round_score)"
          />
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="text-xs-center">
        <v-btn 
          text="vahvista"
          @click="matchStore.validateClick()" 
          color="error"
          v-if="dataReady && isAwayCaptain && !matchData.is_validated"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useMatchStore } from '@/stores/match.store';
import { useDate } from 'vuetify';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { watch, ref } from 'vue';

const matchStore = useMatchStore();
const route = useRoute('/ottelut/[id]');
const date = useDate();

const showEdit = ref<boolean>(false);
const showInput = ref<boolean>(false);

const { matchData, dataReady, isAwayCaptain } = storeToRefs(matchStore);
matchStore.getMatchData(route.params.id);

watch(dataReady, (newValue) => {
  if (newValue) {
    if (
      localStorage.roleId == 2 || (
        !matchData.value.is_validated
        && localStorage.teamId == matchData.value.home_team.team_id
        && localStorage.roleId == 1
      )
    ) {
      showEdit.value = true;
    } else {
      showEdit.value = false;
    }
  }
});

/**
 * Returns red/yellow/green depending is it higher, lower or tie
 * @param {*} teamScore Team score that you want to get color
 * @param {*} team2Score The team score that you are comparing teamScore param
 * @returns {*} Color string: 'green' if lower, 'yellow' if tie and 'red' if higher
 */
function getColor(teamScore: number, team2Score: number) {
  if (teamScore < team2Score) {
    return 'green-accent-4';
  } else if (teamScore > team2Score) {
    return 'red-accent-4';
  } else {
    return 'yellow-accent-4';
  }
}
</script>

<style scoped>
a {
  color: black;
  text-decoration: none;
}
</style>
