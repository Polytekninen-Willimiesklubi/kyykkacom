// This files should contain headers and custom sorts to i.e. datatables

/******************* FUNCTIONS **********************/

/**
 * Checks if given value is 'NaN'. Should be used in cases where there is only postive values.
 * @param {number | string} value Given value to check 'NaN'
 * @returns {number} Negative value if True else orginal value
*/
function isStrNaN(value) {
    return value === 'NaN' ? -2 : Number(value)
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
    { title: 'Nimi', key: 'player_name', align: 'left', width: '30%' },
    { title: 'Joukkue', key: 'team_name', align: 'center', width: '10%' },
    { title: 'E', key: 'rounds_total', align: 'center', tooltip: 'Pelatut Erät' },
    { title: 'K', key: 'score_total', align: 'center', tooltip: 'Poistetut Kyykät' },
    { title: 'KPH', key: 'score_per_throw', align: 'center', tooltip: 'Kyykkää Per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'SP', key: 'scaled_points', align: 'center', tooltip: 'Skaalatut Pisteet: S=2n*(h+w)/10, missä h: heittopaikka, w: Heittäjän 1./2. heitoilta 9, 3./4. 13, n: Poistetut kyykät' },
    { title: 'SPPH', key: 'scaled_points_per_throw', align: 'center', tooltip: 'Skaalatut Pisteet Per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'kHP', key: 'avg_throw_turn', align: 'center', tooltip: 'Keskimääräinen Heittopaikka', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'H', key: 'pikes_total', align: 'center', tooltip: 'Heitetyt Hauet (Ohi heitto)' },
    { title: 'H%', key: 'pike_percentage', align: 'center', tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'VM', key: 'zeros_total', align: 'center', tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)' },
    { title: 'JK', key: 'gte_six_total', align: 'center', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' },
];

export const headerAllPlayersPerSeason = [
    { title: 'Nimi', key: 'player_name', align: 'left', width: '30%' },
    { title: 'Kausi', key: 'season', align: 'center', width: '10%' },
    { title: 'Joukkue', key: 'team_name', align: 'center', width: '10%' },
    { title: 'E', key: 'rounds_total', align: 'center', tooltip: 'Pelatut Erät' },
    { title: 'K', key: 'score_total', align: 'center', tooltip: 'Poistetut Kyykät' },
    { title: 'KPH', key: 'score_per_throw', align: 'center', tooltip: 'Kyykkää Per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'SP', key: 'scaled_points', align: 'center', tooltip: 'Skaalatut Pisteet: S=2n*(h+w)/10, missä h: heittopaikka, w: Heittäjän 1./2. heitoilta 9, 3./4. 13, n: Poistetut kyykät' },
    { title: 'SPPH', key: 'scaled_points_per_throw', align: 'center', tooltip: 'Skaalatut Pisteet Per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'kHP', key: 'avg_throw_turn', align: 'center', tooltip: 'Keskimääräinen Heittopaikka', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'H', key: 'pikes_total', align: 'center', tooltip: 'Heitetyt Hauet (Ohi heitto)' },
    { title: 'H%', key: 'pike_percentage', align: 'center', tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'VM', key: 'zeros_total', align: 'center', tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)' },
    { title: 'JK', key: 'gte_six_total', align: 'center', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' },
];

export const headerAllPlayers = [
    { title: 'Nimi', key: 'player_name', align: 'left', width: '30%' },
    { title: 'Kaudet', key: 'season_count', align: 'center', width: '5%', tooltip: 'Kaikki pelatut kaudet' },
    { title: 'E', key: 'rounds_total', align: 'center', tooltip: 'Pelatut Erät' },
    { title: 'K', key: 'score_total', align: 'center', tooltip: 'Poistetut Kyykät' },
    { title: 'KPH', key: 'score_per_throw', align: 'center', tooltip: 'Kyykkää Per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'SP', key: 'scaled_points', align: 'center', tooltip: 'Skaalatut Pisteet: S=2n*(h+w)/10, missä h: heittopaikka, w: Heittäjän 1./2. heitoilta 9, 3./4. 13, n: Poistetut kyykät' },
    { title: 'SPPH', key: 'scaled_points_per_throw', align: 'center', tooltip: 'Skaalatut Pisteet Per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'kHP', key: 'avg_throw_turn', align: 'center', tooltip: 'Keskimääräinen Heittopaikka', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'H', key: 'pikes_total', align: 'center', tooltip: 'Heitetyt Hauet (Ohi heitto)' },
    { title: 'H%', key: 'pike_percentage', align: 'center', tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'VM', key: 'zeros_total', align: 'center', tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)' },
    { title: 'JK', key: 'gte_six_total', align: 'center', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' },
];


/********** PLAYER PAGE **********/

export const headersPlayerPeriod = [
    { title: 'Aika', key: 'match_time' },
    { title: 'Vastustaja', key: 'opp_name' },
    { title: 'Erä', key: 'period' },
    { title: 'HP', key: 'turn', tooltip: 'Heittopaikka' },
    {
        title: 'Heitot',
        children: [
            { title: '1', key: 'score_first', tooltip: '1. heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '2', key: 'score_second', tooltip: '2. heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '3', key: 'score_third', tooltip: '3. heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '4', key: 'score_fourth', tooltip: '4. heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
        ]
    },
    { title: 'Yht.', key: 'score_total', tooltip: 'Heitot Yhteensä (Kyykkää)' },
    { title: 'KPH', key: 'score_average_round', tooltip: 'Kyykkää per Heitto' },
    { title: 'OJ pis.', key: 'own_score_round', tooltip: 'Oman joukkueen pisteet' },
    { title: 'VJ pis.', key: 'opp_score_round', tooltip: 'Vastustaja joukkueen pisteet' }
];

export const headersPlayerGames = [
    { title: 'Aika', key: 'match_time' },
    { title: 'Vastustaja', key: 'opponent_name' },
    { title: 'HP1', key: 'throw_turn_one', tooltip: '1. erän heittopaikka' },
    { title: 'HP2', key: 'throw_turn_two', tooltip: '2. erän heittopaikka' },
    {
        title: '1.erän Heitot',
        children: [
            { title: '1', key: 'score_first', tooltip: '1.erän 1.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '2', key: 'score_second', tooltip: '1.erän 2.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '3', key: 'score_third', tooltip: '1.erän 3.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '4', key: 'score_fourth', tooltip: '1.erän 4.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
        ]
    },
    {
        title: '2.erän Heitot',
        children: [
            { title: '5', key: 'score_fifth', tooltip: '2.erän 1.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '6', key: 'score_sixth', tooltip: '2.erän 2.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '7', key: 'score_seventh', tooltip: '2.erän 3.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '8', key: 'score_eighth', tooltip: '2.erän 4.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
        ]
    },
    { title: 'Yht.', key: 'score_total', tooltip: 'Poistetut kyykät Yhteensä (Kyykkää)' },
    { title: 'KPH', key: 'score_average_match', tooltip: 'Kyykkää per Heitto' },
    { title: 'OJ pis.', key: 'own_score', tooltip: 'Oman joukkueen pisteet' },
    { title: 'VJ pis.', key: 'opponent_score', tooltip: 'Vastustaja joukkueen pisteet' }
];

export const headerPlayerOverallStats = [
    { title: '', key: 'season', sortable: false },
    { title: 'Kaudet', key: 'season_count', sortable: false },
    { title: 'Erät', key: 'all_rounds_total', sortable: false },
    { title: 'Kyykät', key: 'all_score_total', sortable: false },
    { title: 'Heitot', key: 'all_throws_total', sortable: false },
    { title: 'KPH', key: 'total_average_throw', sortable: false, tooltip: 'Kyykkää per Heitto' },
    { title: 'kHP', key: 'total_average_throw_turn', sortable: false, tooltip: 'Keskimääräinen heittopaikka' },
    { title: 'Hauet', key: 'all_pikes_total', sortable: false, tooltip: 'Kaikki Hauet (=Ohi heitot)' },
    { title: 'H%', key: 'total_pike_percentage', sortable: false, tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
    { title: 'VM', key: 'all_zeros_total', sortable: false, tooltip: 'Virkamiehet: Nollaheitot ilman haukia' },
    { title: 'VM%', key: 'total_zero_percentage', sortable: false, tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
    { title: 'JK', key: 'all_gteSix_total', sortable: false, tooltip: 'Joulukuuset (yli viiden kyykän heitot)' }
];

export const headerPlayerSeasonStats = [
    { title: 'Kausi', key: 'season' },
    { title: 'Joukkue', key: 'team_name' },
    { title: 'Erät', key: 'rounds_total' },
    { title: 'Kyykät', key: 'score_total' },
    { title: 'Heitot', key: 'throws_total' },
    { title: 'KPH', key: 'score_per_throw', tooltip: 'Kyykkää per Heitto' },
    { title: 'kHP', key: 'avg_throw_turn', tooltip: 'Keskimääräinen heittopaikka' },
    { title: 'Hauet', key: 'pikes_total', tooltip: 'Kaikki Hauet (=Ohi heitot)' },
    { title: 'H%', key: 'pike_percentage', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
    { title: 'VM', key: 'zeros_total', tooltip: 'Virkamiehet: Nollaheitot ilman haukia' },
    { title: 'VM%', key: 'zero_percentage', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
    { title: 'JK', key: 'gteSix_total', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' }
];

/********** TEAMS PAGE **********/

export const headersTeams = [
    { title: 'Nimi', key: 'current_name', align: 'center' },
    { title: 'Lyhenne', key: 'current_abbreviation', align: 'center' },
    { title: 'Ottelut', key: 'matches_played', align: 'center' },
    { title: 'Voitot', key: 'matches_won', align: 'center' },
    { title: 'Häviöt', key: 'matches_lost', align: 'center' },
    { title: 'Tasurit', key: 'matches_tie', align: 'center' },
    { title: 'Ottelu Ka', key: 'match_average', align: 'center' }
];

/********** TEAM PAGE **********/

export const headersTeamReserve = [
    { title: 'Pelaajan nimi', key: 'player_name' },
    { title: 'Varaa', key: 'actions', align: 'left', sortable: false }
];

export const headersTeamPlayers = [
    { title: 'Nimi', key: 'player_name', width: '20%', align: 'left' },
    { title: 'Erät', key: 'rounds_total', width: '1%', align: 'center', },
    { title: 'K', key: 'score_total', width: '1%', align: 'center', tooltip: 'Poistetut Kyykkät' },
    { title: 'KPH', key: 'score_per_throw', width: '1%', align: 'center', tooltip: 'Kyykkää per Heitto' },
    { title: 'SP', key: 'scaled_points', width: '1%', align: 'center', tooltip: 'Skaalatut Pisteet: S=2n*(h+w)/10, missä h: heittopaikka, w: Heittäjän 1./2. heitoilta 9, 3./4. 13, n: Poistetut kyykät' },
    { title: 'SPPH', key: 'scaled_points_per_throw', width: '1%', align: 'center', tooltip: 'Skaalatut Pisteet per Heitto', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'kHP', key: 'avg_throw_turn', width: '1%', align: 'center', tooltip: 'Keskimääräinen Heittopaikka', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'H', key: 'pikes_total', width: '1%', align: 'center', tooltip: 'Heitetyt Hauet (Ohi heitto)' },
    { title: 'H%', key: 'pike_percentage', width: '1%', align: 'center', tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: (a, b) => isStrNaN(a) - isStrNaN(b) },
    { title: 'VM', key: 'zeros_total', width: '1%', align: 'center', tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)' },
    { title: 'JK', key: 'gteSix_total', width: '1%', align: 'center', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' }
];

export const headersTeamMatch = [
    { title: 'Aika', key: 'match_time', align: 'center', tooltip: 'Pelausaika' },
    { title: 'Tyyppi', key: 'match_type', align: 'center', tooltip: 'Peli Tyyppi' },
    { title: 'Vastustaja', key: 'opposite_team', align: 'center', tooltip: 'Vastustaja joukkue' },
    { title: 'OJ 1', key: 'own_first', align: 'center', tooltip: 'Oman Joukkueen 1. Erä', width: '2%' },
    { title: 'OJ 2', key: 'own_second', align: 'center', tooltip: 'Oman Joukkueen 2. Erä', width: '2%' },
    { title: 'VJ 1', key: 'opp_first', align: 'center', tooltip: 'Vastustaja Joukkueen 1. Erä', width: '2%' },
    { title: 'VJ 2', key: 'opp_second', align: 'center', tooltip: 'Vastustaja Joukkueen 2. Erä', width: '2%' },
    // { title: 'H+VM',        key: 'jotain',              align: 'center', tooltip: 'Yhteensä pelissä oman joukkueen heittämät nolla heitot'},
    // { title: 'JK',          key: 'jotain',              align: 'center', tooltip: '(Joulukuusi) Yhteensä pelissä oman joukkueen heittämät "6 kyykkää tai enemmän"- heitot'},
    { title: 'OJ pis.', key: 'own_team_total', align: 'center', tooltip: 'Oman joukkueen pisteet', width: '2%' },
    { title: 'VJ pis.', key: 'opposite_team_total', align: 'center', tooltip: 'Vastustaja joukkueen pisteet', width: '2%' }
];

export const headersTeamSeasonStats = [
    { title: 'Poistetut Kyykät', key: 'score_total' },
    { title: 'Heitot', key: 'throws_total' },
    { title: 'Ottelut', key: 'match_count' },
    { title: 'Ottelu keskiarvo', key: 'match_average' },
    { title: 'Hauet', key: 'pikes_total' },
    { title: 'Haukiprosentti', key: 'pike_percentage' },
    { title: 'Nolla heitot', key: 'zeros_total' },
    { title: 'Nollaprosentti', key: 'zero_percentage' },
    { title: 'Nolla aloitukset', key: 'zero_or_pike_first_throw_total' },
    { title: 'Joulukuuset', key: 'gteSix_total' },
];

/********** MATCHES PAGE **********/

export const headersMatches = [
    { title: 'Aika', key: 'match_time', width: '20%', align: 'left' },
    { title: 'Tyyppi', key: 'type_name', width: '10%', align: 'center' },
    { title: 'Kenttä', key: 'field', width: '1%', align: 'center' },
    { title: 'Koti', key: 'home_team.current_abbreviation', align: 'center' },
    { title: 'Vieras', key: 'away_team.current_abbreviation', align: 'center' },
    { title: '', key: 'home_score_total', width: '3%', align: 'center' },
    { title: 'Tulos', key: 'dash', width: '1%', align: 'center', sortable: false },
    { title: '', key: 'away_score_total', width: '3%', align: 'center' }
];

export const headersMatchesPostSeason = [
    { key: 'data-table-group', width: '0px', sortable: false }, // This removes 'group-by' header -> https://github.com/vuetifyjs/vuetify/issues/17863
    { title: 'Aika', key: 'match_time', align: 'left' },
    { title: 'Kenttä', key: 'field', width: '1%', align: 'center' },
    { title: 'Koti', key: 'home_team.current_abbreviation', align: 'center' },
    { title: 'Vieras', key: 'away_team.current_abbreviation', align: 'center' },
    { title: '', key: 'home_score_total', width: '3%', align: 'center' },
    { title: 'Tulos', key: 'dash', width: '1%', align: 'center', sortable: false },
    { title: '', key: 'away_score_total', width: '3%', align: 'center' }
];

/********** PLAYOFF PAGE **********/

export const headersPlayoff = [
    { title: 'Sij.', key: 'bracket_placement' },
    { title: 'Joukkue', key: 'current_abbreviation', sortable: false, width: '10%' },
    { title: 'O', key: 'matches_played', sortable: false, width: '3%' },
    { title: 'V', key: 'matches_won', sortable: false, width: '3%' },
    { title: 'T', key: 'matches_tie', sortable: false, width: '3%' },
    { title: 'H', key: 'matches_lost', sortable: false, width: '3%' },
    { title: 'P', key: 'points_total', sortable: false, width: '3%' },
    { title: 'OKA', key: 'match_average', sortable: false, width: '5%' }
];

/********** SUPERWEEKEND PAGE **********/

export const superSidebarHeaders = [
    { title: 'Sij.', key: 'super_weekend_bracket_placement' },
    { title: 'Joukkue', key: 'current_abbreviation', sortable: false, width: '10%' },
    { title: 'V', key: 'matches_won', sortable: false, width: '3%' },
    { title: 'T', key: 'matches_tie', sortable: false, width: '3%' },
    { title: 'H', key: 'matches_lost', sortable: false, width: '3%' },
    { title: 'OKA', key: 'match_average', sortable: false, width: '5%' }
];

/********** ROUND Component **********/

export const headersRound = [
    { title: 'Pelaaja', value: 'player.player_name', width: '45%' },
    { title: 1, align: 'center', value: 'score_first', width: '10%' },
    { title: 2, align: 'center', value: 'score_second', width: '10%' },
    { title: 3, align: 'center', value: 'score_third', width: '10%' },
    { title: 4, align: 'center', value: 'score_fourth', width: '10%' },
    { title: 'Yht.', align: 'center', value: 'score_total', width: '5%' }
];

/********** NAVBAR Component **********/

export const headersNavBar = [
    { title: 'Koti', route: '/', icon: 'mdi-home' },
    { title: 'Ottelut', route: '/ottelut', icon: 'mdi-space-invaders' },
    { title: 'Joukkueet', route: '/joukkueet', icon: 'mdi-emoticon-poop' },
    { title: 'Runkosarja', route: '/runkosarja', icon: 'mdi-format-list-numbered' },
    { title: 'Pelaajat', route: '/pelaajat', icon: 'mdi-account-group' },
    { title: 'Oma Joukkue', route: '/joukkueet/', icon: 'mdi-account' }, // Add if-clause and id to route in place of use   
    { title: 'Pudotuspelit', route: '/jatkosarja', icon: 'mdi-bank' },
    { title: 'SuperWeekend', route: '/superweekend', icon: 'mdi-nuke' },
    { title: 'Info', route: '/info', icon: 'mdi-information-outline' }
];

/********** SIDEBAR Component **********/

export const headersDefaultSideBar = [
    { title: 'Joukkue', key: 'current_abbreviation', sortable: false },
    { title: 'O', key: 'matches_played', sortable: false, tooltip: "Pelatut Ottelut" },
    { title: 'V', key: 'matches_won', sortable: false, tooltip: "Voitot" },
    { title: 'T', key: 'matches_tie', sortable: false, tooltip: "Tasapelit" },
    { title: 'H', key: 'matches_lost', sortable: false, tooltip: "Häviöt" },
    { title: 'P', key: 'points_total', sortable: false, tooltip: "Pisteet" },
    { title: 'P/O', key: 'points_average', sortable: false, tooltip: "Pistettä per Ottelu " },
    { title: 'OKA', key: 'match_average', sortable: false, tooltip: "Ottelu keskiarvo" }
];

/********** Hall-of-fame Page **********/


export const headersHof = [
    { title: 'Kausi', key: 'year', align: 'center', sortable: false },
    { title: '🏆', key: 'first', align: 'center', sortable: false, tooltip: '1. Sija' },
    { title: '🥈', key: 'second', align: 'center', sortable: false, tooltip: '2. Sija' },
    { title: '🥉', key: 'third', align: 'center', sortable: false, tooltip: '3. Sija' },
    { title: '4.Sija', key: 'fourth', align: 'center', sortable: false },
];

export const headerHofPerson = [
    { title: 'Vuosi', key: 'year', align: 'center' },
    { title: 'Nimi', key: 'name', align: 'center' },
]

export const headerHofMisc = [
    { title: 'Vuosi', key: 'year', align: 'center' },
    { title: 'Palkinto', key: 'name', align: 'center' },
    { title: 'Nimi', key: 'person', align: 'center' },
]
