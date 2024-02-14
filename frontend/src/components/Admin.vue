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
                <v-btn class="ma-4 ml-10" v-on:click="validateResult" x-large color="error">Vahvista Runkosarjan tulos</v-btn>
                <v-btn class="ma-4 ml-10" v-on:click="validateWinner" x-large color="error">Vahvista Runkosarjan Voittaja</v-btn>
            
            </v-window-item>
            <v-window-item
                :key="1"
                :value="1"
            >
                <v-tabs fixed-tabs color="black" v-model='sub_tab'>
                    <v-tab :value="0">Joukkueet Lohkoihin</v-tab>
                    <v-tab :value="1">Ratkaise Lohkot</v-tab>
                    <v-tab :value="2">Seedaa Joukkueet</v-tab>
                    <v-tab :value="3">Ratkaise Voittaja</v-tab>
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
                                    <!-- <v-card-title>{{this.not_in_super}}</v-card-title> -->
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
                    </v-window-item>
                    <v-window-item
                        :key="1"
                        :value="1"
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
                tab: null,
                super_teams: [],
                sub_tab: null,
                no_brackets: 1,
                not_in_super: [],
        };
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
                    // if (data.body.super_weekend_playoff_format != 0) {
                    //     tmp_rounds = this.seasons_mapping[data.body.super_weekend_playoff_format].one_bracket
                    // } else {
                    //     tmp_rounds = []
                    // }
                    
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
                        let all_super_teams = this.super_teams.flat()
                        this.not_in_super = this.all_teams.filter(ele => !all_super_teams.find(team => ele.id === team.id ))
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
        validateResult() {
            if (confirm('Oletko tyytyväinen runkosarjan tuloksiin?')) {
                this.teams.forEach(ele => {
                    ele.forEach(e => {
                        let post_url = 'api/kyykka_admin/team/update/' + e.id
                        let post_data = {'bracket_placement' : e.order}
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
        }
    }
  };
  </script>
  