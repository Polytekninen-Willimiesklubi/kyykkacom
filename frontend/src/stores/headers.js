// This files should contain headers and custom sorts to i.e. datatables

/******************* FUNCTIONS **********************/

/**
 * Comparisson that will sort 'NaN' value to bottom
 * @param {number} a
 * @param {number} b
 * @returns {number} a - b if both not 'NaN'
*/
function nanSort(a, b) {
    if (isNaN(a) && isNaN(b)) {
        return 0
    } else if (isNaN(a)) {
        return -1
    } else if (isNaN(b)) {
        return 1
    }
    return Number(a) - Number(b)
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
    { title: 'KPH', key: 'score_per_throw', align: 'center', tooltip: 'Kyykkää Per Heitto', sort: nanSort },
    { title: 'SP', key: 'scaled_points', align: 'center', tooltip: 'Skaalatut Pisteet: S=2n*(h+w)/10, missä h: heittopaikka, w: Heittäjän 1./2. heitoilta 9, 3./4. 13, n: Poistetut kyykät' },
    { title: 'SPPH', key: 'scaled_points_per_throw', align: 'center', tooltip: 'Skaalatut Pisteet Per Heitto', sort: nanSort },
    { title: 'kHP', key: 'avg_throw_turn', align: 'center', tooltip: 'Keskimääräinen Heittopaikka', sort: nanSort },
    { title: 'H', key: 'pikes_total', align: 'center', tooltip: 'Heitetyt Hauet (Ohi heitto)' },
    { title: 'H%', key: 'pike_percentage', align: 'center', tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: nanSort },
    { title: 'VM', key: 'zeros_total', align: 'center', tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)' },
    // { title: 'Tyh.', key: 'clearence_count', width: '1%', align: 'center', tooltip: 'Tyhjennykset (Pelannut tyhjennetyssä erässä)' },
    { title: 'JK', key: 'gte_six_total', align: 'center', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' },
];

// `headerAllPlayersTemplate` is meant to be reduced in the UI based on filters one applies
export const headerAllPlayersTemplate = [
    { title: 'Nimi', key: 'player_name', align: 'start', width: '30%' },
    { title: 'Kausi', key: 'season', align: 'center', width: '10%' },
    { title: 'Kaudet', key: 'season_count', align: 'center', width: '5%', tooltip: 'Kaikki pelatut kaudet' },
    { title: 'Joukkue', key: 'team_name', align: 'center', width: '10%' },
    { title: 'E', key: 'rounds_total', align: 'center', tooltip: 'Pelatut Erät' },
    { title: 'K', key: 'score_total', align: 'center', tooltip: 'Poistetut Kyykät' },
    { title: 'KPH', key: 'score_per_throw', align: 'center', tooltip: 'Kyykkää Per Heitto', sort: nanSort },
    { title: 'SP', key: 'scaled_points', align: 'center', tooltip: 'Skaalatut Pisteet: S=2n*(h+w)/10, missä h: heittopaikka, w: Heittäjän 1./2. heitoilta 9, 3./4. 13, n: Poistetut kyykät' },
    { title: 'SPPH', key: 'scaled_points_per_throw', align: 'center', tooltip: 'Skaalatut Pisteet Per Heitto', sort: nanSort },
    { title: 'kHP', key: 'avg_throw_turn', align: 'center', tooltip: 'Keskimääräinen Heittopaikka', sort: nanSort },
    { title: 'H', key: 'pikes_total', align: 'center', tooltip: 'Heitetyt Hauet (Ohi heitto)' },
    { title: 'VM', key: 'zeros_total', align: 'center', tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)' },
    { title: 'H+VM', key: 'combined_total', align: 'center', tooltip: 'Kaikki nollaheitot (hauet + virkamiehet)' },
    { title: 'H%', key: 'pike_percentage', align: 'center', tooltip: 'Hauki-prosentti (heityt hauet/kaikki heitot)', sort: nanSort },
    { title: 'VM%', key: 'zero_percentage', align: 'center', tooltip: 'Virkamies-prosentti (kyykkään osuttu nolla/kaikki heitot)', sort: nanSort },
    { title: 'H+VM%', key: 'combined_percentage', align: 'center', tooltip: 'Nolla-prosentti (Nollat/kaikki heitot)', sort: nanSort },
    { title: 'Tyh.', key: 'clearence_count', width: '1%', align: 'center', tooltip: 'Tyhjennykset (Pelannut tyhjennetyssä erässä)' },
    { title: 'TH', key: 'clearence_throws_total', width: '1%', align: 'center', tooltip: 'Tyhjennys heitot (Heitto joka tyhjensi erän)' },
    { title: 'JK', key: 'gte_six_total', align: 'center', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' },
];


/********** PLAYER PAGE **********/

export const headersPlayerPeriod = [
    { title: 'Aika', key: 'time' },
    { title: 'Vastustaja', key: 'oppenent_name' },
    { title: 'Erä', key: 'throw_round' },
    { title: 'HP', key: 'throw_turn', tooltip: 'Heittopaikka' },
    {
        title: 'Heitot',
        children: [ // TODO sorting check
            { title: '1', key: 'score_first', tooltip: '1. heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '2', key: 'score_second', tooltip: '2. heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '3', key: 'score_third', tooltip: '3. heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '4', key: 'score_fourth', tooltip: '4. heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
        ]
    },
    { title: 'Yht.', key: 'score', tooltip: 'Heitot Yhteensä (Kyykkää)' },
    { title: 'KPH', key: 'avg_round_score', tooltip: 'Kyykkää per Heitto' },
    { title: 'OJ pis.', key: 'own_team_score', tooltip: 'Oman joukkueen pisteet' },
    { title: 'VJ pis.', key: 'opponent_score', tooltip: 'Vastustaja joukkueen pisteet' }
];

export const headersPlayerGames = [
    { title: 'Aika', key: 'time' },
    { title: 'Vastustaja', key: 'opponent_name' },
    { title: '1.HP', key: 'position_one', tooltip: '1. erän heittopaikka' },
    { title: '2.HP', key: 'position_two', tooltip: '2. erän heittopaikka' },
    {
        title: '1. Erän Heitot',
        children: [
            { title: '1', key: 'first', tooltip: '1.erän 1.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '2', key: 'second', tooltip: '1.erän 2.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '3', key: 'third', tooltip: '1.erän 3.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '4', key: 'fourth', tooltip: '1.erän 4.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
        ]
    },
    {
        title: '2. Erän Heitot',
        children: [
            { title: '1', key: 'fifth', tooltip: '2.erän 1.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '2', key: 'sixth', tooltip: '2.erän 2.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '3', key: 'seventh', tooltip: '2.erän 3.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
            { title: '4', key: 'eighth', tooltip: '2.erän 4.heitto (Kyykkää)', sort: (a, b) => throwSort(a, b) },
        ]
    },
    { title: 'Yht.', key: 'score', tooltip: 'Poistetut kyykät Yhteensä (Kyykkää)' },
    { title: 'KPH', key: 'score_per_throw', tooltip: 'Kyykkää per Heitto' },
    { title: 'OJ pis.', key: 'own_team_score', tooltip: 'Oman joukkueen pisteet' },
    { title: 'VJ pis.', key: 'opponent_score', tooltip: 'Vastustaja joukkueen pisteet' }
];

export const headerPlayerOverallStats = [
    { title: '', key: 'season', sortable: false },
    { title: 'Kaudet', key: 'season_count', sortable: false },
    { title: 'Erät', key: 'rounds', sortable: false },
    { title: 'Kyykät', key: 'scores', sortable: false },
    { title: 'Heitot', key: 'throws', sortable: false },
    { title: 'KPH', key: 'avg_score', sortable: false, tooltip: 'Kyykkää per Heitto' },
    { title: 'kHP', key: 'avg_position', sortable: false, tooltip: 'Keskimääräinen heittopaikka' },
    { title: 'Hauet', key: 'pikes', sortable: false, tooltip: 'Kaikki Hauet (=Ohi heitot)' },
    { title: 'H%', key: 'pike_percentage', sortable: false, tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
    { title: 'VM', key: 'zeros', sortable: false, tooltip: 'Virkamiehet: Nollaheitot ilman haukia' },
    // { title: 'VM%', key: 'total_zero_percentage', sortable: false, tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
    { title: 'Tyh.', key: 'clearences', align: 'center', tooltip: 'Tyhjennykset (Pelannut tyhjennetyssä erässä)' },
    { title: 'JK', key: 'gte_six', sortable: false, tooltip: 'Joulukuuset (yli viiden kyykän heitot)' },
];

export const headerPlayerSeasonStats = [
    { title: 'Kausi', key: 'season' },
    { title: 'Joukkue', key: 'team_name' },
    { title: 'Erät', key: 'rounds_total' },
    { title: 'Kyykät', key: 'score_total' },
    { title: 'Heitot', key: 'throws_total' },
    { title: 'KPH', key: 'avg_score', tooltip: 'Kyykkää per Heitto' },
    { title: 'kHP', key: 'avg_position', tooltip: 'Keskimääräinen heittopaikka' },
    { title: 'Hauet', key: 'pikes_total', tooltip: 'Kaikki Hauet (=Ohi heitot)' },
    { title: 'H%', key: 'pike_percentage', tooltip: 'Hauki-prosentti: Hauet / Kaikki heitot' },
    { title: 'VM', key: 'zeros_total', tooltip: 'Virkamiehet: Nollaheitot ilman haukia' },
    // { title: 'VM%', key: 'zero_percentage', tooltip: 'Virkamies-prosentti: Nollat ilman haukia/ Kaikki heitot' },
    { title: 'Tyh.', key: 'clearence_count', align: 'center', tooltip: 'Tyhjennykset (Pelannut tyhjennetyssä erässä)' },
    { title: 'JK', key: 'pike_percentage', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' },
];

export const headerPlayerSeasonStatsRanking = [
    ...headerPlayerSeasonStats.slice(0, 2),
    { title: 'Sij.', key: 'ranking', width: '1%' },
    ...headerPlayerSeasonStats.slice(2)
];



/********** TEAMS PAGE **********/

export const headersTeams = [
    { title: 'Nimi', key: 'current_name', align: 'center' },
    { title: 'Lyhenne', key: 'current_abbreviation', align: 'center' },
    { title: 'Ottelut', key: 'matches_played', align: 'center' },
    { title: 'Voitot', key: 'matches_won', align: 'center' },
    { title: 'Häviöt', key: 'matches_lost', align: 'center' },
    { title: 'Tasurit', key: 'matches_tie', align: 'center' },
    { title: 'Ottelu Ka', key: 'match_average', align: 'center' },
    { title: 'Paras Erä', key: 'best_round', align: 'center' },
    { title: 'Paras Ottelu', key: 'best_match', align: 'center' },
    { title: 'Tyhjennykset', key: 'clearences', align: 'center' },

];

/********** ALL TEAMS PAGE **********/

export const headersTeamsAllTime = [
    { title: 'Nimi', key: 'current_name', align: 'center', tooltip: 'Viimeisin nimi' },
    { title: 'Lyhenne', key: 'current_abbreviation', align: 'center', tooltip: 'Viimeisin lyhenne' },
    { title: 'Kaudet', key: 'season_count', align: 'center', tooltip: 'Pelatut kaudet' },
    { title: 'Ottelut', key: 'matches_played', align: 'center' },
    { title: 'Voitot', key: 'matches_won', align: 'center' },
    { title: 'Häviöt', key: 'matches_lost', align: 'center' },
    { title: 'Tasurit', key: 'matches_tie', align: 'center' },
    { title: 'Ottelu Ka', key: 'match_average', align: 'center' },
    { title: 'Paras Erä', key: 'best_round', align: 'center' },
    { title: 'Paras Ottelu', key: 'best_match', align: 'center' },
    { title: 'Tyhjennykset', key: 'clearences', align: 'center' },

];

export const headersAllTeamsPerSeason = [
    { title: 'Nimi', key: 'current_name', align: 'center' },
    { title: 'Lyhenne', key: 'current_abbreviation', align: 'center' },
    { title: 'Kausi', key: 'season', align: 'center', tooltip: 'Pelatut kaudet' },
    { title: 'Ottelut', key: 'matches_played', align: 'center' },
    { title: 'Voitot', key: 'matches_won', align: 'center' },
    { title: 'Häviöt', key: 'matches_lost', align: 'center' },
    { title: 'Tasurit', key: 'matches_tie', align: 'center' },
    { title: 'Ottelu Ka', key: 'match_average', align: 'center' },
    { title: 'Paras Erä', key: 'best_round', align: 'center' },
    { title: 'Paras Ottelu', key: 'best_match', align: 'center' },
    { title: 'Tyhjennykset', key: 'clearences', align: 'center' },

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
    { title: 'SPPH', key: 'scaled_points_per_throw', width: '1%', align: 'center', tooltip: 'Skaalatut Pisteet per Heitto', sort: nanSort },
    { title: 'kHP', key: 'avg_throw_turn', width: '1%', align: 'center', tooltip: 'Keskimääräinen Heittopaikka', sort: nanSort },
    { title: 'H', key: 'pikes_total', width: '1%', align: 'center', tooltip: 'Heitetyt Hauet (Ohi heitto)' },
    { title: 'H%', key: 'pike_percentage', width: '1%', align: 'center', tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: nanSort },
    { title: 'VM', key: 'zeros_total', width: '1%', align: 'center', tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)' },
    { title: 'JK', key: 'gteSix_total', width: '1%', align: 'center', tooltip: 'Joulukuuset (yli viiden kyykän heitot)' },
    { title: 'Tyh.', key: 'clearence_count', width: '1%', align: 'center', tooltip: 'Tyhjennykset (Pelannut tyhjennetyssä erässä)' }
];

export const headersTeamMatch = [
    { title: 'Aika', key: 'match_time', align: 'center', tooltip: 'Milloin peli pelattiin' },
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
    { title: 'Virkamiehet', key: 'zeros_total' },
    { title: 'Nolla aloitukset', key: 'zero_or_pike_first_throw_total' },
    { title: 'Tyhjennykset', key: 'clearances' },
    { title: 'Joulukuuset', key: 'gteSix_total' },
    { title: 'Paras Peli', key: 'best_match' },
    { title: 'Paras Erä', key: 'best_round' },
];

/********** MATCHES PAGE **********/

export const headersMatches = [
    { title: '', width: "1%", key: 'match_link', sortable: false },
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
    // This extra entry removes 'group-by' header -> https://github.com/vuetifyjs/vuetify/issues/17863
    { key: 'data-table-group', width: '0px', sortable: false },
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
    { title: 'Oma Joukkue', route: '/joukkueet/', icon: 'mdi-account' },
    { title: 'Ottelut', route: '/ottelut', icon: 'mdi-space-invaders' },
    { title: 'Joukkueet', route: '/joukkueet', icon: 'mdi-emoticon-poop' },
    { title: 'Runkosarja', route: '/runkosarja', icon: 'mdi-format-list-numbered' },
    { title: 'Pelaajat', route: '/pelaajat', icon: 'mdi-account-group' },
    { title: 'Pudotuspelit', route: '/jatkosarja', icon: 'mdi-bank' },
    // { title: 'SuperWeekend', route: '/superweekend', icon: 'mdi-nuke' },
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

export const headerHofMedals = [
    { title: 'Nimi', key: 'name', align: 'center' },
    { title: '🥇', key: 'first', align: 'center', tooltip: 'Liigamestaruuksien määrä (1. sija)' },
    { title: '🥈', key: 'second', align: 'center', tooltip: 'Liigamestaruus 2. sijoitusten määrä' },
    { title: '🥉', key: 'third', align: 'center', tooltip: 'Liigamestaruus 3. sijoitusten määrä' },
    { title: '⭐', key: 'super', align: 'center', tooltip: 'SuperWeekend-Cupin mestaruuksien määrä' },
    { title: '🏆', key: 'bracket', align: 'center', tooltip: 'Runkosarjamestaruuksien määrä' },
];

