<template>
    <v-layout class="pt-5">
        <div width="100px" class="pr-10">
            <side-bar 
                title="Runkosarja"
                :headers="headers"
            />
        </div>
        <v-flex width="100px">
            <tournament
                :played_games="games"
                :rounds_parrent="rounds"
                :first_round="first_round"
                :first="first"
            />
        </v-flex>
    </v-layout>
</template>
  
<script>
import Tournament from '@/components/Tournament.vue';
import SideBar from '../components/SideBar.vue';
import two_22 from '../tournament_templates/two_bracket_22.json'
import one_16 from '../tournament_templates/one_bracket_16.json'
import one_12 from '../tournament_templates/one_bracket_12.json'
import one_8 from '../tournament_templates/one_bracket_8.json'
import one_4 from '../tournament_templates/one_bracket_4.json'

export default {
    name: 'JatkosarjaView',
    components: {
        Tournament,
        SideBar
    },
    data() {
        return {
            headers: [
            { text: 'Joukkue', value: 'current_abbreviation', sortable: false, width:"10%"},
            { text: 'O', value: 'matches_played', sortable: false, width:"3%" },
            { text: 'V', value: 'matches_won', sortable: false, width:"3%"},
            { text: 'T', value: 'matches_tie', sortable: false, width:"3%"},
            { text: 'H', value: 'matches_lost', sortable: false, width:"3%"},
            { text: 'P', value: 'points_total', width:"3%"},
            { text: 'OKA', value: 'match_average', sortable: false, width:"5%"},
            ],
            games: [],
            rounds: [],
            first_round: false,
            first: 7,
            seasons_mapping: {
                101 : one_16,
                102 : one_8,
                103 : one_4,
                // 104 : one_22,  <-- Not yet needed or templated
                105 : one_12,
                204 : two_22,
            }
        }
    },
    created() {
        this.$http.get('api/matches/'+ '?season=' + sessionStorage.season_id).then(
            function(data) {
            this.games = data.body
        })
        let this_season = JSON.parse(sessionStorage.all_seasons)
        this_season = this_season.filter(
            ele => ele.id == sessionStorage.season_id
        )[0]
        let no_brackets = this_season.no_brackets
        let json = this.seasons_mapping[this_season.playoff_format + 100*no_brackets]
        this.rounds = json['default']
        this.first_round = json['first_round']
        this.first = this.first_round ? 6 : 0
    }

};
</script>

<style>
</style>