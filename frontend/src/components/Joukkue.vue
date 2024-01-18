<template>
  <v-card>
    <v-card elevation=0>
      <v-row style="height:130px margin-bottom:3px">
        <v-col align="center" justify="center" cols="2">
          <img src="../../public/kyykkalogo120px.png">
        </v-col>
        <v-col cols="10">
          <v-row>
            <v-col>
              <v-app-bar color="red darken-5" dark text>
                  <v-spacer></v-spacer>
                  <v-toolbar-title>{{header}}</v-toolbar-title>
                  <v-spacer></v-spacer>
              </v-app-bar>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-btn-toggle v-model="selected_season" mandatory>
                <v-slide-group multiple show-arrows>
                    <v-slide-item>
                        <v-btn text 
                          :value="all_time" 
                          @click="jotain('all_time')">
                          All-Time
                        </v-btn>
                    </v-slide-item>
                    <v-slide-item v-for="year in Object.keys(this.seasons_data).sort((a,b) => b-a)" :key="year">
                      <v-btn text
                        :value="year"
                        @click="jotain(year)">
                        {{ year }}
                      </v-btn>
                    </v-slide-item>
                </v-slide-group>
              </v-btn-toggle>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
            <v-row style="height:220px">
              <v-col class="pt-0">
              <v-data-iterator
                :items="stats"
                :headers="header"
                hide-default-footer
              >
                <template v-slot:item="props">
                      <v-list dense>
                        <v-list-item>
                          <v-list-item-content>Poistetut Kyykät:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.score_total }}</v-list-item-content>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item>
                          <v-list-item-content>Ottelut:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.match_count }}</v-list-item-content>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item>
                          <v-list-item-content>Hauet:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.pikes_total }}</v-list-item-content>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item>
                          <v-list-item-content>Nolla heitot:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.zeros_total }}</v-list-item-content>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item>
                          <v-list-item-content>Nolla aloitukset:</v-list-item-content>
                          <v-list-item-content
                            class="align-end"
                          >{{ props.item.zero_or_pike_first_throw_total }}</v-list-item-content>
                        </v-list-item>
                      </v-list>
                </template>
              </v-data-iterator>
              </v-col>
              <v-divider vertical></v-divider>
              <v-col class="pt-0">
              <v-data-iterator :items="stats" hide-default-footer row wrap>
                <template v-slot:item="props">
                      <v-list dense>
                        <v-list-item>
                          <v-list-item-content>Heitot:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.throws_total }}</v-list-item-content>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item>
                          <v-list-item-content>Ottelu keskiarvo:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.match_average }}</v-list-item-content>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item>
                          <v-list-item-content>Haukiprosentti:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.pike_percentage }}</v-list-item-content>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item>
                          <v-list-item-content>Nollaprosentti:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.zero_percentage }}</v-list-item-content>
                        </v-list-item>
                        <v-divider></v-divider>
                        <v-list-item>
                          <v-list-item-content>Joulukuuset:</v-list-item-content>
                          <v-list-item-content class="align-end">{{ props.item.gteSix_total }}</v-list-item-content>
                        </v-list-item>
                      </v-list>
                </template>
              </v-data-iterator>
              </v-col>
            </v-row>
        </v-card>
        <v-divider></v-divider>
    <v-expansion-panels v-model="panel" multiple>
      <v-expansion-panel>
        <v-expansion-panel-header>
          Pelaajat
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-data-table mobile-breakpoint="0" class="mt-5" 
          disable-pagination 
          :headers="headers"
          @click:row="handleRedirect"
          :items="players"
           hide-default-footer>
            <template slot="no-data">
              <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
            </template>
          </v-data-table>
          <v-spacer></v-spacer>
          <v-expansion-panels>
            <v-expansion-panel v-if="isCaptain">
              <v-expansion-panel-header>
                Varaa pelaajia
              </v-expansion-panel-header>
                <v-expansion-panel-content>
                <v-text-field class="mb-10 mt-0" style="width: 50%;" color="red" v-model="search" label="Search" single-line hide-details/>
                  <v-data-table mobile-breakpoint="0" disable-pagination dense :search="search" :items="reserve" :headers="reserveHeaders" hide-default-footer>
                    <!-- [``] needed to prevent eslint error -->
                    <template v-slot:[`item.actions`]="{ item }">
                      <v-icon
                        v-if="!item.team.current_name"
                        color=green
                        @click="reserveButton(item)"
                      >
                        mdi-plus
                      </v-icon>
                      <v-icon
                        v-else  
                        color=gray
                        >
                        <!-- @click="deleteItem(item)" -->
                        mdi-lock
                      </v-icon>
                    </template>
                  </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>Ottelut</v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-data-table mobile-breakpoint="0" @click:row="handleRedirect" dense color='alert' 
          :search="search" 
          :headers="match_headers"
          :items="matches">
            <template slot="no-data">
              <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
            </template>
            <template v-for="h in match_headers" v-slot:[`header.${h.value}`]="{ header }">
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
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card>
</template>

<script>
export default {
    data: function() {
        return {
            search: '',
            header: '',
            isCaptain: false,
            team_id: this.$route.fullPath.substr(
                this.$route.fullPath.lastIndexOf('/') + 1
            ),
            reserveHeaders: [
                { text: '#', value: 'player_number'},
                { text: 'Pelaajan nimi', value: 'player_name' },
                {
                    text: 'Varaa',
                    value: 'actions',
                    align: 'left',
                    sortable: false,
                },
            ],
            headers: [
                { text: '#', value: 'player_number', width:"1%" },
                {
                    text: 'Nimi',
                    value: 'player_name',
                    width: '20%',
                    align: 'left'
                },
                {
                    text: 'E',
                    value: 'rounds_total',
                    width: '1%',
                    align: 'left'
                },
                { text: 'P', value: 'score_total', width: '1%', align: 'left' },
                {
                    text: 'PPH',
                    value: 'score_per_throw',
                    width: '1%',
                    align: 'left'
                },
                {
                    text: 'SP',
                    value: 'scaled_points',
                    width: '1%',
                    alignt: 'left'
                },
                {
                    text: 'SPPH',
                    value: 'scaled_points_per_throw',
                    width: '1%',
                    alignt: 'left'
                },
                {
                    text: 'kHP',
                    value: 'avg_throw_turn',
                    width: '1%',
                    align: 'left'
                },
                { text: 'H', value: 'pikes_total', width: '1%', align: 'left' },
                {
                    text: 'H%',
                    value: 'pike_percentage',
                    width: '1%',
                    align: 'left'
                },
                {
                    text: 'VM',
                    value: 'zeros_total',
                    width: '1%',
                    align: 'left'
                },
                {
                    text: 'JK',
                    value: 'gteSix_total',
                    width: '1%',
                    alignt: 'left'
                }
            ],
            match_headers: [
            { text: 'Aika', value: 'match_time', align: 'center', tooltip:'Pelausaika'},
            { text: 'Tyyppi', value: 'match_type', align: 'center',tooltip: 'Peli Tyyppi' },
            { text: 'Vastustaja', value: 'opposite_team', align: 'center', tooltip: 'Vastustaja joukkue'},
            { text: 'OJ 1', value: 'own_first', align: 'center', tooltip:'Oman Joukkueen 1. Erä', width: '2%'},
            { text: 'OJ 2', value: 'own_second', align: 'center', tooltip: 'Oman Joukkueen 2. Erä', width: '2%'},
            { text: 'V 1', value: 'opp_first', align: 'center', tooltip: 'Vastustaja Joukkueen 1. Erä', width: '2%'},
            { text: 'V 2', value: 'opp_second', align: 'center', tooltip: 'Vastustaja Joukkueen 2. Erä', width: '2%'},
            // { text: 'H+VM', value: 'jotain', align: 'center', tooltip: 'Yhteensä pelissä oman joukkueen heittämät nolla heitot'},
            // { text: 'JK', value: 'jotain', align: 'center', tooltip: '(Joulukuusi) Yhteensä pelissä oman joukkueen heittämät "6 kyykkää tai enemmän"- heitot'},
            { text: 'OJ pis.', value: 'own_team_total', align: 'center', tooltip:'Oman joukkueen pisteet' },
            { text: 'V pis.', value: 'opposite_team_total', align: 'center', tooltip:'Vastustaja joukkueen pisteet' }
            ],
            panel: [0],
            stats: [],
            players: [],
            reserve: [],
            matches: [],
            selected_season: null,
            all_time: [],
            seasons_data: {}
        };
    },
    methods: {
        getPlayers: function() {
            this.$http
                .get('api/teams/' + this.team_id +'/?season='+sessionStorage.season_id)
                .then(
                    function(data) {
                        for (const [k, v] of Object.entries(data.body)) {
                          if (k == 'all_time') {
                            this.all_time = v
                          } else {
                            this.seasons_data[k] = v
                          }
                        }
                        if (sessionStorage.season_id in this.seasons_data) {
                          this.selected_season = sessionStorage.season_id.toString()
                        } else {
                          this.selected_season = Math.max(...Object.keys(this.seasons_data).map(x => +x)).toString()
                        }
                        const tmp = this.seasons_data[this.selected_season]
                        this.players = tmp.players;
                        this.header = tmp.current_name;
                        this.stats = [tmp];
                        this.matches = tmp.matches;
                    },
                );
        },
        getReserve: function() {
            this.$http.get('api/reserve/', {
                  'withCredentials': true,
                }).then(
                function(data) {
                    var i = 0;
                    for (var player in data.body) {
                        if (data.body[i].team.current_name == "") {
                            this.reserve.push(data.body[i]);
                        }
                        i++;
                    }
                },
                function(error) {
                    console.log(error.statusText);
                }
            );
        },
        reserveButton: function(item) {
            let post_data = {'player': item.id}
            let post_url = 'api/reserve/'+'?season='+sessionStorage.season_id;
            var index = this.reserve.findIndex(player => player.id === item.id);

            if (confirm('Haluatko varmasti varata pelaajan "'+item.player_name+'"?')) {
              this.$http.post(post_url, post_data, {
                headers: {
                  'X-CSRFToken': this.getCookie('csrftoken')
                },
                  'withCredentials': true,        
                }).then(function(response) {
                  if (response.status === 200) {
                      this.getPlayers();
                      this.reserve.splice(index, 1);
                  }
                }).catch(function(response) {
                  if (response.status == 403) {
                    this.$http
                      .get('api/csrf', {'withCredentials': true})
                      .then(function(response) {
                          if (response.status === 200) {
                              this.getPlayers();
                              this.reserve.splice(index, 1);
                              this.$http.patch(post_url, post_data, {
                              headers: {
                                'X-CSRFToken': this.getCookie('csrftoken')
                              },
                                'withCredentials': true,
                              })
                          }
                      });
                  }
              })
            }
        },
        handleRedirect: function(value) {
          location.href = '/pelaaja/'+value.id;
        },
        jotain: function(value) {
          this.selected_season = value
          if (value == 'all_time') {
            this.stats = [this.all_time]
            this.players = this.all_time.players;
            this.matches = this.all_time.matches
          } else {
            this.players = this.seasons_data[value].players;
            this.header = this.seasons_data[value].current_name;
            this.stats = [this.seasons_data[value]];
            this.matches = this.seasons_data[value].matches
            console.log(this.selected_season)
          }
        },
        getColor: function(val1, val2) {
          if (val1 < val2) return '#C8E6C9' // green-lighten-4
          else if (val1 > val2) return '#EF9A9A' // red-lighten-4
          else return '#F0F4C3' // yellow-lighten-4
        },
    },
    mounted: function() {
        this.header = '';
        this.getPlayers();
        if (this.$session.get('user_id') && this.$session.get('role_id') == 1) {
            this.getReserve();
            this.isCaptain = true;
        }
    }
};
</script>


<style>

tbody tr :hover {
    cursor: unset;
}

</style>

