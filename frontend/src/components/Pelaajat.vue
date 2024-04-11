<template>
  <v-card>
    <v-card-title>
      Pelaajat
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
      <template v-slot:no-data>
        <v-progress-linear color="red" slot="progress" indeterminate></v-progress-linear>
      </template>
      <template
        bind:key="props.item.id"
        v-slot:items="props"

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
      <template v-slot:no-results>
<v-alert

        :value="true"
        color="error"
      >Your search for "{{ search }}" found no results.</v-alert>
</template>
    </v-data-table>
  </v-card>
</template>

<script>
export default {
  data () {
    return {
      search: '',
      sortBy: 'rounds_total',
      sortDesc: false,
      isCaptain: false,
      headers: [
        {
          text: 'Nimi',
          value: 'player_name',
          align: 'left'
        },
        {
          text: 'Joukkue',
          value: 'team.current_abbreviation',
          align: 'left'
        },
        {
          text: 'E',
          value: 'rounds_total',
          align: 'left'
        },
        { text: 'P', value: 'score_total', width: '1%', align: 'left' },
        {
          text: 'PPH',
          value: 'score_per_throw',
          align: 'left'
        },
        {
          text: 'SP',
          value: 'scaled_points',
          align: 'left'
        },
        {
          text: 'SPH',
          value: 'scaled_points_per_throw',
          align: 'left'
        },
        {
          text: 'kHP',
          value: 'avg_throw_turn',
          align: 'left'
        },
        { text: 'H', value: 'pikes_total', align: 'left' },
        {
          text: 'H%',
          value: 'pike_percentage',
          align: 'left'
        },
        {
          text: 'VM',
          value: 'zeros_total',
          align: 'left'
        },
        {
          text: 'JK',
          value: 'gteSix_total',
          align: 'left'
        }
      ],
      players: [],
      selected: []
    }
  },
  methods: {
    getPlayers () {
      this.$http.get('api/players/' + '?season=' + sessionStorage.season_id).then(
        function (data) {
          this.players = data.body
        }
      )
    },
    handleRedirect (value) {
      location.href = '/pelaaja/' + value.id
    },
    custSort (items, index, isDescending) {
      function d (p1) {
        switch (p1) {
          case 'NaN':
            return -2
          default:
            return p1
        }
      }

      items.sort((a, b) => {
        const a1 = d(a[index[0]])
        const b1 = d(b[index[0]])
        if (!isDescending[0]) {
          return a1 < b1 ? 1 : a1 === b1 ? 0 : -1
        } else {
          return a1 < b1 ? -1 : a1 === b1 ? 0 : 1
        }
      })
      return items
    }
  },
  mounted () {
    this.getPlayers()
  }
}
</script>
<style scoped>

tbody tr :hover {
    cursor: unset;
}

</style>
