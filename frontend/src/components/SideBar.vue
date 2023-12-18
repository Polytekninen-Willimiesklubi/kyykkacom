<template>
  <v-card>
    <v-card-title> Runkosarja </v-card-title>
    <v-row>
      <v-col>
        <v-card-subtitle v-if="multible_brackets"> Lohko A </v-card-subtitle>
        <v-data-table mobile-breakpoint="0" :header-props="{ sortIcon: null }" disable-pagination 
        @click:row="handleRedirect" dense 
        :headers="headers" 
        :items="teams" 
        :sort-by.sync="sortBy" 
        :sort-desc.sync="sortDesc" 
        hide-default-footer>
          <template slot="no-data">
            <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-divider v-if="multible_brackets"></v-divider>
    <v-row v-if="multible_brackets">
      <v-col>
        <v-card-subtitle> Lohko B </v-card-subtitle>
        <v-data-table mobile-breakpoint="0" :header-props="{ sortIcon: null }" disable-pagination 
        @click:row="handleRedirect" dense 
        :headers="headers" 
        :items="other_teams" 
        :sort-by.sync="sortBy" 
        :sort-desc.sync="sortDesc" 
        hide-default-footer>
      </v-data-table>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
export default {
    data: function() {
        return {
            season: false,
            sortBy: 'points_total',
            sortDesc: true,
            multible_brackets: false,
            headers: [
                { text: 'Joukkue', value: 'current_abbreviation', sortable: false},
                { text: 'O', value: 'matches_played', sortable: false},
                { text: 'V', value: 'matches_won', sortable: false},
                { text: 'H', value: 'matches_lost', sortable: false},
                { text: 'T', value: 'matches_tie', sortable: false},
                { text: 'P', value: 'points_total'},
                { text: 'P/O', value: 'points_average', sortable: false},
                { text: 'OKA', value: 'match_average', sortable: false},
            ],
            teams: [],
            other_teams: []
        };
    },
    methods: {
        getTeams: function() {
            this.$http.get('api/teams/'+'?season='+sessionStorage.season_id+'&post_season=0').then(
                function(data) {
                    this.teams = data.body;
                    sessionStorage.teams = JSON.stringify(data.body)
                    var all_seasons = JSON.parse(sessionStorage.all_seasons)
                    var this_season = ''
                    for (let i = 0; i < all_seasons.length; i++) {
                     var s = all_seasons[i]
                     if (s.id == sessionStorage.season_id) {
                      this_season = s
                      break
                     }
                    }
                    if (this_season.no_brackets > 1) {
                      this.multible_brackets = true
                      var tmp_teams = []
                      for (let i = 0; i < this_season.no_brackets; i++) {
                        tmp_teams.push([])
                      }
                      this.teams.forEach(ele => {
                        tmp_teams[ele.bracket -1].push(ele)
                      })
                      this.teams = tmp_teams[0]
                      this.other_teams = tmp_teams[1]
                    } else {
                      this.multible_brackets = false
                    }
                },
                function(error) {
                    console.log(error.statusText);
                }
            );
        },
        handleRedirect: function(value) {
          location.href = '/joukkue/'+value.id;
        }
    },
    mounted: function() {
      if (sessionStorage.loaded_season != sessionStorage.season_id) {
        this.getTeams()
        sessionStorage.setItem("loaded_season", sessionStorage.season_id)
      } else {
        this.teams = JSON.parse(sessionStorage.teams)
      }
      var all_seasons = JSON.parse(sessionStorage.all_seasons)
      var this_season = ''
      for (let i = 0; i < all_seasons.length; i++) {
        var s = all_seasons[i]
        if (s.id == sessionStorage.season_id) {
        this_season = s
        break
        }
      }
      if (this_season.no_brackets > 1) {
        this.multible_brackets = true
        var tmp_teams = []
        for (let i = 0; i < this_season.no_brackets; i++) {
          tmp_teams.push([])
        }
        this.teams.forEach(ele => {
          tmp_teams[ele.bracket -1].push(ele)
        })
        this.teams = tmp_teams[0]
        this.other_teams = tmp_teams[1]
      } else {
        this.multible_brackets = false
      }
    }
};
</script>
<style>

</style>
