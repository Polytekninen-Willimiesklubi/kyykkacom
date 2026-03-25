/**
 * API Type Definitions
 * These interfaces match the Django backend serializers
 */

export interface Season {
    id: number
    name: string
    playoff_format: number
    no_brackets: number
}

export interface Team {
    id: number
    name: string
    season_id: number
}

export interface Player {
    id: number
    name: string
    team_id: number
    number?: number
}

export interface Match {
    id: number
    season_id: number
    team1_id: number
    team2_id: number
    result?: number
}

export interface User {
    id: number
    username: string
    email: string
    role_id: number
}

export interface RoleType {
    CAPTAIN: 1
    SUPERUSER: 2
    [key: number]: string
}

export interface LoginCredentials {
    username: string
    password: string
}

export interface LoginResponse {
    user: {
        id: number
        username: string
        player_name: string
    }
    role: number
    team_id: number | null
    team_season_id: number | null
}

export interface TeamStats {
    current_name: string
    current_abbreviation: string
    id: number
    bracket?: number
    bracket_placement?: number
    order?: number
    second_stage_bracket?: number | null
    players: any[]
    matches: any[]
}

export interface SeasonStats {
    [seasonId: number]: TeamStats
}

export interface AccoladeRecord {
    name: string
    placement: number
    icon?: string
}
