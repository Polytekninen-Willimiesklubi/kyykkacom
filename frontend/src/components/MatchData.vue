<template>
      <v-card>
        <h3 class="text-md-left headline">
          {{this.type_name}} kenttä <span v-if="this.match_field">{{this.match_field}}</span><span v-else>TBD</span>
          <span style="float:right;">{{ this.match_time | luxon('y-MM-dd HH:mm') }}</span>
        </h3>
        <v-row>
          <v-container fill-height>
            <v-col justify="center" align="center" class="ml-5">
              <figure>
                <img src="../../public/kyykkalogo120px.png">
                <figcaption v-if="this.home.score_total">
                  <br>
                  <v-chip
                    :color="`${this.home.color} lighten-2`"
                  >{{this.home.score_total}}</v-chip>
                </figcaption>
              </figure>
            </v-col>
            <v-col justify="center" align="center">
              <a :href="'/joukkue/'+this.home.id">{{this.home.name}}</a>
            </v-col>
            <v-col justify="center" align="center">
              vs.
            </v-col>
            <v-col justify="center" align="center">
              <a :href="'/joukkue/'+this.away.id">{{this.away.name}}</a>
            </v-col>
            <v-col justify="center" align="center" class="mr-5">
              <figure style="float:right;">
                <img src="../../kyykkalogo120px.png">
                <figcaption v-if="this.home.score_total">
                  <br>
                  <v-chip
                    :color="`${this.away.color} lighten-2`"
                  >{{this.away.score_total}}</v-chip>
                </figcaption>
              </figure>
            </v-col>
          </v-container>
        </v-row>
      </v-card>
</template>

<script>
export default {
  props: {
    matchData: Object
  },
  data () {
    return {
      match_time: '',
      match_field: '',
      type_name: '',
      home: {
        name: '',
        score_total: '',
        color: ''
      },
      away: {
        name: '',
        score_total: '',
        color: ''
      }
    }
  },
  methods: {
    getMatch () {
      this.match_time = this.matchData.match_time
      this.match_field = this.matchData.field
      this.away.name = this.matchData.away_team.current_name
      this.home.name = this.matchData.home_team.current_name
      this.home.id = this.matchData.home_team.id
      this.away.id = this.matchData.away_team.id
      this.type_name = this.matchData.type_name

      this.home.score_total = this.matchData.home_score_total
      this.away.score_total = this.matchData.away_score_total

      if (
        this.home.score_total > this.away.score_total
      ) {
        this.home.color = 'red'
        this.away.color = 'green'
      } else if (
        this.home.score_total < this.away.score_total
      ) {
        this.home.color = 'green'
        this.away.color = 'red'
      } else {
        this.home.color = 'yellow'
        this.away.color = 'yellow'
      }
    }
  },
  mounted () {
    this.getMatch()
  }
}
</script>

<style scoped>
a {
  color: black;
  text-decoration: none;
}

</style>
