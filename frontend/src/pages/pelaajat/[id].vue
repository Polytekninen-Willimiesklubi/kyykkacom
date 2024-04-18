<template>
  <v-layout>
    <div class="d-flex">
      <v-card>
        <v-row>
          <v-col>
            <v-card>
              <v-card-title align="center">{{playerStore.player.player_name}}</v-card-title>
              <v-data-table
                mobile-breakpoint="0"
                :headers="overallPlayerStats"
                class="allTimeStats"
                :items="[playerStore.player]"
              >
                <template #headers="{ columns }">
                  <tr align="center" class="allTimeHeaders">
                    <template v-for="column in columns" :key="column.key">
                      <td class="cursor-pointer" @click="chanceHeaderStat">
                        {{ column.title }}
                        <v-tooltip
                          activator="parent"
                          location="bottom"
                        >
                          {{ column.tooltip }}
                        </v-tooltip>
                      </td>
                    </template>
                  </tr>
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
                class="seasonStats"
                :headers="seasonStats"
                height="200px"
                no-data-text="Ei pelattuja kausia"
                :items="playerStore.player.stats_per_seasons"
                fixed-header
              >
                <!-- For god sakes is this the only way to make initial color happen???
                  tried so many ways: setup code watchers, onMounted. Always hits the 'no-data-text'
                  problem
                -->
                <template #item = {item}>
                  <tr
                    :class="{'blue-row': initalColor(item.season)}"
                    @click="chanceSeason"
                  >
                    <td> {{ item.season }}</td>
                    <td> {{ item.team_name }}</td>
                    <td> {{ item.rounds_total }}</td>
                    <td> {{ item.score_total }}</td>
                    <td> {{ item.throws_total }}</td>
                    <td> {{ item.score_per_throw }}</td>
                    <td> {{ item.avg_throw_turn }}</td>
                    <td> {{ item.pikes_total }}</td>
                    <td> {{ item.pike_percentage }}</td>
                    <td> {{ item.zeros_total }}</td>
                    <td> {{ item.zero_percentage }}</td>
                    <td> {{ item.gteSix_total }}</td>
                  </tr>

                </template>
                <template #bottom></template> <!-- This hides the pagination controls-->
              </v-data-table>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="4">
            <v-card>
              <graph
                id="chart"
                title="Heittotuloksen jakauma"
                :datasets="canvas1Data"
                :labels="['0', '1', '2', '3', '4', '5', '≥6']"
                type="bar"
              />
            </v-card>
          </v-col>
          <v-col cols="4">
            <graph
              id="statGraph"
              title="Statsin kehitys kausittain"
              :datasets="canvas2Data"
              :labels="canvas2Labels"
              type="line"
            />
          </v-col>
          <v-col cols="4">
            <graph
              id="kHP KPH"
              title="Heittokeskiarvo heittopaikan mukaan"
              :datasets="canvas3Data"
              :labels="['1', '2', '3', '4']"
              :horizontal=true
              type="bar"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="2">
            <v-switch
              class='pl-2'
              v-model="sortGamesSwitch"
              hide-details
              true-value="Peleittäin"
              false-value="Erittäin"
              :label="`${sortGamesSwitch}`"
              @update:modelValue="filtterItems"
            />
          </v-col>
          <v-col cols="2">
            <v-switch
              v-model="filterGamesSwitch"
              hide-details
              true-value="Valitut kaudet"
              false-value="Kaikki kaudet"
              :label="`${filterGamesSwitch}`"
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
                class="matchesClass"
                no-data-text="Ei dataa :("
                :search="search"
                :headers="matchHeaders"
                :items="matchItems"
                :custom-sort="throwSort"
              >
                <template v-slot:headers="{ columns, isSorted, getSortIcon, toggleSort }">
                  <tr>
                    <template v-for="column in columns" :key="column.key">
                      <td class="mr-2 cursor-pointer" @click="() => toggleSort(column)">
                        <span>
                          {{ column.title }}
                          <v-tooltip
                            activator="parent"
                            location="bottom"
                          >
                            {{ column.tooltip }}
                          </v-tooltip>
                        </span>
                        <template v-if="isSorted(column)">
                          <v-icon :icon="getSortIcon(column)" />
                        </template>
                      </td>
                    </template>
                  </tr>
                </template>
                <template v-slot:item.match_time="{ item }">
                  <span>{{ date.formatByString(date.date(item.match_time), 'yyyy-MM-dd HH:mm') }}</span>
                </template>
                <template v-slot:item.own_team_total="{ item }">
                  <v-chip :color="getColor(item.own_team_total, item.opposite_team_total)">
                    {{ item.own_team_total }}
                  </v-chip>
                </template>
                <template v-slot:item.opposite_team_total="{ item }">
                  <v-chip :color="getColor(item.opposite_team_total, item.own_team_total)">
                    {{ item.opposite_team_total }}
                  </v-chip>
                </template>
              </v-data-table>
            </v-card>
          </v-col>
        </v-row>
      </v-card>
    </div>
    <!-- <div class="d-flex pl-3 xs4 hidden-md-and-down">
      <side-bar
        :no_brackets="no_brackets"
        :non-default-teams="teams"
      />
    </div> -->
  </v-layout>
</template>
<script setup>
import { useNavBarStore } from '@/stores/navbar.store';
import { usePlayerStore } from '@/stores/players.store';
import { useDate } from 'vuetify';
import { useHomeStore } from '@/stores/home.store'
import { onMounted } from 'vue';

const homeStore = useHomeStore();
const teams = homeStore.getTeams();

const playerStore = usePlayerStore();
const navStore = useNavBarStore();
const date = useDate();

const styles = ['blue-row', 'red-row', 'green-row', 'yellow-row', 'purple-row'];
const allColors = ['#B3E5FC', '#EF9A9A', '#A5D6A7', '#DCE775', '#BA68C8'];
const currentSelection = [];
const columnCurrentSelection = [];
const columnColors =  ['KPH', '', '', '', ''];
const colors = ['', '', '', '', ''];
let jotain2 = false;

const search = ref('')
const sortGamesSwitch = ref('Erittäin');
const filterGamesSwitch = ref('Kaikki kaudet');
const canvas2Labels = ref([]);
const canvas1Data = ref([]);
const canvas2Data = ref([]);
const canvas3Data = ref([]);

const matchItems = ref([]);

const headersPeriods = [
  { title: 'Aika', key: 'match_time', tooltip: 'Pelausaika' },
  { title: 'Vastustaja', key: 'opp_name', tooltip: 'Vastustaja joukkue' },
  { title: 'Erä', key: 'period', tooltip: 'Pelin erä' },
  { title: 'HP', key: 'turn',  tooltip: 'Heittopaikka' },
  { title: '1', key: 'score_first', tooltip: '1. heitto (Kyykkää)' },
  { title: '2', key: 'score_second', tooltip: '2. heitto (Kyykkää)' },
  { title: '3', key: 'score_third', tooltip: '3. heitto (Kyykkää)' },
  { title: '4', key: 'score_fourth', tooltip: '4. heitto (Kyykkää)' },
  { title: 'Yht.', key: 'score_total', tooltip: 'Heitot Yhteensä (Kyykkää)' },
  { title: 'KPH', key: 'score_average_round', tooltip: 'Kyykkää per Heitto' },
  { title: 'OJ pis.', key: 'own_score_round', tooltip: 'Oman joukkueen pisteet' },
  { title: 'V pis.', key: 'opp_score_round', tooltip: 'Vastustaja joukkueen pisteet' }
];

const matchHeaders = ref(headersPeriods);

const headersGames = [
  { title: 'Aika', key: 'match_time', tooltip: 'Pelausaika' },
  { title: 'Vastustaja', key: 'opponent_name', tooltip: 'Vastustaja joukkue' },
  { title: 'HP1', key: 'throw_turn_one', tooltip: '1. erän heittopaikka' },
  { title: 'HP2', key: 'throw_turn_two', tooltip: '2. erän heittopaikka' },
  { title: '1', key: 'score_first', tooltip: '1.erän 1.heitto (Kyykkää)' },
  { title: '2', key: 'score_second', tooltip: '1.erän 2.heitto (Kyykkää)' },
  { title: '3', key: 'score_third', tooltip: '1.erän 3.heitto (Kyykkää)' },
  { title: '4', key: 'score_fourth', tooltip: '1.erän 4.heitto (Kyykkää)' },
  { title: '5', key: 'score_fifth', tooltip: '2.erän 1.heitto (Kyykkää)' },
  { title: '6', key: 'score_sixth', tooltip: '2.erän 2.heitto (Kyykkää)' },
  { title: '7', key: 'score_seventh', tooltip: '2.erän 3.heitto (Kyykkää)' },
  { title: '8', key: 'score_eighth', tooltip: '2.erän 4.heitto (Kyykkää)' },
  { title: 'Yht.', key: 'score_total', tooltip: 'Poistetut kyykät Yhteensä (Kyykkää)' },
  { title: 'KPH', key: 'score_average_match', tooltip: 'Kyykkää per Heitto' },
  { title: 'OJ pis.', key: 'own_score', tooltip: 'Oman joukkueen pisteet' },
  { title: 'V pis.', key: 'opponent_score', tooltip: 'Vastustaja joukkueen pisteet' }
]
const overallPlayerStats = [
  { title: 'Kausi', key: 'season', tooltip: 'Kaikkien kausien tulokset', sortable: false },
  { title: 'Kaudet', key: 'season_count', tooltip: 'Pelatut NKL kaudet', sortable: false },
  { title: 'Erät', key: 'all_rounds_total', tooltip: 'Kaikki pelatut erät', sortable: false },
  { title: 'Poistetut kyykät', key: 'all_score_total', tooltip: 'Kaikki poistetut kyykät', sortable: false },
  { title: 'Heitot', key: 'all_throws_total', tooltip: 'Kaikki heitot', sortable: false },
  { title: 'KPH', key: 'total_average_throw', tooltip: 'Kyykkää per Heitto', sortable: false },
  { title: 'kHP', key: 'total_average_throw_turn', tooltip: 'Keskimääräinen heittopaikka', sortable: false },
  { title: 'Hauet', key: 'all_pikes_total', tooltip: 'Kaikki Hauet (=Ohi heitot)', sortable: false },
  { title: 'H%', key: 'total_pike_percentage', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot', sortable: false },
  { title: 'VM', key: 'all_zeros_total', tooltip: 'Virkamiehet: Nollaheitot ilman haukia', sortable: false },
  { title: 'VM%', key: 'total_zero_percentage', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot', sortable: false },
  { title: 'JK', key: 'all_gteSix_total', tooltip: 'Joulukuuset: 6 tai paremmat heitot', sortable: false }
]
const seasonStats = [
  { title: 'Kausi', key: 'season', tooltip: 'Pelikausi (vuosi)' },
  { title: 'Joukkue', key: 'team_name', tooltip: 'Joukkue nimi' },
  { title: 'Erät', key: 'rounds_total', tooltip: 'Kaikki pelatut erät' },
  { title: 'Poistetut kyykät', key: 'score_total', tooltip: 'Kaikki poistetut kyykät' },
  { title: 'Heitot', key: 'throws_total', tooltip: 'Kaikki heitot' },
  { title: 'KPH', key: 'score_per_throw', tooltip: 'Kyykkää per Heitto' },
  { title: 'kHP', key: 'avg_throw_turn', tooltip: 'Keskimääräinen heittopaikka' },
  { title: 'Hauet', key: 'pikes_total', tooltip: 'Kaikki Hauet (=Ohi heitot)' },
  { title: 'H%', key: 'pike_percentage', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
  { title: 'VM', key: 'zeros_total', tooltip: 'Virkamiehet: Nollaheitot ilman haukia' },
  { title: 'VM%', key: 'zero_percentage', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
  { title: 'JK', key: 'gteSix_total', tooltip: 'Joulukuuset: 6 tai paremmat heitot' }
]

function filtterItems() {
  let arr
  if(sortGamesSwitch.value === 'Erittäin') {
    arr = playerStore.playerMatchesPerPeriod;
    matchHeaders.value = headersPeriods

  } else {
    arr = playerStore.playerMatchesPerMatch;
    matchHeaders.value = headersGames
  }
  const returning_arr = filterGamesSwitch.value === 'Kaikki kaudet'
    ? arr
    : arr.filter(ele => currentSelection.includes(ele.season));

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

function chanceHeaderStat(val) {
  const headerClassList = val.target.classList
  const head = val.target.innerText
  const headers = ['Erät', 'Poistetut kyykät', 'Heitot', 'KPH', 'kHP', 'Hauet', 'H%',
    'Virkamiehet', 'VM' ,'VM%', 'JK']
  const header_binds = ['rounds_total', 'score_total', 'throws_total', 'score_per_throw',
    'avg_throw_turn', 'pikes_total', 'pike_percentage', 'zeros_total', 'zero_percentage', 'gteSix_total']

  if (!headers.includes(head)) { return }

  if (columnCurrentSelection.includes(head)) {
    let index = canvas2Data.value.map(ele => ele.label).indexOf(head)
    canvas2Data.value.splice(index, 1)

    canvas2Data.value = [...canvas2Data.value]

    index = columnCurrentSelection.indexOf(head)
    columnCurrentSelection.splice(index, 1)

    index = columnColors.indexOf(head)
    columnColors[index] = ''
    headerClassList.remove(styles[index])
  } else if (columnCurrentSelection.length == 5) {
    // Do nothing
  } else {
    let index = columnColors.indexOf('')
    const color = allColors[index]
    headerClassList.add(styles[index])

    columnColors[index] = head

    const dat = []
    index = headers.indexOf(head)
    playerStore.player.stats_per_seasons.forEach(s => {
      dat.push(s[header_binds[index]])
    })
    canvas2Data.value.push({
      label: head,
      data: dat,
      backgroundColor: color,
      borderColor: color,
    })

    canvas2Data.value = [...canvas2Data.value]

    columnCurrentSelection.push(head)
  }
}
function throwSort (items, index, isDescending) {
  const customColumns = ['score_first', 'score_second', 'score_third', 'score_fourth',
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
    if (!isNaN(customColumns.includes(index[0]))) {
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

function chanceSeason (value) {
  const headerClassList = value.target.tagName === "TD" ? value.target.parentNode.classList : value.target.classList;
  const clickedSeason =  value.target.tagName === "TD" 
    ? value.target.parentNode.children[0].innerText 
    : value.target.children[0].innerText;
  if (currentSelection.includes(clickedSeason)) { // Remove clicked season from datas
    let index = canvas1Data.value.map(e => e.label).indexOf('Kausi ' + clickedSeason)
    canvas1Data.value.splice(index, 1)
    canvas3Data.value.splice(index, 1) // Same index can be used to splice canvas3, because we always update both everywhere
    
    canvas1Data.value = [...canvas1Data.value] // To make it reactive, we must make new array
    canvas3Data.value = [...canvas3Data.value]

    index = currentSelection.indexOf(clickedSeason)
    currentSelection.splice(index, 1)

    index = colors.indexOf(clickedSeason)
    colors[index] = ''
    headerClassList.remove(styles[index])
  } else if (currentSelection.length == 5) { // Not removal, but the 'memory' is full
    // Do nothing
  } else { // Add clicked season
    let tmp = playerStore.player.stats_per_seasons
    let index = tmp.map(ele => ele.season).indexOf(clickedSeason)
    const selected_season = tmp[index]
    
    index = colors.indexOf('') // First valid color
    colors[index] = clickedSeason
    const color = allColors[index]
    headerClassList.add(styles[index])

    canvas1Data.value = [ ...canvas1Data.value,  // To make it reactive, we must make new array
    {
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
    }
  ]

    canvas3Data.value = [ ...canvas3Data.value,  // To make it reactive, we must make new array
    {  
      label: 'Kausi ' + selected_season.season,
      backgroundColor: color,
      data: [
        selected_season.average_score_position_one,
        selected_season.average_score_position_two,
        selected_season.average_score_position_three,
        selected_season.average_score_position_four
      ]
    }
  ]

    currentSelection.push(clickedSeason)
  }
}

function initalColor(value) {
  const tmp = playerStore.player.stats_per_seasons
  let index = tmp.map(ele => ele.id).indexOf(navStore.seasonId)
  // If the selected season is not in players history take the latest
  index = (index === -1) ? tmp.length -1 : index
  if(jotain2 || value !== currentSelection[0]) return false
  jotain2 = true;
  return true
}

playerStore.getPlayer();
watch(() => playerStore.loadedData, () => {

  if (playerStore.loadedData === false) {
    return
  }
  const jotain = playerStore.player.stats_per_seasons
  if (jotain && jotain.length !== 0) {
    let index = jotain.map(ele => ele.id).indexOf(navStore.seasonId)
    // If the selected season is not in players history take the latest
    index = (index === -1) ? jotain.length -1 : index
    const currentSelcSeason = jotain[index]
    const seasonString = currentSelcSeason.season
    
    currentSelection.push(seasonString)
    colors[0] = seasonString
    columnCurrentSelection.push('KPH')
  
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
      canvas2Labels.value.push(s.season)
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
    canvas1Data.value = [init1];
    canvas2Data.value = [init2];
    canvas3Data.value = [init3];
  }

  // Initialize the selected allTime header color
  const headerRow = document.getElementsByClassName('allTimeHeaders')[0]
  for (let i = 0; i < headerRow.childNodes.length; i++) {
    const text = headerRow.childNodes[i].innerText
    if ( text === 'KPH' ) {
      headerRow.childNodes[i].classList.add('blue-row')
      break;
    }
  }
},
{once: true})


// Initialize the match list by calling the filtterItems() once
filtterItems();
</script>


<script>
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

.matchesClass tr {
  text-align: center;
}

.allTimeStats tr {
  text-align: center;
}

.seasonStats tr {
  text-align: center;
}

</style>
