<template>
  <v-layout>
    <div class="d-flex">
      <v-card>
        <v-card-title class="d-flex flex-wrap-reverse">
          <div>
            Ottelut
            <v-select 
              v-model="matchStore.selection"
              style="width: 50%" 
              color="red" 
              :items="selectionOptions" 
            />
          </div>
          <v-spacer />
          <div>
            <v-text-field color="red" 
            v-model="search" 
            label="Search" 
            single-line 
            hide-details 
            />
          </div>
        </v-card-title>
        <!-- Todo: Loading -->
        <v-data-table
          :headers="matchStore.selection !== 'Jatkosarja' 
            ? headers : postHeaders"
          :items="matchStore.selectedMatches"
          :search="search"
          @click:row="handleRedirect"
          :item-class="itemRowBackground"
          no-data-text="Ei dataa :("
          :group-by="matchStore.selection !== 'Jatkosarja' 
           ? [] : ['seriers']"
          mobile-breakpoint="0"
          hide-default-footer
          disable-pagination
          dense
        >
        <template v-slot:headers class="text-xs-center" />
        <!-- [``] needed to prevent eslint error -->
        <template v-slot:[`item.match_time`]="{ item }">
          <span>{{ date.formatByString(date.date(item.match_time), 'yyyy-MM-dd HH:mm') }}</span>
          <v-icon 
            color="gray" 
            class="mr-3">
            info
            <v-tooltip 
              activator='parent'
              text="Ottelu on validoimatta"
              bottom
              v-if="!item.is_validated & 
              (parseInt(item.home_team.id) === parseInt(authStore.teamId) 
              || parseInt(item.away_team.id) === parseInt(authStore.teamId))" 
            />

          </v-icon>
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
    </div>
    <div xs4 class="d-flex pl-3 hidden-md-and-down">
      <!-- <side-bar
        :no_brackets="no_brackets"
        :non-default-teams="teams"
      /> -->
    </div>
  </v-layout>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.store';
import { useMatchesStore } from '@/stores/matches.store';
import { useDate } from 'vuetify';

const search = ref('');

const authStore = useAuthStore();
const matchStore = useMatchesStore();
const date = useDate();

const headers = [
  {
    text: 'Aika',
    align: 'left',
    width: '20%',
    value: 'match_time'
  },
  { text: 'Tyyppi', value: 'type_name', width: '10%' },
  { text: 'Kenttä', value: 'field', width: '15%', align: 'left' },
  { text: 'Koti', value: 'home_team.current_abbreviation' },
  { text: 'Vieras', value: 'away_team.current_abbreviation' },
  { text: '', value: 'home_score_total', width: '3%', align: 'right' },
  { text: 'Tulos', value: 'dash', width: '1%', sortable: false, align: 'center' },
  { text: '', value: 'away_score_total', width: '3%', align: 'left' }
];

const postHeaders =  [
  {
    text: 'Aika',
    align: 'left',
    value: 'match_time'
  },
  { text: 'Kenttä', value: 'field' },
  { text: 'Koti', value: 'home_team.current_abbreviation' },
  { text: 'Vieras', value: 'away_team.current_abbreviation' },
  { text: '', value: 'home_score_total', width: '3%', align: 'right' },
  { text: 'Tulos', value: 'dash', width: '1%', sortable: false, align: 'center' },
  { text: '', value: 'away_score_total', width: '3%', align: 'left' }
];

const selectionOptions = ['Kaikki ottelut', 'Runkosarja', 'Jatkosarja', 'SuperWeekend'];

function  itemRowBackground (item) {
  // Handles the backround color of row items
  const matchDate = moment(item.match_time).format('YYYY-MM-DD HH:MM')
  const currentTime = moment(Date.now()).format('YYYY-MM-DD HH:MM')

  if (!this.team_id) {
    return
  }

  return !item.is_validated & matchDate < currentTime 
    & (
      parseInt(item.home_team.id) === parseInt(this.team_id) 
      || parseInt(item.away_team.id) === parseInt(this.team_id)
    )
    ? 'row__background__style_1' : 'row__background__style_2';
}

function handleRedirect (value, row) {
  location.href = '/ottelut/' + row.item.id;
}

matchStore.getMatches();

</script>

<style>
.row__background__style_1 {
  background-color: rgba(195, 20, 20, 0.781) !important;
}

.row__background__style_2 {
  background-color: white;
}
</style>
