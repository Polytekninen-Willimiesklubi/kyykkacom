<template>
  <v-layout>
    <div class="flex-1-1-100">
      <v-card elevation="1">
        <v-tabs fixed-tabs color="red" v-model='tab'>
          <v-tab :value="0">Runkosarja</v-tab>
          <v-tab :value="1">SuperWeekend</v-tab>
        </v-tabs>
        <v-divider />
        <v-window v-model="tab">
          <v-window-item
            :key="0"
            :value="0"
          >
            <h2 class="pl-10">Ratkaise Runkosarja</h2>
            <v-row>
              <v-col 
                v-for="(listItem, index) in adminStore.regularSeasonTeams" 
                :key="index" 
                cols="4"
              >
                <v-card 
                  class="ml-10" 
                  elevated 
                  width="300px"
                >
                  <v-card-title>Lohko {{ String.fromCharCode(65+index) }} </v-card-title>
                  <v-divider />
                  <draggable
                    class="list-group"
                    :list="listItem"
                    style="padding: 1em;"
                    item-key="current_abbreviation"
                  >
                    <template #item="{ element, index }">
                      <div style="border: solid; margin-bottom: 2px; border-width: 2px;">
                        {{ index+1 }}. {{ element.current_abbreviation }}
                      </div>
                    </template>
                  </draggable>
                </v-card>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="3">
                <v-card class="pl-2 ml-10">
                  <h3 class="pl-2">Runkosarja Voittaja</h3>
                  <v-select class="ma-2" width="300px"
                    label="Valitse"
                    placeholder="Select winner team"
                    v-model="selectValue"
                    :items="teamStore.allTeams"
                    item-title="current_abbreviation"
                    return-object
                  />
                </v-card>
              </v-col>
            </v-row>
            <v-btn 
              class="ma-4 ml-10" 
              @click="validateResult(true)" 
              color="x-large error"
              text="Vahvista Runkosarjan tulos"  
            />
            <v-btn 
              class="ma-4 ml-10" 
              @click="validateWinner" 
              color="x-large error"
              text="Vahvista Runkosarjan Voittaja"
            />
          </v-window-item>
          <v-window-item
            :key="1"
            :value="1"
          >
            <v-tabs fixed-tabs color="black" v-model='subTab'>
              <v-tab :value="0">Joukkueet Lohkoihin</v-tab>
              <v-tab :value="1">Syötä Otteluita</v-tab>
              <v-tab :value="2">Ratkaise Lohkot</v-tab>
              <v-tab :value="3">Seedaa Joukkueet</v-tab>
              <v-tab :value="4">Ratkaise Voittaja</v-tab>
            </v-tabs>
            <v-divider class="mb-2"/>
            <v-window v-model="subTab">
              <v-window-item
                :key="0"
                :value="0"
              >
                <h2 class="pl-10">Laita joukkueet Superin lohkoihin</h2>
                <v-row>
                  <v-col cols="3">
                    <v-card class="ml-10" elevated width="300px">
                      <v-card-title>Ei lohkoissa</v-card-title>
                      <v-divider />
                      <draggable
                        class="list-group"
                        group="people"
                        :list="adminStore.notInSuper"
                        style="padding: 1em;"
                        item-key="current_abbreviation"
                      >
                        <template #item="{ element }">
                          <div
                            class="list-group-item"
                            style="border: solid; margin-bottom: 2px; border-width: 2px;"
                          >
                            {{ element.current_abbreviation }}
                          </div>
                        </template>
                      </draggable>

                    </v-card>
                  </v-col>
                  <v-col cols="9">
                    <v-row>
                      <v-col v-for="(listItem, index) in adminStore.superWeekendTeams" :key="index" :cols="4">
                        <v-card class="ml-10" elevated width="300px">
                          <v-card-title>Lohko {{ String.fromCharCode(65+index) }} </v-card-title>
                          <v-divider />
                          <draggable
                            class="list-group"
                            group="people"
                            :list="listItem"
                            style="padding: 1em;"
                            item-key="current_abbreviation"
                          >
                            <template #item="{ element }">
                              <div
                                class="list-group-item"
                                style="border: solid; margin-bottom: 2px; border-width: 2px;"
                              >
                                {{ element.current_abbreviation }}
                              </div>
                            </template>
                          </draggable>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-col>
                </v-row>
                <v-btn
                  class="ma-4 ml-10"
                  @click="validateBrackets"
                  text="Vahvista Superin lohkot"
                  color="error x-large"
                />
              </v-window-item>
              <v-window-item
                :key="1"
                :value="1"
              >
                <h2 class="pl-10 pb-2">Syötä Superin otteluita</h2>
                <v-form ref='matchSubmit' v-model="submitValid" @submit.prevent="submit" lazy-validation>
                  <v-row>
                    <v-col cols="3">
                      <v-select 
                        class="ma-2" 
                        width="300px"
                        label="Valitse pelityyppi"
                        v-model="selectGameType"
                        :rules="[v => !!v || 'Valitse pelityyppi!']"
                        :items="gameTypes"
                        item-title="name"
                        return-object
                        outlined
                      />
                    </v-col>
                    <v-col cols="1">
                      <v-select 
                        class="ma-2"
                        :items="Array.from(Array(10).keys())"
                        v-model="field"
                        abel="Kenttä"
                      />
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="2">
                      <v-menu
                        v-model="menu"
                        :close-on-content-click="false"
                      >
                        <template #activator="{ props: activatorProps }">
                          <v-combobox
                            v-model="selectDate"
                            label="Pelipäivä"
                            prepend-icon="mdi-calendar"
                            readonly
                            v-bind="activatorProps"
                          />
                        </template>
                        <v-date-picker
                          v-model="selectDate"
                          @update:model-value="menu=!menu, selectDate=String(selectDate).split('T')[0]"
                        />
                      </v-menu>
                    </v-col>
                    <v-col cols="2">
                      <v-menu
                        v-model="menuTime"
                        :close-on-content-click="false"
                      >
                        <template #activator="{ props: activatorProps }">
                          <v-combobox
                            v-model="selectTime"
                            label="Peliaika"
                            prepend-icon="mdi-clock"
                            readonly
                            v-bind="activatorProps"
                          />
                        </template>
                        <v-time-picker
                          v-model="selectTime"
                          no-title
                          format="24hr"
                          scrollable
                          color="red"
                          :allowedMinutes="v => !(v % 5)"
                          @update:model-value="menuTime=!menuTime"
                        />
                      </v-menu>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="2">
                      <v-select 
                        class="ma-2"
                        width="300px"
                        label="Valitse kotijoukkue"
                        v-model="homeSelect"
                        :rules="[v => !!v || 'Valitse Joukkue!']"
                        :items="adminStore.superWeekendTeams.flat()"
                        item-title="current_abbreviation"
                        return-object
                        outlined
                      />
                    </v-col>
                    <v-col cols="2">
                      <v-select
                        class="ma-2"
                        width="300px"
                        label="Valitse vierasjoukkue"
                        v-model="awaySelect"
                        :rules="[v => !!v || 'Valitse Joukkue!']"
                        :items="adminStore.superWeekendTeams.flat()"
                        item-title="current_abbreviation"
                        return-object
                        outlined
                      />
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="2">
                      <v-text-field 
                        class="ma-2"
                        v-model='homeScore'
                        :rules="checkScoreRules"
                        label="Koti joukkueen tulos"
                        required
                        outlined
                      />
                    </v-col>
                    <v-col cols="2">
                      <v-text-field 
                        class="ma-2"
                        v-model='awayScore'
                        :rules="checkScoreRules"
                        label="Vieras joukkueen tulos"
                        required
                        outlined
                      />
                    </v-col>
                  </v-row>
                  <v-btn 
                    type="submit" 
                    class="ma-2"
                    text="Syötä tulos"
                    color="error"
                  />
                </v-form>
              </v-window-item>
              <v-window-item
                :key="2"
                :value="2"
              >
                <h2 class="pl-10">Ratkaise Superin Lohkot</h2>
                <v-row>
                  <v-col v-for="(listItem, index) in adminStore.superWeekendTeams" :key="index" :cols="3">
                    <v-card 
                      class="ml-10" 
                      elevated
                      width="300px"
                    >
                      <v-card-title>Lohko {{ String.fromCharCode(65+index) }} </v-card-title>
                      <v-divider />
                      <draggable
                        class="list-group"
                        :list="listItem"
                        style="padding: 1em;"
                        item-key="current_abbreviation"
                      >
                        <template #item="{ element, index }">
                          <v-row style="border: solid; margin-bottom: 2px; border-width: 2px;">
                            <v-col align="left" cols="6"> {{ index+1 }}. {{ element.current_abbreviation }} </v-col>
                            <v-col align="right" cols="6">(OKa: {{ element.match_average }})</v-col>
                          </v-row>
                        </template>
                      </draggable>
                    </v-card>
                  </v-col>
                </v-row>
                <v-btn
                  class="ma-4 ml-10 x-large"
                  @click="validateResult(false)"
                  text="Vahvista Superin lohko sijoitukset"
                  color="error"
                />
              </v-window-item>
              <v-window-item
                :key="3"
                :value="3"
              >
                <h2 class="pl-10">Seedaa Superin jatkosarja</h2>
                <h3 class="pl-10 pt-3">HUOM! Tarkista seedaus numero formaatista (Kysy Totilta :D)</h3>
                <h3 class="pl-10 pt-1">Vain playoff seedauksella on väliä, eli ne jotka jää ulkopuolella voi olla miten lystää.</h3>
                <v-card class="ml-10" elevated width="400px">
                  <draggable
                    class="list-group"
                    :list="adminStore.flattenSuperTeams"
                    style="padding: 1em;"
                    item-key="current_abbreviation"
                  >
                    <template #item="{ element, index }">                
                      <v-row style="border: solid; margin-bottom: 2px; border-width: 2px;">
                        <v-col align="left" cols="6"> {{ index+1 }}. {{ element.current_abbreviation }} </v-col>
                        <v-col align="right" cols="6"> (Sij. {{ element.super_weekend_bracket_placement }}) (OKa: {{ element.match_average }})</v-col>
                      </v-row>
                    </template>
                  </draggable>
                </v-card>
                <v-btn
                  class="ma-4 ml-10 x-large"
                  @click="validateSeeds"
                  text="Vahvista Superin Seedit"
                  color="error"
                />
              </v-window-item>
              <v-window-item
                :key="4"
                :value="4"
              >
                <h2 class="pl-10">Valitse SuperWeekend voittaja</h2>
                <h3 class="pl-10 pt-3">Toistaiseksi automatiikka ei toimi, että finaalin tuloksen laitettua Superin tulisi tallennettua. Näin voittaja erikseen merkataan muistiin, vaikka superweekend turnaustaulussa voittaja näkyisikin</h3>
                <v-form 
                  v-model="submitValid"
                  ref='superwinnerValid'
                  @submit.prevent="validateSuperWinner"
                  lazy-validation
                >
                  <v-row>
                    <v-col cols="3">
                      <v-select 
                        class="ma-4"
                        label="Valitse Superin voittaja"
                        v-model="superWinnerSelected"
                        :items="adminStore.superWeekendTeams.flat()"
                        item-title="current_abbreviation"
                        required
                        return-object
                        outlined
                      />
                    </v-col>
                  </v-row>
                  <v-btn
                    class="ma-8 x-large"
                    type="submit"
                    text="Vahvista Superin Voittaja"
                    color="error"
                  />
                </v-form>
              </v-window-item>
            </v-window>
          </v-window-item>
        </v-window>
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
import draggable from 'vuedraggable';

import { useTeamsStore } from '@/stores/teams.store';
import { useSuperStore } from '@/stores/superweekend.store';
import { useAdminStore, gameTypes, checkScoreRules } from '@/stores/admin.store';
import { useNavBarStore } from '@/stores/navbar.store';

const teamStore = useTeamsStore();
const superStore = useSuperStore();
const adminStore = useAdminStore();
const navStore = useNavBarStore();

adminStore.getData();
// teamStore.getTeams();
// superStore.getAllData();

const dragging = ref(false);

const selectGameType = ref(null);
const awayScore = ref(null);
const homeScore = ref(null);
const selectDate = ref(null);
const selectTime = ref(false);
const field = ref(null);
const homeSelect = ref(null);
const awaySelect = ref(null);
const selectValue = ref(null);

const tab = ref(null);
const subTab = ref(null);
const menu = ref(false);
const menuTime = ref(null);
const superWinnerSelected = ref(null);
const superWinnerValid = ref(true);
const submitValid = ref(true);

/*  Clock and date initialization  */
const date = new Date();
const day = date.getDate();
let month = date.getMonth() + 1;
month = Number(month) >= 10 ? month : '0' + month;
const year = Number(date.getFullYear())
const hour = date.getHours()
const minute = Number(date.getMinutes()) % 30 ? '30' : '00'

selectDate.value = `${year}-${month}-${day}` // Current date
selectTime.value = `${hour}:${minute}` // Current Time to nearest 30min

/* Event functions i.e. button functionality */
function validateResult(type) {
  if (!confirm('Oletko tyytyväinen tuloksiin?')) return;
  const teams = type ? adminStore.regularSeasonTeams : adminStore.superWeekendTeams 
  const dataKey = type ? 'bracket_placement' : 'super_weekend_bracket_placement';
  teams.forEach(bracket => bracket.forEach(team => {
    let postData = {}
    postData[dataKey] = team.order
    adminStore.patchTeamData(postData, team.id)
  }))
}

function validateSeeds() {
  if (!confirm('Oletko tyytyväinen tuloksiin?')) return;
  adminStore.superWeekendTeams.flat().forEach(team => {
    let postData = {super_weekend_playoff_seed : team.order}
    adminStore.patchTeamData(postData, team.id)
  })
}

function validateWinner() {
  if (selectValue.value.id === undefined) return
  if (!confirm('Oletko tyytyväinen runkosarjan voittajaan?')) return
  adminStore.patchTeamData({bracket_placement : 0}, selectValue.value.id)
}

function validateBrackets() {
  if (!confirm('Oletko tyytyväinen Superin lohkoihin?')) return 
  adminStore.superWeekendTeams.forEach((bracket, index) => {
    bracket.forEach((team) => {
      let postData = { super_weekend_bracket: index + 1 }
      adminStore.patchTeamData(postData, team.id)
    }, index)
  });
  adminStore.notInSuper.forEach(team => {
    let postData = { super_weekend_bracket: null }
    adminStore.patchTeamData(postData, team.id)
  });
}

async function validateSuperWinner() {
  await this.$refs.superwinnerValid.validate()
  if (!confirm('Oletko tyytyväinen Superin voittajaan?')) return;
  if (!superWinnerValid.value || !superStore.superId) return;
  const postData = { winner: this.superWinnerSelected.id }
  adminStore.patchSuperTeamWinner(postData, superStore.superId)
}

async function submit() {
  await this.$refs.matchSubmit.validate()
  if (!submitValid.value) return
  const postData = {
    season                : navStore.seasonId,
    field                 : field.value,
    match_time            : selectDate.value + ' ' + selectTime.value + ':00',
    home_first_round_score: homeScore.value,
    home_second_round_score: 0,
    away_first_round_score: awayScore.value,
    away_second_round_score: 0,
    home_team             : homeSelect.value.id,
    away_team             : awaySelect.value.id,
    is_validated          : true,
    match_type            : selectGameType.value,
    post_season           : 0,
    seriers               : 0,
  }

  superStore.postMatch(postData)
}
</script>