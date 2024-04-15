<template>
  <v-card>
    <v-row>
      <v-col>
        <v-card>
          <v-card-title align="center">{{header}}</v-card-title>
          <v-data-table
            :headers="overall_player_stats"
            :items="stats"
            color='alert'
            mobile-breakpoint="0"
          >
            <template v-slot:header="{ props }">
              <th
                v-for="h in props.headers"
                class="head-font"
                :class="returnHeaderColor(h.text)"
                @click="chanceHeaderStat"
              >
                {{ h.text }}
              </th>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card>
          <v-data-table
            mobile-breakpoint="0"
            disable-pagination
            color='alert'
            @click:row="chanceSeason"
            :headers="season_stats"
            height="200px"
            :items="all_seasons"
            :item-class="returnStyle"
            hide-default-footer
            dense
           />
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4">
        <v-card>
          <graph
            id_name="chart"
            height_px="200px"
            title="Heittotuloksen jakauma"
            :dataset="canvas1_data"
            :labels="canvas1_labels"
            :reversed=false
            type="bar"
          />
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card>
          <graph
            id_name="statGraph"
            height_px="200px"
            title="Statsin kehitys kausittain"
            :dataset="canvas2_data"
            :labels="canvas2_labels"
            :reversed=false
            type="line"
          />
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card>
          <graph
            id_name="kHP KPH"
            height_px="200px"
            title="Heittokeskiarvo heittopaikan mukaan"
            :dataset="canvas3_data"
            :labels="canvas3_labels"
            :reversed=true
            type="bar"
          />
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="2">
        <v-switch
          class='pl-2'
          v-model="sort_games_switch"
          hide-details
          true-value="Peleittäin"
          false-value="Erittäin"
          :label="`${sort_games_switch}`"
        />
      </v-col>
      <v-col cols="2">
        <v-switch
          v-model="filter_games_switch"
          hide-details
          true-value="Valitut kaudet"
          false-value="Kaikki kaudet"
          :label="`${filter_games_switch}`"
        />
      </v-col>
      <v-spacer/>
    </v-row>
    <v-row>
      <v-col cols="2">
        <v-text-field
          class='pl-2'
          color="red"
          v-model="search"
          label="Etsi"
          single-line
          ide-details
          variant="outlined"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card>
          <v-data-table
            v-if="sort_games_switch=='Erittäin'"
            @click:row="handleRedirect"
            mobile-breakpoint="0"
            color='alert'
            class="left-border-period"
            :search="search"
            :headers="headers"
            :items="filtterItems"
            :custom-sort="throwSort"
            dense
          >
            <template v-slot:no-data v-if="!data_loaded">
              <v-progress-linear color="red" slot="progress" indeterminate />
            </template>
            <template v-for="h in headers" v-slot:[`header.${h.value}`]="{ header }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                  <span v-on="on">{{h.text}}</span>
                </template>
                <span>{{h.tooltip}}</span>
              </v-tooltip>
            </template>
            <template v-slot:item.match_time="{ item }">
              <span>{{ item.match_time | luxon('y-MM-dd HH:mm') }}</span>
            </template>
            <template v-slot:item.own_score_round="{ item }">
              <v-chip :color="getColor(item.own_score_round, item.opp_score_round)">
                {{ item.own_score_round }}
              </v-chip>
            </template>
            <template v-slot:item.opp_score_round="{ item }">
              <v-chip :color="getColor(item.opp_score_round, item.own_score_round)">
                {{ item.opp_score_round }}
              </v-chip>
            </template>
          </v-data-table>
          <v-data-table v-else
            :headers="headers_games"
            :items="filtterItems"
            @click:row="handleRedirect"
            :custom-sort="throwSort"
            mobile-breakpoint="0"
            class='left-border-match'
            color='alert'
            dense
          >
            <template v-slot:no-data v-if="!data_loaded">
              <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
            </template>
            <template v-for="h in headers_games" v-slot:[`header.${h.value}`]="{ header }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                  <span v-on="on">{{ h.text }}</span>
                </template>
                <span>{{ h.tooltip }}</span>
              </v-tooltip>
            </template>
            <template v-slot:item.match_time="{ item }">
              <span>{{ item.match_time | luxon('y-MM-dd HH:mm') }}</span>
            </template>
            <template v-slot:item.own_score="{ item }">
              <v-chip :color="getColor(item.own_score, item.opponent_score)">
                {{ item.own_score }}
              </v-chip>
            </template>
            <template v-slot:item.opponent_score="{ item }">
              <v-chip :color="getColor(item.opponent_score, item.own_score)">
                {{ item.opponent_score }}
              </v-chip>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { usePlayerStore } from '@/stores/players.store';

const playerStore = usePlayerStore();

const playersSeasons = playerStore.player.stats_per_seasons;

const header = ref('')
const search = ref('')
const sort_games_switch = ref('Erittäin');
const filter_games_switch = ref('Kaikki kaudet');
const stats = ref([]);
const styles = ref(['blue-row', 'red-row', 'green-row', 'yellow-row', 'purple-row']);
const all_colors = ref(['#B3E5FC', '#EF9A9A', '#A5D6A7', '#DCE775', '#BA68C8']);
const canvas1_labels = ref(['0', '1', '2', '3', '4', '5', '≥6']);
const canvas2_labels = ref([]);
const canvas3_labels = ref(['1', '2', '3', '4']);
const canvas1_data = ref([]);
const canvas2_data = ref([]);
const canvas3_data = ref([]);
const matches_periods = ref([]);
const matches_match = ref([]);
const all_seasons = ref([]);
const current_selection = ref([]);
const column_current_selection = ref([]);
const column_colors =  ref(['KPH', '', '', '', '']);
const colors = ref(['', '', '', '', '']);
const throw_chart = ref('');

const headers = [
  { text: 'Aika', value: 'match_time', align: 'center', tooltip: 'Pelausaika' },
  { text: 'Vastustaja', value: 'opp_name', align: 'center', tooltip: 'Vastustaja joukkue' },
  { text: 'Erä', value: 'period', align: 'center', tooltip: 'Pelin erä' },
  { text: 'HP', value: 'turn', align: 'center', tooltip: 'Heittopaikka' },
  { text: '1', value: 'score_first', align: 'center', tooltip: '1. heitto (Kyykkää)' },
  { text: '2', value: 'score_second', align: 'center', tooltip: '2. heitto (Kyykkää)' },
  { text: '3', value: 'score_third', align: 'center', tooltip: '3. heitto (Kyykkää)' },
  { text: '4', value: 'score_fourth', align: 'center', tooltip: '4. heitto (Kyykkää)' },
  { text: 'Yht.', value: 'score_total', align: 'center', tooltip: 'Heitot Yhteensä (Kyykkää)' },
  { text: 'KPH', value: 'score_average_round', align: 'center', tooltip: 'Kyykkää per Heitto' },
  { text: 'OJ pis.', value: 'own_score_round', align: 'center', tooltip: 'Oman joukkueen pisteet' },
  { text: 'V pis.', value: 'opp_score_round', align: 'center', tooltip: 'Vastustaja joukkueen pisteet' }
]
const headers_games = [
  { text: 'Aika', value: 'match_time', align: 'center', tooltip: 'Pelausaika' },
  { text: 'Vastustaja', value: 'opponent_name', align: 'center', tooltip: 'Vastustaja joukkue' },
  { text: 'HP1', value: 'throw_turn_one', align: 'center', tooltip: '1. erän heittopaikka' },
  { text: 'HP2', value: 'throw_turn_two', align: 'center', tooltip: '2. erän heittopaikka' },
  { text: '1', value: 'score_first', align: 'center', tooltip: '1.erän 1.heitto (Kyykkää)' },
  { text: '2', value: 'score_second', align: 'center', tooltip: '1.erän 2.heitto (Kyykkää)' },
  { text: '3', value: 'score_third', align: 'center', tooltip: '1.erän 3.heitto (Kyykkää)' },
  { text: '4', value: 'score_fourth', align: 'center', tooltip: '1.erän 4.heitto (Kyykkää)' },
  { text: '5', value: 'score_fifth', align: 'center', tooltip: '2.erän 1.heitto (Kyykkää)' },
  { text: '6', value: 'score_sixth', align: 'center', tooltip: '2.erän 2.heitto (Kyykkää)' },
  { text: '7', value: 'score_seventh', align: 'center', tooltip: '2.erän 3.heitto (Kyykkää)' },
  { text: '8', value: 'score_eighth', align: 'center', tooltip: '2.erän 4.heitto (Kyykkää)' },
  { text: 'Yht.', value: 'score_total', align: 'center', tooltip: 'Heitot Yhteensä (Kyykkää)' },
  { text: 'KPH', value: 'score_average_match', align: 'center', tooltip: 'Kyykkää per Heitto' },
  { text: 'OJ pis.', value: 'own_score', align: 'center', tooltip: 'Oman joukkueen pisteet' },
  { text: 'V pis.', value: 'opponent_score', align: 'center', tooltip: 'Vastustaja joukkueen pisteet' }
]
const overall_player_stats = [
  { text: 'Kausi', value: 'season', align: 'center', tooltip: 'Kaikkien kausien tulokset', sortable: false },
  { text: 'Kaudet', value: 'season_count', align: 'center', tooltip: 'Pelatut NKL kaudet', sortable: false },
  { text: 'Erät', value: 'all_rounds_total', align: 'center', tooltip: 'Kaikki pelatut erät', sortable: false },
  { text: 'Poistetut kyykät', value: 'all_score_total', align: 'center', tooltip: 'Kaikki poistetut kyykät', sortable: false },
  { text: 'Heitot', value: 'all_throws_total', align: 'center', tooltip: 'Kaikki heitot', sortable: false },
  { text: 'KPH', value: 'total_average_throw', align: 'center', tooltip: 'Kyykkää per Heitto', sortable: false },
  { text: 'kHP', value: 'total_average_throw_turn', align: 'center', tooltip: 'Keskimääräinen heittopaikka', sortable: false },
  { text: 'Hauet', value: 'all_pikes_total', align: 'center', tooltip: 'Kaikki Hauet', sortable: false },
  { text: 'H%', value: 'total_pike_percentage', align: 'center', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot', sortable: false },
  { text: 'Virkamiehet', value: 'all_zeros_total', align: 'center', tooltip: 'Nollaheitot ilman haukia', sortable: false },
  { text: 'VM%', value: 'total_zero_percentage', align: 'center', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot', sortable: false },
  { text: 'JK', value: 'all_gteSix_total', align: 'center', tooltip: 'Joulukuuset: 6 tai paremmat heitot', sortable: false }
]
const season_stats = [
  { text: 'Kausi', value: 'season', align: 'center', tooltip: 'Pelikausi (vuosi)' },
  { text: 'Joukkue', value: 'team_name', align: 'center', tooltip: 'Joukkue nimi' },
  { text: 'Erät', value: 'rounds_total', align: 'center', tooltip: 'Kaikki pelatut erät' },
  { text: 'Poistetut kyykät', value: 'score_total', align: 'center', tooltip: 'Kaikki poistetut kyykät' },
  { text: 'Heitot', value: 'throws_total', align: 'center', tooltip: 'Kaikki heitot' },
  { text: 'KPH', value: 'score_per_throw', align: 'center', tooltip: 'Kyykkää per Heitto' },
  { text: 'kHP', value: 'avg_throw_turn', align: 'center', tooltip: 'Keskimääräinen heittopaikka' },
  { text: 'Hauet', value: 'pikes_total', align: 'center', tooltip: 'Kaikki Hauet' },
  { text: 'H%', value: 'pike_percentage', align: 'center', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
  { text: 'Virkamiehet', value: 'zeros_total', align: 'center', tooltip: 'Nollaheitot ilman haukia' },
  { text: 'VM%', value: 'zero_percentage', align: 'center', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
  { text: 'JK', value: 'gteSix_total', align: 'center', tooltip: 'Joulukuuset: 6 tai paremmat heitot' }
]

function filtterItems() {
  const arr = sort_games_switch.value === 'Erittäin'
    ? playerStore.playerMatchesPerPeriod 
    : playerStore.playerMatchesPerMatch;
  const returning_arr = filter_games_switch.value === 'Kaikki kaudet'
    ? arr
    : arr.filter(ele => current_selection.value.includes(ele.season));

  if (search.value == '') {
    return returning_arr
  }
  return returning_arr.filter(match => {
    let found = false
    for (const key in match) {
      if (key == 'id') { continue }
      const ele = typeof match[key] !== 'string' ? String(match[key]) : match[key]
      if (ele.toLowerCase().includes(search.value.toLowerCase())) {
        found = true
        break
      }
    }
    return found
  })
}

function handleRedirect(value, row) {
  location.href = '/ottelut/' + row.item.match_id
}

function getColor (val1, val2) {
  if (val1 < val2) return '#C8E6C9' // green-lighten-4
  else if (val1 > val2) return '#EF9A9A' // red-lighten-4
  else return '#F0F4C3' // yellow-lighten-4
}

function returnStyle (value) {
  const index = colors.value.indexOf(value.season)
  if (index === -1) {
    return
  }
  return styles.value[index]
}

function returnHeaderColor (value) {
  const index = column_colors.value.indexOf(value)
  if (index === -1) {
    return
  }
  return styles.value[index]
}

function chanceHeaderStat (val) {
  const header_class_list = val.target.classList
  const head = val.target.innerText
  const headers = ['Erät', 'Poistetut kyykät', 'Heitot', 'KPH', 'kHP', 'Hauet', 'H%',
    'Virkamiehet', 'VM%', 'JK']
  const header_binds = ['rounds_total', 'score_total', 'throws_total', 'score_per_throw',
    'avg_throw_turn', 'pikes_total', 'pike_percentage', 'zeros_total', 'zero_percentage', 'gteSix_total']

  if (!headers.includes(head)) { return }

  if (column_current_selection.value.includes(head)) {
    let index = canvas2_data.value.map(ele => ele.label).indexOf(head)
    canvas2_data.value.splice(index, 1)

    index = column_current_selection.value.indexOf(head)
    column_current_selection.value.splice(index, 1)

    index = column_colors.value.indexOf(head)
    column_colors.value[index] = ''
    header_class_list.remove(styles.value[index])
  } else if (column_current_selection.value.length == 5) {

  } else {
    let index = column_colors.value.indexOf('')
    const color = all_colors.value[index]
    header_class_list.add(styles.value[index])

    column_colors.value[index] = head

    const dat = []
    index = headers.indexOf(head)
    playersSeasons.forEach(s => {
      dat.push(s[header_binds[index]])
    })
    canvas2_data.value.push({
      label: head,
      data: dat,
      backgroundColor: color,
      borderColor: color,
      borderColor: color,
      data: dat,
      borderColor: color,
      data: dat
    })

    column_current_selection.value.push(head)
  }
}
function throwSort (items, index, isDescending) {
  const custom_columns = ['score_first', 'score_second', 'score_third', 'score_fourth',
    'score_fifth', 'score_sixth', 'score_seventh', 'score_eighth']

  function d (p1) {
    switch (p1) {
      case 0:
        return -1
      case 'e':
        return 0
      case 'h':
        return -2
      default:
        return p1
    }
  }

  items.sort((a, b) => {
    if (!isNaN(custom_columns.includes(index[0]))) {
      const a1 = d(a[index[0]])
      const b1 = d(b[index[0]])
      if (!isDescending[0]) {
        return a1 < b1 ? 1 : a1 === b1 ? 0 : -1
      } else {
        return a1 < b1 ? -1 : a1 === b1 ? 0 : 1
      }
    } else {
      if (!isDescending[0]) {
        return a[index[0]] > b[index[0]] ? 1 : -1
      } else {
        return a[index[0]] > b[index[0]] ? -1 : 1
      }
    }
  })
  return items
}

function chanceSeason (value, row) {
  row.select(true) // <--- For some reason this is important to make returnStyle method work onclick
  if (current_selection.value.includes(value.season)) { // Remove clicked season from datas
    var index = canvas1_data.value.map(e => e.label).indexOf('Kausi ' + value.season)
    canvas1_data.value.splice(index, 1)
    canvas3_data.value.splice(index, 1) // Same index can be used to splice canvas3, because we always update both everywhere

    index = current_selection.value.indexOf(value.season)
    current_selection.value.splice(index, 1)

    index = colors.value.indexOf(value.season)
    colors.value[index] = ''
  } else if (current_selection.value.length == 5) { // Not removal, but the 'memory' is full

  } else { // Add clicked season
    let idx = playersSeasons.map(ele => ele.season).indexOf(value.season)
    const selected_season = playersSeasons[idx]

    idx = colors.value.indexOf('') // First valid color
    colors.value[index] = value.season
    const color = all_colors.value[index]

    canvas1_data.value.push({
      label: 'Kausi ' + selected_season.season,
      backgroundColor: color,
      data: [
        selected_season.zeros_total + selected_season.pikes_total,
        selected_season.ones_total,
        selected_season.twos_total,
        selected_season.threes_total,
        selected_season.fours_total,
        selected_season.fives_total,
        selected_season.gteSix_total
      ]
    })

    canvas3_data.value.push({
      label: 'Kausi ' + selected_season.season,
      backgroundColor: color,
      data: [
        selected_season.average_score_position_one,
        selected_season.average_score_position_two,
        selected_season.average_score_position_three,
        selected_season.average_score_position_four
      ]
    })

    current_selection.value.push(value.season)
  }
}


playerStore.getPlayers();

if (playersSeasons && playersSeasons.length !== 0) {
  let index = playersSeasons.map(ele => ele.id).index(navStore.seasonId)
  // If the selected season is not in players history take the latest
  index = (index === -1) ? playersSeasons.length -1 : index
  const currentSelcSeason = playersSeasons[index]
  const seasonString = currentSelcSeason.season
  
  current_selection.value.push(seasonString)
  colors.value[0] = seasonString
  column_current_selection.value.push('KPH')
  matches_periods.value = []
  matches_match.value = []

  const init1 = {
    label: 'Kausi ' + currentSelcSeason.season,
    backgroundColor: '#B3E5FC',
    data: [
      currentSelcSeason.zeros_total + currentSelcSeason.pikes_total,
      currentSelcSeason.ones_total,
      currentSelcSeason.twos_total,
      currentSelcSeason.threes_total,
      currentSelcSeason.fours_total,
      currentSelcSeason.fives_total,
      currentSelcSeason.gteSix_total
    ]
  }
  const canvas2_data_tmp = []
  for (const s of playersSeasons) {
    canvas2_data_tmp.push(s.score_per_throw)
    canvas2_labels.value.push(s.season)
  }
  const init2 = {
    label: 'KPH',
    backgroundColor: '#B3E5FC',
    borderColor: '#B3E5FC',
    data: canvas2_data_tmp
  }
  
  const init3 = {
    label: 'Kausi ' + currentSelcSeason.season,
    backgroundColor: '#B3E5FC',
    data: [
      currentSelcSeason.average_score_position_one,
      currentSelcSeason.average_score_position_two,
      currentSelcSeason.average_score_position_three,
      currentSelcSeason.average_score_position_four
    ]
  }
  canvas1_data.value.push(init1)
  canvas2_data.value.push(init2)
  canvas3_data.value.push(init3)
}


</script>

<style>

tbody tr :hover {
    cursor: unset;
}

.left-border-period > .v-data-table__wrapper > table > tbody > tr > td:nth-child(5) {
  border-left: 1px solid grey;
  text-align: center;
}

.left-border-period > .v-data-table__wrapper > table > tbody > tr > td:nth-child(9) {
  border-left: 1px solid grey;
  text-align: center;
}

.left-border-match > .v-data-table__wrapper > table > tbody > tr > td:nth-child(5) {
  border-left: 1px solid grey;
  text-align: center;
}

.left-border-match > .v-data-table__wrapper > table > tbody > tr > td:nth-child(13) {
  border-left: 1px solid grey;
  text-align: center;
}

.v-data-table-header th {
  white-space: nowrap;
}

.head-font {
  margin: auto;
  vertical-align: middle !important;
  height: 32px;
  font-size: 0.75rem;
}

.purple-row {
  background-color: #BA68C8 !important;
}

.yellow-row {
  background-color: #DCE775 !important;
}

.green-row {
  background-color: #A5D6A7 !important;
}

.blue-row {
  background-color: #B3E5FC !important;
}

.red-row {
  background-color: #EF9A9A !important;
}

</style>
