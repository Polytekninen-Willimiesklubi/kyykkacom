<template>
  <v-card>
    <v-card-title class="pa-0 pl-3 pt-3">
      Erä {{this.roundNumber}}
      <v-spacer/>
      <v-progress-circular 
        :size="20" 
        :width="2" 
        indeterminate color="red" 
        v-if="loading"
      />
    </v-card-title>
    <v-row v-if="!show_input" row wrap>
      <v-card-text v-if="this.round_score || this.round_score == '0'">
        <p>
          {{this.team}}
          <v-chip
            style="float:right;"
            :color="this.color"
            label
            small
            class="mr-2"
          >
            {{this.round_score}}
          </v-chip>
        </p>
      </v-card-text>
    </v-row>
    <v-divider />
    <v-row v-if="show_input" row wrap>
      <v-card-text v-if="loaded">
        <p>
          {{this.team}}
          <v-text-field 
            @input="roundScore()" 
            style="width:10%; float:right;" 
            v-model="round_score" 
            class="centered-input" 
            label="total" 
            maxlength="3"
          />
        </p>
      </v-card-text>
    </v-row>
    <!-- TODO loading -->
    <v-data-table 
      v-if="!show_input"
      mobile-breakpoint="0" 
      :headers="headers"
      @click:row="handleRedirect"
      :items="data"
      no-data-text="Ei dataa :("
      :no-filter="true"
    >
      <template #bottom></template> <!-- This hides the pagination controls-->
    </v-data-table>
    <!-- TODO loading -->
    <v-data-table 
      v-else
      mobile-breakpoint="0" 
      v-model="select"
      :headers="headers"
      :items="data"
      :items-per-page="4"
    >
      <template v-slot:headers class="text-xs-center"></template>
      <template v-slot:item="props" >
        <tr>
          <td :ref="'id_'+props.index">{{selected[props.index].player.id}}</td>
          <td>
            <v-select 
              item-color="red"
              color="red"
              v-model="selected[props.index].player.player_name"
              @change="loadPlayer($event, props.index)" 
              class="text-center pr-1" 
              placeholder="Select player" 
              :items="players" 
              single-line
            />
          </td>
          <div v-for="i in ['first', 'second', 'third', 'fourth']">
            <td>
              <v-text-field 
                color="red"
                v-model="selected[props.index]['score_'+ i]"
                :ref="i+'_throw_'+props.index"
                class="centered-input"
                maxlength="2"
                @input="sumTotal(props.index)"
                @keypress="isNumber($event)"
              />
            </td>
          </div>
          <td 
            class="centered-input" 
            style="font-size:18px" 
            :ref="'throw_sum_'+props.index"
          >
            {{selected[props.index]['score_total']}}
          </td>
        </tr>
        
      </template>
      <template #bottom></template> <!-- This hides the pagination controls-->
    </v-data-table>
  </v-card>
</template>
<style scoped>

  p {
    margin-bottom: 0;
    padding-bottom: 0;
    margin-left: .7em;
  }

  td {
    padding: 0 !important;
    text-align: center !important;
  }

  .centered-input >>> input {
    text-align: center
  }

  .v-text-field {
    font-size: 1.1em !important;
  }
</style>

<script>
export default {
  name: 'match-round',
  props: {
    matchData: Object,
    roundNumber: String,
    teamSide: String
  },
  data: function () {
    return {
      select: [],
      selected: [],
      show_input: false,
      loading: false,
      loaded: false,
      round_score: '',
      team: '',
      players: [],
      color: '',
      is_validated: '',
      data: [],
      headers: [
        // {
        //   text: this.teamSide,
        //   value: 'player.player_number',
        //   width: '5%'
        // },
        {
          title: 'Pelaaja',
          value: 'player.player_name',
          width: '45%'
        },
        { title: 1, align: 'center', value: 'score_first', width: '10%' },
        { title: 2, align: 'center', value: 'score_second', width: '10%' },
        { title: 3, align: 'center', value: 'score_third', width: '10%' },
        { title: 4, align: 'center', value: 'score_fourth', width: '10%' },
        { title: 'Yht.', align: 'center', value: 'score_total', width: '5%' }
      ],
      options: {
        itemsPerPage: 4
      }
    }
  },
  methods: {
    handleRedirect (value, row) {
      console.log(value, row)
      location.href = '/pelaajat/' + row.item.player.id
    },
    isNumber (evt) {
      // Checks that the value is an H or a numeric value from the ASCII table.
      // not verified atm?
      evt = (evt) || window.event
      const charCode = (evt.which) ? evt.which : evt.keyCode
      if ((charCode > 31 && (charCode < 48 || charCode > 57)) && charCode !== 72 && charCode !== 104 && charCode !== 69 && charCode !== 101) {
        evt.preventDefault()
      } else {
        return true
      }
    },
    roundScore () {
      const post_url = 'api/matches/' + this.matchData.id
      const post_data = {}
      let key = ''

      if (this.teamSide == 'home') {
        key = (this.roundNumber == 1) ? 'home_first_round_score' : 'home_second_round_score'
      } else if (this.teamSide == 'away') {
        key = (this.roundNumber == 1) ? 'away_first_round_score' : 'away_second_round_score'
      }
      post_data[key] = this.round_score
      this.$http.patch(post_url, post_data, {
        headers: {
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        withCredentials: true
      }).then().catch(function (response) {
        if (response.status == 403) {
          this.$http
            .get('api/csrf', { withCredentials: true })
            .then(function (response) {
              if (response.status === 200) {
                this.$http.patch(post_url, post_data, {
                  headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                  },
                  withCredentials: true
                })
              }
            })
        }
      })
    },
    sumTotal (index) {
      /* The function loops through all the column elements of the corresponding row
          and adds them up as total to the last column. The function also updates the database
          accordingly on each runthrough. */
      this.loading = true

      let throws
      let total = 0
      const array = [
        'first',
        'second',
        'third',
        'fourth'
      ]

      const post_data =
          {
            score_first: 0,
            score_second: 0,
            score_third: 0,
            score_fourth: 0,
            player: this.$refs['id_' + index].firstChild.data
          }

      if (this.teamSide == 'home') {
        throws = (this.roundNumber == 1) ? [0, 1, 2, 3] : [8, 9, 10, 11]
      } else if (this.teamSide == 'away') {
        throws = (this.roundNumber == 1) ? [4, 5, 6, 7] : [12, 13, 14, 15]
      }

      array.forEach(function (item) {
        const element = this.$refs[item + '_throw_' + index].$refs.input.value
        if (element.toLowerCase() == 'h') {
          var score = 'h'
        } else if (element.toLowerCase() == 'e') {
          var score = 'e'
        } else {
          var score = (!isNaN(parseInt(element))) ? parseInt(element) : 0
          total += score
        }
        if (element.length > 0) {
          post_data['score_' + item] = score
        }
      }, this)

      this.$refs['throw_sum_' + index].firstChild.data = total

      const post_url = 'api/throws/update/' + this.data[index].id + '/'

      this.$http.patch(post_url, post_data, {
        headers: {
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        withCredentials: true
      }).then(
        setTimeout(() => {
          this.loading = false
        }, 500)
      ).catch(error => {
        setTimeout(() => {
          this.loading = false
        }, 500)
      }).catch(function (response) {
        if (response.status == 403) {
          this.$http
            .get('api/csrf', { withCredentials: true })
            .then(function (response) {
              if (response.status === 200) {
                this.$http.patch(post_url, post_data, {
                  headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                  },
                  withCredentials: true
                })
              }
            })
        }
      })
    },
    loadPlayer (player, index) {
      // Finds the selected player object from the dataset and sets it's id to the id field.
      const obj = this.matchData[this.teamSide + '_team'].players.find(o => o.player_name === player)
      this.$refs['id_' + index].innerHTML = obj.id
      this.select = []
      this.sumTotal(index)
    },
    getMatch () {
      this.is_validated = this.matchData.is_validated

      const roundString = this.roundNumber == 1 ? 'first_round' : 'second_round'
      const opponent = this.teamSide == 'home' ? 'away' : 'home'
      const team = this.matchData[this.teamSide + '_team']

      this.team_name = team.current_name
      this.data = this.matchData[roundString][this.teamSide]
      this.opponent_score = this.matchData[opponent + '_' + roundString + '_score']
      this.round_score = this.matchData[this.teamSide + '_' + roundString + '_score']

      if (this.round_score > this.opponent_score) {
        this.color = 'red'
      } else if (this.round_score < this.opponent_score) {
        this.color = 'green'
      } else {
        this.color = 'yellow'
      }

      const tmp_selected = []
      const tmp_players = []

      this.data.forEach(function (item) {
        tmp_selected.push(item)
      })

      team.players.forEach(function (player) {
        tmp_players.push(player.player_name)
      })

      this.players = tmp_players
      this.selected = tmp_selected
      this.loaded = true
      if (!this.is_validated) {
        if (localStorage.team_id == this.matchData.home_team.id) {
          this.show_input = (localStorage.role_id == 1)
        }
      }
    }
  },
  mounted () {
    this.getMatch()
  }
}
</script>
