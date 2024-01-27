<template>
    <v-layout>
        <div v-if="st_round.length" class="pr-10">
            <div v-for="listItem in st_round" :key="listItem.name" class="pt-10">
                <bracket :flat-tree="[listItem]">
                    <template slot="player" slot-scope="{player}">
                        {{player.name}}
                    </template>
                    <template #player-extension-bottom="{ match }">
                        <div align="center">
                            {{ match.other_info }}
                        </div>
                    </template>
                </bracket>
            </div>
        </div>
        <v-flex>
            <bracket :flat-tree="data">
                <template slot="player" slot-scope="{player}">
                    {{player.name}}
                </template>
                <template #player-extension-bottom="{ match }">
                    <div align="center">
                        {{ match.other_info }}
                    </div>
                </template>
            </bracket>
        </v-flex>
    </v-layout>
</template>


<script>
import Bracket from "vue-tournament-bracket";

export default {
    name: 'Tournament',
    props: {
        type: Number,
        played_games: Array,
        rounds: Array,
        first_round: Boolean,
        first: Number
    },
    components: {
    Bracket
},
    data() {
        return {
            tmp_rounds: [{}, {}, {}, {}, {}, {}],
            bracket_placements : [],
            multible_brackets: false,
            data: [],
            teams: [],
            bracket_matches: [],
            st_round: [],
        }
    },
    mounted() {
        if (this.teams.length == 0) {
            this.splitToBrackets()
        }

        
    },
    created() {
        if (type(this.rounds) !== Object)
        this.$http
            .get('api/teams/?season=' + sessionStorage.season_id)
            .then( 
                function(data) {
                    const max_bracket = Math.max(...data.body.map(ele => ele.bracket))
                    let tmp = []
                    for (var i = 0 ; i < max_bracket; i++) {
                        tmp.push([])
                    }
                    for (let i=0; i < data.body.length; i++) {
                        let team = data.body[i]
                        tmp[team.bracket-1].push([team.current_abbreviation, team.bracket_placement])
                    }
                    tmp.forEach(ele => ele.sort((a, b) => a[1] - b[1]))
                    this.bracket_placements = tmp
                }
            )

    },
    methods: {
        splitToBrackets: function() {
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
              }, this)

            } else {
              this.teams = [this.data]
              this.multible_brackets = false
            }
          }
        },
        sortTeams: function() {
            this.teams.forEach(ele => {
                ele.sort((a,b) => {
                    let total = b.points_total - a.points_total
                    // Order sort: bracket points
                    if (total != 0) {
                        return total < 0 ? -1 : 1
                    }
                    // First Tiebreaker: Match result between the teams
                    let bracket_match = this.bracket_matches.filter(ele =>
                        (ele.home_team.current_abbreviation == a.current_abbreviation || ele.home_team.current_abbreviation == b.current_abbreviation) &&
                        (ele.away_team.current_abbreviation == a.current_abbreviation || ele.away_team.current_abbreviation == b.current_abbreviation)
                    )
                    if (!bracket_match.length) {
                        console.log('Too many matches found: ' + bracket_match.length)
                        return 0
                    }
                    bracket_match = bracket_match[0]
                    let match_result = bracket_match.away_score_total - bracket_match.home_score_total
                    if (a.current_abbreviation == bracket_match.home_team.current_abbreviation) {
                        match_result *= -1
                    }
                    if (match_result != 0) {
                        return match_result < 0 ? 1 : -1 
                    }

                    // Second Tiebreaker: Match average
                    let average_total = b.match_average - a.match_average
                    if (average_total != 0) {
                        return match_result < 0 ? 1 : -1 
                    }
                    // Third Tiebreaker: Chance, not implemented here
                    return 0
                })
            })
            function innerFunction(array, bracket_matches, big_arr) {
                let games = bracket_matches.filter( e => 
                    (e.home_team.current_abbreviation in array) &&
                    (e.away_team.current_abbreviation in array) 
                )
                games.forEach(e => {
                    console.log(e.home_team.current_abbreviation, e.away_team.current_abbreviation)
                    if (e.home_score_total > e.away_score_total) {
                        array[e.away_team.current_abbreviation] += 2
                    } else if (e.home_score_total < e.away_score_total) {
                        array[e.home_team.current_abbreviation] += 2
                    } else {
                        ++array[e.away_team.current_abbreviation]
                        ++array[e.home_team.current_abbreviation]
                    }
                })
                let sortable = []
                for (var tmp in array) {
                    sortable.push([tmp, array[tmp]])
                }
                sortable.sort((a,b) => b[1]-a[1])
                var i = 0
                while (i < sortable.length) {
                    let points = sortable[i][1]
                    let j = i + 1
                    while (j < sortable.length) {
                        if (sortable[j][1] != points) {
                            break
                        }
                        j++
                    }
                    if (j-i <= 1) {
                        i++
                        continue
                    } else if (j-i === 2) {
                        let match = bracket_matches.filter(e => 
                            (e.home_team.current_abbreviation == sortable[i][0] || e.home_team.current_abbreviation == sortable[j-1][0]) &&
                            (e.away_team.current_abbreviation == sortable[i][0] || e.away_team.current_abbreviation == sortable[j-1][0])
                        )
                        match = match[0]
                        if (match.home_score_total > match.away_score_total) {
                            if(match.home_team.current_abbreviation == sortable[i][0]) {
                                sortable[j-1][1] += 0.5
                            } else {
                                sortable[i][1] += 0.5
                            }
                        } else if (match.home_score_total < match.away_score_total) {
                            if(match.home_team.current_abbreviation == sortable[i][0]) {
                                sortable[i][1] += 0.5
                            } else {
                                sortable[j-1][1] += 0.5
                            }
                        } else {
                            let team_i = big_arr.filter(e => e.current_abbreviation == sortable[i][0])[0]
                            let team_j = big_arr.filter(e => e.current_abbreviation == sortable[j-1][0])[0]
                            if (team_i.match_average > team_j.match_average) {
                                sortable[i][1] += 0.5
                            } else { // We ignore == conditional. There is no way this can be same between two teams 
                                sortable[j-1][1] += 0.5
                            }
                        }
                        i = j
                    } else {
                        if (j-i == sortable.length) {
                            let tmp_sortable = []
                            sortable.forEach(e => {
                                let team = big_arr.filter(tmp_e => tmp_e.current_abbreviation == e[0])[0]
                                tmp_sortable.push([e[0], team.match_average])
                            }, tmp_sortable)
                            

                            tmp_sortable.sort((a,b) => b[1] - a[1])
                            let inc = 1 / sortable.length
                            for(let k = 0; k < tmp_sortable.length; k++) {
                                let tmp = tmp_sortable[k]
                                let team_index = sortable.map(e => e[0]).indexOf(tmp[0])
                                sortable[team_index][1] += inc*k
                            }

                        } else {
                            console.log('Dont come here') // Here sould come recursive call that call 'innerFunction'
                        }
                        i = j
                    }    
                    console.log(sortable)
                }
                sortable.sort((a,b) => b[1]-a[1])
                return sortable.map(ele => ele[0])
            }

            // Resolve "3 or more"- way ties
            this.teams.forEach(ele => {
                let i = 0
                let j = 0
                let points = 0
                while(i < ele.length) {
                    points = ele[i].points_total
                    j = i + 1
                    while (j < ele.length) {
                        if (ele[j].points_total != points) {
                            break
                        }
                        j++
                    }
                    if (j-i <= 2) {
                        i = j
                        continue
                    }
                    // Initialize match results with names
                    let match_results = {}
                    for (let k=i; k < j; k++) {
                        match_results[ele[k].current_abbreviation] = 0
                    }
                    let correct_order = innerFunction(match_results, this.bracket_matches, ele)
                    let datas = []
                    correct_order.forEach(name => {
                        datas.push(structuredClone(ele.filter(e => e.current_abbreviation == name)[0]))
                    })
                    let k = i
                    datas.forEach(data => {
                        ele[k] = data,
                        k++
                    }, k)
                    i = j
                }
            })
        },
        putTeamsPlayoffBracket: function () {
            const bracket_limit = sessionStorage.season_id in [24, 25] ? 11 : 16
            this.bracket_placements.forEach((bracket, idx) => {
                for (let i = 0; i < bracket_limit; i++) {
                    for (let matchIdx = 0; matchIdx < this.rounds.length; matchIdx++) {
                        let placementString = this.bracket_placements.length >= 2 ? String.fromCharCode(65+idx) + (i+1).toString()
                                                                    : (i+1).toString() + '. Seed'
                        let match = this.rounds[matchIdx] 
                        if (match.player1.name === placementString) {
                            match.player1.name = bracket[i][0]
                            break
                        } else if (match.player2.name === placementString) {
                            match.player2.name = bracket[i][0]
                            break
                        }
                    }
                }
            })
        },
        splitFirstRound: function() {
            let first_round_matches = this.rounds.filter(e => e.type == this.first)
            this.st_round = structuredClone(first_round_matches)
            this.data = this.rounds.filter(e => e.type != this.first)
            let games = this.tmp_rounds[this.first - 2]
            let winners = []
            for (const [key, el] of Object.entries(games)) {
                let match = this.st_round.filter(e => (Object.keys(el)[0] == e.player1.name || Object.keys(el)[0] == e.player2.name), el)
                if (match.length != 1) {
                    console.log('moi' + match)
                    console.log('Matches length not right: '+ match.length.toString())
                } else {
                    match = match[0]
                    if (el[match.player1.name] > el[match.player2.name]) {
                        winners.push(structuredClone(match.player1))
                        match.player1['winner'] = true
                        match.player2['winner'] = false
                    } else {
                        winners.push(structuredClone(match.player2))
                        match.player1['winner'] = false
                        match.player2['winner'] = true
                    }
                    match.other_info = el[match.player1.name].toString() + ' - ' + el[match.player2.name].toString()
                }
            }
            winners.sort((a,b) =>  Number(b.id) - Number(a.id))

            winners.forEach((ele, i) => {
                let placementString = (i+1).toString() + ". Low Seed"
                let new_match = this.rounds.filter(el => el.player1.name == placementString || el.player2.name == placementString)[0]
                if (new_match.player1.name.includes(placementString)) {
                    new_match.player1 = ele
                } else {
                    new_match.player2 = ele
                }
                
            })
        },
        resolvePlayoffs: function() {
            let reversed_list = this.tmp_rounds.reverse()
            reversed_list.forEach((ele, i) => {
                for (const [key, el] of Object.entries(ele)) {
                    let match = this.data.filter(e => e.type == 7-i && (Object.keys(el)[0] == e.player1.name || Object.keys(el)[0] == e.player2.name), el, i)
                    if (match.length != 1) {
                        console.log('moi' + match)
                        console.log('Matches length not right: '+ match.length.toString())
                    } else {
                        match = match[0]
                        let winner = ''
                        let loser = ''
                        if (el[match.player1.name] > el[match.player2.name]) {
                            winner = structuredClone(match.player1)
                            loser = structuredClone(match.player2)
                            match.player1['winner'] = true
                            match.player2['winner'] = false
                        } else {
                            winner = structuredClone(match.player2)
                            loser = structuredClone(match.player1)
                            match.player1['winner'] = false
                            match.player2['winner'] = true
                        }
                        match.other_info = el[match.player1.name].toString() + ' - ' + el[match.player2.name].toString()
                        if (7-i >= 4) {
                            if (7-i == 4) { // SemiFinals -> Loser needs to be assigned to Bronze match
                                let bronze_match = this.rounds.filter(ele => ele.type === 3)[0]
                                if (bronze_match.player1.name.includes(match.loser_name)) {
                                    bronze_match.player1 = loser
                                } else {
                                    bronze_match.player2 = loser
                                }
                                let finals = this.rounds.filter(ele => ele.type === 2)[0]
                                if (finals.player1.name.includes(match.name)) {
                                    finals.player1 = winner
                                } else {
                                    finals.player2 = winner
                                }
                            } else {
                                let new_match = this.rounds.filter(ele => ele.id === match.next)[0]
                                if (new_match.player1.name.includes(match.name)) {
                                    new_match.player1 = winner
                                } else {
                                    new_match.player2 = winner
                                }
                            }
                        }
                    }
                }
            })
        }
    },
    watch: {
        played_games() {
            this.bracket_matches = this.played_games.filter(ele => !ele.post_season)
            let playoff_games = this.played_games.filter(ele => ele.post_season)
            playoff_games.forEach(ele => {
                if (ele.match_type >= 2 & ele.match_type < 10) {
                    var round = this.tmp_rounds[ele.match_type - 2]
                    if (ele.seriers in round === false) {
                        round[ele.seriers] = {}
                        round[ele.seriers][ele.home_team.current_abbreviation] = 0
                        round[ele.seriers][ele.away_team.current_abbreviation] = 0
                    }
                    if (ele.home_score_total < ele.away_score_total) {
                        ++round[ele.seriers][ele.home_team.current_abbreviation]
                    } else if (ele.home_score_total > ele.away_score_total) {
                        ++round[ele.seriers][ele.away_team.current_abbreviation]
                    }
                }
            })
            this.putTeamsPlayoffBracket()
            if (this.first_round) {
                this.splitFirstRound()
            } else {
                this.data = this.rounds
            }
            this.resolvePlayoffs()
        }
    }
}
</script>
<style>
    .vtb-player {
        background-color: white;
        border-color: black;
        border-style: solid solid none solid;
        border-width: 1px;
        color: black;
        text-align: center;
    }
    .vtb-item-players .winner {
        color: white;
    }
    .vtb-item-players .defeated {
        color: white;
    }
    .vtb-item-players > div {
        width: 125px;
    }
</style>