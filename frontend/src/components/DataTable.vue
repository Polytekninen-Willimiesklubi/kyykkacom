<template>
  <v-card>
    <v-card-title>
      Joukkueet
      <v-spacer></v-spacer>
      <v-text-field color="red" v-model="search" label="Search" single-line hide-details></v-text-field>
    </v-card-title>
    <v-data-table mobile-breakpoint="0" disable-pagination @click:row="handleRedirect" dense color='alert' :headers="headers" :search="search" :items="teams" hide-default-footer>
      <template slot="no-data">
        <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
export default {
    data() {
        return {
            search: '',
            headers: [
                { text: 'Nimi', value: 'current_name', align: 'center' },
                { text: 'Lyhenne', value: 'current_abbreviation' },
                { text: 'Ottelut', value: 'matches_played' },
                { text: 'Voitot', value: 'matches_won' },
                { text: 'Häviöt', value: 'matches_lost' },
                { text: 'Tasurit', value: 'matches_tie' },
                { text: 'Ottelu Ka', value: 'match_average' }
            ],
            teams: []
        };
    },
    methods: {
        getTeams() {
            this.$http.get('api/teams/'+'?season='+sessionStorage.season_id).then(
                function(data) {
                    this.teams = data.body;
                    sessionStorage.teams = JSON.stringify(data.body)
                }
            );
        },
        handleRedirect(value) {
          location.href = '/joukkue/'+value.id;
        }
    },
    mounted() {
      console.log(sessionStorage.loaded_season)
      if (!sessionStorage.loaded_season || sessionStorage.loaded_season != sessionStorage.season_id) {
        this.getTeams();
        sessionStorage.loaded_season = sessionStorage.season_id
      } else {
        this.teams = JSON.parse(sessionStorage.teams)
      }
    }
};
</script>
