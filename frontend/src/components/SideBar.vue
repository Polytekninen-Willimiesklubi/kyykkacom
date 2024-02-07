<template>
  <v-card>
    <v-card-title>{{ this.title }}</v-card-title>
    <v-row v-for="(listItem, index) in teams" :key="index">
      <v-col>
        <v-card-subtitle v-if="multible_brackets"><b> Lohko {{ String.fromCharCode(65+index) }} </b></v-card-subtitle>
        <v-divider></v-divider>
        <!-- note on :items="[...listItem]" here we make reduntant array just unpack it immediately, 
          because otherwise returns an 'expected an array' error. This might be caused by listItem 
          not being defined before the mouting happens (?) -->
        <v-data-table mobile-breakpoint="0" disable-pagination dense
          :class="{regular_season : isClass, regular_season16 : is16Class, regular_season12: is12Class, regular_season8: is8Class,
             regular_season16_2 : is16_2Class, regular_season4_2: is4_2Class, regular_season4: is4Class , regular_season6: is6Class}"
          :header-props="{ sortIcon: null }"
          @click:row="handleRedirect"
          :headers="headers" 
          :items="[...listItem]"
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
  </v-card>
</template>

<script>
export default {
    props: {
      title: {
        type: String,
        default: 'Runkosarja'
      },
      headers: {
        type: Array,
        default: function() { 
          return [
            { text: 'Joukkue', value: 'current_abbreviation', sortable: false},
            { text: 'O', value: 'matches_played', sortable: false},
            { text: 'V', value: 'matches_won', sortable: false},
            { text: 'T', value: 'matches_tie', sortable: false},
            { text: 'H', value: 'matches_lost', sortable: false},
            { text: 'P', value: 'points_total'},
            { text: 'P/O', value: 'points_average', sortable: false},
            { text: 'OKA', value: 'match_average', sortable: false},
          ]}
      },
      sortBy: {
        type: String,
        default: 'points_total'
      },
      sortDesc: {
        type: Boolean,
        default: true
      },
      defaultData: {
        type: Boolean,
        default: true
      },
      no_brackets: { // This is expected if defaultData is False 
        type: Number,
        default: 1
      },
    },
    data: function() {
        return {
            season: false,
            isClass: false,
            is12Class: false,
            is16Class: false,
            is16_2Class: false,
            is4Class: false,
            is4_2Class: false,
            is6Class: false,
            is8Class: false,

            multible_brackets: false,
            data: [],
            teams: [],
        };
    },
    methods: {
        getTeams: function() {
            this.$http.get('api/teams/'+'?season='+sessionStorage.season_id+'&post_season=0').then(
                function(data) {
                    sessionStorage.teams = JSON.stringify(data.body)
                },
                function(error) {
                    console.log(error.statusText);
                }
            ).then(
              function() {
                this.splitToBrackets()
              }
            );
        },
        getSuperTeams: function() {
            this.$http.get('api/teams/'+'?season='+sessionStorage.season_id+'&super_weekend=1').then(
                function(data) {
                    sessionStorage.super_teams = JSON.stringify(data.body)
                },
                function(error) {
                    console.log(error.statusText);
                }
            ).then(
              function() {
                this.splitToBrackets()
              }
            );
        },
        splitToBrackets: function() {
          if (this.defaultData) {
            this.data = JSON.parse(sessionStorage.teams)
            this.isClass = (sessionStorage.season_id == 24 || sessionStorage.season_id == 25)
            this.is16Class = (sessionStorage.season_id == 23 || sessionStorage.season_id == 21 || sessionStorage.season_id == 20)
            this.is16_2Class = (sessionStorage.season_id == 22)
            this.is12Class = (11 <= sessionStorage.season_id && sessionStorage.season_id <= 19)
            this.is4_2Class = (sessionStorage.season_id == 1)
            this.is4Class = (sessionStorage.season_id == 8 || sessionStorage.season_id == 9)
            this.is6Class = (2 <= sessionStorage.season_id && sessionStorage.season_id <= 7)
            this.is8Class = (sessionStorage.season_id == 10)
  
  
            if (sessionStorage.all_seasons) {
              var all_seasons = JSON.parse(sessionStorage.all_seasons)
              
              var index = all_seasons.map(ele => String(ele.id)).indexOf(sessionStorage.season_id)
              var this_season = all_seasons[index]
  
              if (this_season.no_brackets > 1) {
                this.multible_brackets = true
                for (let i = 0; i < this_season.no_brackets; i++) {
                  this.teams.push([])
                }
                this.data.forEach(ele => {
                  this.teams[ele.bracket -1].push(ele)
                }, this)
  
              } else {
                this.teams = [this.data]
                this.multible_brackets = false
              }
            }
          } else {
            if(sessionStorage.super_teams) {
              console.log('moi')
              this.data = JSON.parse(sessionStorage.super_teams)
              if (this.no_brackets > 1) {
                this.multible_brackets = true
                for (let i = 0; i < this.no_brackets; i++) {
                    this.teams.push([])
                  }
                this.data.forEach(ele => {
                  this.teams[ele.super_weekend_bracket -1].push(ele)
                }, this)
              } else {
                this.teams = [this.data]
                this.multible_brackets = false
              }
            }
          }
        },
        handleRedirect: function(value) {
          location.href = '/joukkue/'+value.id;
        }
    },
    created: function() {
      if (!this.defaultData) {
        this.getSuperTeams()
        sessionStorage.setItem("loaded_season", sessionStorage.season_id)
        this.splitToBrackets()

      } else {
        if (sessionStorage.loaded_season != sessionStorage.season_id) {
          this.getTeams()
          sessionStorage.setItem("loaded_season", sessionStorage.season_id)
        } else {
          this.splitToBrackets()
        }
      }
    }
};
</script>

<style>

.regular_season12 > .v-data-table__wrapper > table > tbody > tr:nth-child(4) > td {
  border-bottom: 0.15rem dashed red !important;
}

.regular_season12 > .v-data-table__wrapper > table > tbody > tr:nth-child(12) > td {
 border-bottom: 0.2rem double red !important;
}

.regular_season > .v-data-table__wrapper > table > tbody > tr:nth-child(5) > td {
  border-bottom: 0.15rem dashed red !important;
}

.regular_season > .v-data-table__wrapper > table > tbody > tr:nth-child(11) > td {
 border-bottom: 0.2rem double red !important;
}

.regular_season16 > .v-data-table__wrapper > table > tbody > tr:nth-child(16) > td {
 border-bottom: 0.2rem double red !important;
}

.regular_season16_2 > .v-data-table__wrapper > table > tbody > tr:nth-child(8) > td {
 border-bottom: 0.2rem double red !important;
}

.regular_season4_2 > .v-data-table__wrapper > table > tbody > tr:nth-child(2) > td {
 border-bottom: 0.2rem double red !important;
}

.regular_season4 > .v-data-table__wrapper > table > tbody > tr:nth-child(4) > td {
 border-bottom: 0.2rem double red !important;
}

.regular_season6 > .v-data-table__wrapper > table > tbody > tr:nth-child(6) > td {
  border-bottom: 0.15rem dashed red !important;
}

.regular_season6 > .v-data-table__wrapper > table > tbody > tr:nth-child(2) > td {
 border-bottom: 0.2rem double red !important;
}

.regular_season8 > .v-data-table__wrapper > table > tbody > tr:nth-child(8) > td {
 border-bottom: 0.2rem double red !important;
}

</style>
