<template>
  <v-card>
    <v-row>
      <v-col>
        <v-card>
          <v-card-title align="center">{{playerStore.player.player_name}}</v-card-title>
          <v-data-table
            :headers="overall_player_stats"
            :items="[playerStore.player]"
            color='alert'
            mobile-breakpoint="0"
          >
            <template v-for="h in overall_player_stats" v-slot:[`header.${h.value}`]="{ header }"> 
              <th>
                {{ h.title }}
                <v-tooltip
                  activator="parent"
                  location="bottom"
                >
                  {{ h.tooltip }}
                </v-tooltip>
              </th>
              <!-- <th
                v-for="h in header"
                class="head-font"
                :class="returnHeaderColor(h.text)"
                @click="chanceHeaderStat"
              >
                {{ h.text }}
              </th> -->
          
            </template>
            <template #bottom></template> <!-- This hides the pagination controls-->
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card>
          <v-data-table
            mobile-breakpoint="0"
            color='alert'
            @click:row="chanceSeason"
            :headers="season_stats"
            height="200px"
            no-data-text="Ei pelattuja kausia"
            :items="playerStore.player.stats_per_seasons"
            :item-class="returnStyle"
            fixed-header
          >
            <template #bottom></template> <!-- This hides the pagination controls-->
          </v-data-table>
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
          @update:modelValue="filtterItems"
        />
      </v-col>
      <v-col cols="2">
        <v-switch
          v-model="filter_games_switch"
          hide-details
          true-value="Valitut kaudet"
          false-value="Kaikki kaudet"
          :label="`${filter_games_switch}`"
          @update:modelValue="filtterItems"
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
          <!-- TODO: loading -->
          <v-data-table
            @click:row="handleRedirect"
            mobile-breakpoint="0"
            color='alert'
            class="left-border-period"
            no-data-text="Ei dataa :("
            :search="search"
            :headers="matchHeaders"
            :items="matchItems"
            :custom-sort="throwSort"
          >
            <template v-for="h in matchHeaders" v-slot:[`header.${h.value}`]="{ header }">  
              <span>
                {{ h.title }}
                <v-tooltip
                  activator="parent"
                  location="bottom"
                >
                  {{ h.tooltip }}
                </v-tooltip>
              </span>
            </template>
            <template v-slot:[`item.match_time`]="{ item }">
              <span>{{ date.formatByString(date.date(item.match_time), 'yyyy-MM-dd HH:mm') }}</span>
            </template>
            <template v-slot:item.own_team_total="{ item }">
              <v-chip :color="getColor(item.own_team_total, item.opposite_team_total)">
                {{ item.own_team_total }}
              </v-chip>
            </template>
            <template v-slot:item.opposite_team_total="{item}">
              <v-chip :color="getColor(item.opposite_team_total, item.own_team_total)">
                {{ item.opposite_team_total }}
              </v-chip>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { useNavBarStore } from '@/stores/navbar.store';
import { usePlayerStore } from '@/stores/players.store';
import { useDate } from 'vuetify';

const playerStore = usePlayerStore();
const navStore = useNavBarStore();
const date = useDate();

const playersSeasons = playerStore.player.stats_per_seasons;

const search = ref('')
const sort_games_switch = ref('Erittäin');
const filter_games_switch = ref('Kaikki kaudet');
const styles = ref(['blue-row', 'red-row', 'green-row', 'yellow-row', 'purple-row']);
const all_colors = ref(['#B3E5FC', '#EF9A9A', '#A5D6A7', '#DCE775', '#BA68C8']);
const canvas1_labels = ref(['0', '1', '2', '3', '4', '5', '≥6']);
const canvas2_labels = ref([]);
const canvas3_labels = ref(['1', '2', '3', '4']);
const canvas1_data = ref([]);
const canvas2_data = ref([]);
const canvas3_data = ref([]);
const current_selection = ref([]);
const column_current_selection = ref([]);
const column_colors =  ref(['KPH', '', '', '', '']);
const colors = ref(['', '', '', '', '']);

const matchItems = ref([]);

const headers_periods = [
  { title: 'Aika', value: 'match_time', align: 'center', tooltip: 'Pelausaika' },
  { title: 'Vastustaja', value: 'opp_name', align: 'center', tooltip: 'Vastustaja joukkue' },
  { title: 'Erä', value: 'period', align: 'center', tooltip: 'Pelin erä' },
  { title: 'HP', value: 'turn', align: 'center', tooltip: 'Heittopaikka' },
  { title: '1', value: 'score_first', align: 'center', tooltip: '1. heitto (Kyykkää)' },
  { title: '2', value: 'score_second', align: 'center', tooltip: '2. heitto (Kyykkää)' },
  { title: '3', value: 'score_third', align: 'center', tooltip: '3. heitto (Kyykkää)' },
  { title: '4', value: 'score_fourth', align: 'center', tooltip: '4. heitto (Kyykkää)' },
  { title: 'Yht.', value: 'score_total', align: 'center', tooltip: 'Heitot Yhteensä (Kyykkää)' },
  { title: 'KPH', value: 'score_average_round', align: 'center', tooltip: 'Kyykkää per Heitto' },
  { title: 'OJ pis.', value: 'own_score_round', align: 'center', tooltip: 'Oman joukkueen pisteet' },
  { title: 'V pis.', value: 'opp_score_round', align: 'center', tooltip: 'Vastustaja joukkueen pisteet' }
];

const matchHeaders = ref(headers_periods);

const headers_games = [
  { title: 'Aika', value: 'match_time', align: 'center', tooltip: 'Pelausaika' },
  { title: 'Vastustaja', value: 'opponent_name', align: 'center', tooltip: 'Vastustaja joukkue' },
  { title: 'HP1', value: 'throw_turn_one', align: 'center', tooltip: '1. erän heittopaikka' },
  { title: 'HP2', value: 'throw_turn_two', align: 'center', tooltip: '2. erän heittopaikka' },
  { title: '1', value: 'score_first', align: 'center', tooltip: '1.erän 1.heitto (Kyykkää)' },
  { title: '2', value: 'score_second', align: 'center', tooltip: '1.erän 2.heitto (Kyykkää)' },
  { title: '3', value: 'score_third', align: 'center', tooltip: '1.erän 3.heitto (Kyykkää)' },
  { title: '4', value: 'score_fourth', align: 'center', tooltip: '1.erän 4.heitto (Kyykkää)' },
  { title: '5', value: 'score_fifth', align: 'center', tooltip: '2.erän 1.heitto (Kyykkää)' },
  { title: '6', value: 'score_sixth', align: 'center', tooltip: '2.erän 2.heitto (Kyykkää)' },
  { title: '7', value: 'score_seventh', align: 'center', tooltip: '2.erän 3.heitto (Kyykkää)' },
  { title: '8', value: 'score_eighth', align: 'center', tooltip: '2.erän 4.heitto (Kyykkää)' },
  { title: 'Yht.', value: 'score_total', align: 'center', tooltip: 'Heitot Yhteensä (Kyykkää)' },
  { title: 'KPH', value: 'score_average_match', align: 'center', tooltip: 'Kyykkää per Heitto' },
  { title: 'OJ pis.', value: 'own_score', align: 'center', tooltip: 'Oman joukkueen pisteet' },
  { title: 'V pis.', value: 'opponent_score', align: 'center', tooltip: 'Vastustaja joukkueen pisteet' }
]
const overall_player_stats = [
  { title: 'Kausi', value: 'season', align: 'center', tooltip: 'Kaikkien kausien tulokset', sortable: false },
  { title: 'Kaudet', value: 'season_count', align: 'center', tooltip: 'Pelatut NKL kaudet', sortable: false },
  { title: 'Erät', value: 'all_rounds_total', align: 'center', tooltip: 'Kaikki pelatut erät', sortable: false },
  { title: 'Poistetut kyykät', value: 'all_score_total', align: 'center', tooltip: 'Kaikki poistetut kyykät', sortable: false },
  { title: 'Heitot', value: 'all_throws_total', align: 'center', tooltip: 'Kaikki heitot', sortable: false },
  { title: 'KPH', value: 'total_average_throw', align: 'center', tooltip: 'Kyykkää per Heitto', sortable: false },
  { title: 'kHP', value: 'total_average_throw_turn', align: 'center', tooltip: 'Keskimääräinen heittopaikka', sortable: false },
  { title: 'Hauet', value: 'all_pikes_total', align: 'center', tooltip: 'Kaikki Hauet', sortable: false },
  { title: 'H%', value: 'total_pike_percentage', align: 'center', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot', sortable: false },
  { title: 'Virkamiehet', value: 'all_zeros_total', align: 'center', tooltip: 'Nollaheitot ilman haukia', sortable: false },
  { title: 'VM%', value: 'total_zero_percentage', align: 'center', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot', sortable: false },
  { title: 'JK', value: 'all_gteSix_total', align: 'center', tooltip: 'Joulukuuset: 6 tai paremmat heitot', sortable: false }
]
const season_stats = [
  { title: 'Kausi', value: 'season', align: 'center', tooltip: 'Pelikausi (vuosi)' },
  { title: 'Joukkue', value: 'team_name', align: 'center', tooltip: 'Joukkue nimi' },
  { title: 'Erät', value: 'rounds_total', align: 'center', tooltip: 'Kaikki pelatut erät' },
  { title: 'Poistetut kyykät', value: 'score_total', align: 'center', tooltip: 'Kaikki poistetut kyykät' },
  { title: 'Heitot', value: 'throws_total', align: 'center', tooltip: 'Kaikki heitot' },
  { title: 'KPH', value: 'score_per_throw', align: 'center', tooltip: 'Kyykkää per Heitto' },
  { title: 'kHP', value: 'avg_throw_turn', align: 'center', tooltip: 'Keskimääräinen heittopaikka' },
  { title: 'Hauet', value: 'pikes_total', align: 'center', tooltip: 'Kaikki Hauet' },
  { title: 'H%', value: 'pike_percentage', align: 'center', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
  { title: 'Virkamiehet', value: 'zeros_total', align: 'center', tooltip: 'Nollaheitot ilman haukia' },
  { title: 'VM%', value: 'zero_percentage', align: 'center', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
  { title: 'JK', value: 'gteSix_total', align: 'center', tooltip: 'Joulukuuset: 6 tai paremmat heitot' }
]

function filtterItems() {
  let arr
  if(sort_games_switch.value === 'Erittäin') {
    arr = playerStore.playerMatchesPerPeriod;
    matchHeaders.value = headers_periods

  } else {
    arr = playerStore.playerMatchesPerMatch;
    matchHeaders.value = headers_games
  }
  const returning_arr = filter_games_switch.value === 'Kaikki kaudet'
    ? arr
    : arr.filter(ele => current_selection.value.includes(ele.season));

  if (search.value == '') {
    matchItems.value = returning_arr
    return
  }
  matchItems.value = returning_arr.filter(match => {
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
  // row.select(true) // <--- For some reason this is important to make returnStyle method work onclick
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


playerStore.getPlayer();
// TODO: maybe not with the timeout??
setTimeout(() => {
  console.log('jotain')
  const jotain = playerStore.player.stats_per_seasons
  if (jotain && jotain.length !== 0) {
    console.log('jotain')
    let index = jotain.map(ele => ele.id).indexOf(navStore.seasonId)
    // If the selected season is not in players history take the latest
    index = (index === -1) ? jotain.length -1 : index
    const currentSelcSeason = jotain[index]
    const seasonString = currentSelcSeason.season
    
    current_selection.value.push(seasonString)
    colors.value[0] = seasonString
    column_current_selection.value.push('KPH')

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
    for (const s of jotain) {
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
},5000)

// Initialize the match list by calling the filtterItems() once
filtterItems();

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
