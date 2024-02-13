<template>
    <v-card elevation="1">
        <v-card-title>
            Ratkaise Runkosarja
            <v-spacer></v-spacer>
        </v-card-title>
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
                            v-for="(element, index) in listItem"
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
            all_teams: [],
            teams: [],
            selectValue: {}
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
          splitToBrackets() {
            this.data = JSON.parse(sessionStorage.teams)

            if (sessionStorage.all_seasons) {
                var all_seasons = JSON.parse(sessionStorage.all_seasons)
                
                var index = all_seasons.map(ele => String(ele.id)).indexOf(sessionStorage.season_id)
                var this_season = all_seasons[index]

                if (this_season.no_brackets > 1) {
                    this.multible_brackets = true
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
        handleRedirect(value) {
            location.href = '/joukkue/'+value.id;
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
        },
        get_post_data() {
            let post_data = {}
            this.teams.forEach(ele => {
                post_data[ele.id] = ele.order
            }, post_data)
            return post_data
        }
    },
    mounted() {
        if (!sessionStorage.loaded_season || sessionStorage.loaded_season != sessionStorage.season_id) {
            this.getTeams();
            sessionStorage.loaded_season = sessionStorage.season_id
        } else {
            this.splitToBrackets()
        }
      },
    watch: {
        teams() {
            this.teams.forEach((element) => element.forEach((ele, index) => ele.order = index +1))
        }
    }
  };
  </script>
  