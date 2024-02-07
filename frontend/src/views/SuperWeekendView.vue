<template>
    <v-layout class="pt-5 mr-2">
        <div width="100px">
            <side-bar 
                title="Alkulohko"
                :headers="headers"
                :no_brackets="no_brackets"
                :defaultData="false"
            />
        </div>
        <v-flex width="100px">
            <tournament
                :played_games="games"
                :rounds_parrent="rounds"
                :first_round="first_round"
                :first="first"
                :only_format="showFormat"
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
    name: 'SuperWeekendView',
    components: {
        Tournament,
        SideBar
    },
    data: function () {
        return {
            headers: [
                { text: 'Joukkue', value: 'current_abbreviation', sortable: false, width:"10%"},
                { text: 'V', value: 'matches_won', sortable: false, width:"3%"},
                { text: 'T', value: 'matches_tie', sortable: false, width:"3%"},
                { text: 'H', value: 'matches_lost', sortable: false, width:"3%"},
                { text: 'OKA', value: 'match_average', sortable: false, width:"5%"},
            ],
            games: [],
            rounds: [],
            first_round: false,
            first: 0,
            no_brackets: 1,
            seasons_mapping: {
                1 : cup_16,
                2 : cup_8,
                3 : cup_4,
                4 : cup_22,
                5 : cup_6,
                6 : cup_12,
            },
            showFormat: false
        }
    },
    created() {
        this.$http.get('api/matches/?season=' + sessionStorage.season_id + '&super_weekend=1').then(
            function(data) {
                let games = data.body
                this.games = data.body
                console.log(games)
        })
        this.$http.get('api/superweekend/?season=' + sessionStorage.season_id).then(
            function(data) {
                this.no_brackets = data.body.super_weekend_no_brackets
                let playoff_format = this.seasons_mapping[data.body.super_weekend_playoff_format]
                this.rounds = playoff_format['one_bracket']
                console.log(playoff_format)
        })
    }
};
</script>

<style>
</style>