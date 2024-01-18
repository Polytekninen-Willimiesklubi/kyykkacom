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
            />
        </v-flex>
    </v-layout>
</template>
  
<script>
import Tournament from '@/components/Tournament.vue';
import SideBar from '../components/SideBar.vue';

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
            games: []
        }
    },
    created() {
        this.$http.get('api/matches/'+ '?season=' + sessionStorage.season_id).then(
            function(data) {
            this.games = data.body
        })
    }

};
</script>

<style>
</style>