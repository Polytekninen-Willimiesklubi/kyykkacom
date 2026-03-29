/**
 * API Type Definitions
 * These interfaces match the Django backend serializers
 */

import { NumericalString } from '@/types/utils';

export interface Season {
  id: number;
  name: string;
  playoff_format: number;
  no_brackets: number;
}

export interface Team {
  id: number;
  name: string;
  season_id: number;
}

export interface Player {
  id: number;
  name: string;
  team_id: number;
  number?: number;
}

export interface Match {
  id: number;
  season_id: number;
  team1_id: number;
  team2_id: number;
  result?: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role_id: number;
}

export interface RoleType {
  CAPTAIN: 1;
  SUPERUSER: 2;
  [key: number]: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  user: {
    id: number;
    username: string;
    player_name: string;
  };
  role: number;
  team_id: number | null;
  team_season_id: number | null;
}

export interface PlayerStats {
  player: number;
  player_name: string;
  score_total: number;
  rounds_total: number;
  pikes_total: number;
  zeros_total: number;
  throws_total: number;
  scaled_points: number;
  gteSix_total: number;
  clearence_count: number;
  clearence_throws_total: number;
  score_per_throw: number | 'NaN';
  scaled_points_per_throw: number | 'NaN';
  pike_percentage: number | 'NaN';
  avg_throw_turn: number | 'NaN';
  // weighted_throw_count is used for single team page
  weighted_throw_count?: number;
}

export interface MatchRecord {
  id: number;
  match_time: string;
  match_type: string;
  opposite_team: string;
  own_first: number | null;
  own_second: number | null;
  opp_first: number | null;
  opp_second: number | null;
  own_team_total: number | null;
  opposite_team_total: number | null;
}

export interface AllTimeSingleTeamStats {
  score_total: number;
  match_count: number;
  pikes_total: number;
  zeros_total: number;
  throws_total: number;
  gteSix_total: number;
  zero_or_pike_first_throw_total: number;
  clearences: number;
  best_round: number | 'NaN';
  best_match: number | 'NaN';
  match_average: number | 'NaN';
  pike_percentage: number | 'NaN';
  zero_percentage: number | 'NaN';
  players: PlayerStats[];
  matches: MatchRecord[];
}

export type SingleTeamStats = AllTimeSingleTeamStats & {
  current_name: string;
  current_abbreviation: string;
};

export type TeamDetails = {
  all_time: AllTimeSingleTeamStats;
  [year: NumericalString]: SingleTeamStats;
};

export interface AllTeamsSingleTeamStatsPlayoff {
  id: number;
  team_id: number;
  current_name: string;
  current_abbreviation: string;
  bracket: number;
  bracket_placement: number | null;
  second_stage_bracket: number | null; // TODO check if this is even field always
  season: NumericalString;
  playoff: boolean;
  matches_lost: number;
  matches_won: number;
  matches_tie: number;
  matches_played: number;
  weighted_sum: number;
  best_round: number | 'NaN';
  best_match: number | 'NaN';
  clearences: number;
  points_total: number;
  match_type: string;
  match_average: number | 'NaN';
}

export type AllTeamsSingleTeamStatsBracket = AllTeamsSingleTeamStatsPlayoff & {
  points_average: number | 'NaN';
};

export type AllTeamsSingleTeamStatsAllTime = AllTeamsSingleTeamStatsPlayoff & {
  season_count: number;
};

export type AllTeamsSingleTeamStats =
  | AllTeamsSingleTeamStatsPlayoff
  | AllTeamsSingleTeamStatsBracket
  | AllTeamsSingleTeamStatsAllTime;

export interface StandingTeamStats {
  current_name: string;
  current_abbreviation: string;
  id: number;
  bracket?: number;
  bracket_placement?: number;
  second_stage_bracket?: number | null;
  players: PlayerStats[];
  matches: MatchRecord[];
}

export interface SeasonStats {
  [seasonId: number]: StandingTeamStats;
}

export interface AccoladeRecord {
  name: string;
  placement: number;
  season: number;
  icon?: string | null;
}

export interface TeamsListResponse {
  all: AllTeamsSingleTeamStats[];
  bracket: AllTeamsSingleTeamStatsBracket[];
  playoff: AllTeamsSingleTeamStatsPlayoff[];
  first_stage: AllTeamsSingleTeamStatsBracket[];
  accolades: Record<string, AccoladeRecord[]>;
}
