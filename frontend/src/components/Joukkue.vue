<template>
  <v-card>
        <v-card elevation=0>
            <v-row style="height:130px">
              <v-col align="center" justify="center">
                  <img
                    src="../../public/kyykkalogo120px.png"
                  >
              </v-col>
            </v-row>
            <v-row>
              <v-col>
              <v-app-bar color="red darken-5" dark text>
                <v-spacer></v-spacer>
                <v-toolbar-title>{{header}}</v-toolbar-title>
                <v-spacer></v-spacer>
              </v-app-bar>
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
                          <v-list-item-content>Tehdyt pisteet:</v-list-item-content>
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
                    text: 'SPH',
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
            stats: [],
            players: [],
            reserve: []
        };
    },
    methods: {
        getPlayers: function() {
            this.$http
                .get('api/teams/' + this.team_id +'/?season='+sessionStorage.season_id)
                .then(
                    function(data) {
                        this.stats = [data.body];
                        this.players = data.body.players;
                        this.header = data.body.current_name;
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
        }
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

