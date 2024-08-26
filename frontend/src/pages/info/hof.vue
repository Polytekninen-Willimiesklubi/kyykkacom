<template>
    <v-row>
        <v-col cols="12">            
            <v-tabs v-model="tab" align-tabs="center">
                <v-tab value="one">Kilpailut</v-tab>
                <v-tab value="two">Henkilölle myönnetyt</v-tab>
                <v-tab value="three">Palkinto info</v-tab>
            </v-tabs>
        </v-col>
        <v-col>
            <v-tabs-window v-model="tab">
                <v-tabs-window-item value="one">
                    <v-row>
                        <template v-for="table in tab_one_data">
                            <v-col :cols="table.cols">
                                <simple-table
                                    :title="table.title"
                                    :headers="headersHof.slice(...table.slice)"
                                    :items="table.data"
                                />
                            </v-col>
                        </template>
                    </v-row>
                </v-tabs-window-item>
                <v-tabs-window-item value="two">
                    <v-row>
                        <template v-for="table in tab_two_data">
                            <v-col cols="4">
                                <simple-table
                                    :title="table.title"
                                    :headers="headerHofPerson"
                                    :items="table.data"
                                />
                            </v-col>
                        </template>
                        <v-col cols="4">
                            <simple-table
                                title="Sekalaiset"
                                :headers="headerHofMisc"
                                :items="hof.misc"
                            />
                        </v-col>
                    </v-row>
                </v-tabs-window-item>
                <v-tabs-window-item value="three">
                    jotain
                    <!-- <v-row>
                        <v-col>
                            <simple-table
                                title="NKL Pariliiga"
                                :headers="[{title: 'Vuosi', key: 'year'}, {title: 'Nimi', key: 'name'}]"
                                :items="jaskanKarttu"
                            />
                        </v-col>
                    </v-row> -->
                </v-tabs-window-item>
            </v-tabs-window>
        </v-col>
    </v-row>

</template>
<route lang="yaml">
meta:
    layout: "withoutSidebar"
</route>

<script setup>
import { headersHof, headerHofPerson, headerHofMisc } from '@/stores/headers';
import { useHofStore } from '@/stores/hof.store';

const hof = useHofStore();

const tab_one_data = [
    {title: "Liiga mestaruus", cols: 5, slice: [undefined, undefined], data: hof.championship},
    {title: "SuperWeekend", cols: 4, slice: [0, 3], data: hof.superData},
    {title: "Runkosarjan Voittaja", cols: 3, slice: [0, 2], data: hof.bracketWinners},
    {title: "Henkkaricup", cols: 5, slice: [0, 3], data: hof.singleWinner},
    {title: "Parikyykkä liiga", cols: 4, slice: [0, 3], data: hof.pairWinners},
];

const tab_two_data = [
    {title: "Jaskan Karttu", data: hof.jaskanKarttu},
    {title: "KCK Ahti",  data: hof.KCKAhti},
    {title: "Haukikuningas/-tar",  data: hof.hauki},
    {title: "Vuoden Kyykkäjä/MVP",  data: hof.mvp},
    {title: "Runkosarjan Paras",  data: hof.bracketBest},
    {title: "Jatkosarjan Paras",  data: hof.playoffBest},
    {title: "Vuoden Viimeistelijä",  data: hof.last},
    {title: "Vuoden Tulokas",  data: hof.rookie},
    {title: "Vuoden mieskyykkääjä",  data: hof.man},
    {title: "Vuoden naiskyykkääjä",  data: hof.woman},
]



const tab = ref(null);

</script>