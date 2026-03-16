<template>
    <v-row class="align-start">
        <v-col cols="12">            
            <v-tabs v-model="tab" align-tabs="center">
                <v-tab value="one">Kilpailut</v-tab>
                <v-tab value="two">Henkilölle myönnetyt</v-tab>
                <v-tab value="three">Palkinto info</v-tab>
                <v-tab value="four">MitalliTaulukko</v-tab>
            </v-tabs>
        </v-col>
        <v-col cols="12">
            <v-tabs-window v-model="tab" >
                <v-tabs-window-item value="one">
                    <v-row>
                        <template v-for="table in tab_one_data">
                            <v-col :cols="table.cols">
                                <simple-table
                                    :title="table.title"
                                    :headers="headersHof.slice(...table.slice)"
                                    :items="table.data"
                                    :icon="table.icon"
                                >
                                    <template #bottom_legend
                                        v-if="table.title == 'Runkosarjan Voittaja'"
                                    >
                                        <div class="d-flex">
                                            <p class="legend_text ml-2" style="text-align: left;">* : Ei (ehkä) virallinen</p>
                                            <v-spacer/>
                                            <p class="legend_text mr-2" style="text-align: right;">✞ : Kaksi lohkoa</p>
                                        </div>
                                    </template>
                                </simple-table>
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
                                    :icon="table.icon"
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
                        <v-col cols="4">
                            <simple-table
                                title="Vanhat palkinnot"
                                :headers="headerHofMisc"
                                :items="hof.old_mentions"
                            />
                        </v-col>
                    </v-row>
                </v-tabs-window-item>
                <v-tabs-window-item value="three">
                    <v-card>
                       <v-list lines="three">
                            <template v-for="i in info">
                                <v-list-item
                                    :title="i.title"
                                    :subtitle="i.subtitle"
                                >
                                    <template #title="{ title }">
                                        <span class="item_title">{{ title }}</span>
                                    </template>
                                    <template #subtitle="{ subtitle }">
                                        <span class="item_subtitle">{{ subtitle }}</span>
                                        <a :href=i.ref class="a_link">{{ i.hyperlink }}</a>
                                    </template>
                                </v-list-item>
                            </template>
                       </v-list>
                    </v-card>
                </v-tabs-window-item>
                <v-tabs-window-item value="four">
                    <v-row style="align-self: start">
                        <v-col cols="12">
                            <v-card 
                                title="Mitallitaulukko"
                            >
                                <v-row>
                                    <v-col cols="12">
                                        <div class="d-flex justify-center">
                                            <v-btn-toggle
                                                v-model="toggleMultiple"
                                                variant="outlined"
                                                divided
                                                mandotory
                                            >
                                                <v-btn
                                                    size="small"
                                                    text="Joukkueet"
                                                />
                                                <v-btn
                                                    size="small"
                                                    text="Pelaajat"
                                                />
                                            </v-btn-toggle>
                                        </div>
                                    </v-col>
                                    <v-col>
                                        <v-card
                                            class="ma-5"
                                        >
                                            <v-data-table
                                                :headers="headerHofMedals"
                                                :items="toggleMultiple ? hof.medalTablePlayers : hof.medalTableTeams"
                                                :sort-by="[{key: 'first', order: 'desc'}]"
                                                :multi-sort="true"
                                                :items-per-page="-1"
                                                density="compact"
                                            >
                                                <template v-for="header in headerHofMedals"
                                                    #[`header.${header.key}`]="{ column, toggleSort, getSortIcon }"
                                                >
                                                    <v-tooltip :text="column.tooltip" v-if="column.tooltip" location="top">
                                                        <template #activator="{ props }">
                                                        <div class="v-data-table-header__content" v-bind="props">
                                                            <!-- HACK To properly center column header with the sort icon
                                                                    just add another span to other side -->
                                                            <span v-if="column.align !== 'left'" style="width:14px"></span>
                                                            <span @click="() => toggleSort(column)">{{ column.title }}</span>
                                                            <v-icon v-if="column.sortable" 
                                                                class="v-data-table-header__sort-icon" 
                                                                :icon="getSortIcon(column)"
                                                                size="x-small"
                                                            />
                                                        </div>
                                                        </template>
                                                    </v-tooltip>
                                                    <template v-else>
                                                        <div class="v-data-table-header__content">
                                                        <!-- HACK To properly center column header with the sort icon
                                                                    just add another span to other side -->
                                                        <span v-if="column.align !== 'left'" style="width:14px"></span>
                                                        <span @click="() => toggleSort(column)">{{ column.title }}</span>
                                                        <v-icon v-if="column.sortable" 
                                                            class="v-data-table-header__sort-icon" 
                                                            :icon="getSortIcon(column)"
                                                            size="x-small"
                                                        />
                                                        </div>
                                                    </template>
                                                </template>
                                                <template #item.name = "{ item }">
                                                    <span class="">
                                                        <a class="a_link_no_under"
                                                            :href="(toggleMultiple ? `pelaajat/${item.id}` : `joukkueet/${item.id}`)"
                                                        >
                                                            {{ item.name }}
                                                        </a>
                                                    </span>
                                                </template>
                                                <template #bottom></template>
                                            </v-data-table>
                                        </v-card>
                                    </v-col>
                                </v-row>
                            </v-card>
                        </v-col>
                        <v-spacer></v-spacer>
                    </v-row>
                    <v-spacer></v-spacer>
                </v-tabs-window-item>
            </v-tabs-window>
        </v-col>
    </v-row>

</template>

<route lang="yaml">
    meta:
        layout: "default"
</route>

<script setup>
import { headersHof, headerHofPerson, headerHofMisc, headerHofMedals } from '@/stores/headers';
import { useHofStore } from '@/stores/hof.store';

const hof = useHofStore();
const toggleMultiple = ref(0);

const tab_one_data = [
    { title: "Liigamestaruus", cols: 5, slice: [undefined, undefined], data: hof.championship, icon: "mestari.ico" },
    { title: "SuperWeekend-Cup", cols: 4, slice: [0, 3], data: hof.superData, icon: "superweekend.ico" },
    { title: "Runkosarjan Voittaja", cols: 3, slice: [0, 2], data: hof.bracketWinners, icon: "runkomestari.ico" },
    { title: "Henkkari-Cup", cols: 4, slice: [0, 3], data: hof.singleWinner, icon: null },
    { title: "Parikyykkäliiga", cols: 4, slice: [0, 3], data: hof.pairWinners, icon: "apila_palkinto.png" },
    { title: "SM-Kyykkä", cols: 4, slice: [0, 3], data: hof.sm, icon: null },
    { title: "Kyykkää tähtien kanssa", cols: 4, slice: [0, 3], data: hof.stars, icon: "star_trophy.svg" }
];

const tab_two_data = [
    { title: "Jaskan Karttu", data: hof.jaskanKarttu, icon: null },
    { title: "KCK Ahti", data: hof.KCKAhti, icon: null },
    { title: "Vuoden Kyykkäjä", data: hof.p_o_y, icon: "vuoden_kyykkaaja.svg" },
    { title: "Haukikuningas/-tar", data: hof.hauki, icon: "hauki.png" },
    { title: "Vuoden MVP", data: hof.mvp, icon: "mvp.png" },
    { title: "Runkosarjan Paras", data: hof.bracketBest, icon: "runkosarja_paras.ico" },
    { title: "Pudotuspelien Paras", data: hof.playoffBest, icon: "pudotus.ico" },
    { title: "Vuoden Viimeistelijä", data: hof.last, icon: "lakaisija.png" },
    { title: "Vuoden Tulokas", data: hof.rookie, icon: "vuoden_tulokas.svg" },
    { title: "Vuoden nais-/mieskyykkääjä", data: hof.man_woman, icon: null },
    { title: "Vuoden Kuusenkaataja", data: hof.tree, icon: "joulukuusen_kaataja.png" },
];

const info = [
    { title: "Liigan mestaruus", subtitle: "Liigan mestaruuden saavuttaa voittamalla joka talvi järjestettävän NKL pudotuspelien finaalin. Voittajalle saa TEK-malja kiertopalkinnon, joka on ollut kierrossa 1998 lähtien (?). Pokaalin jalustalle kirjoitetaan voittaja joukkueen lisäksi joukkueen pelaaajat (jotka voisivat pelata jatkosarjassa, sääntö: 2.2.8)." },
    { title: "SuperWeekend-Cup", subtitle: "NKL kauden aikana pidetty yhden päivän viikonlopputurnaus mihin kaikki joukkueet voivat osallistua. Yleensä Cup-muotoinen turnaus ja on ollut osa NKL kautta vuodesta 2001 lähtien. Voittajalle jaetaan Kiiski-malja, joka on ollut kierrossa 2015 lähtien. Malja on Simo Kiiskin muistolle, joka nukkui pois 2014 Superweekendin aamuna. Superweekendin alkulohko on voinut olla osa NKLn runkosarjaa, mutta jatkopelit eivät ole koskaan vaikuttaneet runkosarja sijoitukseen. NKL-Cup on vaihtoehtoinen, mutta nykyään ehkä vähemmän käytetty nimitys. Vanhoja nimiä Cupille: TietoEnator-Cup." },
    { title: "Runkosarja Voittaja", subtitle: "Joukkue joka voittaa NKL runkosarjan jaetaan SEFE-malja. Joukkueen nimen lisäksi jalustaan kirjoitetaan myös joukkueen pelaajien nimet. Runkosarja on ollut joskus jaettuna kahteen eri lohkoon (-21, -23 ja -24), jolloin lohkon voittajien välillä on ollut 'Runkosarjafinaali', jonka voittaja on julistettu runkosarjan voittajaksi. SEFE-malja on ollut kierrossa ainakin vuodesta 2007 lähtien." },
    { title: "Henkkari-Cup", subtitle: "Tavallisesti NKL pudotuspelien lähettyvillä on pelattu HenkkariCup- turnaus. Nimensä veroisesti peli pelataan henkilökohtaisena pelinä, missä joukkue-kentän 20 tornin sijaan keskellä on 10 tornia ja per erä pelaajalla on käytettävissä 20 heittoa. Henkkaricup- turnaukseen osallistumisperuste vaihtelee vuosittain, usein henkkaria on pitänyt pelata ELO muotoisena x-määrän, joskus turnaukseen pääsee vain ilmottautumalla. Pokaaliin kirjoitetaan voittajan nimi. Turnaus on järjestetty 2010 lähtien." },
    { title: "Parikyykkäliiga", subtitle: "Syksyllä pelattava Parikyykkäliiga pelataan henkkarimuotoisena kentän kyykkien osalta, mutta paripelinä. Pudotuspeli vaiheen voittajalle jaetaan Apila-pokaali. Apila-pokaalin kiertoon lahjoitti lassi onne. Liiga on järjestty vuodesta 2022 lähtien." },
    { title: "Kyykkää Tähtien Kanssa", subtitle: "Kevytmielisempi turnaus, missä NKL pelaaja ja NKLssä pelaamaton (usein fuksi) pelaavat parina. Järjestetään syksyisin. Järjestetty jo kauan." },
    { title: "SM-Kyykkä", subtitle: "Wappuna järjestettävä joukkuemuotoinen turnaus. 'S' nimessä viittaa Skinnarilaan, ei Suomeen. Kilpailu on järjestty ainakin vuodesta 2014. Tarkkaa vuotta ei nyt koodaja itse tiedä." },
    { title: "Skinnarilan Paras Kyykän Pelaaja (SPKP)", subtitle: "Kiertopalkinto, jonka voittaa haastamalla ja voittamalla nykyisen palkinnon haltijan ELO-henkkarissa. Palkintoon saa nimen, jos 'eläköityy' aktiivisesta pelaamisesta palkinnon kanssa." },

    { title: "Jaskan Karttu", subtitle: "Myönnettään henkilölle, joka on tehnyt jotain merkittävää lappeen Rantalaisen kyykän edistämiseksi. Kyseessä ei ole lähtökohtaisesti vuosittain jaettava palkinto.", hyperlink: "Jaskan muistolle", ref: "/info/jaska" },
    { title: "KCK-Ahti - Pysti", subtitle: "Palkinto jaetaan vuosittain sellaiselle pelaajalle, joka päättyvän kauden aikana on huomionarvoisasti vaikuttanut edustamansa liigassa pelaavan joukkueen menestykseen erittäin jalolla haukienheiton saralla. Mitä kriittisemmässä paikassa, sitä parempi. ", hyperlink: "Julkilausuma", ref: '/info/ahti' },
    { title: "Vuoden kyykkääjä", subtitle: "Pelaaja, joka on osoittanut kauden aikana parasta urheiluhenkeä ja herrasmiesmäistä käytöstä yhdistettynä pelin hyvään tasoon" },
    { title: "Haukikuningas/-tar", subtitle: "Runsaasti tai erittäin runsaasti haukia kauden aikana heittänyt henkilö." },
    { title: "Vuoden Tulokas", subtitle: "Ensimmäisen kauden pelaaja, joka on pelannut hyvällä tasolla ja osoittanut hyvää kyykkä-henkeä" },
    { title: "Runkosarjan paras pelaaja", subtitle: "Joukkueen pelin edistäminen sekä korkea henkilökohtaisen pelaamisen taso runkosarjassa." },
    { title: "Pudotuspelien paras pelaaja", subtitle: "Joukkueen pelin edistäminen sekä korkea henkilökohtaisen pelaamisen taso jatkosarjassa." },
    { title: "Vuoden viimeistelijä", subtitle: "Paras yksittäisten kyykkien sekä vaikeiden linjojen poistaja; joukkueen kovan tuloksen viimeistelevä pelaaja sekä voittojen ratkaisija. Painoarvo varsinkin 4.paikan pelaajille." },
    { title: "Vuoden nais-/mieskyykkääjä", subtitle: "Kauden paras nais-/miespuolinen kyykänpelaaja, vastine Vuoden Kyykkääjän vastine. Joukkueen pelin edistäminen sekä korkea henkilökohtaisen pelaamisen taso." },
    { title: "Vuoden MVP", subtitle: "Arvokkain/Paras pelaaja läpi kauden." },
    { title: "Vuoden Kuusenkaataja", subtitle: "Eniten joulukuusia (heitto joka poistaa 6 tai enemmän kyykkää) heittänyt pelaaja." },
];


const tab = ref(null);

hof.getAllAccolades();

</script>

<style scoped>
.align-start {
    align-items: flex-start !important;
}

.a_link_no_under {
    font-size: 1em;
    color: blue;
}

.a_link {
    color: blue;
    text-decoration: underline;
    font-size: 1.1em;
}

.a_link_no_under:hover,
.a_link:hover {
    opacity: 0.7;
    text-decoration: underline;
    cursor: pointer;
}

.item_title {
    font-size: 1.2em;
    font-weight: bold;
}

.item_subtitle {
    font-size: 1.1em;
    font-weight: 550;
    color: black;
}

.legend_text {
    font-size: 0.8em;
}
</style>