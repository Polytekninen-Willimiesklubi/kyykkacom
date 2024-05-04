// This files should contain headers and custom sorts to i.e. datatables

/******************* FUNCTIONS **********************/

/**
 * Checks if given value is 'NaN'. Should be used in cases where there is only postive values.
 * @param {float} value Given value to check 'NaN'
 * @returns {float} Negative value if True else orginal value
*/
function isStrNaN(value) {
    return value === 'NaN' ? -2 : value
}

/** 
 * Custom sort to revaluate string values in throw values ('e' and 'h')
 * @param {number} a 
 * @param {number} b 
 * @returns Difference of a and b
 */
function throwSort(a, b) {
    function d(p1) {
        switch (p1) {
            case 0:
                return -2
            case 'e':
                return 0
            case '-':
                return -1
            case 'h':
                return -3
            default:
                return p1
        }
    }
    return d(a) - d(b)
}


/******************* HEADERS **********************/


/********** PLAYERS PAGE **********/

export const headerPlayers = [
    { title: 'Nimi',    key: 'player_name'              , align: 'left',    width: '30%' },
    { title: 'Joukkue', key: 'team.current_abbreviation', align: 'center',  width: '10%' },
    { title: 'E',       key: 'rounds_total'             , align: 'center',  tooltip: 'Pelatut Erät'},
    { title: 'K',       key: 'score_total'              , align: 'center',  tooltip: 'Poistetut Kyykät'},
    { title: 'KPH',     key: 'score_per_throw'          , align: 'center',  tooltip: 'Kyykkää Per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b)},
    { title: 'SP',      key: 'scaled_points'            , align: 'center',  tooltip: 'Skaalatut Pisteet'},
    { title: 'SPPH',    key: 'scaled_points_per_throw'  , align: 'center',  tooltip: 'Skaalatut Pisteet Per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b)},
    { title: 'kHP',     key: 'avg_throw_turn'           , align: 'center',  tooltip: 'Keskimääräinen Heittopaikka',  sort: (a, b) => isStrNaN(a) - isStrNaN(b)},
    { title: 'H',       key: 'pikes_total'              , align: 'center',  tooltip: 'Heitetyt Hauet (Ohi heitto)'},
    { title: 'H%',      key: 'pike_percentage'          , align: 'center',  tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: (a, b) => isStrNaN(a) - isStrNaN(b)},
    { title: 'VM',      key: 'zeros_total'              , align: 'center',  tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)'},
    { title: 'JK',      key: 'gteSix_total'             , align: 'center',  tooltip: 'Joulukuuset (yli viiden kyykän heitot)'},
];

/********** PLAYER PAGE **********/

export const headersPlayerPeriod = [
    { title: 'Aika',        key: 'match_time' },
    { title: 'Vastustaja',  key: 'opp_name' },
    { title: 'Erä',         key: 'period'},
    { title: 'HP',          key: 'turn',                tooltip: 'Heittopaikka' },
    { title: '1',           key: 'score_first',         tooltip: '1. heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '2',           key: 'score_second',        tooltip: '2. heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '3',           key: 'score_third',         tooltip: '3. heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '4',           key: 'score_fourth',        tooltip: '4. heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: 'Yht.',        key: 'score_total',         tooltip: 'Heitot Yhteensä (Kyykkää)' },
    { title: 'KPH',         key: 'score_average_round', tooltip: 'Kyykkää per Heitto' },
    { title: 'OJ pis.',     key: 'own_score_round',     tooltip: 'Oman joukkueen pisteet' },
    { title: 'VJ pis.',     key: 'opp_score_round',     tooltip: 'Vastustaja joukkueen pisteet' }
];

export const headersPlayerGames = [
    { title: 'Aika',        key: 'match_time' },
    { title: 'Vastustaja',  key: 'opponent_name' },
    { title: 'HP1',         key: 'throw_turn_one',      tooltip: '1. erän heittopaikka' },
    { title: 'HP2',         key: 'throw_turn_two',      tooltip: '2. erän heittopaikka' },
    { title: '1',           key: 'score_first',         tooltip: '1.erän 1.heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '2',           key: 'score_second',        tooltip: '1.erän 2.heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '3',           key: 'score_third',         tooltip: '1.erän 3.heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '4',           key: 'score_fourth',        tooltip: '1.erän 4.heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '5',           key: 'score_fifth',         tooltip: '2.erän 1.heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '6',           key: 'score_sixth',         tooltip: '2.erän 2.heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '7',           key: 'score_seventh',       tooltip: '2.erän 3.heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: '8',           key: 'score_eighth',        tooltip: '2.erän 4.heitto (Kyykkää)', sort: (a, b) => throwSort(a,b) },
    { title: 'Yht.',        key: 'score_total',         tooltip: 'Poistetut kyykät Yhteensä (Kyykkää)' },
    { title: 'KPH',         key: 'score_average_match', tooltip: 'Kyykkää per Heitto' },
    { title: 'OJ pis.',     key: 'own_score',           tooltip: 'Oman joukkueen pisteet' },
    { title: 'VJ pis.',     key: 'opponent_score',      tooltip: 'Vastustaja joukkueen pisteet' }
];

export const headerPlayerOverallStats = [
    { title: '',                 key: 'season',                   sortable: false },
    { title: 'Kaudet',           key: 'season_count',             sortable: false },
    { title: 'Erät',             key: 'all_rounds_total',         sortable: false },
    { title: 'Kyykät',           key: 'all_score_total',          sortable: false },
    { title: 'Heitot',           key: 'all_throws_total',         sortable: false },
    { title: 'KPH',              key: 'total_average_throw',      sortable: false, tooltip: 'Kyykkää per Heitto'},
    { title: 'kHP',              key: 'total_average_throw_turn', sortable: false, tooltip: 'Keskimääräinen heittopaikka' },
    { title: 'Hauet',            key: 'all_pikes_total',          sortable: false, tooltip: 'Kaikki Hauet (=Ohi heitot)'},
    { title: 'H%',               key: 'total_pike_percentage',    sortable: false, tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
    { title: 'VM',               key: 'all_zeros_total',          sortable: false, tooltip: 'Virkamiehet: Nollaheitot ilman haukia'},
    { title: 'VM%',              key: 'total_zero_percentage',    sortable: false, tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
    { title: 'JK',               key: 'all_gteSix_total',         sortable: false, tooltip: 'Joulukuuset (yli viiden kyykän heitot)' }
];

export const headerPlayerSeasonStats = [
    { title: 'Kausi',            key: 'season' },
    { title: 'Joukkue',          key: 'team_name' },
    { title: 'Erät',             key: 'rounds_total'},
    { title: 'Kyykät',           key: 'score_total'},
    { title: 'Heitot',           key: 'throws_total'},
    { title: 'KPH',              key: 'score_per_throw', tooltip: 'Kyykkää per Heitto' },
    { title: 'kHP',              key: 'avg_throw_turn',  tooltip: 'Keskimääräinen heittopaikka' },
    { title: 'Hauet',            key: 'pikes_total',     tooltip: 'Kaikki Hauet (=Ohi heitot)' },
    { title: 'H%',               key: 'pike_percentage', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
    { title: 'VM',               key: 'zeros_total',     tooltip: 'Virkamiehet: Nollaheitot ilman haukia' },
    { title: 'VM%',              key: 'zero_percentage', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
    { title: 'JK',               key: 'gteSix_total',    tooltip: 'Joulukuuset (yli viiden kyykän heitot)' }
];

/********** TEAMS PAGE **********/

export const headersTeams = [
    { title: 'Nimi',      key: 'current_name',         align: 'center' },
    { title: 'Lyhenne',   key: 'current_abbreviation', align: 'center' },
    { title: 'Ottelut',   key: 'matches_played',       align: 'center' },
    { title: 'Voitot',    key: 'matches_won',          align: 'center' },
    { title: 'Häviöt',    key: 'matches_lost',         align: 'center' },
    { title: 'Tasurit',   key: 'matches_tie',          align: 'center' },
    { title: 'Ottelu Ka', key: 'match_average',        align: 'center' }
];  

/********** TEAM PAGE **********/

export const headersTeamReserve = [
    { title: 'Pelaajan nimi', key: 'player_name' },
    { title: 'Varaa',         key: 'actions', align: 'left', sortable: false}
];
  
export const headersTeamPlayers = [
    { title: 'Nimi', key: 'player_name',             width: '20%',  align: 'left'},
    { title: 'Erät', key: 'rounds_total',            width: '1%',   align: 'center', },
    { title: 'K',    key: 'score_total',             width: '1%',   align: 'center', tooltip: 'Poistetut Kyykkät' },
    { title: 'KPH',  key: 'score_per_throw',         width: '1%',   align: 'center', tooltip: 'Kyykkää per Heitto' },
    { title: 'SP',   key: 'scaled_points',           width: '1%',   align: 'center', tooltip: 'Skaalatut Pisteet '},
    { title: 'SPPH', key: 'scaled_points_per_throw', width: '1%',   align: 'center', tooltip: 'Skaalatut Pisteet per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'kHP',  key: 'avg_throw_turn',          width: '1%',   align: 'center', tooltip: 'Keskimääräinen Heittopaikka',  sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'H',    key: 'pikes_total',             width: '1%',   align: 'center', tooltip: 'Heitetyt Hauet (Ohi heitto)'},
    { title: 'H%',   key: 'pike_percentage',         width: '1%',   align: 'center', tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'VM',   key: 'zeros_total',             width: '1%',   align: 'center', tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)'},
    { title: 'JK',   key: 'gteSix_total',            width: '1%',   align: 'center', tooltip: 'Joulukuuset (yli viiden kyykän heitot)'}
];
  
export const headersTeamMatch = [
    { title: 'Aika',        key: 'match_time',          align: 'center', tooltip: 'Pelausaika' },
    { title: 'Tyyppi',      key: 'match_type',          align: 'center', tooltip: 'Peli Tyyppi' },
    { title: 'Vastustaja',  key: 'opposite_team',       align: 'center', tooltip: 'Vastustaja joukkue' },
    { title: 'OJ 1',        key: 'own_first',           align: 'center', tooltip: 'Oman Joukkueen 1. Erä',      width: '2%' },
    { title: 'OJ 2',        key: 'own_second',          align: 'center', tooltip: 'Oman Joukkueen 2. Erä',      width: '2%' },
    { title: 'V 1',         key: 'opp_first',           align: 'center', tooltip: 'Vastustaja Joukkueen 1. Erä', width: '2%' },
    { title: 'V 2',         key: 'opp_second',          align: 'center', tooltip: 'Vastustaja Joukkueen 2. Erä', width: '2%' },
    // { title: 'H+VM',        key: 'jotain',              align: 'center', tooltip: 'Yhteensä pelissä oman joukkueen heittämät nolla heitot'},
    // { title: 'JK',          key: 'jotain',              align: 'center', tooltip: '(Joulukuusi) Yhteensä pelissä oman joukkueen heittämät "6 kyykkää tai enemmän"- heitot'},
    { title: 'OJ pis.',     key: 'own_team_total',      align: 'center', tooltip: 'Oman joukkueen pisteet',      width: '2%' },
    { title: 'VJ pis.',     key: 'opposite_team_total', align: 'center', tooltip: 'Vastustaja joukkueen pisteet', width: '2%' }
];
  
export const headersTeamSeasonStats = [
    { title: 'Poistetut Kyykät',    key: 'score_total' },
    { title: 'Heitot',              key: 'throws_total' },
    { title: 'Ottelut',             key: 'match_count' },
    { title: 'Ottelu keskiarvo',    key: 'match_average' },
    { title: 'Hauet',               key: 'pikes_total' },
    { title: 'Haukiprosentti',      key: 'pike_percentage' },
    { title: 'Nolla heitot',        key: 'zeros_total' },
    { title: 'Nollaprosentti',      key: 'zero_percentage' },
    { title: 'Nolla aloitukset',    key: 'zero_or_pike_first_throw_total' },
    { title: 'Joulukuuset',         key: 'gteSix_total' } ,
];
