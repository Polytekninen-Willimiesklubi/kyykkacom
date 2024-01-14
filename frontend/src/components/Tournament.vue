<template>
    <bracket :rounds="rounds">
        <template slot="player" slot-scope="{player}">
            {{player.name}}
        </template>
    </bracket>
</template>


<script>
import Bracket from "vue-tournament-bracket";

export default {
    name: 'Tournament',
    components: {
    Bracket
},
    data:  function() {
        return {
            rounds: [
        //Semi finals
                {
                    games: [
                        {
                            player1: { id: "1", name: "Competitor 1", winner: false },
                            player2: { id: "4", name: "Competitor 4", winner: true },
                        },
                        {

                            player1: { id: "5", name: "Competitor 5", winner: false },
                            player2: { id: "8", name: "Competitor 8", winner: true },
                        }
                    ]
                },
                //Final
                {
                    games: [
                        {
                            player1: { id: "4", name: "Competitor 4", winner: false },
                            player2: { id: "8", name: "Competitor 8", winner: true },
                        }
                    ]
                }
            ]
        }
    }
}
</script>