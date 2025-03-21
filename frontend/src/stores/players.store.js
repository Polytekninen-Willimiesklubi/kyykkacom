import { useNavBarStore } from "./navbar.store";

const baseUrl = `${import.meta.env.VITE_API_URL}/players/`;

export const usePlayerStore = defineStore('players', () => {
  const loading = ref(false);
  const loadingPlayer = ref(false);
  const loadedData = ref(false);
  const players = ref([]);
  const player = ref({})
  const playerMatchesPerPeriod = ref([]);
  const playerMatchesPerMatch = ref([]);

  async function getPlayers() {
    loading.value = true;
    const navStore = useNavBarStore();
    const question = '?season=' + navStore.seasonId;
    const response = await fetch(baseUrl + question, { method: 'GET' });
    const payload = await response.json();

    players.value = payload;
    loading.value = false;
  }

  async function getPlayer(playerIndex) {
    loadingPlayer.value = true;
    const navStore = useNavBarStore();
    const question = playerIndex + '/?season=' + navStore.seasonId;
    try {
      const response = await fetch(baseUrl + question, { method: 'GET' });
      const payload = await response.json();

      player.value = payload;
    } catch (error) {
      console.log(error)
    }

    for (const season of player.value.stats_per_seasons) {
      for (const match of season.matches) {
        for (let i = 1; i < 3; i++) {
          if (i == 1 && match.throw_turn_one != '-') {
            var own_score = match.own_score_first
            var opp_score = match.opponent_score_first
            var throw_turn = match.throw_turn_one
            var first = match.score_first
            var second = match.score_second
            var third = match.score_third
            var fourth = match.score_fourth
            var average = match.score_average_round_one
            var total = match.score_total_one
          } else if (i == 2 && match.throw_turn_two != '-') {
            var own_score = match.own_score_second
            var opp_score = match.opponent_score_second
            var throw_turn = match.throw_turn_two
            var first = match.score_fifth
            var second = match.score_sixth
            var third = match.score_seventh
            var fourth = match.score_eighth
            var average = match.score_average_round_two
            var total = match.score_total_two
          } else {
            continue
          }
          playerMatchesPerPeriod.value.push({
            id: match.id * 2 + (i - 1),
            match_id: match.id,
            season: season.season,
            own_score_round: own_score,
            opp_score_round: opp_score,
            opp_name: match.opponent_name,
            match_time: match.match_time,
            period: i,
            turn: throw_turn,
            score_first: first,
            score_second: second,
            score_third: third,
            score_fourth: fourth,
            score_total: total,
            score_average_round: average
          })
        }
        const input = match
        input.season = season.season
        input.match_id = match.id
        input.id = match.id
        playerMatchesPerMatch.value.push(input)
      }
    }

    loadingPlayer.value = false;
    loadedData.value = true;
  }

  return {
    loading,
    loadingPlayer,
    loadedData,
    players,
    player,
    playerMatchesPerPeriod,
    playerMatchesPerMatch,
    getPlayers,
    getPlayer,
  }
})