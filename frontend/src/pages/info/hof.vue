<template>
    <v-row>
        <v-col cols="12">            
            <v-tabs v-model="tab">
                <v-tab value="one">Kilpailut</v-tab>
                <v-tab value="two">Henkilölle myönnetyt</v-tab>
                <v-tab value="three">Palkinto info</v-tab>
            </v-tabs>
        </v-col>
        <v-col>
            <v-tabs-window v-model="tab">
                <v-tabs-window-item value="one">
                    <v-row>
                        <v-col cols="5">
                            <simple-table
                                title="Liiga mestaruus"
                                :headers="headersHof"
                                :items="data"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="SuperWeekend"
                                :headers="headersHof.slice(0,3)"
                                :items="superData"
                            />
                        </v-col>
                        <v-col cols="3">
                            <simple-table
                                title="Runkosarjan Voittaja"
                                :headers="headersHof.slice(0,2)"
                                :items="brackerWinners"
                            />
                        </v-col>
                        <v-col cols="5">
                            <simple-table
                                title="Henkkaricup"
                                :headers="headersHof.slice(0,3)"
                                :items="singleWinner"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="Parikyykkä liiga"
                                :headers="headersHof.slice(0,3)"
                                :items="pairWinners"
                            />
                        </v-col>
                    </v-row>
                </v-tabs-window-item>
                <v-tabs-window-item value="two">
                    <v-row>
                        <v-col cols="4">
                            <simple-table
                                title="Jaskan Karttu"
                                :headers="headerHofPerson"
                                :items="jaskanKarttu"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="KCK Ahti - Pysti"
                                :headers="headerHofPerson"
                                :items="KCKAhti"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="Haukikuningas/-tar"
                                :headers="headerHofPerson"
                                :items="hauki"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="Vuoden Kyykkäjä/MVP"
                                :headers="headerHofPerson"
                                :items="mvp"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="Vuoden Paras Jatkosarjassa"
                                :headers="headerHofPerson"
                                :items="playoffBest"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="Vuoden Paras Runkosarjassa"
                                :headers="headerHofPerson"
                                :items="bracketBest"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="Vuoden Viimeistelijä"
                                :headers="headerHofPerson"
                                :items="last"
                            />
                        </v-col>
                        <v-col cols="4">
                            <simple-table
                                title="Vuoden Tulokas"
                                :headers="headerHofPerson"
                                :items="rookie"
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
import { headersHof, headerHofPerson } from '@/stores/headers';

const data = [
    {'year': 2024, 'first' : 'Dra', 'second': 'MaHaLasku', 'third': 'SuLaKe', 'fourth': 'DiSKO'},
    {'year': 2023, 'first' : 'MaHaLasKu', 'second': 'SÄTKY KY', 'third': 'DiSKO', 'fourth': 'VSOP'},
    {'year': 2022, 'first' : 'Ei', 'second': 'MaHaLasKu', 'third': 'SÄTKY KY', 'fourth': 'LSP'},
    {'year': 2021, 'first' : '-', 'second': '-', 'third': '-', 'fourth': '-'},
    {'year': 2020, 'first' : 'Ei', 'second': 'Dra', 'third': 'SFS-6016', 'fourth': 'MaMut'},
    {'year': 2019, 'first' : 'Dra', 'second': 'SICK', 'third': 'LePi', 'fourth': 'SFS-6016'},
    {'year': 2018, 'first' : 'YÖK', 'second': 'Darts', 'third': 'Dra', 'fourth': 'HC RiceCows'},
    {'year': 2017, 'first' : 'Darts', 'second': 'YÖK', 'third': 'Dra', 'fourth': 'PkO'},
    {'year': 2016, 'first' : 'GPK', 'second': 'Dra', 'third': 'FC HR', 'fourth': 'KC SKP'},
    {'year': 2015, 'first' : 'GPK', 'second': 'HC RiceCows', 'third': 'PkO', 'fourth': 'Dra'},
    {'year': 2014, 'first' : 'ASS', 'second': 'GPK', 'third': 'Dra', 'fourth': 'Panis'},
    {'year': 2013, 'first' : 'ASS', 'second': 'GPK', 'third': 'Panis', 'fourth': 'PaVa'},
    {'year': 2012, 'first' : 'Ak-47', 'second': 'Dra', 'third': 'ASS', 'fourth': 'GPK'},
    {'year': 2011, 'first' : 'ASS', 'second': 'LMTVO', 'third': 'PaVa', 'fourth': 'La Sól'},
    {'year': 2010, 'first' : 'LMTVO', 'second': 'GPK', 'third': 'HeMi', 'fourth': 'MULK'},
    {'year': 2009, 'first' : 'LMTVO', 'second': 'GPK', 'third': 'MULK', 'fourth': 'HUMP'},
    {'year': 2008, 'first' : 'LMTVO', 'second': 'PKMM', 'third': 'VTTU', 'fourth': 'GPK'},
    {'year': 2007, 'first' : 'LMTVO', 'second': 'Dra', 'third': 'ITKK', 'fourth': 'GPK'},
    {'year': 2006, 'first' : 'Dra', 'second': 'ITKK', 'third': 'LMTVO', 'fourth': 'PKMM'},
    {'year': 2005, 'first' : 'LMTVO', 'second': 'Dra', 'third': 'ITKK', 'fourth': 'KCK'},
    {'year': 2004, 'first' : 'Dra', 'second': 'ITKK', 'third': 'LMTVO', 'fourth': 'PLEE'},
    {'year': 2003, 'first' : 'ITKK', 'second': 'LSD', 'third': 'Dra', 'fourth': 'PKMM'},
    {'year': 2002, 'first' : 'ITKK', 'second': 'LMTVO', 'third': 'KCK', 'fourth': 'PKMM'},
    {'year': 2001, 'first' : 'PKMM', 'second': 'TPNMP', 'third': 'SMS', 'fourth': 'ITKK99'},
    {'year': 2000, 'first' : 'ITKK99', 'second': 'KCK', 'third': 'SMS', 'fourth': 'TPNMP'},
    {'year': 1999, 'first' : 'TPNMP', 'second': '?', 'third': '?', 'fourth': '?'},
    {'year': 1998, 'first' : 'PKMM', 'second': '?', 'third': '?', 'fourth': '?'},
    {'year': 1997, 'first' : '?', 'second': '?', 'third': '?', 'fourth': '?'},
];

const superData = [
    {'year': 2024, 'first' : 'Dra', 'second' : 'VSOP' },
    {'year': 2023, 'first' : 'MaHaLasKu', 'second' : 'VSOP' },
    {'year': 2022, 'first' : 'MaHaLasKu', 'second' : "Ei" },
    {'year': 2021, 'first' : 'MaHaLasKu', 'second' : "Dra" },
    {'year': 2020, 'first' : 'Dra', 'second': "Darts (?)" },
    {'year': 2019, 'first' : 'Dra', 'second': "Darts" },
    {'year': 2018, 'first' : 'Darts', 'second' : "YÖK" },
    {'year': 2017, 'first' : 'Dra', 'second' : "?" },
    {'year': 2016, 'first' : 'Dra', 'second' : "?" },
    {'year': 2015, 'first' : 'Dra', 'second' : "?" },
    {'year': 2014, 'first' : 'ASS', 'second': 'GPK', 'third': 'VajaKK', 'fourth': 'MINT'},
    {'year': 2013, 'first' : '?', 'second': '?', },
    {'year': 2012, 'first' : '?', 'second': '?'},
    {'year': 2011, 'first' : 'ASS', 'second': 'HeMi'},
    {'year': 2010, 'first' : '?', 'second': '?'},
    {'year': 2009, 'first' : '?', 'second': '?'},
    {'year': 2008, 'first' : 'LMTVO', 'second': 'PKMM'},
    {'year': 2007, 'first' : 'LMTVO', 'second': 'ITKK', 'third': 'Dra', 'fourth': 'PKMM'},
    {'year': 2006, 'first' : 'GPK', 'second': 'Dra',},
    {'year': 2005, 'first' : 'ITKK', 'second': 'Dra'},
    {'year': 2004, 'first' : '?', 'second': '?',},
    {'year': 2003, 'first' : 'Dra', 'second': 'PKMM', },
    {'year': 2002, 'first' : 'KCK', 'second': 'LMTVO', },
    {'year': 2001, 'first' : 'KCK', 'second': 'SMS', },
];

const brackerWinners = [
    {'year': 2024, 'first' : 'Dra' },
    {'year': 2023, 'first' : 'SÄTKY KY' },
    {'year': 2022, 'first' : 'MaHaLasKu' },
    {'year': 2021, 'first' : 'SFS-6016' },
    {'year': 2020, 'first' : 'Ei' },
    {'year': 2019, 'first' : 'Darts' },
    {'year': 2018, 'first' : 'YÖK' },
    {'year': 2017, 'first' : 'Dra' },
    {'year': 2016, 'first' : 'GPK' },
    {'year': 2015, 'first' : 'GPK' },
    {'year': 2014, 'first' : 'ASS' },
    {'year': 2013, 'first' : 'GPK' },
    {'year': 2012, 'first' : 'GPK' },
    {'year': 2011, 'first' : 'ASS' },
    {'year': 2010, 'first' : 'LMTVO' },
    {'year': 2009, 'first' : 'LMTVO' },
    {'year': 2008, 'first' : 'LMTVO' },
    {'year': 2007, 'first' : 'Dra' },
];

const singleWinner = [
    {'year': 2024, 'first' : 'Leevi Hovatov', 'second': 'Mikko "Temmi" Kuusio'},
    {'year': 2023, 'first' : 'Atte Putkonen', 'second': 'Sami Valjakka'},
    {'year': 2022, 'first' : 'Lassi Onne', 'second': "Leevi Hovatov" },
    {'year': 2021, 'first' : '-' , 'second': '-'},
    {'year': 2020, 'first' : 'Elmo Pärssinen', 'second': "Lassi Onne"},
    {'year': 2019, 'first' : 'Armi Rissanen', 'second': "Leevi Hovatov"},
    {'year': 2018, 'first' : 'Jyri "Kode" Koistinen', 'second': "?" },
    {'year': 2017, 'first' : 'Ville Kytömäki', 'second': "?" },
    {'year': 2016, 'first' : '-', 'second': "-" },
    {'year': 2015, 'first' : '-', 'second': "-" },
    {'year': 2014, 'first' : 'Juha Varis', 'second': "Petteri Westerholm (?)" },
    {'year': 2013, 'first' : 'Petteri Westerholm', 'second': "Anssi Tura (?)" },
    {'year': 2012, 'first' : 'Petteri Westerholm', 'second': "Juha Varis (?)" },
    {'year': 2011, 'first' : 'Petteri Westerholm', 'second': "?" },
    {'year': 2010, 'first' : 'Mikko "Temmi" Kuusio', 'second': "?" },
];

const pairWinners = [
    {'year': 2024, 'first' : 'TBA', 'second': "TBA"},
    {'year': 2023, 'first' : 'Erik Kuitunen, Totti Sillanpää', 'second': "Mikko 'Temmi' Kuusio, Pasi Kortelainen"},
    {'year': 2023, 'first' : 'Erik Kuitunen, Jarno Mikkola', 'second': "Totti Sillanpää, Veikka Immonen"},
    {'year': 2022, 'first' : 'Lassi Onne, Elmo Pärssinen', 'second': "Jarno Mikkola, Totti Sillanpää"},
]

const jaskanKarttu = [
    {'year': 2024, 'name' : 'Lassi Onne'},
    {'year': 2022, 'name' : 'Heikki Lohilahti'},
]

const KCKAhti = [
    {'year': 2024, 'name' : '-'},
    {'year': 2023, 'name' : "Saara Inkinen"},
    {'year': 2022, 'name' : "Tomi Krokberg"},
    {'year': 2021, 'name' : "-"},
    {'year': 2020, 'name' : "Saku Laakkonen"},
    {'year': 2019, 'name' : "Niko Sievänen"},
    {'year': 2018, 'name' : "Lauri Tuimala"},
    {'year': 2017, 'name' : "-"},
    {'year': 2016, 'name' : "-"},
    {'year': 2015, 'name' : "Niko Sievänen"},
    {'year': 2014, 'name' : "Petteri Mustonen"},
    {'year': 2013, 'name' : "Ilkka Kari"},
    {'year': 2012, 'name' : "Matti Peittilä"},
    {'year': 2011, 'name' : "-"},
    {'year': 2010, 'name' : "-"},
    {'year': 2009, 'name' : "Tuomas Aalto"},
    {'year': 2008, 'name' : "Outi Matikainen"},
    {'year': 2007, 'name' : "Jyri Koistinen"},
    {'year': 2006, 'name' : "Kalle Rannikko"},
    {'year': 2005, 'name' : "Mikko Raatikainen"},
    {'year': 2004, 'name' : "Janne Matikainen"},
    {'year': 2003, 'name' : "Samu Uimonen"},
    {'year': 2002, 'name' : "Mikko Drocan"},
    {'year': 2001, 'name' : "Sami Mannelin"},
    {'year': 2000, 'name' : "Raine Koponen"},
];

const hauki = [
    {'year': 2024, 'name' : 'Armi Rissanen'},
    {'year': 2023, 'name' : "Saara Inkinen"},
    {'year': 2022, 'name' : "Tomi Krokberg"},
    {'year': 2021, 'name' : "-"},
    {'year': 2020, 'name' : "?"},
    {'year': 2019, 'name' : "?"},
    {'year': 2018, 'name' : "?"},
    {'year': 2017, 'name' : "?"},
    {'year': 2016, 'name' : "?"},
    {'year': 2015, 'name' : "?"},
    {'year': 2014, 'name' : "Harri Renkonen"},
    {'year': 2013, 'name' : "?"},
    {'year': 2012, 'name' : "?"},
    {'year': 2011, 'name' : "?"},
    {'year': 2010, 'name' : "?"},
    {'year': 2009, 'name' : "?"},
    {'year': 2008, 'name' : "?"},
    {'year': 2007, 'name' : "?"},
    {'year': 2006, 'name' : "Seppo Kyynäräinen"},
    {'year': 2005, 'name' : "Risto Tapanen"},
    {'year': 2004, 'name' : "Sami Kontio"},
    {'year': 2003, 'name' : "Janne Lahdenperä"},
    {'year': 2002, 'name' : "?"},
    {'year': 2001, 'name' : "Sampo Kokkonen"},
    {'year': 2000, 'name' : "?"},
]

const last = [
    {'year' : 2024, 'name' : "Jyri 'Kode' Koistinen"},
    {'year' : 2023, 'name' : "Totti Sillanpää"},
    {'year' : 2022, 'name' : "Totti Sillanpää"},
    {'year' : 2021, 'name' : "-"},
    {'year' : 2020, 'name' : "?"},
    {'year' : 2019, 'name' : "?"},
    {'year' : 2018, 'name' : "?"},
    {'year' : 2017, 'name' : "?"},
    {'year' : 2016, 'name' : "?"},
    {'year' : 2015, 'name' : "?"},
    {'year' : 2014, 'name' : "Anssi Tura"},
    {'year' : 2013, 'name' : "?"},
    {'year' : 2012, 'name' : "?"},
    {'year' : 2011, 'name' : "?"},
    {'year' : 2010, 'name' : "?"},
    {'year' : 2009, 'name' : "?"},
    {'year' : 2008, 'name' : "?"},
    {'year' : 2007, 'name' : "?"},
    {'year' : 2006, 'name' : "Sami Pyykkö"},
    {'year' : 2005, 'name' : "Sami Pyykkö"},
    {'year' : 2004, 'name' : "Janne Pulli"},
    {'year' : 2003, 'name' : "Mikko Drocan"},
    {'year' : 2002, 'name' : "?"},
    {'year' : 2001, 'name' : "-"},
    {'year' : 2000, 'name' : "?"},
]

const mvp = [
    {'year' : 2024, 'name' : "Mikko 'Temmi' Kuusio"},
    {'year' : 2023, 'name' : "Atte Putkonen"},
    {'year' : 2022, 'name' : "Jarno Mikkola"},
    {'year' : 2021, 'name' : "-"},
    {'year' : 2020, 'name' : "?"},
    {'year' : 2019, 'name' : "?"},
    {'year' : 2018, 'name' : "?"},
    {'year' : 2017, 'name' : "?"},
    {'year' : 2016, 'name' : "?"},
    {'year' : 2015, 'name' : "?"},
    {'year' : 2014, 'name' : "Petteri Westerholm"},
    {'year' : 2013, 'name' : "?"},
    {'year' : 2012, 'name' : "?"},
    {'year': 2011, 'name' : "-"},
    {'year': 2010, 'name' : "-"},
    {'year': 2009, 'name' : "?"},
    {'year': 2008, 'name' : "?"},
    {'year': 2007, 'name' : "?"},
    {'year': 2006, 'name' : "Niko Kuikka"},
    {'year': 2005, 'name' : "Juha Varis"},
    {'year': 2004, 'name' : "Jussi Ahonen"},
    {'year': 2003, 'name' : "Juha Varis"},
    {'year': 2002, 'name' : "?"},
    {'year': 2001, 'name' : "Saku Ruottinen"},
    {'year': 2000, 'name' : "?"},
];

const man = [
    {'year' : 2024, 'name' : "Totti Sillanpää"},
    {'year' : 2023, 'name' : "Markus Laitinen"},
    {'year' : 2022, 'name' : ""},
    {'year' : 2021, 'name' : "-"},
    {'year' : 2020, 'name' : "?"},
    {'year' : 2019, 'name' : "?"},
    {'year' : 2018, 'name' : "?"},
    {'year' : 2017, 'name' : "?"},
    {'year' : 2016, 'name' : "?"},
    {'year' : 2015, 'name' : "?"},
    {'year' : 2014, 'name' : "-"},
    {'year' : 2013, 'name' : "?"},
    {'year' : 2012, 'name' : "?"},

];

const woman = [
    {'year' : 2024, 'name' : "Armi Rissanen"},
    {'year' : 2023, 'name' : "Armi Rissanen"},
    {'year' : 2022, 'name' : "Armi Rissanen"},
    {'year' : 2021, 'name' : "-"},
    {'year' : 2020, 'name' : "?"},
    {'year' : 2019, 'name' : "?"},
    {'year' : 2018, 'name' : "?"},
    {'year' : 2017, 'name' : "?"},
    {'year' : 2016, 'name' : "?"},
    {'year' : 2015, 'name' : "?"},
    {'year' : 2014, 'name' : "Tiina Viitanen"},
    {'year' : 2013, 'name' : "?"},
    {'year' : 2012, 'name' : "?"},


];

const bracketBest = [
    {'year' : 2024, 'name' : "Mikko 'Temmi' Kuusio"},
    {'year' : 2023, 'name' : "Niko Grön"},
    {'year' : 2022, 'name' : "Sami Valjakka"},
    {'year' : 2021, 'name' : "-"},
    {'year' : 2020, 'name' : "?"},
    {'year' : 2019, 'name' : "?"},
    {'year' : 2018, 'name' : "?"},
    {'year' : 2017, 'name' : "?"},
    {'year' : 2016, 'name' : "?"},
    {'year' : 2015, 'name' : "?"},
    {'year' : 2014, 'name' : "Petteri Westerholm"},
    {'year' : 2013, 'name' : "?"},
    {'year' : 2012, 'name' : "?"},
    {'year': 2011, 'name' : "?"},
    {'year': 2010, 'name' : "?"},
    {'year': 2009, 'name' : "?"},
    {'year': 2008, 'name' : "?"},
    {'year': 2007, 'name' : "?"},
    {'year': 2006, 'name' : "Niko Kuikka"},
    {'year': 2005, 'name' : "Jussi Ahonen"},
    {'year': 2004, 'name' : "Jukka Tanninen"},
    {'year': 2003, 'name' : "Juha Varis"},
    {'year': 2002, 'name' : "?"},
    {'year': 2001, 'name' : "Tero Turtiainen"},
    {'year': 2000, 'name' : "?"},
]

const playoffBest = [
    {'year' : 2024, 'name' : "Leevi Hovatov"},
    {'year' : 2023, 'name' : "Leevi Hovatov"},
    {'year' : 2022, 'name' : "Atte Putkonen"},
    {'year' : 2021, 'name' : "-"},
    {'year' : 2020, 'name' : "?"},
    {'year' : 2019, 'name' : "?"},
    {'year' : 2018, 'name' : "?"},
    {'year' : 2017, 'name' : "?"},
    {'year' : 2016, 'name' : "?"},
    {'year' : 2015, 'name' : "?"},
    {'year' : 2014, 'name' : "Petteri Westerholm"},
    {'year' : 2013, 'name' : "?"},
    {'year' : 2012, 'name' : "?"},
    {'year': 2011, 'name' : "?"},
    {'year': 2010, 'name' : "?"},
    {'year': 2009, 'name' : "?"},
    {'year': 2008, 'name' : "?"},
    {'year': 2007, 'name' : "?"},
    {'year': 2006, 'name' : "Janne Matikainen"},
    {'year': 2005, 'name' : "Sami Pyykkö"},
    {'year': 2004, 'name' : "Jussi Ahonen"},
    {'year': 2003, 'name' : "Mikko 'Temmi' Kuusio"},
    {'year': 2002, 'name' : "?"},
    {'year': 2001, 'name' : "Mika Alitalo"},
    {'year': 2000, 'name' : "?"},
]

const rookie = [
    {'year' : 2024, 'name' : "Eino Auvinen"},
    {'year' : 2023, 'name' : "Eetu Knutars"},
    {'year' : 2022, 'name' : "Lauri Lempiö"},
    {'year' : 2021, 'name' : "-"},
    {'year' : 2020, 'name' : "?"},
    {'year' : 2019, 'name' : "?"},
    {'year' : 2018, 'name' : "?"},
    {'year' : 2017, 'name' : "?"},
    {'year' : 2016, 'name' : "?"},
    {'year' : 2015, 'name' : "?"},
    {'year' : 2014, 'name' : "Niko Strömberg"},
    {'year' : 2013, 'name' : "?"},
    {'year' : 2012, 'name' : "?"},
    {'year': 2011, 'name' : "?"},
    {'year': 2010, 'name' : "?"},
    {'year': 2009, 'name' : "?"},
    {'year': 2008, 'name' : "?"},
    {'year': 2007, 'name' : "?"},
    {'year': 2006, 'name' : "Henrik Tarkkio"},
    {'year': 2005, 'name' : "Fredrik Löfberg"},
    {'year': 2004, 'name' : "Janne Keränen"},
    {'year': 2003, 'name' : "Jukka Tanninen"},
    {'year': 2002, 'name' : "?"},
    {'year': 2001, 'name' : "Sami Hämäläinen"},
    {'year': 2000, 'name' : "?"},
]

const tree = [
    {'year' : 2024, 'name' : "Mikko 'Temmi' Kuusio"},
    {'year' : 2023, 'name' : "Joona Lappalainen"},
    {'year' : 2022, 'name' : "Jarno Mikkola"},
]

const misc = [
    {'year' : 2024, 'name' : 'Vuoden ilmiö', 'person' : "KOFF"},
    {'year' : 2024, 'name' : "Vuoden kyykkacom", 'person' : "Totti Sillanpää"},
    {'year' : 2022, 'name' : "Vuoden Suurin Yllätys", 'person' : "SÄTKY ky:n pronssi"},
    {'year' : 2022, 'name' : "Suurin sulaminen", 'person' : "LSP kolme viimeistä mailaa yhteen kyykkään haukia, johtaen häviöön TAI K-Mafian häviö sätkyä vastaan jatkosarjassa."},
    {'year' : 2022, 'name' : "Vuoden Heitto", 'person' : "Elmon kahdeksan kyykän poisto finaalin viimeisen ottelun viimeisessä erässä."},
    {'year' : 2022, 'name' : "Vuoden Pettymys", 'person' : "K-Mafia ei tyhjentänyt"},
    {'year' : 2022, 'name' : "Vuoden Onnekas", 'person' : "Atso Härkönen, kolme kappaletta kolmen kyykän kilkkejä yhden pelipäivän aikana. Myös Lassi."},
    
    
    {'year' : 2006, 'name': 'Illan Tähti', 'person': "Niko Kuikka"},
    {'year' : 2006, 'name': 'Faniklubin suosikkipelaaja', 'person': 'Marjo Nieminen'},
    {'year' : 2005, 'name': 'Illan Tähti', 'person': "Mikko 'Temmi' Kuusio"},
    {'year' : 2005, 'name': 'Faniklubin suosikkipelaaja', 'person': 'Mikko Raatikainen'},
    {'year' : 2004, 'name': 'Illan Tähti', 'person': 'Katja Talvirinne'},
    {'year' : 2004, 'name': 'Faniklubin suosikkipelaaja', 'person': 'Jussi Ahonen'}



]

const tab = ref(null);

</script>