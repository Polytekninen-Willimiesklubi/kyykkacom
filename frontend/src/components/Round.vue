<!-- TODO Pitää tarkistaa patchien ja loadien toimivuus -->

<template>
  <v-card>
    <v-card-title class="pa-0 pl-3 pt-3 pb-3">
      <v-row>
        <v-col cols="2">
          Erä {{ props.roundNumber }}
        </v-col>
        <v-spacer />
        <v-col cols="8" style="text-align:center">
          {{ teamName }}
        </v-col>
        <v-col
          cols="2"
          style="text-align:right; padding-right: 1em;"
        >
          <v-chip v-if="!showInput && (roundScore || roundScore == '0')"
            style="float:right;"
            :color="color"
            label
            small
            class="mr-2"
          >
            {{ roundScore }}
          </v-chip>
          <v-text-field v-else-if="showInput"
            @input="roundStore.patchRoundScore(props.teamSide, props.roundNumber, roundScore)" 
            v-model="roundScore" 
            class="centered-input" 
            label="Tulos" 
            maxlength="3"
          />
        </v-col>
      </v-row>
    </v-card-title>
    <!-- TODO loading -->
    <v-data-table 
      v-if="!showInput"
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
          <td>
            <v-select 
              item-color="red"
              color="red"
              v-model="selected[props.index].player"
              class="text-center pr-1" 
              placeholder="Valitse pelaaja"
              :items="players"
              item-title="player_name"
              item-value="id"
              @update:model-value="(playerId) => roundStore.updateThrower(selected[props.index].id, playerId)"
              single-line
            />
          </td>
          <td v-for="throwString in ['first', 'second', 'third', 'fourth']">
            <v-text-field 
              color="red"
              class="centered-input"
              maxlength="2"
              v-model="selected[props.index]['score_'+ throwString]"
              @input="
                roundStore.updateThrowScore('score_'+ throwString, selected[props.index]);
                updateThrowTotal(selected[props.index])
              "
              @keypress="isNumber($event)"
            />
          </td>
          <td class="centered-input" style="font-size:18px">
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
import { useRoundStore } from '@/stores/round.store'

const props = defineProps({
    color: String,
    matchData: Object,
    roundNumber: String,
    teamSide: String,
});

const roundStore = useRoundStore();

const roundString = props.roundNumber === '1' ? 'first_round' : 'second_round';

const data = props.matchData[roundString][props.teamSide];
const roundScore = ref(props.matchData[props.teamSide + '_' + roundString + '_score']);
const players = props.matchData[props.teamSide+'_team'].players;
const teamName = props.matchData[props.teamSide+'_team'].current_abbreviation;

const select = ref([]);
const selected = ref([]);
const showInput = ref(false);

data.forEach(function (item) {
  if (Object.keys(item.player).length === 0) {
    item.player = null;
  }
  selected.value.push(item);
})

if (
  !props.matchData.is_validated
  && localStorage.teamId == props.matchData.home_team.id 
  && (localStorage.roleId == 1 || localStorage.roleId == 2)
) {
  showInput.value = true;
} else {
  showInput.value = false;
}

function handleRedirect (value, row) {
  if (row.item.player.id !== undefined) {
    location.href = '/pelaajat/' + row.item.player.id;
  }
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

function updateThrowTotal(throwerObject) {
  throwerObject["score_total"] = 0
  
  for (let order of ["first", "second", "third", "fourth"]) {
    let score = throwerObject[`score_${order}`];
    let number;
    if (score === null || score.toLowerCase() === "h" || score.toLowerCase() === "e" ) {
      number = 0
    } else {
      number = (!isNaN(parseInt(score))) ? parseInt(score) : 0;
    }
    throwerObject["score_total"] += number
  }
}

</script>

<style scoped>
p {
  margin-bottom: 0;
  padding-bottom: 0;
  margin-left: 0.5em;
  font-size: large;
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
