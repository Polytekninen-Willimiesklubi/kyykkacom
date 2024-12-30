<!-- TODO Pitää tarkistaa patchien ja loadien toimivuus -->

<template>
  <v-card>
    <v-card-title class="pa-0 pl-3 pt-3">
      Erä {{props.roundNumber}}
      <v-spacer/>
      <v-progress-circular
        :size="20"
        :width="2"
        color="red"
        indeterminate
        v-if="loading"
      />
    </v-card-title>
    <v-row v-if="!show_input" row wrap>
      <v-card-text v-if="roundScore || roundScore == '0'">
        <p>
          {{teamName}}
          <v-chip
            style="float:right;"
            :color="color"
            label
            small
            class="mr-2"
          >
            {{ roundScore }}
          </v-chip>
        </p>
      </v-card-text>
    </v-row>
    <v-divider />
    <v-row v-if="show_input" row wrap>
      <v-card-text v-if="loaded">
        <p>
          {{teamName}}
          <v-text-field 
            @input="roundScore()" 
            style="width:10%; float:right;" 
            v-model="roundScore" 
            class="centered-input" 
            label="total" 
            maxlength="3"
          />
        </p>
      </v-card-text>
    </v-row>
    <!-- TODO loading -->
    <v-data-table 
      v-if="!show_input"
      mobile-breakpoint="0" 
      :headers="headersRound"
      @click:row="handleRedirect"
      :items="data"
      no-data-text="Ei dataa :("
      :no-filter="true"
    >
      <template #bottom></template> <!-- This hides the pagination controls-->
    </v-data-table>
    <!-- TODO loading -->
    <v-data-table 
      v-else
      mobile-breakpoint="0" 
      v-model="select"
      :headers="headersRound"
      :items="data"
      :items-per-page="4"
    >
      <template v-slot:headers class="text-xs-center"></template>
      <template v-slot:item="props" >
        <tr>
          <!-- <td :ref="'id_'+props.index">{{selected[props.index].player.id}}</td> -->
          <td>
            <v-select 
              item-color="red"
              color="red"
              v-model="selected[props.index].player.player_name"
              @change="loadPlayer($event, props.index)" 
              class="text-center pr-1" 
              placeholder="Select player" 
              :items="players"
              item-title="player_name"
              single-line
            />
          </td>
          <td v-for="i in ['first', 'second', 'third', 'fourth']">
            <v-text-field 
              color="red"
              v-model="selected[props.index]['score_'+ i]"
              :ref="i+'_throw_'+props.index"
              class="centered-input"
              maxlength="2"
              @input="sumTotal(props.index)"
              @keypress="isNumber($event)"
            />
          </td>
          <td 
            class="centered-input" 
            style="font-size:18px" 
            :ref="'throw_sum_'+props.index"
          >
            {{selected[props.index]['score_total']}}
          </td>
        </tr>
        
      </template>
      <template #bottom></template> <!-- This hides the pagination controls-->
    </v-data-table>
  </v-card>
</template>

<script setup>
import { headersRound } from '@/stores/headers';

const props = defineProps({
    color: String,
    matchData: Object,
    roundNumber: String,
    teamSide: String,
})

const roundString = props.roundNumber === '1' ? 'first_round' : 'second_round';

const data = props.matchData[roundString][props.teamSide];
const roundScore = props.matchData[props.teamSide + '_' + roundString + '_score'];
const players = props.matchData[props.teamSide+'_team'].players
const teamName = props.matchData[props.teamSide+'_team'].current_abbreviation

const select = [];
const tmp_selected = [];

data.forEach(function (item) {
  tmp_selected.push(item)
})
const selected = tmp_selected;
const loaded = true;
let show_input
if (!props.matchData.is_validated) {
  if (localStorage.team_id == props.matchData.home_team.id) {
    show_input = (localStorage.role_id == 1)
  }
}

function handleRedirect (value, row) {
  location.href = '/pelaajat/' + row.item.player.id
}

function isNumber(evt) {
  // Checks that the value is an H or a numeric value from the ASCII table.
  // not verified atm?
  evt = (evt) || window.event
  const charCode = (evt.which) ? evt.which : evt.keyCode
  if ((charCode > 31 && (charCode < 48 || charCode > 57)) && charCode !== 72 && charCode !== 104 && charCode !== 69 && charCode !== 101) {
    evt.preventDefault()
  } else {
    return true
  }
}

function loadPlayer(player, index) {
  // Finds the selected player object from the dataset and sets it's id to the id field.
  const obj = props.matchData[props.teamSide + '_team'].players.find(o => o.player_name === player)
  this.$refs['id_' + index].innerHTML = obj.id
  select = []
  sumTotal(index)
}
</script>

<style scoped>
p {
  margin-bottom: 0;
  padding-bottom: 0;
  margin-left: .7em;
}

td {
  padding: 0 !important;
  text-align: center !important;
}

.centered-input :deep(input) {
  text-align: center
}

.v-text-field {
  font-size: 1.1em !important;
}
</style>
