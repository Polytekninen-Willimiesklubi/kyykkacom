<template>
    <v-flex v-if="loaded_undefined">
        <div align="center">
            <h1>TBD</h1>
        </div>
    </v-flex>
    <v-layout v-else>
        <div v-if="st_round.length" class="pr-10">
            <div v-for="listItem in st_round" :key="listItem.name" class="pt-10">
                <bracket :flat-tree="[listItem]">
                    <template slot="player" slot-scope="{player}">
                        {{ !only_format ? player.name : player.template_name }}
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
                    {{ !only_format ? player.name : player.template_name }}
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
        rounds_parrent: Array,
        first_round: Boolean,
        first: Number,
        only_format: Boolean,
        bracket_placements: Array,
        load_ended: Boolean,
        non_default_seeds: Array,
        bronze: {
            type: Boolean,
            default: true,
        }
    },
    components: {
    Bracket
},
    data() {
        return {
            tmp_rounds: [{}, {}, {}, {}, {}, {}],
            rounds: [],
            data: [],
            bracket_matches: [],
            st_round: [],
            loaded_undefined: false
        }
    },
    methods: {
        putTeamsPlayoffBracket() {
            console.log(this.rounds)
            if (this.non_default_seeds !== undefined) {
                this.non_default_seeds.forEach(ele => {
                    console.log(ele)
                    if (ele[1] !== undefined) {
                        for (let matchIdx = 0; matchIdx < this.rounds.length; matchIdx++) {
                            let placementString = (ele[1]).toString() + '. Seed'
                            let match = this.rounds[matchIdx] 
                            if (match.player1.name.startsWith(placementString)) {
                                match.player1.name = ele[0]
                                break
                            } else if (match.player2.name.startsWith(placementString)) {
                                match.player2.name = ele[0]
                                break
                            }
                        }
                    }
                })
            } else {
                this.bracket_placements.forEach((bracket, idx) => {
                    for (let i = 0; i < bracket.length; i++) {
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
            }
        },
        resolveGames() {
            this.bracket_matches = this.played_games.filter(ele => !ele.post_season)
            let playoff_games = this.played_games.filter(ele => ele.post_season || ele.match_type >= 32)
            playoff_games.forEach(ele => {
                ele.match_type =  ele.match_type >= 32 ? ele.match_type - 30 : ele.match_type
            })
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
        },
        loadRounds() {
            if (this.rounds_parrent.length == 0) {
                this.loaded_undefined = true
                return
            }
            this.rounds = structuredClone(this.rounds_parrent)
            this.rounds.forEach(ele => {
                ele.player1['template_name'] = ele.player1['name']
                ele.player2['template_name'] = ele.player2['name']
            })
            this.loaded_undefined = false
        },
        splitFirstRound() {
            if (!this.first_round) {
                this.data = this.rounds
                return
            }
            let first_round_matches = this.rounds.filter(e => e.type == this.first)
            this.st_round = first_round_matches
            let games = this.tmp_rounds[this.first - 2]
            let winners = []
            for (const [key, el] of Object.entries(games)) {
                let match = this.st_round.find(e => e.player1.name == Object.keys(el)[0] || e.player2.name == Object.keys(el)[0])
                if (match === undefined) {
                    console.log("Didn't find correct match. First round +  element: " + Object.keys(el))
                    return
                }
                let winner_team = el[match.player1.name] > el[match.player2.name] ? match.player1 : match.player2
                let loser_team = el[match.player1.name] > el[match.player2.name] ? match.player2 : match.player1
                let new_winner_team = structuredClone(winner_team)
                new_winner_team['winner'] = null
                winners.push(new_winner_team)
                winner_team['winner'] = true
                loser_team['winner'] = false
                match.other_info = el[match.player1.name].toString() + ' - ' + el[match.player2.name].toString()
            }
            winners.sort((a,b) =>  Number(b.id) - Number(a.id))
            winners.forEach((winner, i) => {
                let placementString = (i+1).toString() + ". Low Seed"
                let new_match = this.rounds.find(el => el.player1.name == placementString || el.player2.name == placementString)
                let correct_column = new_match.player1.name.includes(placementString) ? 'player1' : 'player2'
                let template = new_match[correct_column].template_name 
                winner.template_name = template
                new_match[correct_column] = winner
            })
            this.data = this.rounds.filter(e => e.type != this.first)
        },
        resolvePlayoffs() {
            let reversed_list = this.tmp_rounds.reverse()
            reversed_list.forEach((ele, i) => {
                for (const [key, el] of Object.entries(ele)) {
                    if (this.first_round && this.first == 7-i) { continue }
                    let match = this.data.find(e => e.type == 7-i && (Object.keys(el)[0] == e.player1.name || Object.keys(el)[0] == e.player2.name))
                    if (match === undefined) {
                        console.log("Didn't find correct match. type: " + 7-i + " element: " + Object.keys(el))
                        return
                    }
                    if (el[match.player1.name] !== el[match.player2.name]) { // Not a tie
                        let winner = el[match.player1.name] > el[match.player2.name] ? match.player1 : match.player2
                        let loser = el[match.player1.name] > el[match.player2.name] ? match.player2 : match.player1
                        let new_winner = structuredClone(winner)
                        let new_loser = structuredClone(loser)
                        new_winner['winner'] = null
                        new_loser['winner'] = null
                        winner['winner'] = true
                        loser['winner'] = false
                        match.other_info = el[match.player1.name].toString() + ' - ' + el[match.player2.name].toString()
                        if (7-i >= 4) { // Ignore Bronze and Finals
                            if (7-i == 4) { // SemiFinals -> Winner needs to be assigned to Finals
                                let finals = this.rounds.find(ele => ele.type === 2)
                                let correct_column = finals.player1.name.includes(match.name) ? 'player1' : 'player2'
                                let template = finals[correct_column].template_name
                                new_winner.template_name = template
                                finals[correct_column] = new_winner
                            }
                            let new_match = this.rounds.find(ele => ele.id === match.next)
                            let n = (7-i != 4) ? 'name' : 'loser_name'
                            let correct_column = new_match.player1.name.includes(match[n]) ? 'player1' : 'player2'
                            let template = new_match[correct_column].template_name
                            
                            new_match[correct_column] = (7-i == 4) && this.bronze ? new_loser : new_winner // SemiFinals -> Loser needs to be assigned to Bronze match
                            new_match[correct_column].template_name = template
                        }
                    }
                }
            }, this)
        }
    },
    watch: {
        load_ended() {
            this.loadRounds()
            if (!this.loaded_undefined) {
                this.resolveGames()
                this.putTeamsPlayoffBracket()
                this.splitFirstRound()
                this.resolvePlayoffs()
            }
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
        width: 135px;
    }
</style>