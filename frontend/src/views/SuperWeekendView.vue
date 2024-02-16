<template>
    <v-layout class="pt-5 mr-2">
        <div width="100px" class="pr-10">
            <v-btn class="mb-5"
                @click="showFormat = !showFormat"
                width="150px"
            >
                {{!showFormat ? "Vain Formaatti" : "Tulokset"}}
            </v-btn>
            <side-bar 
                title="Alkulohko"
                :headers="headers"
                sortBy="super_weekend_bracket_placement"
                :sortDesc="false"
                :no_brackets="no_brackets"
                :super="true"
                :nonDefaultTeams="teams"
            />
        </div>
        <v-flex width="100px">
            <tournament
                :played_games="games"
                :rounds_parrent="rounds"
                :first_round="first_round"
                :first="first"
                :only_format="showFormat"
                :bracket_placements="bracket_placements"
                :non_default_seeds="seeded_teams"
                :load_ended="load_ended"
            />
        </v-flex>
    </v-layout>
</template>
  
<script>
import Tournament from '@/components/Tournament.vue';
import SideBar from '../components/SideBar.vue';
import cup_22 from '../tournament_templates/cup_template_22_teams.json'
import cup_16 from '../tournament_templates/cup_template_16_teams.json'
import cup_12 from '../tournament_templates/cup_seeded_template_12_teams.json'
import cup_8 from '../tournament_templates/cup_template_8_teams.json'
import cup_6 from '../tournament_templates/cup_seeded_template_6_teams.json'
import cup_4 from '../tournament_templates/cup_template_4_teams.json'
import super_cup_14 from '../tournament_templates/super_cup_template_14_teams.json'

export default {
    name: 'SuperWeekendView',
    components: {
        Tournament,
        SideBar
    },
    data: function () {
        return {
            headers: [
                { text: 'Sij.', value: 'super_weekend_bracket_placement'},
                { text: 'Joukkue', value: 'current_abbreviation', sortable: false, width:"10%"},
                { text: 'V', value: 'matches_won', sortable: false, width:"3%"},
                { text: 'T', value: 'matches_tie', sortable: false, width:"3%"},
                { text: 'H', value: 'matches_lost', sortable: false, width:"3%"},
                { text: 'OKA', value: 'match_average', sortable: false, width:"5%"},
            ],
            games: [],
            bracket_placements: [],
            rounds: [],
            first_round: false,
            load_ended: false,
            first: 0,
            no_brackets: 1,
            seasons_mapping: {
                1 : cup_16,
                2 : cup_8,
                3 : cup_4,
                4 : cup_22,
                5 : cup_6,
                6 : cup_12,
                7 : super_cup_14
            },
            showFormat: false,
            teams: [],
            seeded_teams: []
        }
    },
    created() {
        let games = []
        this.$http.get('api/matches/?season=' + sessionStorage.season_id + '&super_weekend=1').then(
            function(data) {
                games = data.body
                console.log(games)
            }
        )
            
        let tmp = []
        let tmp_rounds = []
        let no_brackets = 1
        let teams = []
        let tmp_seeded = []
        this.$http.get('api/superweekend/?season=' + sessionStorage.season_id).then(
            function(data) {
                console.log(data)
                no_brackets = data.body.super_weekend_no_brackets
                if (data.body.super_weekend_playoff_format != 0) {
                    tmp_rounds = this.seasons_mapping[data.body.super_weekend_playoff_format].one_bracket
                } else {
                    tmp_rounds = []
                }
                
                this.$http.get('api/teams/?season=' + sessionStorage.season_id + '&super_weekend=1').then(
                    function(data) {
                        for (var i = 0 ; i < no_brackets; i++) {
                        tmp.push([])
                        }
                        for (let i=0; i < data.body.length; i++) {
                            let team = data.body[i]
                            tmp[team.super_weekend_bracket-1].push([team.current_abbreviation, team.super_weekend_bracket_placement])
                            tmp_seeded.push([team.current_abbreviation, team.super_weekend_playoff_seed])
                        }
                        tmp.forEach(ele => ele.sort((a, b) => a[1] - b[1]))
                        teams = data.body
                    }
                ).finally( () => {
                    this.rounds = tmp_rounds
                    this.no_brackets = no_brackets
                    this.bracket_placements = tmp
                    this.games = games
                    this.teams = teams
                    this.seeded_teams = tmp_seeded
                    this.load_ended = true
                })
            }
        ).catch(() => {
            this.rounds = tmp_rounds
            this.no_brackets = no_brackets
            this.bracket_placements = tmp
            this.teams = []
            this.seeded_teams = []
            this.load_ended = true
        })
    }
};
</script>

<style>
</style>