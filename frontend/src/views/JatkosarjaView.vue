<template>
    <v-layout class="pt-5">
        
        <div width="100px" class="pr-10">
            <v-btn class="mb-5"
                @click="showFormat = !showFormat"
                width="150px"
            >
                {{!showFormat ? "Vain Formaatti" : "Tulokset"}}
            </v-btn>
            <side-bar 
                title="Runkosarja"
                :headers="headers"
                sort-by="bracket_placement"
                :sort-desc=false
                :no_brackets="no_brackets"
                :non-default-teams="teams"
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

export default {
    name: 'JatkosarjaView',
    components: {
        Tournament,
        SideBar
    },
    data() {
        return {
            headers: [
            { text: 'Sij.', value: 'bracket_placement'},
            { text: 'Joukkue', value: 'current_abbreviation', sortable: false, width:"10%"},
            { text: 'O', value: 'matches_played', sortable: false, width:"3%" },
            { text: 'V', value: 'matches_won', sortable: false, width:"3%"},
            { text: 'T', value: 'matches_tie', sortable: false, width:"3%"},
            { text: 'H', value: 'matches_lost', sortable: false, width:"3%"},
            { text: 'P', value: 'points_total', sortable: false, width:"3%"},
            { text: 'OKA', value: 'match_average', sortable: false, width:"5%"},
            ],
            games: [],
            rounds: [],
            no_brackets: 1,
            first_round: false,
            first: 0,
            seasons_mapping: {
                1 : cup_16,
                2 : cup_8,
                3 : cup_4,
                4 : cup_22,
                5 : cup_6,
                6 : cup_12,
            },
            showFormat: false,
            teams: [],
            load_ended: false,
            bracket_placements: []
        }
    },
    created() {
        let no_brackets = 1
        let this_season = undefined
        let games = []
        let tmp = []
        let teams = []
        if (sessionStorage.all_seasons) {
            this_season = JSON.parse(sessionStorage.all_seasons)
            this_season = this_season.filter(
                ele => ele.id == sessionStorage.season_id
            )[0]
            no_brackets = this_season.no_brackets
        }
        let promise1 = this.$http.get('api/matches/?season=' + sessionStorage.season_id).then(
            data => games = data.body.filter(ele => ele.match_type < 30)
        )

        let promise2 = this.$http.get('api/teams/?season=' + sessionStorage.season_id + '&post_season=0').then(
            function(data) {
                for (var i = 0 ; i < no_brackets; i++) {
                    tmp.push([])
                }
                for (let i=0; i < data.body.length; i++) {
                    let team = data.body[i]
                    tmp[team.bracket-1].push([team.current_abbreviation, team.bracket_placement])
                }
                tmp.forEach(ele => ele.sort((a, b) => a[1] - b[1]))
                sessionStorage.teams = JSON.stringify(data.body)
                teams = data.body
            }
        )
        Promise.allSettled([promise1, promise2]).then( () => {
            if (this_season !== undefined && this_season.playoff_format && this_season.playoff_format != 0) {
                let json = this.seasons_mapping[this_season.playoff_format]
                this.rounds = no_brackets == 1 ? json['one_bracket'] : json['two_bracket']
                this.first = json['first_round']
            }
            this.first_round = !!this.first
            this.bracket_placements = tmp
            this.no_brackets = no_brackets
            this.teams = teams
            this.games = games
            this.load_ended = true
        })
    }

};
</script>

<style>
</style>