<template>
  <v-card>
    <v-row>
      <v-col>
        <v-card>
          <v-toolbar-title align="center">{{header}}</v-toolbar-title>
          <v-data-table mobile-breakpoint="0" disable-pagination dense color='alert' 
          :headers="overall_player_stats" 
          :items="stats"
          hide-default-header
          hide-default-footer>
            <template v-slot:header="{ props }">
              <th v-for="h in props.headers" class="head-font"
              :class="returnHeaderColor(h.text)"
              @click="chanceHeaderStat">
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
          <v-data-table mobile-breakpoint="0" disable-pagination dense color='alert'
        @click:row="chanceSeason"
        :headers="season_stats" 
        height = "200px"
        :items="all_seasons"
        :item-class="returnStyle" hide-default-footer>
          </v-data-table>
        </v-card>
      </v-col>
      <v-col>
        <v-card>
          <canvas id="chart" width="300px" height="200px"></canvas>
        </v-card>
      </v-col> 
      <v-col>
        <v-card>
          <canvas id="statGraph" width="300px" height="200px"></canvas>
        </v-card>
      </v-col>
      <v-col>
        <v-card>
          <canvas id="kHP KPH" width="300px" height="200px"></canvas>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-switch v-model="sort_games_switch"
        hide-details
        true-value="Peleittäin"
        false-value="Erittäin"
        :label="`${sort_games_switch}`"></v-switch>
      </v-col>
      <v-col>
        <v-switch v-model="filter_games_switch"
        hide-details
        true-value="Valitut kaudet"
        false-value="Kaikki kaudet"
        :label="`${filter_games_switch}`"></v-switch>
      </v-col>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
    </v-row>
    <v-row>
      <v-col>
        <v-text-field color="red" v-model="search" label="Etsi" single-line hide-details variant="outlined"></v-text-field>
      </v-col>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
    </v-row>
    <v-row>
      <v-col>
        <v-card>
          <v-data-table mobile-breakpoint="0" @click:row="handleRedirect" dense color='alert' 
          :search="search" 
          :headers="headers"
          :items="filtteredItems"
          :custom-sort="throwSort"
          v-if="sort_games_switch=='Erittäin'">
            <template slot="no-data">
              <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
            </template>
            <template v-for="h in headers" v-slot:[`header.${h.value}`]="{ header }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                  <span v-on="on">{{h.text}}</span>
                </template>
                <span>{{h.tooltip}}</span>
              </v-tooltip>
            </template>
            <template v-slot:[`item.match_time`]="{ item }">
              <span>{{ item.match_time | luxon('y-MM-dd HH:mm') }}</span>
            </template>
            <template v-slot:item.own_score_round="{ item }">
              <v-chip :color="getColor(item.own_score_round, item.opp_score_round)">
                {{ item.own_score_round }}
              </v-chip>              
            </template>
            <template v-slot:item.opp_score_round="{item}">
              <v-chip :color="getColor(item.opp_score_round, item.own_score_round)">
                {{ item.opp_score_round }}
              </v-chip>              
            </template>
            <template v-slot:item.score_first="{item}">
              <td class="border_left">
                {{ item.score_first }}
              </td>
            </template>
            <template v-slot:item.score_total="{item}">
              <td class="border_left">
                {{ item.score_total }}
              </td>
            </template>
          </v-data-table>
          <v-data-table mobile-breakpoint="0" @click:row="handleRedirect" dense color='alert'
          :headers="headers_games"
          :items="filtteredItems"
          :custom-sort="throwSort"
          v-else>
            <template slot="no-data">
              <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
            </template>
            <template v-for="h in headers_games" v-slot:[`header.${h.value}`]="{ header }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                  <span v-on="on">{{h.text}}</span>
                </template>
                <span>{{h.tooltip}}</span>
              </v-tooltip>
            </template>
            <template v-slot:[`item.match_time`]="{ item }">
              <span>{{ item.match_time | luxon('y-MM-dd HH:mm') }}</span>
            </template>
            <template v-slot:[`item.own_score`]="{ item }">
              <v-chip :color="getColor(item.own_score, item.opponent_score)">
                {{ item.own_score }}
              </v-chip>              
            </template>
            <template v-slot:item.opponent_score="{item}">
              <v-chip :color="getColor(item.opponent_score, item.own_score)">
                {{ item.opponent_score }}
              </v-chip>              
            </template>
            <template v-slot:item.score_first="{item}">
              <td class="border_left">
                {{ item.score_first }}
              </td>
            </template>
            <template v-slot:item.score_total="{item}">
              <td class="border_left">
                {{ item.score_total }}
              </td>
            </template>
          </v-data-table>


        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>
  

<script>
import Chart, { _adapters } from "chart.js/auto"

export default {
    data: function() {
        return {
            search: '',
            header: '',
            headers: [
              { text: 'Aika', value: 'match_time', align: 'center', tooltip:'Pelausaika'},
              { text: 'Vastustaja', value: 'opp_name', align: 'center', tooltip: 'Vastustaja joukkue'},
              { text: 'Erä', value: 'period', align: 'center',tooltip: 'Pelin erä' },
              { text: 'HP', value: 'turn', align: 'center', tooltip:'Heittopaikka' },
              { text: '1', value: 'score_first', align: 'center', tooltip: '1. heitto (Kyykkää)'},
              { text: '2', value: 'score_second', align: 'center', tooltip: '2. heitto (Kyykkää)'},
              { text: '3', value: 'score_third', align: 'center', tooltip: '3. heitto (Kyykkää)'},
              { text: '4', value: 'score_fourth', align: 'center', tooltip: '4. heitto (Kyykkää)'},
              { text: 'Yht.', value: 'score_total', align: 'center', tooltip: 'Heitot Yhteensä (Kyykkää)'},
              { text: 'KPH', value: 'score_average_round', align: 'center', tooltip:'Kyykkää per Heitto' },
              { text: 'OJ pis.', value: 'own_score_round', align: 'center', tooltip:'Oman joukkueen pisteet' },
              { text: 'V pis.', value: 'opp_score_round', align: 'center', tooltip:'Vastustaja joukkueen pisteet' }
          ],
          headers_games : [
              { text: 'Aika', value: 'match_time', align: 'center', tooltip:'Aika'},
              { text: 'Vastustaja', value: 'opponent_name', align: 'center', tooltip:'Vastustaja joukkue'},
              { text: 'HP1', value: 'throw_turn_one', align: 'center', tooltip:'1. erän heittopaikka'},
              { text: 'HP2', value: 'throw_turn_two', align: 'center', tooltip:'2. erän heittopaikka'},
              { text: '1', value: 'score_first', align: 'center', tooltip:'1.erän 1.heitto (Kyykkää)'},
              { text: '2', value: 'score_second', align: 'center', tooltip:'1.erän 2.heitto (Kyykkää)'},
              { text: '3', value: 'score_third', align: 'center', tooltip:'1.erän 3.heitto (Kyykkää)'},
              { text: '4', value: 'score_fourth', align: 'center', tooltip:'1.erän 4.heitto (Kyykkää)'},
              { text: '5', value: 'score_fifth', align: 'center', tooltip: '2.erän 1.heitto (Kyykkää)'},
              { text: '6', value: 'score_sixth', align: 'center', tooltip:'2.erän 2.heitto (Kyykkää)'},
              { text: '7', value: 'score_seventh', align: 'center', tooltip:'2.erän 3.heitto (Kyykkää)'},
              { text: '8', value: 'score_eighth', align: 'center', tooltip:'2.erän 4.heitto (Kyykkää)'},
              { text: 'Yht.', value: 'score_total', align: 'center', tooltip:'Heitot Yhteensä (Kyykkää)' },
              { text: 'KPH', value: 'score_average_match', align: 'center', tooltip:'Kyykkää per Heitto'},
              { text: 'OJ pis.', value: 'own_score', align: 'center', tooltip:'Oman joukkueen pisteet'},
              { text: 'V pis.', value: 'opponent_score', align: 'center', tooltip: 'Vastustaja joukkueen pisteet'}
          ],
            player_id: this.$route.fullPath.substr(
                this.$route.fullPath.lastIndexOf('/') + 1
            ),
            isActive: false,
            sort_games_switch :"Erittäin",
            filter_games_switch :"Kaikki kaudet",
            stats: [],
            matches_periods: [],
            matches_match: [],
            all_seasons: [],
            current_selection: [],
            column_current_selection : [],
            column_colors: ['KPH','','','',''],
            colors : ['','','','',''],
            throw_chart: "",
            overall_player_stats: [
              { text: 'Kausi', value: 'season', align: 'center', tooltip: 'Kaikkien kausien tulokset',sortable: false},
              { text: 'Kaudet', value: 'season_count', align: 'center', tooltip: 'Pelatut NKL kaudet',sortable: false},
              { text: 'Erät', value: 'all_rounds_total', align: 'center', tooltip: 'Kaikki pelatut erät',sortable: false},
              { text: 'Poistetut kyykät', value: 'all_score_total', align: 'center', tooltip: 'Kaikki poistetut kyykät',sortable: false},
              { text: 'Heitot', value: 'all_throws_total', align: 'center', tooltip: 'Kaikki heitot',sortable: false},
              { text: 'KPH', value: 'total_average_throw', align: 'center', tooltip: 'Kyykkää per Heitto',sortable: false},
              { text: 'kHP', value: 'total_average_throw_turn', align: 'center', tooltip: 'Keskimääräinen heittopaikka',sortable: false },
              { text: 'Hauet', value: 'all_pikes_total', align: 'center', tooltip: 'Kaikki Hauet',sortable: false},   
              { text: 'H%', value: 'total_pike_percentage', align: 'center', tooltip:'Hauki-prosentti: Hauet / Kaikki heitot',sortable: false},
              { text: 'Virkamiehet', value: 'all_zeros_total', align: 'center', tooltip:'Nollaheitot ilman haukia' ,sortable: false},
              { text: 'VM%', value: 'total_zero_percentage', align: 'center', tooltip:'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot',sortable: false},
              { text: 'JK', value: 'all_gteSix_total', align: 'center', tooltip: 'Joulukuuset: 6 tai paremmat heitot',sortable: false},
            ],
            season_stats: [
              { text: 'Kausi', value: 'season', align: 'center', tooltip: 'Pelikausi (vuosi)'},
              { text: 'Joukkue', value: 'team_name', align: 'center', tooltip: 'Joukkue nimi'},
              { text: 'Erät', value: 'rounds_total', align: 'center', tooltip: 'Kaikki pelatut erät'},
              { text: 'Poistetut kyykät', value: 'score_total', align: 'center', tooltip: 'Kaikki poistetut kyykät'},
              { text: 'Heitot', value: 'throws_total', align: 'center', tooltip: 'Kaikki heitot'},
              { text: 'KPH', value: 'score_per_throw', align: 'center', tooltip: 'Kyykkää per Heitto'},
              { text: 'kHP', value: 'avg_throw_turn', align: 'center', tooltip: 'Keskimääräinen heittopaikka' },
              { text: 'Hauet', value: 'pikes_total', align: 'center', tooltip: 'Kaikki Hauet'},   
              { text: 'H%', value: 'pike_percentage', align: 'center', tooltip:'Hauki-prosentti: Hauet / Kaikki heitot'},
              { text: 'Virkamiehet', value: 'zeros_total', align: 'center', tooltip:'Nollaheitot ilman haukia' },
              { text: 'VM%', value: 'zero_percentage', align: 'center', tooltip:'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
              { text: 'JK', value: 'gteSix_total', align: 'center', tooltip: 'Joulukuuset: 6 tai paremmat heitot' },
            ]
        };
    },
    computed: {
      filtteredItems: function() {
        var arr = this.sort_games_switch == "Erittäin" ? this.matches_periods : this.matches_match
        return this.filtterItems(arr, this.filter_games_switch, this.search)
      }
    },
    methods: {
        getPlayer: function() {
            this.$http
                .get('api/players/' + this.player_id +'/?season='+sessionStorage.season_id)
                .then(
                  function(data) {
                      this.stats = [data.body];
                      this.header = data.body.player_name;
                      this.all_seasons = data.body.stats_per_seasons
                      
                      var selectSeason = sessionStorage.season_id
                      var all_seasons = JSON.parse(sessionStorage.all_seasons)
                      var season_year = ''
                      
                      all_seasons.forEach(ele => {
                        if (ele.id == selectSeason) {
                          season_year = ele.name.split(" ")[1]
                        }
                      })
                      
                      var i = 0
                      var list_index = -1
                      this.all_seasons.forEach(ele => {
                        if (ele.season == season_year) {
                          list_index = i
                        }
                        i++
                      })
                      if (list_index === -1) {
                        list_index = this.all_seasons.length-1
                        season_year = this.all_seasons[list_index].season
                      }
                      this.current_selection.push(season_year)
                      this.colors[0] = season_year
                      this.column_current_selection.push('KPH')
                      this.matches_periods = []
                      this.matches_match = []

                      for (const season of this.all_seasons) {
                        for(const match of season['matches']) {
                          for (let i = 1; i<3; i++) {
                            if (i == 1 & match.throw_turn_one != '-') {
                              var own_score = match.own_score_first
                              var opp_score = match.opponent_score_first
                              var throw_turn = match.throw_turn_one
                              var first = match.score_first
                              var second = match.score_second
                              var third = match.score_third
                              var fourth = match.score_fourth
                              var average = match.score_average_round_one
                              var total = match.score_total_one
                            } else if(i == 2 & match.throw_turn_two != '-') {
                              var own_score = match.own_score_second
                              var opp_score = match.opponent_score_second
                              var throw_turn = match.throw_turn_two
                              var first = match.score_fifth
                              var second = match.score_sixth
                              var third = match.score_seventh
                              var fourth = match.score_eighth
                              var average = match.score_average_round_two
                              var total = match.score_total_two
                            } else {
                              continue
                            }
                            this.matches_periods.push({
                              "id" : match.id*2 + (i-1),
                              "match_id": match.id,
                              "season" : season['season'],
                              "own_score_round" : own_score,
                              "opp_score_round" : opp_score,
                              "opp_name" : match.opponent_name,
                              "match_time" : match.match_time,
                              "period" : i,
                              "turn" : throw_turn,
                              "score_first" : first,
                              "score_second" : second,
                              "score_third" : third,
                              "score_fourth" : fourth,
                              "score_total" : total,
                              "score_average_round" : average
                            })
                          }
                          var input = match
                          input['season'] = season['season']
                          input['match_id'] = match.id
                          input['id'] = match.id
                          this.matches_match.push(input)
                        }

                      }
                      const jotain = document.getElementById('chart')
                      var config = {
                        type: 'bar',
                        data: {
                          labels: ['0', '1', '2', '3', '4', '5', '≥6'],
                          datasets: [{
                            label: "Kausi " + this.all_seasons[list_index].season,
                            backgroundColor: '#B3E5FC',
                            data: [
                              this.all_seasons[list_index].zeros_total + this.all_seasons[list_index].pikes_total,
                              this.all_seasons[list_index].ones_total,
                              this.all_seasons[list_index].twos_total,
                              this.all_seasons[list_index].threes_total,
                              this.all_seasons[list_index].fours_total,
                              this.all_seasons[list_index].fives_total,
                              this.all_seasons[list_index].gteSix_total
                          ],
                            borderWidth: 1
                          }]
                        },
                        options: {
                          scales: {
                            y: {
                              beginAtZero: true
                            }
                          },
                          plugins: {
                            title: {
                              text:'Heittotuloksen jakauma',
                              display: true
                            }
                          }
                        }
                      }
                    new Chart(jotain, config)
                    var dat = []
                    var labs = []
                    for (const s of this.all_seasons) {
                      dat.push(s.score_per_throw)
                      labs.push(s.season)
                    }
                    const jotain2 = document.getElementById('statGraph')
                    // labs.reverse()
                    // dat.reverse()
                    var config2 = {
                        type: 'line',
                        data :{
                          labels: labs,
                          datasets : [
                          {
                            backgroundColor: '#B3E5FC',
                            borderColor : '#B3E5FC',
                            label : 'KPH',
                            data : dat
                          }
                        ]
                      },
                        options: {
                          scales: {
                            y: {
                              beginAtZero: true
                            }
                          },
                          plugins: {
                            title: {text:'Statsin kehitys kausittain',
                            display: true
                          
                          }
                          }
                        }
                      }
                    new Chart(jotain2, config2)

                    const jotain3 = document.getElementById('kHP KPH')
                    var config3 = {
                      type: 'bar',
                        data: {
                          labels: [ '1', '2', '3', '4'],
                          datasets: [{
                            label: "Kausi " + this.all_seasons[list_index].season,
                            backgroundColor: '#B3E5FC',
                            data: [
                              this.all_seasons[list_index].average_score_position_one,
                              this.all_seasons[list_index].average_score_position_two,
                              this.all_seasons[list_index].average_score_position_three,
                              this.all_seasons[list_index].average_score_position_four,
                          ],
                            borderWidth: 1
                          }]
                        },
                        options: {
                          indexAxis: 'y',
                          scales: {
                            y: {
                              beginAtZero: true
                            }
                          },
                          plugins: {
                            title: {text:'Heittokeskiarvo heittopaikan mukaan',
                            display: true
                          
                          }
                          }
                        }
                      }
                    new Chart(jotain3, config3)
                    }
                  );
        },
        handleRedirect: function(value) {
          location.href = '/ottelu/'+value.id;
        },
        chanceSeason: function(value, row) {
          var year = Number(value.season)
          var index = 2023 - year
          const chart = Chart.getChart('chart')
          const chart3 = Chart.getChart('kHP KPH')
          row.select(true)  // For some reason this is important to make returnStyle method work onclick
          if (this.current_selection.includes(value.season)) {
            var j = 0
            for (const i of chart.data.datasets) {
              if (i.label == "Kausi " + value.season) {
                break
              }
              j++
            }
            chart.data.datasets.splice(j,1)
            var j = 0
            for (const i of chart3.data.datasets) {
              if (i.label == "Kausi " + value.season) {
                break
              }
              j++
            }
            chart3.data.datasets.splice(j,1)
            var j = 0
            for (const i of this.current_selection) {
              if (i == value.season) {
                break
              }
              j++
            }
            this.current_selection.splice(j,1)
            var j = 0
            for (const i of this.colors) {
              if (i == value.season) {
                this.colors[j] = ''
                break
              }
              j++
            }
          } else if (this.current_selection.length == 5 ) {
            return
          } else {
            var index = 0
            for (const i of this.all_seasons) {
              if (i.season == value.season) {
                break
              }
              index++
            }
            var tmp = this.all_seasons[index]
            var color = ''
            var index = 0
            for (const i of this.colors) {
              if (i == '') {break}
              index ++
            }
            if (index == 0) {
              color = '#B3E5FC'
            } else if (index == 1) {
              color = '#EF9A9A' 
            } else if (index== 2) {
              color = '#A5D6A7'
            } else if (index == 3) {
              color = '#DCE775'
            } else if (index == 4) {
              color = '#BA68C8'
            }
            this.colors[index] = value.season

            chart.data.datasets.push({
              label: "Kausi " + tmp.season,
              backgroundColor: color,
              data: [
                tmp.zeros_total + tmp.pikes_total,
                tmp.ones_total,
                tmp.twos_total,
                tmp.threes_total,
                tmp.fours_total,
                tmp.fives_total,
                tmp.gteSix_total
              ],
                borderWidth: 1
              })

              chart3.data.datasets.push({
                label: "Kausi " + tmp.season,
                backgroundColor: color,
                data: [
                tmp.average_score_position_one,
                tmp.average_score_position_two,
                tmp.average_score_position_three,
                tmp.average_score_position_four,
              ],
                borderWidth: 1
              })

            this.current_selection.push(value.season)
          }
          chart.update()
          chart3.update()
        },
        getColor: function(val1, val2) {
          if (val1 < val2) return '#C8E6C9' // green-lighten-4
          else if (val1 > val2) return '#EF9A9A' // red-lighten-4
          else return '#F0F4C3' // yellow-lighten-4
        },
        returnStyle: function(value) {
          var index = 0
          var found = false
          for (const i of this.colors) {
            if (i == value.season) {
              found = true
              break
            }
            index++
          }
          if (!found) {return}
          if (index == 0) {
            return 'blue-row'
          } else if (index == 1) {
            return 'red-row' 
          } else if (index== 2) {
            return 'green-row'
          } else if (index == 3) {
            return 'yellow-row'
          } else if (index == 4) {
            return 'purple-row'
          }
        },
        returnHeaderColor: function(value) {
          var index = 0
          var found = false 
          for (const i of this.column_colors) {
            if (i == value) {
              found = true
              break
            }
            index++
          }
          if (!found) {return}
          if (index == 0) {
            return 'blue-row'
          } else if (index == 1) {
            return 'red-row' 
          } else if (index== 2) {
            return 'green-row'
          } else if (index == 3) {
            return 'yellow-row'
          } else if (index == 4) {
            return 'purple-row'
          }
        },
        chanceHeaderStat: function(val) {
          var the_list = val.target.classList
          var head = val.target.innerText
          var tmp = ["Erät", "Poistetut kyykät","Heitot","KPH","kHP", "Hauet", "H%", 
          "Virkamiehet", "VM%", "JK"]

          if (!tmp.includes(head)) {return}
          const chart2 = Chart.getChart('statGraph')
          
          if (this.column_current_selection.includes(head)) {
            var j = 0
            for (const i of chart2.data.datasets) {
              if (i.label == head) {
                break
              }
              j++
            }
            chart2.data.datasets.splice(j,1)

            j = 0
            for (const i of this.column_current_selection) {
              if (i == head) {
                break
              }
              j++
            }
            this.column_current_selection.splice(j,1)
            j = 0
            for (const i of this.column_colors) {
              if (i == head) {
                this.column_colors[j] = ''
                break
              }
              j++
            }
            if (j == 0) {
              the_list.remove('blue-row')
            } else if (j == 1) {
              the_list.remove('red-row')
            } else if (j== 2) {
              the_list.remove('green-row')
            } else if (j == 3) {
              the_list.remove('yellow-row')
            } else if (j == 4) {
              the_list.remove('purple-row')
            }
          } else if (this.column_current_selection.length == 5 ) {
            return
          } else {
            var color = ''
            var index = 0
            for (const i of this.column_colors) {
              if (i == '') {break}
              index ++
            }
            if (index == 0) {
              the_list.add('blue-row')
              color = '#B3E5FC'
            } else if (index == 1) {
              the_list.add('red-row')
              color = '#EF9A9A'
            } else if (index== 2) {
              the_list.add('green-row')
              color = '#A5D6A7'
            } else if (index == 3) {
              the_list.add('yellow-row')
              color = '#DCE775'
            } else if (index == 4) {
              the_list.add('purple-row')
              color = '#BA68C8'
            }
            this.column_colors[index] = head

            var dat = []
            this.all_seasons.forEach(s => {
              switch (head) {
                case "Erät":
                  dat.push(s.rounds_total)
                  break
                case "Poistetut kyykät":
                  dat.push(s.score_total)
                  break
                case "Heitot":
                  dat.push(s.throws_total)
                  break
                case "KPH":
                  dat.push(s.score_per_throw)
                  break
                case "kHP":
                  dat.push(s.avg_throw_turn)
                  break
                case "Hauet":
                  dat.push(s.pikes_total)
                  break
                case "H%":
                  dat.push(s.pike_percentage)
                  break
                case "Virkamiehet":
                  dat.push(s.zeros_total)
                  break
                case "VM%":
                  dat.push(s.zero_percentage)
                  break
                case "JK":
                  dat.push(s.gteSix_total)
                  break
                default:
                  // This shouldn't be possible
                  console.log("Something went wrong: " + head)
                  return
              }
            })
            chart2.data.datasets.push({
              label: head,
              backgroundColor: color,
              borderColor: color,
              data: dat,
              })

            this.column_current_selection.push(head)
          }
          chart2.update()
        },
        throwSort(items, index, isDescending) {
          const custom_columns = ['score_first','score_second', 'score_third', 'score_fourth', 'score_fifth', 'score_sixth', 'score_seventh', 'score_eighth']

          function d(p1) {
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

          items.sort((a,b) => {
            if(!isNaN(custom_columns.includes(index[0]))) {
              var a1 = d(a[index[0]])
              var b1 = d(b[index[0]])
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
        },
        filtterItems(arr, all_time_vs_seasons, search) {
          var returning_arr = all_time_vs_seasons == 'Kaikki kaudet' ? arr 
          : arr.filter(ele => this.current_selection.includes(ele['season']))
          
          if (search == '') {
            return returning_arr
          }
          return returning_arr.filter(match => {
            var found = false
            for (const key in match) {
              if (key == 'id') {continue}
              const ele = typeof match[key] !== 'string' ? String(match[key]) : match[key]
              if (ele.toLowerCase().includes(search.toLowerCase())) {
                found = true
                break
              }
            }
            return found
          })
        }

    },
    mounted: function() {
        this.getPlayer();
    }

};
</script>


<style>

tbody tr :hover {
    cursor: unset;
}

.border_left {
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

.blue {
  background-color: #B3E5FC !important;
}

</style>