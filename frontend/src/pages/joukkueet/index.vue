<template>
  <v-layout>
    <div class="d-flex auto">
      <v-card>
        <v-card-title>
          Joukkueet
          <v-row>
            <v-spacer />
            <v-col cols="4">
              <v-text-field 
                color="red" 
                v-model="search" 
                label="Etsi" 
                single-line 
              />
            </v-col>
          </v-row>
        </v-card-title>
        <v-data-table
          mobile-breakpoint="0"
          density='compact'
          @click:row="handleRedirect"
          color='alert'
          :headers="headers"
          :search="search"
          :items="teamStore.allTeams"
          :loading="teamStore.loading"
          no-data-text="Ei dataa :("
          items-per-page="-1"
        >
          <template #bottom></template>
        </v-data-table>
      </v-card>
    </div>
  </v-layout>
</template>

<script setup>
import { useTeamsStore } from '@/stores/teams.store';

const teamStore = useTeamsStore();

const search = ref('');
const headers = [
  { title: 'Nimi', key: 'current_name', align: 'center' },
  { title: 'Lyhenne', key: 'current_abbreviation', align: 'center' },
  { title: 'Ottelut', key: 'matches_played', align: 'center' },
  { title: 'Voitot', key: 'matches_won', align: 'center' },
  { title: 'Häviöt', key: 'matches_lost', align: 'center' },
  { title: 'Tasurit', key: 'matches_tie', align: 'center' },
  { title: 'Ottelu Ka', key: 'match_average', align: 'center' }
];

function handleRedirect(value, row) {
  location.href = '/joukkueet/' + row.item.id;
}

</script>
