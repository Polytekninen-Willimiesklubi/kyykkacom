// This files should contain headers and custom sorts to i.e. datatables

/**
 * Checks if given value is 'NaN'. Should be used in cases where there is only postive values.
 * 
 * @param {float} value Given value to check 'NaN' property
 * @returns {float} Negative value if True else orginal value
*/
function isNaN(value) {
    return value === 'NaN' ? -2 : value
}

// ALL PLAYERS PAGE 
export const headerPlayers = [
    { title: 'Nimi',    key: 'player_name'              , align: 'left',    width: '30%' },
    { title: 'Joukkue', key: 'team.current_abbreviation', align: 'center',  width: '10%' },
    { title: 'E',       key: 'rounds_total'             , align: 'center',  tooltip: 'Pelatut Erät'},
    { title: 'K',       key: 'score_total'              , align: 'center',  tooltip: 'Poistetut Kyykät'},
    { title: 'KPH',     key: 'score_per_throw'          , align: 'center',  tooltip: 'Kyykkää Per Heitto', sort: (a, b) => isNaN(b) - isNaN(a)},
    { title: 'SP',      key: 'scaled_points'            , align: 'center',  tooltip: 'Skaalatut Pisteet'},
    { title: 'SPPH',    key: 'scaled_points_per_throw'  , align: 'center',  tooltip: 'Skaalatut Pisteet Per Heitto', sort: (a, b) => isNaN(b) - isNaN(a)},
    { title: 'kHP',     key: 'avg_throw_turn'           , align: 'center',  tooltip: 'Keskimääräinen Heittopaikka',  sort: (a, b) => isNaN(b) - isNaN(a)},
    { title: 'H',       key: 'pikes_total'              , align: 'center',  tooltip: 'Heitetyt Hauet (Ohi heitto)'},
    { title: 'H%',      key: 'pike_percentage'          , align: 'center',  tooltip: 'Hauki prosentti (heityt hauet/kaikki heitot)', sort: (a, b) => isNaN(b) - isNaN(a)},
    { title: 'VM',      key: 'zeros_total'              , align: 'center',  tooltip: 'Virkamiehet (ei-hauki-nolla-heitto)'},
    { title: 'JK',      key: 'gteSix_total'             , align: 'center',  tooltip: 'Joulukuuset (yli viiden kyykän heitot)'},
];