<template>
  <v-layout class="pt-5" align="center">
    <div class="flex-1-1-100">
      <v-card>
        <v-card-title>
          Joukkueet
          <v-row>
            <v-col cols="4">
              <v-text-field 
              color="red" 
              v-model="search" 
              label="Etsi" 
              single-line 
              />
            </v-col>
            <v-spacer />
          </v-row>
        </v-card-title>
        <v-data-table
          mobile-breakpoint="0"
          density='compact'
          @click:row="handleRedirect"
          color='alert'
          :headers="headersTeams"
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
<route>
{
  meta: {
    layout: "withoutSidebar"
  }
}
</route>
<script setup>
import { useTeamsStore } from '@/stores/teams.store';
import { headersTeams } from '@/stores/headers';

const teamStore = useTeamsStore();

const search = ref('');


function handleRedirect(value, row) {
  location.href = '/joukkueet/' + row.item.id;
}

</script>
