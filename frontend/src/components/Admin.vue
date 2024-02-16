<template>
    <v-card elevation="1">
        <v-tabs fixed-tabs color="red" v-model='tab'>
            <v-tab :value="0">Runkosarja</v-tab>
            <v-tab :value="1">SuperWeekend</v-tab>
        </v-tabs>
        <v-divider />
        <v-window v-model="tab">
            <v-window-item
                :key="0"
                :value="0">

                <h2 class="pl-10">Ratkaise Runkosarja</h2>
                <v-row>
                    <v-col v-for="(listItem, index) in this.teams" :key="index" :cols="2">
                        <v-card class="ml-10" elevated width="300px">
                            <v-card-title>Lohko {{ String.fromCharCode(65+index) }} </v-card-title>
                            <v-divider></v-divider>
                            <draggable
                                class="v-item-group"
                                :list="listItem"
                                item-key="current_abbreviation"
                                style="padding: 1em;"
                            >
                                <div
                                    class="v-item"
                                    v-for="element in listItem"
                                    :key="element.current_abbreviation"
                                    style="border: solid; margin-bottom: 2px; border-width: 2px;"
                                >
                                    {{ element.order }}. {{ element.current_abbreviation }}
                                </div>
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
                            v-model="selectValue"
                            :items="all_teams"
                            :item-text="item => item.current_abbreviation"
                            return-object
                            />
                        </v-card>
                    </v-col>
                </v-row>
                <v-btn class="ma-4 ml-10" v-on:click="validateResult(true)" x-large color="error">Vahvista Runkosarjan tulos</v-btn>
                <v-btn class="ma-4 ml-10" v-on:click="validateWinner" x-large color="error">Vahvista Runkosarjan Voittaja</v-btn>
            
            </v-window-item>
            <v-window-item
                :key="1"
                :value="1"
            >
                <v-tabs fixed-tabs color="black" v-model='sub_tab'>
                    <v-tab :value="0">Joukkueet Lohkoihin</v-tab>
                    <v-tab :value="1">Syötä Otteluita</v-tab>
                    <v-tab :value="2">Ratkaise Lohkot</v-tab>
                    <v-tab :value="3">Seedaa Joukkueet</v-tab>
                    <v-tab :value="4">Ratkaise Voittaja</v-tab>
                </v-tabs>
                <v-divider class="mb-2"/>
                <v-window v-model="sub_tab">
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
                                        class="v-item-group"
                                        group="people"
                                        :list="not_in_super"
                                        style="padding: 1em;"
                                    >
                                        <div
                                            class="v-item"
                                            v-for="element in not_in_super"
                                            :key="element.current_abbreviation"
                                            style="border: solid; margin-bottom: 2px; border-width: 2px;"
                                        >
                                        {{ element.current_abbreviation }}
                                        </div>
                                    </draggable>
                                </v-card>
                            </v-col>
                            <v-col cols="9">
                                <v-row>
                                    <v-col v-for="(listItem, index) in this.super_teams" :key="index" :cols="4">
                                        <v-card class="ml-10" elevated width="300px">
                                            <v-card-title>Lohko {{ String.fromCharCode(65+index) }} </v-card-title>
                                            <v-divider></v-divider>
                                            <draggable
                                                class="v-item-group"
                                                group="people"
                                                :list="listItem"
                                                item-key="current_abbreviation"
                                                style="padding: 1em;"
                                            >
                                                <div
                                                    class="v-item"
                                                    v-for="element in listItem"
                                                    :key="element.current_abbreviation"
                                                    style="border: solid; margin-bottom: 2px; border-width: 2px;"
                                                >
                                                    {{ element.current_abbreviation }} 
                                                </div>
                                            </draggable>
                                        </v-card>
                                    </v-col>
                                </v-row>
                            </v-col>
                        </v-row>
                        <v-btn class="ma-4 ml-10" v-on:click="validateBrackets()" x-large color="error">Vahvista Superin lohkot</v-btn>
                    </v-window-item>
                    <v-window-item
                        :key="1"
                        :value="1"
                    >
                        <h2 class="pl-10 pb-2">Syötä Superin otteluita</h2>
                        <v-form ref='matchSubmit' v-model="submitValid" @submit.prevent="submit" lazy-validation>
                            <v-row>
                                <v-col cols="3">
                                    <v-select class="ma-2" width="300px"
                                        label="Valitse pelityyppi"
                                        v-model="selectGametype"
                                        :rules="[v => !!v || 'Valitse pelityyppi!']"
                                        :items="game_types"
                                        :item-text="item => item.name"
                                        return-object
                                        outlined
                                    />
                                </v-col>
                                <v-col cols="1">
                                    <v-select class="ma-2" 
                                        :items="Array.from(Array(10).keys())"
                                        v-model="field" label="Kenttä"
                                    />

                                </v-col>
                            </v-row>
                            <v-row>
                                <v-col cols="2">
                                    <v-menu
                                        ref="menu"
                                        v-model="menu"
                                        :close-on-content-click="false"
                                        :return-value.sync="selectDate"
                                        transition="scale-transition"
                                        offset-y
                                        min-width="auto"
                                        outlined
                                    >
                                        <template v-slot:activator="{ on, attrs }">
                                            <v-combobox 
                                                v-model="selectDate"
                                                label="Pelipäivä"
                                                prepend-icon="mdi-calendar"
                                                readonly
                                                v-bind="attrs"
                                                v-on="on"
                                            />
                                        </template>
                                        <v-date-picker 
                                            v-model="selectDate"
                                            no-title
                                            scrollable
                                            @click:date="$refs.menu.save(selectDate)"
                                        />
                                    </v-menu>
                                </v-col>
                                <v-col cols="2">
                                    <v-menu
                                        ref="menu_time"
                                        v-model="menu_time"
                                        :close-on-content-click="false"
                                        :return-value.sync="selectTime"
                                        transition="scale-transition"
                                        offset-y
                                        min-width="auto"
                                        outlined
                                    >
                                        <template v-slot:activator="{ on, attrs }">
                                            <v-combobox 
                                                v-model="selectTime"
                                                label="Peliaika"
                                                prepend-icon="mdi-clock"
                                                readonly
                                                v-bind="attrs"
                                                v-on="on"
                                            />
                                        </template>
                                        <v-time-picker
                                            v-model="selectTime"
                                            no-title
                                            format="24hr"
                                            scrollable
                                            color="red"
                                            :allowedMinutes="v => !(v % 5)"
                                            @click:minute="$refs.menu_time.save(selectTime)"
                                        />
                                    </v-menu>
                                </v-col>
                            </v-row>
                            <v-row>
                                <v-col cols="2">
                                    <v-select class="ma-2" width="300px"
                                        label="Valitse kotijoukkue"
                                        v-model="selectHome"
                                        :rules="[v => !!v || 'Valitse Joukkue!']"
                                        :items="seedable_super_teams"
                                        :item-text="item => item.current_abbreviation"
                                        return-object
                                        outlined
                                    />
                                </v-col>
    
                                <v-col cols="2">
                                    <v-select class="ma-2" width="300px"
                                        label="Valitse vierasjoukkue"
                                        v-model="selectAway"
                                        :rules="[v => !!v || 'Valitse Joukkue!']"
                                        :items="seedable_super_teams"
                                        :item-text="item => item.current_abbreviation"
                                        return-object
                                        outlined
                                    />
                                </v-col>
                            </v-row>
                            <v-row>
                                <v-col cols="2">
                                    <v-text-field class="ma-2"
                                        v-model='homeScore'
                                        :rules="scoreRules"
                                        label="Koti joukkueen tulos"
                                        required
                                        outlined
                                    />
                                </v-col>
                                <v-col cols="2">
                                    <v-text-field class="ma-2"
                                        v-model='awayScore'
                                        :rules="scoreRules"
                                        label="Vieras joukkueen tulos"
                                        required
                                        outlined
                                    />
                                </v-col>
                            </v-row>
                            <v-btn type="submit" class="ma-2" color="error">Syötä tulos</v-btn>
                        </v-form>


                    </v-window-item>
                    <v-window-item
                        :key="2"
                        :value="2"
                    >
                        <h2 class="pl-10">Ratkaise Superin Lohkot</h2>
                        <v-row>
                            <v-col v-for="(listItem, index) in this.super_teams" :key="index" :cols="3">
                                <v-card class="ml-10" elevated width="300px">
                                    <v-card-title>Lohko {{ String.fromCharCode(65+index) }} </v-card-title>
                                    <v-divider></v-divider>
                                    <draggable
                                        class="v-item-group"
                                        :list="listItem"
                                        item-key="current_abbreviation"
                                        style="padding: 1em;"
                                    >
                                        <div
                                            class="v-item"
                                            v-for="element in listItem"
                                            :key="element.current_abbreviation"
                                            style="border: solid; margin-bottom: 2px; border-width: 2px;"
                                        >
                                            <v-row>
                                                <v-col align="left" cols="6"> {{ element.order }}. {{ element.current_abbreviation }} </v-col> 
                                                <v-col align="right" cols="6">(OKa: {{ element.match_average }})</v-col>
                                            </v-row>
                                        </div>
                                    </draggable>
                                </v-card>
                            </v-col>
                        </v-row>
                        <v-btn class="ma-4 ml-10" v-on:click="validateResult(false)" x-large color="error">Vahvista Superin lohko sijoitukset</v-btn>

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
                                class="v-item-group"
                                :list="seedable_super_teams"
                                style="padding: 1em;"
                            >
                                <div
                                    class="v-item"
                                    v-for="element in seedable_super_teams"
                                    :key="element.current_abbreviation"
                                    style="border: solid; margin-bottom: 2px; border-width: 2px;"
                                >
                                    <v-row>
                                            <v-col align="left" cols="6"> {{ element.order }}. {{ element.current_abbreviation }} </v-col> 
                                            <v-col align="right" cols="6"> (Sij. {{ element.super_weekend_bracket_placement }}) (OKa: {{ element.match_average }})</v-col>
                                    </v-row>
                                </div>
                            </draggable>
                            <v-btn class="ma-4 ml-10" v-on:click="validateSeeds()" x-large color="error">Vahvista Superin Seedit</v-btn>

                        </v-card>
                    </v-window-item>
                    <v-window-item
                        :key="4"
                        :value="4"
                    >
                        <h2 class="pl-10">Valitse SuperWeekend voittaja</h2>
                        <h3 class="pl-10 pt-3">Toistaiseksi automatiikka ei toimi, että finaalin tuloksen laitettua Superin tulisi tallennettua. Näin voittaja erikseen merkataan muistiin, vaikka superweekend turnaustaulussa voittaja näkyisikin</h3>
                        <v-form v-model="submitValid" ref='superwinnerValid' @submit.prevent="validateSuperWinner" lazy-validation>
                            <v-row>
                                <v-col cols="3">
                                    <v-select class="ma-4"
                                        label="Valitse Superin voittaja"
                                        v-model="superWinnerSelected"
                                        :items="seedable_super_teams"
                                        :item-text="item => item.current_abbreviation"
                                        required
                                        return-object
                                        outlined
                                    />
                                </v-col>
                            </v-row>
                            <v-btn class="ma-8" type="submit" x-large color="error">Vahvista Superin Voittaja</v-btn>
                        </v-form>
                    </v-window-item>
                </v-window>

            </v-window-item>
        </v-window>
        <v-card>
        </v-card>
    </v-card>
</template>
  
  <script>
    import draggable from 'vuedraggable'
    export default {
        components: {
            draggable,
        },
        data() {
            return {
                data: [],
                all_teams: [],
                teams: [],
                selectValue: {},
                selectHome: null,
                selectAway: null,
                tab: null,
                menu: false,
                menu_time: false,
                field: null,
                submitValid: true,
                superWinnerValid: true,
                superWinnerSelected: null,
                super_weekend_id: null,
                super_teams: [],
                sub_tab: null,
                no_brackets: 1,
                not_in_super: [],
                seedable_super_teams: [],
                game_types: [
                    {"name" : "Alkulohko", "value" : 31},
                    {"name": "Finaali", "value": 32},
                    {"name": "Pronssi", "value": 33},
                    {"name": "Välierä", "value": 34},
                    {"name": "Puolivälierä", "value": 35},
                    {"name": "Neljännesvälierä", "value": 36},
                    {"name": "Kahdeksannesvälierä", "value": 37}
                ],
                homeScore: null,
                awayScore: null,
                selectGametype: null,
                selectDate: null,
                selectTime: null,
                scoreRules: [
                    value => {
                        return !isNaN(parseInt(value)) || value === '' ? true : "Pitää olla numero!";
                    },
                    value => {
                        return parseInt(value) <= 160 || value === '' ? true : "Liian iso ottelutulos!" 
                    },
                    value => {
                        return parseInt(value) >= -13 || value === '' ? true : "Liian pieni ottelutulos!"
                    },
                ],
        };
      },
      created() {
        const date = new Date()
        let day = date.getDate();
        let month = date.getMonth() + 1;
        month =  Number(month) >= 10 ? month : '0' + month 
        let year = Number(date.getFullYear());

        // This arrangement can be altered based on how we want the date's format to appear.
        let currentDate = `${year}-${month}-${day}`;

        let hour = date.getHours()
        let minute = Number(date.getMinutes()) % 30 ? '30' : '00'

        let currentTime = `${hour}:${minute}`

        this.selectDate = currentDate
        this.selectTime = currentTime
      },
      methods: {
        getTeams() {
            this.$http.get('api/teams/'+'?season='+sessionStorage.season_id+'&post_season=0').then(
                function(data) {
                    sessionStorage.teams = JSON.stringify(data.body)
                },
                function(error) {
                    console.log(error.statusText);
                }
            ).then(
              function() {
                this.splitToBrackets()
              }
            );
        },
        getSuperTeams() {
            this.$http.get('api/superweekend/?season=' + sessionStorage.season_id).then(
                function(data) {
                    this.no_brackets = data.body.super_weekend_no_brackets
                    this.super_weekend_id = data.body.id
                    this.$http.get('api/teams/?season=' + sessionStorage.season_id + '&super_weekend=1').then(
                        function(data) {
                            for (var i = 0 ; i < this.no_brackets; i++) {
                            this.super_teams.push([])
                            }
                            for (let i=0; i < data.body.length; i++) {
                                let team = data.body[i]
                                this.super_teams[team.super_weekend_bracket-1].push(team)
                            }
                        }
                    ).then(() => {
                        this.super_teams.forEach(ele => {
                            ele.forEach((e, i) => {
                                e.order = i + 1
                            })
                        })
                        this.seedable_super_teams = structuredClone(this.super_teams.flat())
                        this.not_in_super = this.all_teams.filter(ele => !this.seedable_super_teams.find(team => ele.id === team.id ))
                        this.seedable_super_teams.forEach((ele, index) => ele.order = index + 1)
                    })
                }
            )

        },
        splitToBrackets() {
            this.data = JSON.parse(sessionStorage.teams)

            if (sessionStorage.all_seasons) {
                var all_seasons = JSON.parse(sessionStorage.all_seasons)
                
                var index = all_seasons.map(ele => String(ele.id)).indexOf(sessionStorage.season_id)
                var this_season = all_seasons[index]

                if (this_season.no_brackets > 1) {
                    for (let i = 0; i < this_season.no_brackets; i++) {
                        this.teams.push([])
                    }
                    this.data.forEach(ele => {
                        this.teams[ele.bracket -1].push(ele)
                        this.all_teams.push(ele)
                    }, this)
                    
                } else {
                    this.teams = [this.data]
                    this.all_teams = this.data
                }
                this.teams.forEach(ele => {
                    ele.forEach((e, i) => {
                        e.order = i + 1
                    })
                })
            }
            this.all_teams.sort((a,b) => (a.current_abbreviation > b.current_abbreviation) ? 1 : ((b.current_abbreviation > a.current_abbreviation) ? -1 : 0))
        },
        validateResult(type) {
            let post_data_key = type ? 'bracket_placement' : 'super_weekend_bracket_placement'
            let team_set = type ? this.teams : this.super_teams
            
            if (confirm('Oletko tyytyväinen tuloksiin?')) {
                team_set.forEach(ele => {
                    ele.forEach(e => {
                        console.log(post_data_key)
                        let post_url = 'api/kyykka_admin/team/update/' + e.id
                        let post_data = {}
                        post_data[post_data_key] = e.order
                        console.log(post_data)
                        this.$http.patch(post_url, post_data, {
                            headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                            },
                            'withCredentials': true,
                        }).catch(function(response) {
                            if (response.status == 403) {
                            this.$http
                                .get('api/csrf', {'withCredentials': true})
                                .then(function(response) {
                                    if (response.status === 200) {
                                        this.$http.patch(post_url, post_data, {
                                            headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                                            'withCredentials': true,
                                        })
                                    }
                                });
                            }
                        })
                    })
                })
            }
        },
        validateSeeds() {
            if (confirm('Oletko tyytyväinen tuloksiin?')) {
                this.seedable_super_teams.forEach(ele => {
                    let post_url = 'api/kyykka_admin/team/update/' + e.id
                    let post_data = {'super_weekend_playoff_seed' : e.order}
                    this.$http.patch(post_url, post_data, {
                        headers: {
                        'X-CSRFToken': this.getCookie('csrftoken')
                        },
                        'withCredentials': true,
                    }).catch(function(response) {
                        if (response.status == 403) {
                        this.$http
                            .get('api/csrf', {'withCredentials': true})
                            .then(function(response) {
                                if (response.status === 200) {
                                    this.$http.patch(post_url, post_data, {
                                        headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                                        'withCredentials': true,
                                    })
                                }
                            });
                        }
                    })
                })
            }
        },
        validateWinner() {
            if (this.selectValue.id === undefined) {
                return
            }
            if (confirm('Oletko tyytyväinen runkosarjan voittajaan?')) {
                let post_url = 'api/kyykka_admin/team/update/' + this.selectValue.id
                let post_data = {'bracket_placement' : 0}
                this.$http.patch(post_url, post_data, {
                    headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                    'withCredentials': true,
                }).catch(function(response) {
                    if (response.status == 403) {
                    this.$http
                        .get('api/csrf', {'withCredentials': true})
                        .then(function(response) {
                            if (response.status === 200) {
                                this.$http.patch(post_url, post_data, {
                                    headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                                    'withCredentials': true,
                                })
                            }
                        });
                    }
                })
            }
        },
        async validateSuperWinner() {
            await this.$refs.superwinnerValid.validate()
            console.log('mpoi')
            console.log(this.superWinnerValid, this.super_weekend_id)
            if (!this.superWinnerValid || !this.super_weekend_id) {
                return
            }
            if (confirm('Oletko tyytyväinen Superin voittajaan?')) {
                let post_url = 'api/kyykka_admin/superweekend/' + this.super_weekend_id
                let post_data = {'winner' : this.superWinnerSelected.id}
                this.$http.patch(post_url, post_data, {
                    headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                    'withCredentials': true,
                }).catch(function(response) {
                    if (response.status == 403) {
                    this.$http
                        .get('api/csrf', {'withCredentials': true})
                        .then(function(response) {
                            if (response.status === 200) {
                                this.$http.patch(post_url, post_data, {
                                    headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                                    'withCredentials': true,
                                })
                            }
                        });
                    }
                })
            }
        },
        validateBrackets() {
            if (confirm('Oletko tyytyväinen Superin lohkoihin?')) {
                this.super_teams.forEach((ele, index) => {
                    ele.forEach((e) => {
                        let post_url = 'api/kyykka_admin/team/update/' + e.id
                        let post_data = {'super_weekend_bracket' : index+1}
                        this.$http.patch(post_url, post_data, {
                            headers: {
                            'X-CSRFToken': this.getCookie('csrftoken')
                            },
                            'withCredentials': true,
                        }).catch(function(response) {
                            if (response.status == 403) {
                            this.$http
                                .get('api/csrf', {'withCredentials': true})
                                .then(function(response) {
                                    if (response.status === 200) {
                                        this.$http.patch(post_url, post_data, {
                                            headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                                            'withCredentials': true,
                                        })
                                    }
                                });
                            }
                        })
                    }, index)
                })
                this.not_in_super.forEach(ele => {
                    let post_url = 'api/kyykka_admin/team/update/' + ele.id
                    let post_data = {'super_weekend_bracket' : null}
                    this.$http.patch(post_url, post_data, {
                        headers: {
                        'X-CSRFToken': this.getCookie('csrftoken')
                        },
                        'withCredentials': true,
                    }).catch(function(response) {
                        if (response.status == 403) {
                        this.$http
                            .get('api/csrf', {'withCredentials': true})
                            .then(function(response) {
                                if (response.status === 200) {
                                    this.$http.patch(post_url, post_data, {
                                        headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                                        'withCredentials': true,
                                    })
                                }
                            });
                        }
                    })
                })
            }
        },
        async submit() {
            await this.$refs.matchSubmit.validate()
            if (!this.submitValid) {return}
            let postData = {}
            postData['season'] = sessionStorage.season_id
            postData['field'] = this.field
            let match_time = this.selectDate + ' ' + this.selectTime + ':00'
            postData['match_time'] = match_time
            postData['home_first_round_score'] = this.homeScore
            postData['home_second_round_score'] = 0
            postData['away_first_round_score'] = this.awayScore
            postData['away_second_round_score'] = 0
            postData['home_team'] = this.selectHome.id
            postData['away_team'] = this.selectAway.id
            postData['is_validated'] = this.is_validated
            postData['match_type'] = this.selectGametype.value
            postData['post_season'] = 0
            postData['seriers'] = 0

            this.$http.post('api/kyykka_admin/match', postData, {
                headers: {
                'X-CSRFToken': this.getCookie('csrftoken')
                },
                'withCredentials': true,
            }).catch(function(response) {
                if (response.status == 403) {
                this.$http
                    .get('api/csrf', {'withCredentials': true})
                    .then(function(response) {
                        if (response.status === 200) {
                            this.$http.patch(post_url, post_data, {
                                headers: {'X-CSRFToken': this.getCookie('csrftoken')},
                                'withCredentials': true,
                            })
                        }
                    });
                }
            })
        }
    },
    mounted() {
        if (!sessionStorage.loaded_season || sessionStorage.loaded_season != sessionStorage.season_id) {
            this.getTeams();
            sessionStorage.loaded_season = sessionStorage.season_id
        } else {
            this.splitToBrackets()
        }
        this.getSuperTeams()
      },
    watch: {
        teams() {
            this.teams.forEach((element) => element.forEach((ele, index) => ele.order = index +1))
        },
        super_teams() {
            this.super_teams.forEach((element) => element.forEach((ele, index) => ele.order = index +1))
        },
        seedable_super_teams() {
            this.seedable_super_teams.forEach((element, index) => element.order = index +1)
        }
    }
  };
  </script>
  