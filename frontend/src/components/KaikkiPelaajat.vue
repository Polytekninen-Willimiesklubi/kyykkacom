<template>
    <v-card>
      <v-card-title>
        Kaikki Pelaajat
        <v-spacer></v-spacer>
        <v-text-field color="red" v-model="search" label="Search" single-line hide-details></v-text-field>
      </v-card-title>
      <v-data-table mobile-breakpoint="0" disable-pagination dense hide-default-footer
      :headers="headers" 
      @click:row="handleRedirect"
      :sortDesc="sortDesc"
      :sortBy="sortBy" 
      :items="players" 
      :custom-sort="custSort"
      :search="search">
        <template slot="no-data">
          <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
        </template>
        <template
          bind:key="props.item.id"
          slot="items"
          slot-scope="props"
        >
          <td>{{ props.item.player_name }}</td>
          <td class="text-xs-left" v-if="props.item.team !== null">{{ props.item.team.current_abbreviation }}</td>
          <td v-else>Ei varausta</td>
          <td class="text-xs-left">{{ props.item.rounds_total }}</td>
          <td class="text-xs-left">{{ props.item.score_total }}</td>
          <td class="text-xs-left">{{ props.item.score_per_throw }}</td>
          <td class="text-xs-left">{{ props.item.scaled_points }}</td>
          <td class="text-xs-left">{{ props.item.scaled_points_per_throw }}</td>
          <td class="text-xs-left">{{ props.item.avg_throw_turn }}</td>
          <td class="text-xs-left">{{ props.item.pikes_total }}</td>
          <td class="text-xs-left">{{ props.item.pike_percentage }}</td>
          <td class="text-xs-left">{{ props.item.zeros_total }}</td>
          <td class="text-xs-left">{{ props.item.gteSix_total }}</td>
        </template>
        <v-alert
          slot="no-results"
          :value="true"
          color="error"
        >Your search for "{{ search }}" found no results.</v-alert>
      </v-data-table>
    </v-card>
  </template>
  
  <script>
  export default {
      name: "KaikkiPelaajat",
      data: function() {
          return {
              search: '',
              sortBy: 'rounds_total',
              sortDesc: false,
              isCaptain: false,
              headers: [
                  { text: 'Nimi', value: 'player_name', align: 'left'},
                  { text: 'Kaudet', value: 'season_count', align: 'left'},
                  { text: 'Erät', value: 'all_rounds_total', align: 'left'},
                  { text: 'Poistot', value: 'all_score_total', width: '1%', align: 'left' },
                  { text: 'Heitot', value: 'all_throws_total', align: 'left'},
                  { text: 'KPH', value: 'total_average_throw', align: 'left'},
                  { text: 'kHP', value: 'total_average_throw_turn', align: 'left'},
                  { text: 'H', value: 'all_pikes_total', align: 'left'},
                  { text: 'H%', value: 'total_pike_percentage', align: 'left' },
                  { text: 'VM',value: 'all_zeros_total', align: 'left'},
                  { text: 'VM%',value: 'total_zero_percentage', align: 'left'},
                  { text: 'JK',value: 'all_gteSix_total', align: 'left'}
              ],
              players: [],
              selected: []
          };
      },
      methods: {
          getPlayers: function() {
              this.$http.get('api/tilasto_autismi').then(
                  function(data) {
                      this.players = data.body;
                  }
              );
          },
          handleRedirect: function(value) {
              location.href = '/pelaaja/'+value.id;
          },
          custSort(items, index, isDescending) {
            function d(p1) {
              switch (p1) {
                case 'NaN':
                  return -2
                default:
                  return p1
              }
            }
  
            items.sort((a,b) => {
              var a1 = d(a[index[0]])
              var b1 = d(b[index[0]])
              if (!isDescending[0]) {
                  return a1 < b1 ? 1 : a1 === b1 ? 0 : -1
              } else {
                  return a1 < b1 ? -1 : a1 === b1 ? 0 : 1
              }
            })
            return items
          }
      },
      mounted: function() {
          this.getPlayers();
      }
  };
  </script>
  <style scoped>
  
  tbody tr :hover {
      cursor: unset;
  }
  
  </style>
  
  