<!-- sortTeams: function() {
    this.teams.forEach(ele => {
        ele.sort((a,b) => {
            let total = b.points_total - a.points_total
            // Order sort: bracket points
            if (total != 0) {
                return total < 0 ? -1 : 1
            }
            // First Tiebreaker: Match result between the teams
            let bracket_match = this.bracket_matches.filter(ele =>
                (ele.home_team.current_abbreviation == a.current_abbreviation || ele.home_team.current_abbreviation == b.current_abbreviation) &&
                (ele.away_team.current_abbreviation == a.current_abbreviation || ele.away_team.current_abbreviation == b.current_abbreviation)
            )
            if (!bracket_match.length) {
                console.log('Too many matches found: ' + bracket_match.length)
                return 0
            }
            bracket_match = bracket_match[0]
            let match_result = bracket_match.away_score_total - bracket_match.home_score_total
            if (a.current_abbreviation == bracket_match.home_team.current_abbreviation) {
                match_result *= -1
            }
            if (match_result != 0) {
                return match_result < 0 ? 1 : -1
            }

            // Second Tiebreaker: Match average
            let average_total = b.match_average - a.match_average
            if (average_total != 0) {
                return match_result < 0 ? 1 : -1
            }
            // Third Tiebreaker: Chance, not implemented here
            return 0
        })
    })
    function innerFunction(array, bracket_matches, big_arr) {
        let games = bracket_matches.filter( e =>
            (e.home_team.current_abbreviation in array) &&
            (e.away_team.current_abbreviation in array)
        )
        games.forEach(e => {
            console.log(e.home_team.current_abbreviation, e.away_team.current_abbreviation)
            if (e.home_score_total > e.away_score_total) {
                array[e.away_team.current_abbreviation] += 2
            } else if (e.home_score_total < e.away_score_total) {
                array[e.home_team.current_abbreviation] += 2
            } else {
                ++array[e.away_team.current_abbreviation]
                ++array[e.home_team.current_abbreviation]
            }
        })
        let sortable = []
        for (var tmp in array) {
            sortable.push([tmp, array[tmp]])
        }
        sortable.sort((a,b) => b[1]-a[1])
        var i = 0
        while (i < sortable.length) {
            let points = sortable[i][1]
            let j = i + 1
            while (j < sortable.length) {
                if (sortable[j][1] != points) {
                    break
                }
                j++
            }
            if (j-i <= 1) {
                i++
                continue
            } else if (j-i === 2) {
                let match = bracket_matches.filter(e =>
                    (e.home_team.current_abbreviation == sortable[i][0] || e.home_team.current_abbreviation == sortable[j-1][0]) &&
                    (e.away_team.current_abbreviation == sortable[i][0] || e.away_team.current_abbreviation == sortable[j-1][0])
                )
                match = match[0]
                if (match.home_score_total != match.away_score_total) {
                    let home_team = match.home_team.current_abbreviation == sortable[i][0] ? sortable[i] : sortable[j-1]
                    let away_team = match.home_team.current_abbreviation == sortable[i][0] ? sortable[j-1] : sortable[i]
                    let winner = match.home_score_total < match.away_score_total ? home_team : away_team
                    winner[1] += 0.5
                } else {
                    let team_i = big_arr.filter(e => e.current_abbreviation == sortable[i][0])[0]
                    let team_j = big_arr.filter(e => e.current_abbreviation == sortable[j-1][0])[0]
                    if (team_i.match_average > team_j.match_average) {
                        sortable[i][1] += 0.5
                    } else { // We ignore == conditional. There is no way this can be same between two teams
                        sortable[j-1][1] += 0.5
                    }
                }
                i = j
            } else {
                if (j-i == sortable.length) {
                    let tmp_sortable = []
                    sortable.forEach(e => {
                        let team = big_arr.filter(tmp_e => tmp_e.current_abbreviation == e[0])[0]
                        tmp_sortable.push([e[0], team.match_average])
                    }, tmp_sortable)

                    tmp_sortable.sort((a,b) => b[1] - a[1])
                    let inc = 1 / sortable.length
                    for(let k = 0; k < tmp_sortable.length; k++) {
                        let tmp = tmp_sortable[k]
                        let team_index = sortable.map(e => e[0]).indexOf(tmp[0])
                        sortable[team_index][1] += inc*k
                    }

                } else {
                    console.log('Dont come here') // Here sould come recursive call that call 'innerFunction'
                }
                i = j
            }
            console.log(sortable)
        }
        sortable.sort((a,b) => b[1]-a[1])
        return sortable.map(ele => ele[0])
    }

    // Resolve "3 or more"- way ties
    this.teams.forEach(ele => {
        let i = 0
        let j = 0
        let points = 0
        while(i < ele.length) {
            points = ele[i].points_total
            j = i + 1
            while (j < ele.length) {
                if (ele[j].points_total != points) {
                    break
                }
                j++
            }
            if (j-i <= 2) {
                i = j
                continue
            }
            // Initialize match results with names
            let match_results = {}
            for (let k=i; k < j; k++) {
                match_results[ele[k].current_abbreviation] = 0
            }
            let correct_order = innerFunction(match_results, this.bracket_matches, ele)
            let datas = []
            correct_order.forEach(name => {
                datas.push(structuredClone(ele.filter(e => e.current_abbreviation == name)[0]))
            })
            let k = i
            datas.forEach(data => {
                ele[k] = data,
                k++
            }, k)
            i = j
        }
    })
}, -->
