interface Header {
  title: string;
  value: string;
  width?: string;
  align?: 'center' | 'start' | 'end';
}

/********** ROUND Component **********/

export const headersRound: Header[] = [
  { title: 'Pelaaja', value: 'player.player_name', width: '40%' },
  { title: '1', align: 'center', value: 'score_first', width: '10%' },
  { title: '2', align: 'center', value: 'score_second', width: '10%' },
  { title: '3', align: 'center', value: 'score_third', width: '10%' },
  { title: '4', align: 'center', value: 'score_fourth', width: '10%' },
  { title: 'Yht.', align: 'center', value: 'score_total', width: '10%' },
];


/********** TEAMS PAGE **********/

export const headersTeams: Header[] = [
  { title: 'Nimi', value: 'current_name', align: 'center' },
  { title: 'Lyhenne', value: 'current_abbreviation', align: 'center' },
  { title: 'Ottelut', value: 'matches_played', align: 'center' },
  { title: 'Voitot', value: 'matches_won', align: 'center' },
  { title: 'Häviöt', value: 'matches_lost', align: 'center' },
  { title: 'Tasurit', value: 'matches_tie', align: 'center' },
  { title: 'Ottelu Ka', value: 'match_average', align: 'center' },
  { title: 'Paras Erä', value: 'best_round', align: 'center' },
  { title: 'Paras Ottelu', value: 'best_match', align: 'center' },
  { title: 'Tyhjennykset', value: 'clearences', align: 'center' },
];

