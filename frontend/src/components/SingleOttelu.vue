<template>
  <v-container grid-list-md>
    <v-row>
      <v-col>
        <match v-if="data_ready" :matchData="data"></match>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card color="secondary">
          <round v-if="data_ready" :matchData="data" roundNumber="1" teamSide="home"></round>
        </v-card>
      </v-col>
      <v-col>
        <v-card color="secondary">
          <round v-if="data_ready" :matchData="data" roundNumber="1" teamSide="away"></round>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card color="secondary">
          <round v-if="data_ready" :matchData="data" roundNumber="2" teamSide="home"></round>
        </v-card>
      </v-col>
      <v-col>
        <v-card color="secondary">
          <round v-if="data_ready" :matchData="data" roundNumber="2" teamSide="away"></round>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="text-xs-center">
        <v-btn v-if="data_ready && away_captain" v-on:click="validateClick" x-large color="error">vahvista</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Round from '@/components/SingleRound';
import Match from '@/components/MatchData';

export default {
    name: 'ottelu',
    components: {
        Round,
        Match
    },
    data() {
        return {
          data: {},
          data_ready: false,
          away_captain: false,
        };
    },
    methods: {
      getData() {
        this.$http
        .get(
            'api/matches/' +
                this.$route.fullPath.substr(
                    this.$route.fullPath.lastIndexOf('/') + 1
                )
        )
        .then(function(data) {
          this.data = data.body
          this.data_ready = true
          if(!data.body.is_validated && localStorage.role_id == 1 && localStorage.team_id == data.body.away_team.id) {
            this.away_captain = true
          }
        })
      },
      validateClick() {
        let post_url = 'api/matches/'+this.data.body.id
        let post_data = {"is_validated": true}

        if (confirm('Oletko tyytyväinen ottelun tuloksiin?')) {
          this.$http.patch(post_url, post_data, {
            headers: {
              'X-CSRFToken': this.getCookie('csrftoken')
            },
            'withCredentials': true,
          }).then(function(response){
            this.data.is_validated = true
            window.location.reload()
            }).catch(function(response) {
              if (response.status == 403) {
                this.$http
                  .get('api/csrf', {'withCredentials': true})
                  .then(function(response) {
                      if (response.status === 200) {
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
      }
    },
    created() {
      this.getData()
    },
};
</script>

<style>
</style>
