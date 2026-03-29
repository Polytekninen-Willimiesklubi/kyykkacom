import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useNavBarStore } from '@/stores/navbar.store';
import { useAuthStore } from '@/stores/auth.store';
import { fetchWrapper, withLoading } from '@/utils/fetchWrapper';
import { getLocal } from '@/utils/localUtils';
import type {
  AllTimeSingleTeamStats,
  AccoladeRecord,
  MatchRecord,
  PlayerStats,
  AllTeamsSingleTeamStatsAllTime,
  AllTeamsSingleTeamStats,
  AllTeamsSingleTeamStatsBracket,
  TeamDetails,
  SingleTeamStats,
  TeamsListResponse,
} from '@/types/api';
import type { AllOrNone, NumericalString } from '@/types/utils';

const baseUrl = `${import.meta.env.VITE_API_URL}/teams/`;
const reserveUrl = `${import.meta.env.VITE_API_URL}/reserve/`;

type TeamWithBracket = AllTeamsSingleTeamStatsBracket & { bracket: number };
const hasBrackets = (team: AllTeamsSingleTeamStatsBracket): team is TeamWithBracket =>
  !!team.bracket;

type TeamWithNdBracket = AllTeamsSingleTeamStatsBracket & { second_stage_bracket: number };

interface SeasonsStatsPerAggregationType {
  all?: AllTeamsSingleTeamStatsAllTime[];
  bracket?: AllTeamsSingleTeamStatsBracket[];
  playoff?: AllTeamsSingleTeamStats[];
}

interface ReservePlayer {
  id: number;
  player_name: string;
}

const FilterSetting = {
  ALL: 0,
  BRACKET: 1,
  PLAYOFF: 2,
} as const;
type FilterSetting = (typeof FilterSetting)[keyof typeof FilterSetting];

const AggregationSetting = {
  PER_SEASON: 1,
  ALL_TIME: 2,
} as const;
type AggregationSetting = (typeof AggregationSetting)[keyof typeof AggregationSetting];

export const useTeamsStore = defineStore('joukkue', () => {
  const allTimeStats = ref<AllOrNone<AllTimeSingleTeamStats>>({});
  const seasonsStats = ref<Record<NumericalString, SingleTeamStats>>({});
  const allTeamsAllSeasonsStats = ref<SeasonsStatsPerAggregationType>({});
  const allTeamsAllTimeStats = ref<SeasonsStatsPerAggregationType>({});
  const selectedSeasonId = ref<'allTime' | NumericalString>('allTime');
  const unReservedPlayers = ref<ReservePlayer[]>([]);
  // Local storage values
  const allTeams = ref<AllTeamsSingleTeamStatsBracket[]>(getLocal('allTeams') || []);
  const seasonTeamAccolades = ref<Record<string, AccoladeRecord[]>>(
    getLocal('seasonTeamAccolades') || {},
  );
  const secondStage = ref<AllTeamsSingleTeamStatsBracket[]>(getLocal('secondStage') || []);
  /**************/
  const loading = ref<boolean>(false);
  const singleLoading = ref<boolean>(false);
  const reserveLoading = ref<boolean>(false);
  const reserveAllowed = ref<boolean>(true);
  const filterSetting = ref<FilterSetting>(FilterSetting.ALL);
  const aggregationSetting = ref<AggregationSetting>(AggregationSetting.PER_SEASON);

  const seasonStats = computed<AllOrNone<SingleTeamStats | AllTimeSingleTeamStats>>(() => {
    if (selectedSeasonId.value === 'allTime') {
      return allTimeStats.value;
    }
    return Object.keys(seasonsStats.value).length ? seasonsStats.value[selectedSeasonId.value] : {};
  });

  const seasonPlayers = computed<PlayerStats[]>(() => {
    return seasonStats.value.players || [];
  });

  const teamName = computed<string>(() => {
    // TODO - More elegant way would be to get teamName from API instead of calculating it here.
    if (!('current_name' in seasonStats.value)) {
      const latestIndex = Math.max(...Object.keys(seasonsStats.value).map((x) => +x));
      return seasonsStats.value[`${latestIndex}`].current_name;
    }
    return seasonStats.value.current_name || '';
  });

  const matches = computed<MatchRecord[]>(() => {
    return seasonStats.value.matches || [];
  });

  const bracketedTeams = computed<AllTeamsSingleTeamStatsBracket[][]>(() => {
    const navStore = useNavBarStore();
    if (!navStore.selectedSeason?.no_brackets || allTeams.value.length === 0) {
      return [];
    }
    // Separate teams into brackets by putting them into different arrays
    const returnedTeams: AllTeamsSingleTeamStatsBracket[][] = Array.from(
      { length: navStore.selectedSeason.no_brackets },
      () => [],
    );
    //
    allTeams.value.filter(hasBrackets).forEach((ele) => returnedTeams[ele.bracket - 1].push(ele));
    return returnedTeams;
  });

  const secondStageBrackets = computed<AllTeamsSingleTeamStatsBracket[][]>(() => {
    const navStore = useNavBarStore();
    if (
      !navStore.selectedSeason ||
      navStore.selectedSeason.playoff_format !== 8 ||
      allTeams.value.length === 0
    ) {
      return [[], [], []];
    }
    // Only one format uses second stage brackets, so we can hardcode the number of brackets
    const returnedTeams: AllTeamsSingleTeamStatsBracket[][] = [[], [], []];
    const hasNdBracket = (team: AllTeamsSingleTeamStatsBracket): team is TeamWithNdBracket =>
      !!team.second_stage_bracket;
    secondStage.value
      .filter(hasNdBracket)
      .forEach((ele) => returnedTeams[ele.second_stage_bracket - 1].push(ele));
    return returnedTeams;
  });

  const onlyPlacements = computed<[string, number | null][][]>(() => {
    const navStore = useNavBarStore();
    if (!navStore.selectedSeason?.no_brackets || allTeams.value.length === 0) {
      return [];
    }

    const teams: [string, number | null][][] = Array.from(
      { length: navStore.selectedSeason.no_brackets },
      () => [],
    );

    allTeams.value.filter(hasBrackets).forEach((ele) => {
      teams[ele.bracket - 1].push([ele.current_abbreviation, ele.bracket_placement || null]);
    });
    return teams;
  });

  const seasonAggregationStats = computed<SeasonsStatsPerAggregationType>(() => {
    switch (aggregationSetting.value) {
      case AggregationSetting.PER_SEASON:
        return allTeamsAllSeasonsStats.value;
      case AggregationSetting.ALL_TIME:
        return allTeamsAllTimeStats.value;
      default:
        console.warn('Incorrect aggregation setting: ' + aggregationSetting.value);
        return {};
    }
  });

  const filteredAllResults = computed<AllTeamsSingleTeamStats[]>(() => {
    const values = seasonAggregationStats.value;
    switch (filterSetting.value) {
      case FilterSetting.ALL:
        return values?.all ?? [];
      case FilterSetting.BRACKET:
        return values?.bracket ?? [];
      case FilterSetting.PLAYOFF:
        return values?.playoff ?? [];
      default:
        console.warn('Incorrect filter setting: ' + filterSetting.value);
        return [];
    }
  });

  async function getTeams(seasonId: number | undefined = undefined): Promise<void> {
    const navStore = useNavBarStore();
    let _id: number | null = null;
    if (seasonId !== undefined) {
      _id = seasonId;
    } else {
      if (navStore.seasonId === undefined) {
        console.warn('Season Id was undefined');
        return;
      }
      _id = navStore.seasonId;
    }
    const question = '?season=' + _id + '&post_season=0';
    await withLoading(loading, async () => {
      const payload = (await fetchWrapper(
        baseUrl + question,
        {},
        'GET',
        true,
      )) as TeamsListResponse;
      if (navStore.selectedSeason?.playoff_format === 8) {
        allTeams.value = payload['first_stage'] || [];
        secondStage.value = payload['bracket'] || [];
      } else {
        allTeams.value = payload['bracket'] || [];
        secondStage.value = [];
      }
      localStorage.setItem('allTeams', JSON.stringify(allTeams.value));
      localStorage.setItem('secondStage', JSON.stringify(secondStage.value));

      // Filter and Add on accolades to teams seperately since all are not wanted, only major
      // accolades.
      // // TODO This could come from backend rather than doing this filtering here.
      seasonTeamAccolades.value = {};
      const accolades = payload.accolades || {};
      for (const [teamId, teamAccolades] of Object.entries(accolades)) {
        for (const accolade of teamAccolades) {
          const shouldAdd =
            (accolade.name === 'Runkosarjamestaruus' && accolade.placement === 1) ||
            (accolade.name === 'SuperWeekend-Cup' && accolade.placement === 1) ||
            (accolade.name === 'Liigamestaruus' && [1, 2, 3].includes(accolade.placement));

          if (shouldAdd) {
            if (!(teamId in seasonTeamAccolades.value)) {
              seasonTeamAccolades.value[teamId] = [];
            }
            if (accolade.placement === 2) {
              accolade.icon = 'hopea.ico';
            } else if (accolade.placement === 3) {
              accolade.icon = 'pronssi.ico';
            }
            seasonTeamAccolades.value[teamId].push(accolade);
          }
        }
      }
      localStorage.setItem('seasonTeamAccolades', JSON.stringify(seasonTeamAccolades.value));
    });
  }

  async function getTeamsAllSeasons(): Promise<void> {
    await withLoading(loading, async () => {
      const payload = (await fetchWrapper(baseUrl + 'all/', {}, 'GET', true)) as [
        SeasonsStatsPerAggregationType,
        SeasonsStatsPerAggregationType,
      ];

      allTeamsAllSeasonsStats.value = payload[0] || {};
      allTeamsAllTimeStats.value = payload[1] || {};
    });
  }

  async function getTeamPlayers(teamIndex: number): Promise<void> {
    await withLoading(singleLoading, async () => {
      const navStore = useNavBarStore();
      const url = baseUrl + teamIndex + '/?seasons=' + navStore.seasonId;
      const payload = (await fetchWrapper(url, {}, 'GET', true)) as TeamDetails;

      allTimeStats.value = payload.all_time;
      let recent_year = -1;
      for (const [key, value] of Object.entries(payload)) {
        if (key === 'all_time') continue;
        seasonsStats.value[key as NumericalString] = value as SingleTeamStats;
        recent_year = Number(key) > recent_year ? Number(key) : recent_year;
      }
      // Select the most recent year to single team page
      selectedSeasonId.value = recent_year !== -1 ? `${recent_year}` : 'allTime';
    });
  }

  async function getReserve(teamIndex: number): Promise<void> {
    await withLoading(reserveLoading, async () => {
      const url = reserveUrl + '?team=' + teamIndex;
      const payload = (await fetchWrapper(url, {}, 'GET', true)) as ReservePlayer[];

      unReservedPlayers.value = payload || [];
    });
  }

  async function reservePlayer(player: ReservePlayer): Promise<void> {
    const navStore = useNavBarStore();
    const authStore = useAuthStore();
    if (!authStore.loggedIn) {
      window.alert('Kirjaudu sisään varataksesi pelaajan.');
      return;
    }
    if (!window.confirm(`Haluatko varmasti varata pelaajan "${player.player_name}"?`)) {
      return;
    }
    const url = reserveUrl + '?season=' + navStore.seasonId + '&team=' + authStore.teamId;

    try {
      // TODO Feedback to user to response
      const response = await fetchWrapper(url, { player: player.id }, 'POST');
      if (response?.ok) {
        const index = unReservedPlayers.value.findIndex((item) => player.id === item.id);
        if (index > -1) {
          unReservedPlayers.value.splice(index, 1);
        }
      }
    } catch (error) {
      console.error(error);
    }
  }

  return {
    allTeams,
    loading,
    allTimeStats,
    seasonsStats,
    selectedSeasonId,
    seasonTeamAccolades,
    unReservedPlayers,
    seasonStats,
    seasonPlayers,
    bracketedTeams,
    onlyPlacements,
    singleLoading,
    reserveLoading,
    reserveAllowed,
    secondStageBrackets,
    teamName,
    matches,
    allTeamsAllTimeStats,
    allTeamsAllSeasonsStats,
    filterSetting,
    aggregationSetting,
    filteredAllResults,
    getTeams,
    getTeamPlayers,
    getTeamsAllSeasons,
    getReserve,
    reservePlayer,
  };
});
