<template>
    <bracket :flat-tree="rounds" class="jotain">
        <template slot="player" slot-scope="{player}" class="jotain">
            {{player.name}}
        </template>
        <template #player-extension-bottom="{ match }">
            <div align="center">
                {{ match.other_info }}
            </div>
        </template>
    </bracket>
</template>


<script>
import Bracket from "vue-tournament-bracket";

export default {
    name: 'Tournament',
    props: {
        type: Number,
        played_games: Array,
        bracket_results: Array
    },
    components: {
    Bracket
},
    data() {
        return {
            rounds: [
                // 1/16 finals
                {
                    other_info:"Kahteen voittoon",
                    name: 'C3',
                    type: 7,
                    id: 1,
                    next: 7,
                    player1: { id: "19", name: "B8"},
                    player2: { id: "9", name: "A9"}
                },
                {
                    other_info:"Kahteen voittoon",
                    name: 'D2',
                    type: 7,
                    id: 2,
                    next: 9,
                    player1: { id: "7", name: "A7"},
                    player2: { id: "21", name: "B10"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: 'C1',
                    type: 7,
                    id: 3,
                    next: 10,
                    player1: { id: "17", name: "B6"},
                    player2: { id: "11", name: "A11"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name:"D3",
                    type: 7,
                    id: 4,
                    next: 11,
                    player1: { id: "8", name: "A8"},
                    player2: { id: "20", name: "B9"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "C2",
                    type: 7,
                    id: 5,
                    next: 13,
                    player1: { id: "18", name: "B7"},
                    player2: { id: "10", name: "A10"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "D1",
                    type: 7,
                    id: 6,
                    next: 14,
                    player1: { id: "6", name: "A6"},
                    player2: { id: "22", name: "B11"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "Q1",
                    type: 6,
                    id: 7,
                    next: 15,
                    player1: { id: "1", name: "A1"},
                    player2: { id: "-1", name: "B8 / A9"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "Q8",
                    type: 6,
                    id: 8,
                    next: 15,
                    player1: { id: "15", name: "B4"},
                    player2: { id: "8", name: "A5"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "Q4",
                    type: 6,
                    id: 9,
                    next: 16,
                    player1: { id: "13", name: "B2"},
                    player2: { id: "-2", name: "A7 / B10"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "Q5",
                    type: 6,
                    id: 10,
                    next: 16,
                    player1: { id: "3", name: "A3"},
                    player2: { id: "-3", name: "B6 / A11"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "Q2",
                    type: 6,
                    id: 11,
                    next: 17,
                    player1: { id: "12", name: "B1"},
                    player2: { id: "-4", name: "A8 / B9"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "Q7",
                    type: 6,
                    id: 12,
                    next: 17,
                    player1: { id: "4", name: "A4"},
                    player2: { id: "16", name: "B5"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "Q3",
                    type: 6,
                    id: 13,
                    next: 18,
                    player1: { id: "2", name: "A2"},
                    player2: { id: "-6", name: "B7 / A10"},
                },
                {
                    other_info:"Kahteen voittoon",
                    name: "Q6",
                    type: 6,
                    id: 14,
                    next: 18,
                    player1: { id: "14", name: "B3"},
                    player2: { id: "-7", name: "A6 / B11"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    name: "S1",
                    type: 5,
                    id: 15,
                    next: 19,
                    player1: { id: "-8", name: "Q1 (A1 - C3)"},
                    player2: { id: "-9", name: "Q8 (B4 - A5)"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    name: "S4",
                    type: 5,
                    id: 16,
                    next: 19,
                    player1: { id: "-10", name: "Q4 (B2 - D2)"},
                    player2: { id: "-11", name: "Q5 (A3 - C1)"},
                }, 
                {
                    other_info:"Kolmeen voittoon",
                    name: "S2",
                    type: 5,
                    id: 17,
                    next: 20,
                    player1: { id: "-12", name: "Q2 (B1 - D3)"},
                    player2: { id: "-13", name: "Q7 (A4 - B5)"},
                }, 
                {
                    other_info:"Kolmeen voittoon",
                    name: "S3",
                    type: 5,
                    id: 18,
                    next: 20,
                    player1: { id: "-14", name: "Q3 (A2 - C2)"},
                    player2: { id: "-15", name: "Q6 (B3 - D1)"},
                }, 
                {
                    other_info:"Kolmeen voittoon",
                    name: "F1",
                    loser_name:'P1',
                    type: 4,
                    id: 19,
                    next: 21,
                    player1: { id: "-16", name: "S1 (Q1 - Q8)"},
                    player2: { id: "-17", name: "S4 (Q4 - Q5)"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    name: "F2",
                    loser_name: "P2",
                    type: 4,
                    id: 20,
                    next: 21,
                    player1: { id: "-18", name: "S2 (Q2 - Q7)"},
                    player2: { id: "-19", name: "S3 (Q3 - Q6)"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    type: 3,
                    id: 21,
                    next: 22,
                    player1: { id: "-20", name: "P1 (L S1 - S4)"},
                    player2: { id: "-21", name: "P2 (L S2 - S3)"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    type: 2,
                    id: 22,
                    player1: { id: "-22", name: "F1 (W S1 - S4)"},
                    player2: { id: "-23", name: "F2 (W S2 - S3)"},
                },
            ],
            tmp_rounds: [{}, {}, {}, {}, {}, {}],
            multible_brackets: false,
            data: [],
            teams: [],
            bracket_matches: []
        }
    },
    mounted() {
        if (this.teams.length == 0) {
            this.splitToBrackets()
        }
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
            console.log(this.teams)
            this.teams.forEach(ele => {
                ele.sort((a,b) => {
                    let total = b.points_total - a.points_total
                    // Order sort: bracket points
                    if (total < 0) {
                        return -1
                    } else if (total > 0) {
                        return 1 
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
                    if (a.current_abbreviation == bracket_match.home_team.current_abbreviation) {
                        console.log(a.current_abbreviation, b.current_abbreviation)
                        let match_result = bracket_match.away_score_total - bracket_match.home_score_total
                        if (match_result < 0) {
                            return 1
                        } else if (match_result > 0) {
                            return -1
                        }
                    } else {
                        let match_result = bracket_match.home_score_total - bracket_match.away_score_total
                        if (match_result < 0) {
                            return 1
                        } else if (match_result > 0) {
                            return -1
                        }
                    }
                    // Second Tiebreaker: Match average
                    let average_total = b.match_average - a.match_average
                    if (average_total < 0) {
                        return 1
                    } else if (average_total > 0) {
                        return -1
                    }
                    // Third Tiebreaker: Chance, not implemented here
                    return 0
                })
            })
        },
        putTeamsPlayoffBracket: function () {
            this.teams.forEach((ele, idx) => {
            for (let i = 0; i < 11; i++) {
                for (let matchIdx = 0; matchIdx < this.rounds.length; matchIdx++) {
                    let placementString = String.fromCharCode(65+idx) + (i+1).toString()
                    let match = this.rounds[matchIdx] 
                    if (match.player1.name === placementString) {
                        match.player1.name = ele[i].current_abbreviation
                        break
                    } else if (match.player2.name === placementString) {
                        match.player2.name = ele[i].current_abbreviation
                        break
                    }
                }
            }
        })
        },
        resolvePlayoffs: function() {
            let reversed_list = this.tmp_rounds.reverse()
            reversed_list.forEach((ele, i) => {
                for (const [key, el] of Object.entries(ele)) {
                    console.log(el)
                    let match = this.rounds.filter(e => e.type == 7-i && (Object.keys(el)[0] == e.player1.name || Object.keys(el)[0] == e.player2.name), el, i)
                    if (match.length != 1) {
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
            console.log(this.played_games)
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
            if (this.teams.length == 0) {
                this.splitToBrackets()
            }
            this.sortTeams()
            this.putTeamsPlayoffBracket()
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