<template>
  <v-container class='pt-0' grid-list-md>
    <v-row>
      <v-col>
        <v-card v-if="dataReady">
          <v-row>
            <v-col>
              <v-row class="mt-3 ml-2 mr-2">
                <v-col cols="4" align="left" style="font-size: large; font-weight: bold">
                  {{matchData.type_name}} kenttä
                  <span v-if="matchData.field">
                      {{matchData.field}}
                  </span>
                  <span v-else>TBD</span>
                </v-col>
                <v-spacer v-if="matchData.video_link || matchData.stream_link"/>
                <template v-else>
                  <v-col v-if="matchData.stream_link">
                    <v-tooltip
                      activator='parent'
                      text="Striimin linkki"
                      location="left"
                    />
                    <v-btn
                      :href="matchData.stream_link"
                      icon="mdi-access-point"
                      size="small"
                      variant="plain"
                    />
                  </v-col>
                  <v-col v-if="matchData.video_link">
                    <v-tooltip
                      activator='parent'
                      text="Videolinkki"
                      location="left"
                    />
                    <v-btn
                      :href="matchData.video_link"
                      icon="mdi-youtube"
                      size="small"
                      variant="plain"
                    />
                  </v-col>
                </template>
                <v-col cols="4" align="right" style="font-size: large; font-weight: bold">
                  {{ date.formatByString(date.date(matchData.match_time), 'yyyy-MM-dd HH:mm') }}
                </v-col>
              </v-row>
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
                  <v-chip
                    :color="`${getColor(matchData.home_score_total,
                      matchData.away_score_total)}`"
                    :text=String(matchData.home_score_total)
                  />
                </figcaption>
              </figure>
            </v-col>
            <v-col class=''>
              <a :href="'/joukkueet/'+matchData.home_team.id">
                {{matchData.home_team.current_name}}
              </a>
            </v-col>
            <v-col>
              vs.
            </v-col>
            <v-col>
              <a :href="'/joukkueet/'+matchData.away_team.id">
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
                  <v-chip
                    :color="getColor(matchData.away_score_total,
                      matchData.home_score_total)"
                    :text=String(matchData.away_score_total)
                  />
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
            :color="getColor(matchData.home_first_round_score,
              matchData.away_first_round_score)"
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
            :color="getColor(matchData.away_first_round_score,
              matchData.home_first_round_score)"
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
            :color="getColor(matchData.home_second_round_score,
              matchData.away_second_round_score)"
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

<script setup>
import { useMatchStore } from '@/stores/match.store';
import { useDate } from 'vuetify';
import { useRoute } from 'vue-router/auto';

const matchStore = useMatchStore();
const route = useRoute('/ottelut/[id]');
const date = useDate();

const {matchData, dataReady, isAwayCaptain} = storeToRefs(matchStore);
matchStore.getMatchData(route.params.id);

/**
 * Returns red/yellow/green depending is it higher, lower or tie
 * @param {*} teamScore Team score that you want to get color
 * @param {*} team2Score The team score that you are comparing teamScore param
 * @returns {*} Color string: 'green' if lower, 'yellow' if tie and 'red' if higher
 */
function getColor(teamScore, team2Score) {
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
