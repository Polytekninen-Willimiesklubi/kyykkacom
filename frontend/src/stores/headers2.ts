interface Header {
    title: string;
    value: string;
    width: string;
    align?: 'center' | 'start' | 'end';
}


/********** ROUND Component **********/



export const headersRound: Header[] = [
    { title: 'Pelaaja', value: 'player.player_name', width: '40%' },
    { title: '1', align: 'center', value: 'score_first', width: '10%' },
    { title: '2', align: 'center', value: 'score_second', width: '10%' },
    { title: '3', align: 'center', value: 'score_third', width: '10%' },
    { title: '4', align: 'center', value: 'score_fourth', width: '10%' },
    { title: 'Yht.', align: 'center', value: 'score_total', width: '10%' }
];
