<template>
  <v-card :title="title">
    <v-row v-for="(listItem, index) in teams" :key="index">
      <v-col>
        <v-card-subtitle v-if="no_brackets > 1">
          <b> Lohko {{ String.fromCharCode(65+index) }} </b>
        </v-card-subtitle>
        <v-divider />
        <!-- note on :items="[...listItem]" here we make reduntant array just unpack it immediately,
          because otherwise returns an 'expected an array' error. This might be caused by listItem
          not being defined before the mouting happens (?) -->
        <!-- v-model:sort-by="sortBy" TODO 
        v-model:sort-desc="sortDesc"
        v-model:sort-by="sortingType"
        v-model:sort-desc="sortingDesc"
        -->
        <v-data-table
          mobile-breakpoint="0"
          class="sidebar"
          @click:row="handleRedirect"
          :headers="headers"
          :items="[...listItem]"
          :sort-by="[{key: 'points_total', order:'desc'}]"
          no-data-text="Ei dataa :("
          items-per-page="-1"
          density="compact"
        >
          <template #headers="{ columns }">
            <tr>
              <template v-for="column in columns" :key="column.key">
                <th class="v-data-table__td v-data-table__th">
                  <div class="v-data-table-header__content">
                    <span :style="column.title === 'P' ? 'font-weight:bold' : ''">
                      {{ column.title }}
                    </span>
                  </div>
                  <v-tooltip v-if="column.tooltip !== undefined"
                    activator="parent"
                    location="bottom"
                  >
                    {{ column.tooltip }}
                  </v-tooltip>
                </th>
              </template>
            </tr>
          </template>
          <template #item = "{ item, index }">
            <tr
              class="v-data-table__tr v-data-table__tr"
              :class="{'first-border': isFirst(index), 'second-border' : isSecond(index)}"
            >
              <td> {{ item.current_abbreviation }}</td>
              <td> {{ item.matches_played }}</td>
              <td> {{ item.matches_won }}</td>
              <td> {{ item.matches_tie }}</td>
              <td> {{ item.matches_lost }}</td>
              <td style='font-weight:bold'> {{ item.points_total }}</td>
              <td> {{ item.points_average }}</td>
              <td> {{ item.match_average }}</td>
            </tr>
          </template>
          <template #bottom></template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-divider v-if="no_brackets > 1" />
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
      default () {
        return [
          { title: 'Joukkue', key: 'current_abbreviation',  sortable: false },
          { title: 'O',       key: 'matches_played',        sortable: false,  tooltip: "Pelatut Ottelut"},
          { title: 'V',       key: 'matches_won',           sortable: false,  tooltip: "Voitot"},
          { title: 'T',       key: 'matches_tie',           sortable: false,  tooltip: "Tasapelit"},
          { title: 'H',       key: 'matches_lost',          sortable: false,  tooltip: "Häviöt"},
          { title: 'P',       key: 'points_total',          sortable: false,  tooltip: "Pisteet"},
          { title: 'P/O',     key: 'points_average',        sortable: false,  tooltip: "Pistettä per Ottelu "},
          { title: 'OKA',     key: 'match_average',         sortable: false,  tooltip: "Ottelu keskiarvo"}
        ]
      }
    },
    sortBy: {
      type: String,
      default: 'points_total'
    },
    sortDesc: {
      type: Boolean,
      default: true
    },
    super: {
      type: Boolean,
      default: false
    },
    no_brackets: { // This is expected if defaultData is False
      type: Number,
      default: 1
    },
    nonDefaultTeams: Array,
    teams: Array,
    lines: Array,

  },
  data () {
    return {
      sortingType: 'points_total',
      sortingDesc: false,
      season: false,
      multible_brackets: false,
      data: [],
      // teams: []
    }
  },
  methods: {
    handleRedirect (value, row) {
      location.href = '/joukkueet/' + row.item.id
    },
    isFirst(val) {
      if (this.lines.length === 0) return false;
      const index = this.no_brackets > 1 ? 1 : 0;
      return this.lines.length > 1 && this.lines[index][0] === val
    },
    isSecond(val) {
      if (this.lines.length === 0) return false;
      const index = this.no_brackets > 1 ? 1 : 0;
      return this.lines.length === 1 && this.lines[index][0] === val ||
            this.lines.length === 2 && this.lines[index][1] === val
    }
  }
  // watch: {
  //   nonDefaultTeams () {
  //     if (this.no_brackets > 1) {
  //       this.multible_brackets = true
  //       for (let i = 0; i < this.no_brackets; i++) {
  //         this.teams.push([])
  //       }
  //       const attr_string = this.super ? 'super_weekend_bracket' : 'bracket'
  //       this.nonDefaultTeams.forEach(ele => {
  //         this.teams[ele[attr_string] - 1].push(ele)
  //       }, this)
  //     } else {
  //       this.teams = [this.nonDefaultTeams]
  //       this.multible_brackets = false
  //     }
  //   }
  // }
}
</script>

<style>

.first-border {
  border-bottom: 0.15rem dashed red !important;
}

.second-border {
  border-bottom: 0.2rem double red !important;
}

.sidebar div {
  text-align: center;
}

.sidebar .v-data-table-header__content {
  display: grid; /* Hack to get to make header center align. 'text-align' don't work*/
}

</style>
