<template>
  <v-layout>
    <v-flex auto>
      <ottelut />
    </v-flex>
    <v-flex xs4 class="pl-3 hidden-md-and-down">
      <side-bar
        :no_brackets="no_brackets"
        :non-default-teams="teams"
      />
    </v-flex>
  </v-layout>
</template>

<script>
import SideBar from '@/components/SideBar';
import Ottelut from '@/components/Ottelut';

export default {
    name: 'ottelutview',
    components: {
        SideBar,
        Ottelut
    },
    data() {
      return {
        teams: [],
        no_brackets: 1
      }
    },
    methods: {
      getTeams() {
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
      splitToBrackets() {
        let data = JSON.parse(sessionStorage.teams)

        if (sessionStorage.all_seasons) {
          var all_seasons = JSON.parse(sessionStorage.all_seasons)
          
          var index = all_seasons.map(ele => String(ele.id)).indexOf(sessionStorage.season_id)
          this.no_brackets = all_seasons[index].no_brackets

          this.teams = data
        } else {
          this.no_brackets = 1
          this.teams = data
        }
      }
  },
  mounted() {
      if (!sessionStorage.loaded_season || sessionStorage.loaded_season != sessionStorage.season_id) {
          this.getTeams();
          sessionStorage.loaded_season = sessionStorage.season_id
      } else {
          this.splitToBrackets()
      }
    },
};
</script>

<style>
</style>
