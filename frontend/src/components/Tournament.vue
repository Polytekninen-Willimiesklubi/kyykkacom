<template>
  <div class="d-flex" v-if="loaded_undefined">
    <div align="center">
      <h1>TBD</h1>
    </div>
  </div>
  <div v-else class="d-flex">
    <div v-if="st_round.length" class="pr-10 pt-11">
      <div v-for="listItem in st_round" :key="listItem.name" class="pt-10">
        <bracket :flat-tree="[listItem]">
          <template #player="{player}" >
            {{ !only_format ? player.name : player.template_name }}
          </template>
          <template #player-extension-bottom="{ match }">
            <div align="center">
              {{ match.other_info }}
            </div>
          </template>
        </bracket>
      </div>
    </div>
    <div class="d-flex">
      <bracket :flat-tree="data">
        <template #player="{player}" >
          {{ !only_format ? player.name : player.template_name }}
        </template>
        <template #player-extension-bottom="{ match }">
          <div align="center">
            {{ match.other_info }}
          </div>
        </template>
      </bracket>
    </div>
  </div>
</template>

<script setup>
import Bracket from 'vue-tournament-bracket'

const props = defineProps({
  type: Number,
  played_games: Array,
  rounds_parrent: Array,
  first_round: Boolean,
  first: Number,
  only_format: Boolean,
  bracket_placements: Array,
  load_ended: Boolean,
  bronze: {
    type: Boolean,
    default: true
  }
});

const playoffStages = [{}, {}, {}, {}, {}, {}, {}];
let rounds = [];
const data = ref([]);
const st_round = ref([]);
const loaded_undefined = ref(false);

function putTeamsPlayoffBracket() {
  props.bracket_placements.forEach((bracket, idx) => {
    bracket.forEach(team => {
      const [teamName, seed] = team
      const seedString = props.bracket_placements.length >= 2
          ? String.fromCharCode(65 + idx) + (seed).toString()
          : (seed).toString() + '. Seed';
      
      const found = rounds.find(ele => 
           ele.player1.name === seedString
        || ele.player2.name === seedString
      );

      if (found){
        const correctBracket = found.player1.name === seedString 
          ? found.player1 
          : found.player2
        correctBracket.name = teamName
      }
    })

  })
}

function resolveGames() {
  const playoff_games = props.played_games.filter(ele => ele.post_season || ele.match_type >= 32)
  playoff_games.forEach(ele => {
    ele.match_type = ele.match_type >= 32 ? ele.match_type - 30 : ele.match_type
  })
  playoff_games.forEach(ele => {
    if (ele.match_type >= 2 & ele.match_type < 10) {
      const round = playoffStages[ele.match_type - 2]
      if (!(ele.seriers in round)) {
        round[ele.seriers] = {}
        round[ele.seriers][ele.home_team.current_abbreviation] = 0
        round[ele.seriers][ele.away_team.current_abbreviation] = 0
        round[ele.seriers]['tie'] = 0

      }
      if (ele.home_score_total < ele.away_score_total) {
        ++round[ele.seriers][ele.home_team.current_abbreviation]
      } else if (ele.home_score_total > ele.away_score_total) {
        ++round[ele.seriers][ele.away_team.current_abbreviation]
      } else {
        ++round[ele.seriers]['tie']
      }
    }
  })
}

function loadRounds() {
  if (props.rounds_parrent.length == 0) {
    loaded_undefined.value = true
    return
  }
  rounds = structuredClone(toRaw(props.rounds_parrent))
  rounds.forEach(ele => {
    ele.player1.template_name = ele.player1.name
    ele.player2.template_name = ele.player2.name
  })
  loaded_undefined.value = false
}

function splitFirstRound() {
  if (!props.first_round) {
    data.value = rounds
    return
  }
  const first_round_matches = rounds.filter(e => e.type == props.first)
  st_round.value = first_round_matches
  const games = playoffStages[props.first - 2]
  const winners = []
  for (const [key, el] of Object.entries(games)) {
    const match = st_round.value.find(e => e.player1.name == Object.keys(el)[0] || e.player2.name == Object.keys(el)[0])
    if (match === undefined) {
      console.log("Didn't find correct match. First round +  element: " + Object.keys(el))
      return
    }
    const [winner, loser] = el[match.player1.name] > el[match.player2.name] 
        ? [match.player1, match.player2]
        : [match.player2, match.player1];
    const new_winner = structuredClone(toRaw(winner))
    new_winner.winner = null
    winners.push(new_winner)
    winner.winner = true
    loser.winner = false
    match.other_info = el[match.player1.name].toString() + ' - ' + el[match.player2.name].toString()
    if(el[match.tie]) {
      match.other_info += ' (T: ' + el[match.tie] +')'; 
    }
  }
  winners.sort((a, b) => Number(b.id) - Number(a.id))
  winners.forEach((winner, i) => {
    const placementString = (i + 1).toString() + '. Low Seed'
    const new_match = rounds.find(el => el.player1.name == placementString || el.player2.name == placementString)
    const correct_column = new_match.player1.name.includes(placementString) ? 'player1' : 'player2'
    const template = new_match[correct_column].template_name
    winner.template_name = template
    new_match[correct_column] = winner
  })
  data.value = rounds.filter(e => e.type != props.first)
}

function resolvePlayoffs() {
  const reversed_list = playoffStages.reverse()
  reversed_list.forEach((ele, i) => {
    for (const [key, el] of Object.entries(ele)) {
      if (props.first_round && props.first == 7 - i) { continue }
      const match = data.value.find(e => e.type == 7 - i && (Object.keys(el)[0] == e.player1.name || Object.keys(el)[0] == e.player2.name))
      if (match === undefined) {
        console.log("Didn't find correct match. type: " + 7 - i + ' element: ' + Object.keys(el))
        return
      }
      const [team1Wins, team2Wins] = [el[match.player1.name], el[match.player2.name]];
      if (team1Wins !== team2Wins) {
        const [winner, loser] = team1Wins > team2Wins
          ? [match.player1, match.player2]
          : [match.player2, match.player1];
        const new_winner = structuredClone(toRaw(winner))
        const new_loser = structuredClone(toRaw(loser))
        new_winner.winner = null
        new_loser.winner = null
        winner.winner = true
        loser.winner = false
        match.other_info = team1Wins.toString() + ' - ' + team2Wins.toString()
        if(el[match.tie]) {
          match.other_info += ' (Ties: ' + el[match.tie] +')'; 
        }
        if (7 - i >= 4) { // Ignore Bronze and Finals
          if (7 - i == 4) { // SemiFinals -> Winner needs to be assigned to Finals
            const finals = rounds.find(ele => ele.type === 2)
            const correct_column = finals.player1.name.includes(match.name) ? 'player1' : 'player2'
            const template = finals[correct_column].template_name
            new_winner.template_name = template
            finals[correct_column] = new_winner
          }
          const new_match = rounds.find(ele => ele.id === match.next)
          const n = (7 - i != 4) ? 'name' : 'loser_name'
          const correct_column = new_match.player1.name.includes(match[n]) ? 'player1' : 'player2'
          const template = new_match[correct_column].template_name

          new_match[correct_column] = (7 - i == 4) && props.bronze ? new_loser : new_winner // SemiFinals -> Loser needs to be assigned to Bronze match
          new_match[correct_column].template_name = template
        }
      }
    }
  }, this)
}

watch(() => props.load_ended, (loadReady) => {
  if(!loadReady) return
  loadRounds();
  if(!loaded_undefined.value) {
    resolveGames();
    putTeamsPlayoffBracket();
    splitFirstRound();
    resolvePlayoffs();
  }
})

</script>

<style>
.vtb-player {
    background-color: white;
    border-color: black;
    border-style: solid solid none solid;
    border-width: 1px;
    color: black;
    text-align: center;
}
.vtb-item-players .winner {
    color: white;
}
.vtb-item-players .defeated {
    color: white;
}
.vtb-item-players > div {
    width: 135px;
}
</style>
