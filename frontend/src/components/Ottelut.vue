<template>
  <v-card>
    <v-card-title class="d-flex flex-wrap-reverse">
      <div>
        Ottelut
        <v-select v-on:input="selectChange()" v-model="defaultSelected" style="width: 50%" color="red" :items="options" />
      </div>
      <v-spacer />
      <div>
        <v-text-field color="red" v-model="search" label="Search" single-line hide-details />            
      </div>
    </v-card-title>
    <v-data-table 
      v-if="defaultSelected != 'Jatkosarja'"
      :headers="headers"
      :items="data"
      :search="search"
      @click:row="handleRedirect" 
      :item-class="itemRowBackground"
      mobile-breakpoint="0"
      hide-default-footer
      disable-pagination
      dense
    >
    <template slot="no-data">
      <v-progress-linear color="red" slot="progress" indeterminate />
    </template>
    <template slot="headers" class="text-xs-center" />
    <!-- [``] needed to prevent eslint error -->
    <template v-slot:[`item.match_time`]="{ item }">
      <span>{{ item.match_time | luxon('y-MM-dd HH:mm') }}</span>
      <v-tooltip v-if="!item.is_validated & (parseInt(item.home_team.id) === parseInt(team_id) || parseInt(item.away_team.id) === parseInt(team_id))" bottom>
        <template #activator="{ on }">
          <v-icon color="gray" class="mr-3" v-on="on">info</v-icon>
        </template>
        <span>Ottelu on validoimatta</span>
      </v-tooltip>
    </template>
      <v-alert
        slot="no-results"
        :value="true"
        color="error"
      >Your search for "{{ search }}" found no results.</v-alert>
    </v-data-table>
    <v-data-table v-else
      :headers="post_headers"
      :items="data"
      :search="search" 
      @click:row="handleRedirect" 
      :group-by="seriers"
      mobile-breakpoint="0" 
      disable-pagination 
      hide-default-footer
      dense
    >
      <template v-slot:[`item.match_time`]="{ item }">
          <span>{{ item.match_time | luxon('y-MM-dd HH:mm') }}</span>
      </template>
      <template v-slot:group.header="{items, isOpen, toggle}">
        <th colspan="12" @click="toggle">
          <v-icon>
            {{ isOpen ? 'mdi-minus' : 'mdi-plus' }}
          </v-icon>
          {{ items[0].type_name }}
          {{ items[0].home_team.current_abbreviation}} vs. {{ items[0].away_team.current_abbreviation }}
        </th>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import moment from 'moment'
export default {
    data() {
        return {
            search: '',
            headers: [
                {
                    text: 'Aika',
                    align: 'left',
                    width:'20%',
                    value: 'match_time'
                },
                { text: 'Tyyppi', value: 'type_name', width:'10%'},
                { text: 'Kenttä', value: 'field', width:'15%', align:'left'},
                { text: 'Koti', value: 'home_team.current_abbreviation'},
                { text: 'Vieras', value: 'away_team.current_abbreviation'},
                { text: '', value: 'home_score_total', width:'3%', align: 'right'},
                { text: 'Tulos', value: 'dash', width:'1%', sortable: false, align: 'center'},
                { text: '', value: 'away_score_total', width:'3%', align: 'left'}
            ],
            post_headers: [
                {
                    text: 'Aika',
                    align: 'left',
                    value: 'match_time'
                },
                { text: 'Kenttä', value: 'field'},
                { text: 'Koti', value: 'home_team.current_abbreviation' },
                { text: 'Vieras', value: 'away_team.current_abbreviation' },
                { text: '', value: 'home_score_total', width:'3%', align: 'right'},
                { text: 'Tulos', value: 'dash', width:'1%', sortable: false, align: 'center'},
                { text: '', value: 'away_score_total', width:'3%', align: 'left'}
            ],
            data: [],
            matches: [],
            post_season: [],
            super_weekend: [],
            regular_season: [],
            defaultSelected: 'Kaikki ottelut',
            options: ['Kaikki ottelut','Runkosarja','Jatkosarja', 'SuperWeekend'],
            seriers: ['seriers']
        };
    },
    methods: {
        selectChange() {
          if (this.defaultSelected == "Runkosarja") {
            this.data = this.regular_season
          } else if (this.defaultSelected == "Jatkosarja") {
            this.data = this.post_season
          } else if (this.defaultSelected == "SuperWeekend") {
            this.data = this.super_weekend
          } else {
            this.data = this.matches
          }
        },
        getMatches() {
          let url = 'api/matches/?season='+sessionStorage.season_id;
          
          const pelit = {
            1 : "Runkosarja",
            2 : "Finaali",
            3 : "Pronssi",
            4 : "Välierä",
            5 : "Puolivälierä",
            6 : "Neljännesvälierä",
            7 : "Kahdeksannesvälierä",
            10 : "Runkosarjafinaali",
            20 : "Jumbofinaali",
            31: "SuperWeekend: Alkulohko",
            32: "SuperWeekend: Finaali",
            33: "SuperWeekend: Pronssi",
            34: "SuperWeekend: Välierä",
            35: "SuperWeekend: Puolivälierä",
            36: "SuperWeekend: Neljännesvälierä",
            37: "SuperWeekend: Kahdeksannesvälierä",
          }

          this.$http.get(url).then(
              function(data) {
                  data.body.forEach(ele => {
                    ele.type_name = pelit[ele.match_type]
                    ele.dash = "-"
                    if (ele.post_season) {
                      this.post_season.push(ele)
                    } else if (ele.match_type >= 31) {
                      this.super_weekend.push(ele)
                    } else {
                      this.regular_season.push(ele)
                    }
                  })
                  this.data = data.body;
                  this.matches = data.body;
              },
          );
        },
        handleRedirect(value) {
          location.href = '/ottelu/'+value.id
        },
        itemRowBackground(item) {
          // Handles the backround color of row items
          var matchDate = moment(item.match_time).format("YYYY-MM-DD HH:MM")
          var currentTime = moment(Date.now()).format("YYYY-MM-DD HH:MM")

          if (!this.team_id) return

          if (!item.is_validated & matchDate < currentTime & (parseInt(item.home_team.id) === parseInt(this.team_id) || parseInt(item.away_team.id) === parseInt(this.team_id))) return 'row__background__style_1'

          return 'row__background__style_2'
        }
    },
    mounted() {
        if (localStorage.team_id) {
          this.team_id = localStorage.team_id;
        } else {
          this.team_id = '';
        }
        
        this.getMatches();
    }
};
</script>
<style>
.row__background__style_1 {
  background-color: rgba(195, 20, 20, 0.781) !important;
}

.row__background__style_2 {
  background-color: white;
}

</style>

