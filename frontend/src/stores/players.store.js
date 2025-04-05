import { useNavBarStore } from "./navbar.store";

const baseUrl = `${import.meta.env.VITE_API_URL}/players/`;

// TODO doc
function divide_round(value, divider) {
  return divider ? Math.round(value / divider * 100) / 100 : Number.NaN
}
// NOTE this must kept upto date with the API return values
const fields = [
  "score_total",
  "pikes_total",
  "zeros_total",
  "gte_six_total",
  "match_count",
  "rounds_total",
  "throws_total",
  "scaled_points",
  "weighted_throw_total",
]
export const usePlayerStore = defineStore('players', () => {
  const loading = ref(false);
  const loadingPlayer = ref(false);
  const loadedData = ref(false);
  const players = ref([]);
  const player = ref({})
  const playerMatchesPerPeriod = ref([]);
  const playerMatchesPerMatch = ref([]);
  const playersPositionsToggle = ref([]); // Used in players index page
  const emptyFilter = ref(false);
  const playoffFiltter = ref(0);

  // Pre-Filtter that is for internal use only. This is applied before position filtter
  // and should lead better performance
  const stageFilter = computed(() => {
    if (players.value.length === 0) {
      return []
    }
    let filterValues;
    if (playoffFiltter.value === 0) {
      filterValues = ["bracket", "playoff"]
    } else if (playoffFiltter.value === 1) {
      filterValues = ["bracket"]
    } else {
      filterValues = ["playoff"]
    }

    return players.value.reduce((acc, obj) => {
      const extractedData = {
        player_id: obj.player,
        player_name: obj.player_name,
        team_name: obj.team_name,
      };
      for (const stage of filterValues) {
        if (obj[stage] === undefined) {
          continue;
        }
        for (const position of [1, 2, 3, 4]) {
          if (obj[stage][position] == undefined) {
            continue;
          }
          if (extractedData[position] === undefined) {
            extractedData[position] = structuredClone(toRaw(obj[stage][position]));
          } else {
            for (const field of fields) {
              extractedData[position][field] += obj[stage][position][field];
            }
          }
        }
      }
      acc.push(extractedData)
      return acc
    }, [])
  })

  // TODO add also players who hasn't throw any throws yet.
  const playersPostionFilttered = computed(() => {
    if (stageFilter.value.length === 0) {
      return []
    }
    let positionsFilter;
    if (!playersPositionsToggle.value.length) {
      positionsFilter = [1, 2, 3, 4];
    } else {
      positionsFilter = playersPositionsToggle.value;
    }
    let listId = 0
    const filteredData = stageFilter.value.reduce((acc, item) => {
      const extractedData = {
        id: listId++,
        player_id: item.player,
        player_name: item.player_name,
        team_name: item.team_name,
        score_total: 0,
        pikes_total: 0,
        zeros_total: 0,
        gte_six_total: 0,
        match_count: 0,
        rounds_total: 0,
        throws_total: 0,
        scaled_points: 0,
        weighted_throw_total: 0,
        pike_percentage: Number.NaN,
        avg_throw_turn: Number.NaN,
        score_per_throw: Number.NaN,
        scaled_points_per_throw: Number.NaN,
      };
      for (const position of positionsFilter) {
        const nestedData = item[position];
        if (!nestedData) {
          continue;
        }
        for (const field of fields) {
          extractedData[field] += nestedData[field];
        }
      }
      extractedData.pike_percentage = divide_round(
        extractedData.pikes_total * 100, extractedData.throws_total
      );
      extractedData.avg_throw_turn = divide_round(
        extractedData.weighted_throw_total, extractedData.throws_total
      );
      extractedData.score_per_throw = divide_round(
        extractedData.score_total, extractedData.throws_total
      );
      extractedData.scaled_points_per_throw = divide_round(
        extractedData.scaled_points, extractedData.throws_total
      );
      acc.push(extractedData);
      return acc
    }, []);

    if (emptyFilter.value) {
      return filteredData.filter(obj => obj.rounds_total)
    }
    return filteredData
  })


  async function getPlayers() {
    loading.value = true;
    const navStore = useNavBarStore();
    const question = '?season=' + navStore.seasonId;
    const response = await fetch(baseUrl + question, { method: 'GET' });
    const payload = await response.json();
    players.value = payload.filter(obj => obj.player);
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
    playersPositionsToggle,
    playersPostionFilttered,
    emptyFiltter: emptyFilter,
    playoffFiltter,
    getPlayers,
    getPlayer,
  }
})