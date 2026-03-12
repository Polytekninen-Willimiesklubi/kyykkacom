<template>
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
        :mobile-breakpoint="0"
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
        <template #item.current_name = "{ item }">
          <v-row>
            <v-spacer />
            <v-col cols="9">
              <span>{{ item.current_name }}</span>
            </v-col>
            <v-col>
              <v-row class="justify-start">
                <template v-for="accolade in teamStore.seasonTeamAccolades[item.id]">
                  <v-col cols="3">
                    <accolade-icon :filename="accolade.icon">
                      <v-tooltip
                         activator='parent'
                         :text="accolade?.name + ' ' + accolade.placement + '. Sija'"
                         location="right"
                       />
                    </accolade-icon>
                  </v-col>
                </template>
                <v-spacer />
              </v-row>
            </v-col>
          </v-row>
        </template>
        <template #bottom></template>
      </v-data-table>
    </v-card>
  </div>
</template>

<route lang="yaml">
  meta:
      layout: "withoutSidebar"
</route>

<script setup>
import { useTeamsStore } from '@/stores/teams.store';
import { headersTeams } from '@/stores/headers';

const teamStore = useTeamsStore();

const search = ref('');


function handleRedirect(value, row) {
  location.href = '/joukkueet/' + row.item.team_id;
}

</script>
