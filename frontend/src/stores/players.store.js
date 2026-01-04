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
  "clearence_count",
  "clearence_throws_total",
  "scaled_points",
  "weighted_throw_total",
]
export const usePlayerStore = defineStore('players', () => {
  const _ids = ref({})
  const loading = ref(false);
  const loadingPlayer = ref(false);
  const loadedData = ref(false);
  const players = ref([]);
  const player = ref({})
  const playerMatchesPerPeriod = ref([]);
  const playerMatchesPerMatch = ref([]);
  const playersPositionsToggle = ref([]); // Used in players index page
  const emptyFilter = ref(false);
  const playoffFilter = ref(0);
  const aggregationSetting = ref(0); // 0: One season, 1: All season seperatly, 2: All players per season

  // Pre-Filtter that is for internal use only. This is applied before position filtter
  // and should lead better performance
  const stageFilter = computed(() => {
    if (players.value.length === 0) {
      return []
    }
    if (playoffFilter.value === 0) {
      return players.value;
    } else if (playoffFilter.value === 1) {
      return players.value.filter(obj => !obj.playoff)
    } else {
      return players.value.filter(obj => obj.playoff)
    }
  })

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
    const positionFiltered = stageFilter.value.filter(
      obj => positionsFilter.includes(obj["throw_turn"])
    );
    let jotain = Object.groupBy(positionFiltered, ({ player }) => player)

    // Add back the players that haven't thrown yet
    if (!emptyFilter.value) {
      const ids_included = [...Object.keys(jotain)]
      const ids_not_included = Object.keys(_ids.value).filter(key => !ids_included.includes(key))
      for (const player_id of ids_not_included) {
        jotain[player_id] = [{
          score_total: 0,
          pikes_total: 0,
          zeros_total: 0,
          gte_six_total: 0,
          match_count: 0,
          rounds_total: 0,
          throws_total: 0,
          scaled_points: 0,
          weighted_throw_total: 0,
          clearence_count: 0,
          clearence_throws_total: 0,
          player: _ids.value[player_id][0]["player"],
          player_name: _ids.value[player_id][0]["player_name"],
          team_name: _ids.value[player_id][0]["team_name"],
          season: _ids.value[player_id][0]["season"],
        }]
      }
    }

    if (aggregationSetting.value === 1) {
      let listId = 0
      const filteredData = Object.values(jotain).reduce((acc, playerStats) => {
        const yearStats = Object.groupBy(playerStats, ({ season }) => season)
        for (const yearStat of Object.values(yearStats)) {
          const extractedData = {
            id: listId++,
            player_id: yearStat[0]["player"],
            player_name: yearStat[0]["player_name"],
            team_name: yearStat[0]["team_name"],
            season: yearStat[0]["season"],
            score_total: 0,
            pikes_total: 0,
            zeros_total: 0,
            gte_six_total: 0,
            match_count: 0,
            rounds_total: 0,
            throws_total: 0,
            scaled_points: 0,
            clearence_count: 0,
            clearence_throws_total: 0,
            weighted_throw_total: 0,
            pike_percentage: Number.NaN,
            avg_throw_turn: Number.NaN,
            score_per_throw: Number.NaN,
            scaled_points_per_throw: Number.NaN,
          };
          for (const positionStat of yearStat) {
            for (const field of fields) {
              extractedData[field] += positionStat[field];
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
        }
        return acc;
      }, [])
      return filteredData;
    } else if (aggregationSetting.value === 0 || aggregationSetting.value === 2) {
      let listId = 0
      const filteredData = Object.values(jotain).reduce((acc, playerStats) => {
        const extractedData = {
          id: listId++,
          player_id: playerStats[0]["player"],
          player_name: playerStats[0]["player_name"],
          team_name: playerStats[0]["team_name"],
          season: playerStats[0]["season"],
          season_count: new Set(playerStats.map(obj => obj.season)).size,
          score_total: 0,
          pikes_total: 0,
          zeros_total: 0,
          gte_six_total: 0,
          match_count: 0,
          rounds_total: 0,
          throws_total: 0,
          scaled_points: 0,
          weighted_throw_total: 0,
          clearence_count: 0,
          clearence_throws_total: 0,
          pike_percentage: Number.NaN,
          avg_throw_turn: Number.NaN,
          score_per_throw: Number.NaN,
          scaled_points_per_throw: Number.NaN,
        };
        for (const positionStat of playerStats) {
          for (const field of fields) {
            extractedData[field] += positionStat[field];
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
      return filteredData
    }
  })


  /**
   * Get all player statistics from: 
   *    - Season if `season_id` is given
   *    - All season if `season_id` **not** given
   * 
   * When this function runs: `loading` is set to `true`
   * @async
   * @param {Number | null} [season_id=null] Specifies season, from which data is calculated
   * @returns {Promise} Player Statistics
   */
  async function getPlayers(season_id = null) {
    loading.value = true;
    let apiCall = baseUrl
    apiCall += season_id !== null ? '?season=' + season_id : ''
    const response = await fetch(apiCall, { method: 'GET' });
    players.value = await response.json();
    _ids.value = Object.groupBy(players.value, ({ player }) => player)
    loading.value = false;
  }

  async function getPlayer(playerIndex) {
    loadingPlayer.value = true;
    loadedData.value = false;
    const navStore = useNavBarStore();
    const question = playerIndex + '/?season=' + navStore.seasonId;
    try {
      const response = await fetch(baseUrl + question, { method: 'GET' });
      const payload = await response.json();

      player.value = payload;
      player.value.all_time_stats["season"] = "All Time"

    } catch (error) {
      console.log(error)
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
    playoffFiltter: playoffFilter,
    aggregationSetting,
    getPlayers,
    getPlayer,
  }
})