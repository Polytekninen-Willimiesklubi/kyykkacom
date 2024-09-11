<template>
  <div class="flex-1-1-100">
    <v-card>
      <v-row>
        <v-col>
          <v-card class="ma-2">
            <v-card-title align="center">{{playerStore.player.player_name}}</v-card-title>
            <v-data-table
              mobile-breakpoint="0"
              :headers="headerPlayerOverallStats"
              class="allTimeStats"
              :items="[playerStore.player]"
              density="compact"
            >
              <template #headers="{ columns }">
                <tr class="allTimeHeaders">
                  <template v-for="column in columns" :key="column.key">
                    <td class="cursor-pointer" @click="chanceHeaderStat">
                      {{ column.title }}
                      <v-tooltip v-if="column.tooltip"
                        activator="parent"
                        location="bottom"
                        :text="column.tooltip"
                      />
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
          <v-card class="ma-2">
            <v-data-table
              mobile-breakpoint="0"
              class="seasonStats"
              :headers="headerPlayerSeasonStats"
              height="20em"
              no-data-text="Ei pelattuja kausia"
              loading-text="Ladataaan kausia..."
              :items="playerStore.player.stats_per_seasons"
              :loading="playerStore.loadingPlayer"
              density="compact"
              fixed-header
            >
              <!-- For god sakes is this the only way to make initial color happen???
                tried so many ways: setup code watchers, onMounted. Always hits the 'no-data-text'
                problem
              -->
              <template #item = {item}>
                <tr
                  :class="{'blue-row': initalColor(item.season_statistics.season)}"
                  @click="chanceSeason"
                >
                  <td> {{ item.season_statistics.season }}</td>
                  <td> {{ item.season_statistics.team_name }}</td>
                  <td> {{ item.season_statistics.periods }}</td>
                  <td> {{ item.season_statistics.kyykat }}</td>
                  <td> {{ item.season_statistics.throws }}</td>
                  <td> {{ item.season_statistics.score_per_throw }}</td>
                  <td> {{ item.season_statistics.avg_throw_turn }}</td>
                  <td> {{ item.season_statistics.pikes }}</td>
                  <td> {{ item.season_statistics.pike_percentage }}</td>
                  <td> {{ item.season_statistics.zeros }}</td>
                  <td> {{ item.season_statistics.zero_percentage }}</td>
                  <td> {{ item.season_statistics.gte_six }}</td>
                </tr>

              </template>
              <template #bottom></template> <!-- This hides the pagination controls-->
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
      <v-row class="ml-1 mr-1">
        <v-col cols="4">
          <graph
            id="chart"
            title="Heittotuloksen jakauma"
            :datasets="normalizedSwitch ? canvas1DataNormalized : canvas1Data"
            :labels="['0', '1', '2', '3', '4', '5', '≥6']"
            :yLabel="normalizedSwitch ? '%' : 'Kyykkää'"
            type="bar"
          />
          <v-btn
            class="mt-2"
            @click="normalizedSwitch = !normalizedSwitch"
            :text="normalizedSwitch ? '%' : '01'"
          />
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
            yLabel="Heittopaikka"
            type="bar"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2">
          <v-switch
            class='pl-2'
            v-model="sortGamesSwitch"
            true-value="Peleittäin"
            false-value="Erittäin"
            :label="`${sortGamesSwitch}`"
            @update:modelValue="filtterItems"
          />
        </v-col>
        <v-col cols="2">
          <v-switch
            v-model="filterGamesSwitch"
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
            variant="outlined"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card>
            <v-data-table
              mobile-breakpoint="0"
              class="matchesClass"
              @click:row="handleRedirect"
              :search="search"
              :headers="matchHeaders"
              :items="matchItems"
              :loading="playerStore.loadingPlayer"
              no-data-text="Ei dataa :("
              loading-text="Ladataan kausia..."
              density="compact"
            >
              <template #headers="{ columns, isSorted, getSortIcon, toggleSort }">
                <tr>
                  <template v-for="column in columns" :key="column.key">
                    <td class="mr-2 cursor-pointer" @click="() => toggleSort(column)">
                      <span> {{ column.title }} </span>
                      <v-tooltip v-if="column.tooltip"
                        activator="parent"
                        location="bottom"
                        :text="column.tooltip"
                      />
                      <template v-if="isSorted(column)">
                        <v-icon :icon="getSortIcon(column)" />
                      </template>
                    </td>
                  </template>
                </tr>
              </template>
              <template #item.match_time="{ item }">
                <span>{{ date.formatByString(date.date(item.match_time), 'yyyy-MM-dd HH:mm') }}</span>
              </template>
              <template #item.own_team_total="{ item }">
                <v-chip
                  :color="getColor(item.own_team_total, item.opposite_team_total)"
                  :text="item.own_team_total "
                />
              </template>
              <template #item.opposite_team_total="{ item }">
                <v-chip 
                  :color="getColor(item.opposite_team_total, item.own_team_total)"
                  :text="item.opposite_team_total "
                />
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>
<script setup>
import { useNavBarStore } from '@/stores/navbar.store';
import { usePlayerStore } from '@/stores/players.store';
import { useDate } from 'vuetify';
import { useRoute } from 'vue-router/auto';
import { 
  headersPlayerPeriod,
  headersPlayerGames,
  headerPlayerOverallStats,
  headerPlayerSeasonStats
} from '@/stores/headers';

const route = useRoute('/pelaajat/[id]');

const playerStore = usePlayerStore();
const navStore = useNavBarStore();
const date = useDate();

const styles = ['blue-row', 'red-row', 'green-row', 'yellow-row', 'purple-row'];
const allColors = ['#B3E5FC', '#EF9A9A', '#A5D6A7', '#DCE775', '#BA68C8'];
const currentSelection = [];
const columnCurrentSelection = [];
const columnColors =  ['KPH', '', '', '', ''];
const colors = ['', '', '', '', ''];
let colorInitialized = false;

const search = ref('')
const sortGamesSwitch = ref('Erittäin');
const filterGamesSwitch = ref('Kaikki kaudet');
const canvas2Labels = ref([]);
const canvas1Data = ref([]);
const canvas1DataNormalized = ref([]);
const normalizedSwitch = ref(false);
const canvas2Data = ref([]);
const canvas3Data = ref([]);

const matchItems = ref([]);
const matchHeaders = ref(headersPlayerPeriod);

function filtterItems() {
  let arr
  if(sortGamesSwitch.value === 'Erittäin') {
    arr = playerStore.playerMatchesPerPeriod;
    matchHeaders.value = headersPlayerPeriod;
  } else {
    arr = playerStore.playerMatchesPerMatch;
    matchHeaders.value = headersPlayerGames;
  }

  const returning_arr = filterGamesSwitch.value === 'Kaikki kaudet'
    ? arr
    : arr.filter(ele => currentSelection.includes(ele.season));

  if (search.value == '') {
    matchItems.value = returning_arr;
    return;
  }
  matchItems.value = returning_arr.filter(match => {
    let found = false;
    for (const key in match) {
      if (key == 'id') { continue; }
      const ele = typeof match[key] !== 'string' ? String(match[key]) : match[key]
      if (ele.toLowerCase().includes(search.value.toLowerCase())) {
        found = true;
        break;
      }
    }
    return found;
  })

}

function handleRedirect(value, row) {
  location.href = '/ottelut/' + row.item.match_id;
}

function getColor (val1, val2) {
  if (val1 < val2) return 'green-accent-4';
  else if (val1 > val2) return 'red-accent-4';
  else return 'yellow-accent-4';
}

function chanceHeaderStat(val) {
  const headerClassList = val.target.classList;
  const head = val.target.innerText;
  const headers = [
    'Erät', 'Kyykät', 'Heitot', 'KPH', 
    'kHP', 'Hauet', 'H%',
    'VM' ,'VM%', 'JK'
  ];
  const header_binds = [
    'periods', 'kyykat', 'throws', 'score_per_throw',
    'avg_throw_turn', 'pikes', 'pike_percentage', 'zeros', 
    'zero_percentage', 'gte_six'
  ];

  if (!headers.includes(head)) { return; }

  if (columnCurrentSelection.includes(head)) {
    let index = canvas2Data.value.map(ele => ele.label).indexOf(head);
    canvas2Data.value.splice(index, 1);

    canvas2Data.value = [...canvas2Data.value];

    index = columnCurrentSelection.indexOf(head);
    columnCurrentSelection.splice(index, 1);

    index = columnColors.indexOf(head);
    columnColors[index] = '';
    headerClassList.remove(styles[index]);
  } else if (columnCurrentSelection.length < 5) { // Only allow max 5 graphs
    let index = columnColors.indexOf('');
    const color = allColors[index];
    headerClassList.add(styles[index]);

    columnColors[index] = head;

    const stat_per_season = [];
    index = headers.indexOf(head);
    playerStore.player.stats_per_seasons.forEach(stats => {
      stat_per_season.push(stats.season_statistics[header_binds[index]])
    });
    canvas2Data.value.push({
      label: head,
      data: stat_per_season,
      backgroundColor: color,
      borderColor: color,
    });

    canvas2Data.value = [...canvas2Data.value];

    columnCurrentSelection.push(head);
  }
}

function chanceSeason (value) {
  const headerClassList = value.target.tagName === "TD" 
    ? value.target.parentNode.classList 
    : value.target.classList;
  const clickedSeason =  value.target.tagName === "TD" 
    ? value.target.parentNode.children[0].innerText
    : value.target.children[0].innerText;

  if (currentSelection.includes(clickedSeason)) { // Remove clicked season from datas
    
    let index = canvas1Data.value.map(e => e.label).indexOf('Kausi ' + clickedSeason);
    canvas1Data.value.splice(index, 1);
    canvas1DataNormalized.value.splice(index, 1);
    canvas3Data.value.splice(index, 1); // Same index can be used to splice canvas3, because we always update both everywhere
    canvas1Data.value = [...canvas1Data.value]; // To make it reactive, we must make new array
    canvas3Data.value = [...canvas3Data.value];
    canvas1DataNormalized.value = [...canvas1DataNormalized.value]

    index = currentSelection.indexOf(clickedSeason);
    currentSelection.splice(index, 1);
    
    index = colors.indexOf(clickedSeason);
    colors[index] = '';
    headerClassList.remove(styles[index]);
  } else if (currentSelection.length < 5) { // Add Clicked season, only allow max 5
    let tmp = playerStore.player.stats_per_seasons;
    let index = tmp.map(ele => ele.season_statistics.season).indexOf(clickedSeason);
    const selected_season = tmp[index].season_statistics;
    
    index = colors.indexOf(''); // First valid color
    colors[index] = clickedSeason;
    const color = allColors[index];
    headerClassList.add(styles[index]);

    const totalThrow = selected_season.throws 

    canvas1DataNormalized.value = [ ...canvas1DataNormalized.value,
      {
        label: 'Kausi ' + selected_season.season,
        backgroundColor: color,
        data: [
          Math.round((selected_season.zeros + selected_season.pikes) / totalThrow * 100 * 100 ) / 100,
          Math.round((selected_season.ones) / totalThrow * 100 * 100 ) / 100,
          Math.round((selected_season.twos) / totalThrow * 100 * 100 ) / 100,
          Math.round((selected_season.threes) / totalThrow * 100 * 100 ) / 100,
          Math.round((selected_season.fours) / totalThrow * 100 * 100 ) / 100,
          Math.round((selected_season.fives) / totalThrow * 100 * 100 ) / 100,
          Math.round((selected_season.gte_six) / totalThrow * 100 * 100 ) / 100,
        ]
      }
    ];

    canvas1Data.value = [ ...canvas1Data.value,  // To make it reactive, we must make new array
      {
        label: 'Kausi ' + selected_season.season,
        backgroundColor: color,
        data: [
          selected_season.zeros + selected_season.pikes,
          selected_season.ones,
          selected_season.twos,
          selected_season.threes,
          selected_season.fours,
          selected_season.fives,
          selected_season.gte_six
        ]
      }
    ];

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
    ];

    currentSelection.push(clickedSeason);
  }
}

/**
 * Returns True for one season index for to initially color one row in aggregated year stats
 * @param {number} season Season index
 * @returns {bool} True if season is first item in 'currentSelection' and only once else False 
 */
function initalColor(season) {
  if(colorInitialized || season !== currentSelection[0]) {
    return false;
  }
  colorInitialized = true;
  return true;
}

playerStore.getPlayer(route.params.id);
watch(() => playerStore.loadedData, () => {
  if (playerStore.loadedData === false) {
    return;
  }
  const stats_per_seasons = playerStore.player.stats_per_seasons;
  if (stats_per_seasons && stats_per_seasons.length !== 0) {
    let index = stats_per_seasons.map(ele => ele.season_statistics.id).indexOf(navStore.seasonId);
    // If the selected season is not in players history take the latest
    index = (index === -1) ? stats_per_seasons.length -1 : index;
    const currentSelcSeason = stats_per_seasons[index].season_statistics;
    const seasonString = currentSelcSeason.season;
    
    currentSelection.push(seasonString);
    colors[0] = seasonString;
    columnCurrentSelection.push('KPH');

    const totalThrow = currentSelcSeason.throws

    const init1Normalized = {
      label: 'Kausi ' + currentSelcSeason.season,
      backgroundColor: '#B3E5FC',
      data: [
        Math.round((currentSelcSeason.zeros + currentSelcSeason.pikes) / totalThrow * 100 * 100 ) / 100,
        Math.round((currentSelcSeason.ones) / totalThrow * 100 * 100 ) / 100,
        Math.round((currentSelcSeason.twos) / totalThrow * 100 * 100 ) / 100,
        Math.round((currentSelcSeason.threes) / totalThrow * 100 * 100 ) / 100,
        Math.round((currentSelcSeason.fours) / totalThrow * 100 * 100 ) / 100,
        Math.round((currentSelcSeason.fives) / totalThrow * 100 * 100 ) / 100,
        Math.round((currentSelcSeason.gte_six) / totalThrow * 100 * 100 ) / 100,
      ]
    };
  
    const init1 = {
      label: 'Kausi ' + currentSelcSeason.season,
      backgroundColor: '#B3E5FC',
      data: [
        currentSelcSeason.zeros + currentSelcSeason.pikes,
        currentSelcSeason.ones,
        currentSelcSeason.twos,
        currentSelcSeason.threes,
        currentSelcSeason.fours,
        currentSelcSeason.fives,
        currentSelcSeason.gte_six
      ]
    };
    const canvas2_data_tmp = [];
    for (const s of stats_per_seasons) {
      canvas2_data_tmp.push(s.season_statistics.score_per_throw);
      canvas2Labels.value.push(s.season_statistics.season);
    }
    const init2 = {
      label: 'KPH',
      backgroundColor: '#B3E5FC',
      borderColor: '#B3E5FC',
      data: canvas2_data_tmp
    };
    
    const init3 = {
      label: 'Kausi ' + currentSelcSeason.season,
      backgroundColor: '#B3E5FC',
      data: [
        currentSelcSeason.average_score_position_one,
        currentSelcSeason.average_score_position_two,
        currentSelcSeason.average_score_position_three,
        currentSelcSeason.average_score_position_four
      ]
    };
    canvas1DataNormalized.value = [init1Normalized]
    canvas1Data.value = [init1];
    canvas2Data.value = [init2];
    canvas3Data.value = [init3];
  }

  // Initialize the selected allTime header color
  const headerRow = document.getElementsByClassName('allTimeHeaders')[0];
  for (let i = 0; i < headerRow.childNodes.length; i++) {
    const text = headerRow.childNodes[i].innerText;
    if ( text === 'KPH' ) {
      headerRow.childNodes[i].classList.add('blue-row');
      break;
    }
  }
},
{once: true})

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

.v-data-table-header__content {
  justify-content: center;
}

</style>
