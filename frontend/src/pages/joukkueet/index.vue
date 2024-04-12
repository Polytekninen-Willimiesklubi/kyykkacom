<template>
  <v-layout>
    <div class="d-flex auto">
      <v-card
        title="Joukkueet"
      >
        <v-spacer />
        <v-text-field 
          color="red" 
          v-model="search" 
          label="Etsi" 
          single-line 
          hide-details
        ></v-text-field>
        <v-data-table 
          mobile-breakpoint="0"
          @click:row="handleRedirect"
          color='alert'
          :headers="headers"
          :search="search"
          :items="homeStore.allTeams"
          :loading="homeStore.loading"
          no-data-text="Ei dataa :("
          disable-pagination
          hide-default-footer
          dense
        >
        </v-data-table>
      </v-card>
    </div>
  </v-layout>
</template>

<script setup>
import { useHomeStore } from '@/stores/home.store';
import { ref } from 'vue';

const homeStore = useHomeStore();

const search = ref('');
const headers = [
  { text: 'Nimi', value: 'current_name', align: 'center' },
  { text: 'Lyhenne', value: 'current_abbreviation' },
  { text: 'Ottelut', value: 'matches_played' },
  { text: 'Voitot', value: 'matches_won' },
  { text: 'Häviöt', value: 'matches_lost' },
  { text: 'Tasurit', value: 'matches_tie' },
  { text: 'Ottelu Ka', value: 'match_average' }
]

function handleRedirect(value) {
  location.href = '/joukkue/' + value.id
}

</script>
