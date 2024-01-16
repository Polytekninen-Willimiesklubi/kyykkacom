<template>
    <bracket :flat-tree="rounds">
        <template slot="player" slot-scope="{player}">
            {{player.name}}
        </template>
        <template #player-extension-bottom="{ match }">
            {{ match.other_info }}
        </template>
    </bracket>
</template>


<script>
import Bracket from "vue-tournament-bracket";

export default {
    name: 'Tournament',
    props: {
        type: Number,
        played_games: Array
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
                    id: 1,
                    next: 7,
                    player1: { id: "19", name: "B8", winner: true},
                    player2: { id: "9", name: "A9"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 2,
                    next: 9,
                    player1: { id: "7", name: "A7"},
                    player2: { id: "21", name: "B10"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 3,
                    next: 10,
                    player1: { id: "17", name: "B6"},
                    player2: { id: "11", name: "A11"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 4,
                    next: 11,
                    player1: { id: "8", name: "A8"},
                    player2: { id: "20", name: "B9"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 5,
                    next: 13,
                    player1: { id: "18", name: "B7"},
                    player2: { id: "10", name: "A10"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 6,
                    next: 14,
                    player1: { id: "6", name: "A6"},
                    player2: { id: "22", name: "B11"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 7,
                    next: 15,
                    player1: { id: "1", name: "A1"},
                    player2: { id: "-1", name: "B8 / A9"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 8,
                    next: 15,
                    player1: { id: "15", name: "B4"},
                    player2: { id: "8", name: "A5"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 9,
                    next: 16,
                    player1: { id: "13", name: "B2"},
                    player2: { id: "-2", name: "A7 / B10"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 10,
                    next: 16,
                    player1: { id: "3", name: "A3"},
                    player2: { id: "-3", name: "B6 / A11"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 11,
                    next: 17,
                    player1: { id: "12", name: "B1"},
                    player2: { id: "-4", name: "A8 / B9"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 12,
                    next: 17,
                    player1: { id: "4", name: "A4"},
                    player2: { id: "16", name: "B5"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 13,
                    next: 18,
                    player1: { id: "2", name: "A2"},
                    player2: { id: "-6", name: "B7 / A10"},
                },
                {
                    other_info:"Kahteen voittoon",
                    id: 14,
                    next: 18,
                    player1: { id: "14", name: "B3"},
                    player2: { id: "-7", name: "A6 / B11"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    id: 15,
                    next: 19,
                    player1: { id: "-8", name: "Q1 (A1 - C3)"},
                    player2: { id: "-9", name: "Q8 (B4 - A5)"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    id: 16,
                    next: 19,
                    player1: { id: "-10", name: "Q4 (B2 - D2)"},
                    player2: { id: "-11", name: "Q5 (A3 - C1)"},
                }, 
                {
                    other_info:"Kolmeen voittoon",
                    id: 17,
                    next: 20,
                    player1: { id: "-12", name: "Q2 (B1 - D3)"},
                    player2: { id: "-13", name: "Q7 (A4 - B5)"},
                }, 
                {
                    other_info:"Kolmeen voittoon",
                    id: 18,
                    next: 20,
                    player1: { id: "-14", name: "Q3 (A2 - C2)"},
                    player2: { id: "-15", name: "Q6 (B3 - D1)"},
                }, 
                {
                    other_info:"Kolmeen voittoon",
                    id: 19,
                    next: 21,
                    player1: { id: "-16", name: "S1 (Q1 - Q8)"},
                    player2: { id: "-17", name: "S4 (Q4 - Q5)"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    id: 20,
                    next: 21,
                    player1: { id: "-18", name: "S2 (Q2 - Q7)"},
                    player2: { id: "-19", name: "S3 (Q3 - Q6)"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    id: 21,
                    next: 22,
                    player1: { id: "-20", name: "P1 (L S1 - S4)"},
                    player2: { id: "-21", name: "P2 (L S2 - S3)"},
                },
                {
                    other_info:"Kolmeen voittoon",
                    id: 22,
                    player1: { id: "-22", name: "F1 (W S1 - S4)"},
                    player2: { id: "-23", name: "F2 (W S2 - S3)"},
                },
            ]
        }
    },
    mounted() {
        // if (this.type == 1) {
        //     rounds = defaul
        // }
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
    .vtb-item-players .winner {
        color: white;
    }
</style>