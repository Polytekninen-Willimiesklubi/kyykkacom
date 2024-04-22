<template>
  <v-layout>
    <div class="d-flex">
      <v-card>
        <v-card-title>
          <v-row>
            <v-col cols="12">
              Ottelut
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="4">
              <v-select 
                v-model="matchStore.selection"
                color="red" 
                :items="selectionOptions" 
              />
            </v-col>
            <v-spacer />
            <v-col cols="4">
              <v-text-field 
                color="red" 
                v-model="search" 
                label="Search" 
                single-line 
                hide-details 
              />
            </v-col>
          </v-row>
        </v-card-title>
        <!-- Todo: Loading -->
        <v-data-table
          mobile-breakpoint="0"
          :headers="matchStore.selection !== 'Jatkosarja' 
            ? headers : postHeaders"
          :items="matchStore.selectedMatches"
          :search="search"
          @click:row="handleRedirect"
          :item-class="itemRowBackground"
          no-data-text="Ei dataa :("
          :group-by="matchStore.selection !== 'Jatkosarja' 
           ? [] : ['seriers']"
        >
        <template v-slot:[`item.match_time`]="{ item }">
          <span>{{ date.formatByString(date.date(item.match_time), 'yyyy-MM-dd HH:mm') }}</span>
          <v-icon 
            color="gray" 
            class="mr-3"
            icon="info"
          >
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
            <v-icon :icon="isOpen ? 'mdi-minus' : 'mdi-plus'"/>
            {{ items[0].type_name }}
            {{ items[0].home_team.current_abbreviation}} vs. {{ items[0].away_team.current_abbreviation }}
          </th>
        </template>
        </v-data-table>
      </v-card>
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
  { title: 'Aika', key: 'match_time', width: '20%', align: 'left'},
  { title: 'Tyyppi', key: 'type_name', width: '10%', align: 'center' },
  { title: 'Kenttä', key: 'field', width: '1%', align: 'center' },
  { title: 'Koti', key: 'home_team.current_abbreviation', align: 'center' },
  { title: 'Vieras', key: 'away_team.current_abbreviation', align: 'center' },
  { title: '', key: 'home_score_total', width: '3%', align: 'center' },
  { title: 'Tulos', key: 'dash', width: '1%', sortable: false, align: 'center' },
  { title: '', key: 'away_score_total', width: '3%', align: 'center' }
];

const postHeaders =  [
  { title: 'Aika', key: 'match_time', align: 'left' },
  { title: 'Kenttä', key: 'field', aling: 'center' },
  { title: 'Koti', key: 'home_team.current_abbreviation' },
  { title: 'Vieras', key: 'away_team.current_abbreviation' },
  { title: '', key: 'home_score_total', width: '3%', align: 'right' },
  { title: 'Tulos', key: 'dash', width: '1%', sortable: false, align: 'center' },
  { title: '', key: 'away_score_total', width: '3%', align: 'left' }
];

const selectionOptions = ['Kaikki ottelut', 'Runkosarja', 'Jatkosarja', 'SuperWeekend'];

function itemRowBackground(item) {
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
