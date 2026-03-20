const baseUrl = `${import.meta.env.VITE_API_URL}/accolades/`;
const recordsUrl = `${import.meta.env.VITE_API_URL}/records/`;

export const useHofStore = defineStore('hof', () => {
    const accolades = ref([]);
    const records = ref([]);
    const recordsLoading = ref(false);
    const seasonAccolades = ref([]);
    const playerAccolades = ref([]);
    const teamAccolades = ref([]);

    const medalTableTeams = computed(() => {
        const per_name = {};

        function add_new_entry(name, _id) {
            if (name in per_name) return;
            per_name[name] = {
                "id": _id,
                "name": name,
                "first": 0,
                "second": 0,
                "third": 0,
                "super": 0,
                "bracket": 0,
            }
        }

        for (const accolade of accolades.value["team_accolades"]) {
            let org = accolade.org_name
            let accolade_name = accolade.accolade.name
            let placement = accolade.placement

            if (accolade_name === "Liigamestaruus") {
                if (placement == 1) {
                    add_new_entry(org, accolade.team_id)
                    per_name[org]["first"] += 1
                } else if (placement == 2) {
                    add_new_entry(org, accolade.team_id)
                    per_name[org]["second"] += 1
                } else if (placement == 3) {
                    add_new_entry(org, accolade.team_id)
                    per_name[org]["third"] += 1
                }
            } else if (accolade_name === "SuperWeekend-Cup" && placement == 1) {
                add_new_entry(org, accolade.team_id)
                per_name[org]["super"] += 1
            } else if (accolade_name === "Runkosarjamestaruus" && placement == 1) {
                add_new_entry(org, accolade.team_id)
                per_name[org]["bracket"] += 1
            }
        }
        return Object.values(per_name)
    })

    const medalTablePlayers = computed(() => {
        const per_id = {};

        function add_new_entry(name, _id, field) {
            if (!(_id in per_id)) {

                per_id[_id] = {
                    "id": _id,
                    "name": name,
                    "first": 0,
                    "second": 0,
                    "third": 0,
                    "super": 0,
                    "bracket": 0,
                }
            }
            per_id[_id][field] += 1
        }

        for (const accolade of accolades.value["player_team_accolades"]) {
            let accolade_name = accolade.accolade_name
            if (accolade_name === "Liigamestaruus") {
                if (accolade.placement == 1) {
                    add_new_entry(accolade.name, accolade.id, "first")
                } else if (accolade.placement == 2) {
                    add_new_entry(accolade.name, accolade.id, "second")
                } else if (accolade.placement == 3) {
                    add_new_entry(accolade.name, accolade.id, "third")
                }
            } else if (accolade_name === "SuperWeekend-Cup" && accolade.placement == 1) {

                add_new_entry(accolade.name, accolade.id, "super")
            } else if (accolade_name === "Runkosarjamestaruus" && accolade.placement == 1) {
                add_new_entry(accolade.name, accolade.id, "bracket")
            }
        }
        return Object.values(per_id)
    })

    const playerAccoladesBySeason = computed(() => {
        const per_year = {};

        for (const accolade of playerAccolades.value["pair_accolades"]) {
            let year = accolade.season_year
            if (!(year in per_year)) {
                per_year[year] = {};
            }
            // NOTE put the pari accolades to same container as team accolades
            if (!("team_accolades" in per_year[year])) {
                per_year[year]["team_accolades"] = [];
            }

            if (accolade.accolade.name === "Parikyykkäliiga") {
                if (accolade.placement == 1) {
                    accolade.accolade.name += " Mestaruus";
                } else if (accolade.placement == 2) {
                    accolade.accolade.name += " Finalisti";
                    accolade.accolade.icon = "hopea.ico"
                } else {
                    continue;
                }
            } else if (accolade.accolade.name === "Kyykkää tähtien kanssa") {
                if (accolade.placement == 1) {
                    accolade.accolade.name += " Mestaruus";
                } else if (accolade.placement == 2) {
                    accolade.accolade.name += " Finalisti";
                    accolade.accolade.icon = "hopea.ico"
                } else {
                    continue;
                }
            }
            per_year[year]["team_accolades"].push(accolade);
        }

        for (const accolade of playerAccolades.value["player_accolades"]) {
            let year = accolade.season_year;
            if (!(year in per_year)) {
                per_year[year] = {};
            }
            if (!("player_accolades" in per_year[year])) {
                per_year[year]["player_accolades"] = [];
            }

            if (accolade.accolade.name === "Henkkari-Cup") {
                if (accolade.placement == 1) {
                    accolade.accolade.name = "Henkkari-Cup Mestaruus";
                } else if (accolade.placement == 2) {
                    accolade.accolade.name = "Henkkari-Cup Finalisti";
                } else {
                    continue;
                }
            }
            per_year[year]["player_accolades"].push(accolade);
        }
        for (const accolade of playerAccolades.value["team_accolades"]) {
            let year = accolade.season_year;
            if (!(year in per_year)) {
                per_year[year] = {};
            }
            if (!("team_accolades" in per_year[year])) {
                per_year[year]["team_accolades"] = [];
            }
            // Modify the icons for team accolades to give bronze medal and silver
            if (accolade.accolade.name === "Liigamestaruus" && accolade.placement == 2) {
                accolade.accolade.icon = "hopea.ico"
            } else if (accolade.accolade.name === "Liigamestaruus" && accolade.placement == 3) {
                accolade.accolade.icon = "pronssi.ico"
            }

            if (accolade.accolade.name === "Liigamestaruus") {
                let tmp = "";
                if ([8, 16].includes(accolade.placement)) {
                    tmp = `Top${accolade.placement}`;
                } else if (accolade.placement == 1) {
                    tmp = "Mestaruus";
                } else {
                    tmp = `${accolade.placement}. sija`
                }
                if (Number(accolade.placement) > 3) {
                    accolade.accolade.icon = null
                }
                accolade.accolade.name = "NKL " + tmp;
            } else if (accolade.accolade.name === "SuperWeekend-Cup") {
                if (accolade.placement == 1) {
                    accolade.accolade.name = "SuperWeekend-Cup Mestaruus";
                } else if (accolade.placement == 2) {
                    accolade.accolade.name = "SuperWeekend-Cup Finalisti";
                    accolade.accolade.icon = "hopea.ico"
                } else {
                    continue;
                }
            }

            per_year[year]["team_accolades"].push(accolade);
        }
        return per_year;
    })


    const teamAccoladesBySeason = computed(() => {
        const per_year = {};
        for (const accolade of teamAccolades.value["player_accolades"]) {
            let year = accolade.season_year;
            // This output is going to team/[id] page, filter out NKL-outside trophies
            if (accolade.accolade.name.startsWith("Henkkari-Cup")) {
                continue;
            }
            if (!(year in per_year)) {
                per_year[year] = {};
            }
            if (!("player_accolades" in per_year[year])) {
                per_year[year]["player_accolades"] = [];
            }
            per_year[year]["player_accolades"].push(accolade);
        }
        for (const accolade of teamAccolades.value["team_accolades"]) {
            let year = accolade.season_year;

            if (!(year in per_year)) {
                per_year[year] = {};
            }
            if (!("team_accolades" in per_year[year])) {
                per_year[year]["team_accolades"] = [];
            }
            // Modify the icons for team accolades to give bronze medal and silver
            if (accolade.accolade.name === "Liigamestaruus" && accolade.placement == 2) {
                accolade.accolade.icon = "hopea.ico"
            } else if (accolade.accolade.name === "Liigamestaruus" && accolade.placement == 3) {
                accolade.accolade.icon = "pronssi.ico"
            }

            if (accolade.accolade.name === "Liigamestaruus") {
                let tmp = "";
                if ([8, 16].includes(accolade.placement)) {
                    tmp = `Top${accolade.placement}`;
                } else if (accolade.placement == 1) {
                    tmp = "Mestaruus";
                } else {
                    tmp = `${accolade.placement}. sija`
                }
                if (Number(accolade.placement) > 3) {
                    accolade.accolade.icon = null
                }
                accolade.accolade.name = "NKL " + tmp;
            } else if (accolade.accolade.name === "SuperWeekend-Cup") {
                if (accolade.placement == 1) {
                    accolade.accolade.name = "SuperWeekend-Cup Mestaruus";
                } else if (accolade.placement == 2) {
                    accolade.accolade.name = "SuperWeekend-Cup Finalisti";
                    accolade.accolade.icon = "hopea.ico"
                } else {
                    continue;
                }
            }

            per_year[year]["team_accolades"].push(accolade);
        }
        return per_year;
    })

    async function getPlayerAccolades(playerId) {
        try {
            const response = await fetch(baseUrl + `?playerId=${playerId}`, { method: 'GET' });
            const data = await response.json();
            playerAccolades.value = data;
        } catch (error) {
            console.error('Error fetching accolades:', error);
        }
    }

    async function getTeamAccolades(teamId) {
        const response = await fetch(baseUrl + `?teamId=${teamId}`, { method: 'GET' });
        const data = await response.json();
        teamAccolades.value = data;
    }

    async function getAccoladeBySeason(seasonId) {
        try {
            const response = await fetch(baseUrl + `?seasonId=${seasonId}`, { method: 'GET' });
            const data = await response.json();
            seasonAccolades.value = data;
        } catch (error) {
            console.error('Error fetching accolade by season:', error);
        }
    }

    async function getAllAccolades() {
        try {
            const response = await fetch(baseUrl, { method: 'GET' });
            const data = await response.json();
            accolades.value = data;
        } catch (error) {
            console.error('Error fetching accolades:', error);
        }
    }

    async function getRecords() {
        try {
            recordsLoading.value = true;

            const response = await fetch(recordsUrl, { method: 'GET' });
            const data = await response.json();
            records.value = data;
        } catch (error) {
            console.error('Error fetching records:', error);

        } finally {
            recordsLoading.value = false;
        }
    }


    const championship = ref([
        { 'year': 2026, 'first': 'Dra', 'second': 'SulaKe', 'third': 'MCMC', 'fourth': 'STONKS' },
        { 'year': 2025, 'first': 'MaHaLasKu', 'second': 'Dra', 'third': 'ALTF4', 'fourth': 'MCMC' },
        { 'year': 2024, 'first': 'Dra', 'second': 'MaHaLasku', 'third': 'SuLaKe', 'fourth': 'DiSKO' },
        { 'year': 2023, 'first': 'MaHaLasKu', 'second': 'SÄTKY KY', 'third': 'DiSKO', 'fourth': 'VSOP' },
        { 'year': 2022, 'first': 'Ei', 'second': 'MaHaLasKu', 'third': 'SÄTKY KY', 'fourth': 'LSP' },
        { 'year': 2021, 'first': '-', 'second': '-', 'third': '-', 'fourth': '-' },
        { 'year': 2020, 'first': 'Ei', 'second': 'Dra', 'third': 'SFS-6016', 'fourth': 'MaMut' },
        { 'year': 2019, 'first': 'Dra', 'second': 'SICK', 'third': 'LePi', 'fourth': 'SFS-6016' },
        { 'year': 2018, 'first': 'YÖK', 'second': 'Darts', 'third': 'Dra', 'fourth': 'HC RiceCows' },
        { 'year': 2017, 'first': 'Darts', 'second': 'YÖK', 'third': 'Dra', 'fourth': 'PkO' },
        { 'year': 2016, 'first': 'GPK', 'second': 'Dra', 'third': 'FC HR', 'fourth': 'KC SKP' },
        { 'year': 2015, 'first': 'GPK', 'second': 'HC RiceCows', 'third': 'PkO', 'fourth': 'Dra' },
        { 'year': 2014, 'first': 'ASS', 'second': 'GPK', 'third': 'Dra', 'fourth': 'Panis' },
        { 'year': 2013, 'first': 'ASS', 'second': 'GPK', 'third': 'Panis', 'fourth': 'PaVa' },
        { 'year': 2012, 'first': 'Ak-47', 'second': 'Dra', 'third': 'ASS', 'fourth': 'GPK' },
        { 'year': 2011, 'first': 'ASS', 'second': 'LMTVO', 'third': 'PaVa', 'fourth': 'La Sól' },
        { 'year': 2010, 'first': 'LMTVO', 'second': 'GPK', 'third': 'HeMi', 'fourth': 'MULK' },
        { 'year': 2009, 'first': 'LMTVO', 'second': 'GPK', 'third': 'MULK', 'fourth': 'HUMP' },
        { 'year': 2008, 'first': 'LMTVO', 'second': 'PKMM', 'third': 'VTTU', 'fourth': 'GPK' },
        { 'year': 2007, 'first': 'LMTVO', 'second': 'Dra', 'third': 'ITKK', 'fourth': 'GPK' },
        { 'year': 2006, 'first': 'Dra', 'second': 'ITKK', 'third': 'LMTVO', 'fourth': 'PKMM' },
        { 'year': 2005, 'first': 'LMTVO', 'second': 'Dra', 'third': 'ITKK', 'fourth': 'KCK' },
        { 'year': 2004, 'first': 'Dra', 'second': 'ITKK', 'third': 'LMTVO', 'fourth': 'PLEE' },
        { 'year': 2003, 'first': 'ITKK', 'second': 'LSD', 'third': 'Dra', 'fourth': 'PKMM' },
        { 'year': 2002, 'first': 'ITKK', 'second': 'LMTVO', 'third': 'KCK', 'fourth': 'PKMM' },
        { 'year': 2001, 'first': 'PKMM', 'second': 'TPNMP', 'third': 'SMS', 'fourth': 'ITKK99' },
        { 'year': 2000, 'first': 'ITKK99', 'second': 'KCK', 'third': 'SMS', 'fourth': 'TPNMP' },
        { 'year': 1999, 'first': 'TPNMP', 'second': 'LSD', 'third': '?', 'fourth': '?' },
        { 'year': 1998, 'first': 'PKMM', 'second': 'Pentit', 'third': '-', 'fourth': '-' },
    ]);


    const superData = ref([
        { 'year': 2026, 'first': 'SulaKe', 'second': 'STONKS', 'third': 'Dra', 'fourth': 'MÄYRÄKOIRA' },
        { 'year': 2025, 'first': 'MaHaLasKu', 'second': 'SulaKe' },
        { 'year': 2024, 'first': 'Dra', 'second': 'VSOP' },
        { 'year': 2023, 'first': 'MaHaLasKu', 'second': 'VSOP' },
        { 'year': 2022, 'first': 'MaHaLasKu', 'second': "Ei" },
        { 'year': 2021, 'first': 'MaHaLasKu', 'second': "Dra" },
        { 'year': 2020, 'first': 'Dra', 'second': "Ei" },
        { 'year': 2019, 'first': 'Dra', 'second': "Darts" },
        { 'year': 2018, 'first': 'Darts', 'second': "YÖK" },
        { 'year': 2017, 'first': 'Dra', 'second': "?" },
        { 'year': 2016, 'first': 'Dra', 'second': "GPK" },
        { 'year': 2015, 'first': 'Dra', 'second': "?" },
        { 'year': 2014, 'first': 'ASS', 'second': 'GPK', 'third': 'VajaKK', 'fourth': 'MINT' },
        { 'year': 2013, 'first': 'Panis', 'second': 'ASS', 'third': 'GPK', 'fourth': 'TS' },
        { 'year': 2012, 'first': 'ASS', 'second': '?' },
        { 'year': 2011, 'first': 'ASS', 'second': 'HeMi' },
        { 'year': 2010, 'first': '?', 'second': '?' },
        { 'year': 2009, 'first': '?', 'second': '?' },
        { 'year': 2008, 'first': 'LMTVO', 'second': 'PKMM' },
        { 'year': 2007, 'first': 'LMTVO', 'second': 'ITKK', 'third': 'Dra', 'fourth': 'PKMM' },
        { 'year': 2006, 'first': 'GPK', 'second': 'Dra', },
        { 'year': 2005, 'first': 'ITKK', 'second': 'Dra' },
        { 'year': 2004, 'first': 'LSD', 'second': 'Dra', },
        { 'year': 2003, 'first': 'Dra', 'second': 'PKMM', },
        { 'year': 2002, 'first': 'KCK', 'second': 'LMTVO', },
        { 'year': 2001, 'first': 'KCK', 'second': 'SMS', },
    ]);

    const bracketWinners = ref([
        { 'year': 2026, 'first': 'MCMC' },
        { 'year': 2025, 'first': 'MaHaLasKu' },
        { 'year': 2024, 'first': 'Dra' },
        { 'year': 2023, 'first': 'SÄTKY KY' },
        { 'year': 2022, 'first': 'MaHaLasKu' },
        { 'year': 2021, 'first': 'SFS-6016' },
        { 'year': 2020, 'first': 'Ei' },
        { 'year': 2019, 'first': 'Darts' },
        { 'year': 2018, 'first': 'YÖK' },
        { 'year': 2017, 'first': 'Dra' },
        { 'year': 2016, 'first': 'GPK' },
        { 'year': 2015, 'first': 'GPK' },
        { 'year': 2014, 'first': 'ASS' },
        { 'year': 2013, 'first': 'GPK' },
        { 'year': 2012, 'first': 'GPK' },
        { 'year': 2011, 'first': 'ASS' },
        { 'year': 2010, 'first': 'LMTVO' },
        { 'year': 2009, 'first': 'LMTVO' },
        { 'year': 2008, 'first': 'LMTVO' },
        { 'year': 2007, 'first': 'Dra' },
        { 'year': 2006, 'first': 'ITKK*' },
        { 'year': 2005, 'first': 'Dra*' },
        { 'year': 2004, 'first': 'Dra*' },
        { 'year': 2003, 'first': 'Dra*' },
        { 'year': 2002, 'first': 'LMTVO*' },
        { 'year': 2001, 'first': 'ITKK99*' },
        { 'year': 2000, 'first': 'KCK / TPNMP*✞' },
    ]);


    const singleWinner = ref([
        { 'year': 2026, 'first': 'Leevi Hovatov', 'second': 'Atte Putkonen' },
        { 'year': 2025, 'first': 'Totti Sillanpää', 'second': 'Mikko "Temmi" Kuusio' },
        { 'year': 2024, 'first': 'Leevi Hovatov', 'second': 'Mikko "Temmi" Kuusio' },
        { 'year': 2023, 'first': 'Atte Putkonen', 'second': 'Sami Valjakka' },
        { 'year': 2022, 'first': 'Lassi Onne', 'second': "Leevi Hovatov" },
        { 'year': 2021, 'first': '-', 'second': '-' },
        { 'year': 2020, 'first': 'Elmo Pärssinen', 'second': "Lassi Onne" },
        { 'year': 2019, 'first': 'Armi Rissanen', 'second': "Leevi Hovatov" },
        { 'year': 2018, 'first': 'Jyri "Kode" Koistinen', 'second': "Armi Rissanen" },
        { 'year': 2017, 'first': 'Ville Kytömäki', 'second': "Masi Kähkönen" },
        { 'year': 2016, 'first': '-', 'second': "-" },
        { 'year': 2015, 'first': '-', 'second': "-" },
        { 'year': 2014, 'first': 'Juha Varis', 'second': "Petteri Westerholm", 'third': "Tiina Viitanen" },
        { 'year': 2013, 'first': 'Petteri Westerholm', 'second': "Anssi Tura" },
        { 'year': 2012, 'first': 'Petteri Westerholm', 'second': "Juha Varis" },
        { 'year': 2011, 'first': 'Petteri Westerholm', 'second': "?" },
        { 'year': 2010, 'first': 'Mikko "Temmi" Kuusio', 'second': "?" },
    ]);

    const pairWinners = ref([
        { 'year': 2025, 'first': '-', 'second': "-" },
        { 'year': 2024, 'first': 'Totti Sillanpää, Oskari Ekholm', 'second': "Eemil Ivars, Olli Aula" },
        { 'year': 2023, 'first': 'Erik Kuitunen, Totti Sillanpää', 'second': "Mikko 'Temmi' Kuusio, Pasi Kortelainen" },
        { 'year': 2022, 'first': 'Erik Kuitunen, Jarno Mikkola', 'second': "Totti Sillanpää, Veikka Immonen" },
        { 'year': 2021, 'first': 'Lassi Onne, Elmo Pärssinen', 'second': "Jarno Mikkola, Totti Sillanpää" },
    ]);

    const jaskanKarttu = ref([
        { 'year': 2026, 'name': 'Jarno Mikkola' },
        { 'year': 2026, 'name': 'Totti Sillanpää' },
        { 'year': 2024, 'name': 'Lassi Onne' },
        { 'year': 2022, 'name': 'Heikki Lohilahti' },
        { 'year': 2016, 'name': 'Anssi Tura' },
        { 'year': 2012, 'name': 'Paavo Leinonen' },
        { 'year': 2011, 'name': 'Juha Varis' },
        { 'year': 2010, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2009, 'name': 'Tero Turtianen' },

    ]);

    const KCKAhti = ref([
        { 'year': 2026, 'name': 'Oskari Ekholm' },
        { 'year': 2025, 'name': 'Jarno Mikkola' },
        { 'year': 2024, 'name': '-' },
        { 'year': 2023, 'name': "Saara Inkinen" },
        { 'year': 2022, 'name': "Tomi Krokberg" },
        { 'year': 2021, 'name': "-" },
        { 'year': 2020, 'name': "Saku Laakkonen" },
        { 'year': 2019, 'name': "Niko Sievänen" },
        { 'year': 2018, 'name': "Lauri Tuimala" },
        { 'year': 2017, 'name': "-" },
        { 'year': 2016, 'name': "-" },
        { 'year': 2015, 'name': "Niko Sievänen" },
        { 'year': 2014, 'name': "Petteri Mustonen" },
        { 'year': 2013, 'name': "Ilkka Kari" },
        { 'year': 2012, 'name': "Matti Peittilä" },
        { 'year': 2011, 'name': "-" },
        { 'year': 2010, 'name': "-" },
        { 'year': 2009, 'name': "Tuomas Aalto" },
        { 'year': 2008, 'name': "Outi Matikainen" },
        { 'year': 2007, 'name': "Jyri Koistinen" },
        { 'year': 2006, 'name': "Kalle Rannikko" },
        { 'year': 2005, 'name': "Mikko Raatikainen" },
        { 'year': 2004, 'name': "Janne Matikainen" },
        { 'year': 2003, 'name': "Samu Uimonen" },
        { 'year': 2002, 'name': "Mikko Drocan" },
        { 'year': 2001, 'name': "Sami Mannelin" },
        { 'year': 2000, 'name': "Raine Koponen" },
    ]);

    const hauki = ref([
        { 'year': 2026, 'name': 'Joona Vähätiitto' },
        { 'year': 2025, 'name': 'Lauri Sorsa' },
        { 'year': 2024, 'name': 'Armi Rissanen' },
        { 'year': 2023, 'name': "Saara Inkinen" },
        { 'year': 2022, 'name': "Tomi Krokberg" },
        { 'year': 2021, 'name': "-" },
        { 'year': 2020, 'name': "Saku Laakkonen" },
        { 'year': 2019, 'name': "?" },
        { 'year': 2018, 'name': "?" },
        { 'year': 2017, 'name': "Kuisma Närhi" },
        { 'year': 2016, 'name': "?" },
        { 'year': 2015, 'name': "?" },
        { 'year': 2014, 'name': "Harri Renkonen" },
        { 'year': 2013, 'name': "?" },
        { 'year': 2012, 'name': "Erkka Holviala" },
        { 'year': 2011, 'name': "Henrik Tarkkio" },
        { 'year': 2010, 'name': "Jacinto Javier Ramirez Lahti" },
        { 'year': 2009, 'name': "Veli-Mikko Ikonen" },
        { 'year': 2008, 'name': "Ville Varma" },
        { 'year': 2007, 'name': "Seppo Kyynäräinen" },
        { 'year': 2006, 'name': "Seppo Kyynäräinen" },
        { 'year': 2005, 'name': "Risto Tapanen" },
        { 'year': 2004, 'name': "Sami Kontio" },
        { 'year': 2003, 'name': "Janne Lahdenperä" },
        { 'year': 2002, 'name': "Sampo Kokkonen" },
        { 'year': 2001, 'name': "Sampo Kokkonen" },
        { 'year': 2000, 'name': "Ilmari Laakkonen*" },
        { 'year': 1999, 'name': "Tero Turtiainen" },
        { 'year': 1998, 'name': "-" },
    ]);

    const last = ref([
        { 'year': 2026, 'name': "Eero Ryhänen" },
        { 'year': 2025, 'name': "Jyri 'Kode' Koistinen" },
        { 'year': 2024, 'name': "Jyri 'Kode' Koistinen" },
        { 'year': 2023, 'name': "Totti Sillanpää" },
        { 'year': 2022, 'name': "Totti Sillanpää" },
        { 'year': 2021, 'name': "-" },
        { 'year': 2020, 'name': "Kuisma Närhi" },
        { 'year': 2019, 'name': "?" },
        { 'year': 2018, 'name': "?" },
        { 'year': 2017, 'name': "Jesse Meuronen" },
        { 'year': 2016, 'name': "?" },
        { 'year': 2015, 'name': "?" },
        { 'year': 2014, 'name': "Anssi Tura" },
        { 'year': 2013, 'name': "?" },
        { 'year': 2012, 'name': "Juha Varis" },
        { 'year': 2011, 'name': "Uki Vuotilainen" },
        { 'year': 2010, 'name': "Paavo Leinonen" },
        { 'year': 2009, 'name': "Paavo Leinonen" },
        { 'year': 2008, 'name': "Juha Varis" },
        { 'year': 2007, 'name': "Juha Varis" },
        { 'year': 2006, 'name': "Sami Pyykkö" },
        { 'year': 2005, 'name': "Sami Pyykkö" },
        { 'year': 2004, 'name': "Janne Pulli" },
        { 'year': 2003, 'name': "Mikko Drocan" },
        { 'year': 2002, 'name': "-" },
        { 'year': 2001, 'name': "-" },
        { 'year': 2000, 'name': "-" },
    ]);

    const p_o_y = ref([
        { 'year': 2026, 'name': "Atte Putkonen" },
        { 'year': 2025, 'name': "Totti Sillanpää" },
        { 'year': 2024, 'name': "-" },
        { 'year': 2023, 'name': "Armi Rissanen" },
        { 'year': 2022, 'name': "Jarno Mikkola" },
        { 'year': 2021, 'name': "-" },
        { 'year': 2020, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2019, 'name': "Masi Kähkönen" },
        { 'year': 2018, 'name': "Masi Kähkönen" },
        { 'year': 2017, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2016, 'name': "?" },
        { 'year': 2015, 'name': "Juha Varis" },
        { 'year': 2014, 'name': "Petteri Westerholm" },
        { 'year': 2013, 'name': "?" },
        { 'year': 2012, 'name': "Petteri Westerholm" },
        { 'year': 2011, 'name': "Petteri Westerholm" },
        { 'year': 2010, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2009, 'name': "Juha Varis" },
        { 'year': 2008, 'name': "Juha Varis" },
        { 'year': 2007, 'name': "Katja Talvirinne" },
        { 'year': 2006, 'name': "Niko Kuikka" },
        { 'year': 2005, 'name': "Juha Varis" },
        { 'year': 2004, 'name': "Jussi Ahonen" },
        { 'year': 2003, 'name': "Juha Varis" },
        { 'year': 2002, 'name': "Juha Varis" },
        { 'year': 2001, 'name': "Saku Ruottinen" },
        { 'year': 2000, 'name': "?" },
        { 'year': 1999, 'name': "Jaakko Akkanen" },
        { 'year': 1998, 'name': "-" },
    ]);

    const mvp = ref([
        { 'year': 2026, 'name': "Juho Hautaniemi" },
        { 'year': 2025, 'name': "Sami Valjakka" },
        { 'year': 2024, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2023, 'name': "Atte Putkonen" },
    ])

    const man_woman = ref([
        { 'year': 2026, 'name': "Inka Hatara" },
        { 'year': 2025, 'name': "Vilma Rantanen" },
        { 'year': 2024, 'name': "Totti Sillanpää/Armi Rissanen" },
        { 'year': 2023, 'name': "Markus Laitinen" },
        { 'year': 2022, 'name': "Armi Rissanen" },
        { 'year': 2021, 'name': "-" },
        { 'year': 2020, 'name': "Sonja Töyrylä" },
        { 'year': 2019, 'name': "Armi Rissanen" },
        { 'year': 2018, 'name': "?" },
        { 'year': 2017, 'name': "Armi Rissanen" },
        { 'year': 2016, 'name': "?" },
        { 'year': 2015, 'name': "?" },
        { 'year': 2014, 'name': "Tiina Viitanen" },
        { 'year': 2013, 'name': "?" },
        { 'year': 2012, 'name': "Katja Talvirinne" },
        { 'year': 2011, 'name': "Anna Sundquist" },
        { 'year': 2010, 'name': "Maria Viikilä" },
    ]);

    const bracketBest = ref([
        { 'year': 2026, 'name': "Niko Grön" },
        { 'year': 2025, 'name': "Totti Sillanpää" },
        { 'year': 2024, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2023, 'name': "Niko Grön" },
        { 'year': 2022, 'name': "Sami Valjakka" },
        { 'year': 2021, 'name': "-" },
        { 'year': 2020, 'name': "Lassi Onne" },
        { 'year': 2019, 'name': "?" },
        { 'year': 2018, 'name': "?" },
        { 'year': 2017, 'name': "Ville Kytömäki" },
        { 'year': 2016, 'name': "?" },
        { 'year': 2015, 'name': "Juha Varis" },
        { 'year': 2014, 'name': "Petteri Westerholm" },
        { 'year': 2013, 'name': "?" },
        { 'year': 2012, 'name': "Petteri Westerholm" },
        { 'year': 2011, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2010, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2009, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2008, 'name': "Janne Matikainen" },
        { 'year': 2007, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2006, 'name': "Niko Kuikka" },
        { 'year': 2005, 'name': "Jussi Ahonen" },
        { 'year': 2004, 'name': "Jukka Tanninen" },
        { 'year': 2003, 'name': "Juha Varis" },
        { 'year': 2002, 'name': "Juha Varis" },
        { 'year': 2001, 'name': "Tero Turtiainen" },
        { 'year': 2000, 'name': "?" },
        { 'year': 1999, 'name': "-" },
        { 'year': 1998, 'name': "-" },
    ]);

    const playoffBest = ref([
        { 'year': 2026, 'name': "Samuli Kantola" },
        { 'year': 2025, 'name': "Erik 'Eki' Kuitunen" },
        { 'year': 2024, 'name': "Leevi Hovatov" },
        { 'year': 2023, 'name': "Leevi Hovatov" },
        { 'year': 2022, 'name': "Atte Putkonen" },
        { 'year': 2021, 'name': "-" },
        { 'year': 2020, 'name': "Sami Aalto" },
        { 'year': 2019, 'name': "?" },
        { 'year': 2018, 'name': "?" },
        { 'year': 2017, 'name': "Petteri Westerholm" },
        { 'year': 2016, 'name': "?" },
        { 'year': 2015, 'name': "Juha Varis" },
        { 'year': 2014, 'name': "Petteri Westerholm" },
        { 'year': 2013, 'name': "?" },
        { 'year': 2012, 'name': "Juha Varis" },
        { 'year': 2011, 'name': "Petteri Westerholm" },
        { 'year': 2010, 'name': "Tuomas Korppi" },
        { 'year': 2009, 'name': "Janne Matikainen" },
        { 'year': 2008, 'name': "Aki Penttinen" },
        { 'year': 2007, 'name': "Janne Matikainen" },
        { 'year': 2006, 'name': "Janne Matikainen" },
        { 'year': 2005, 'name': "Sami Pyykkö" },
        { 'year': 2004, 'name': "Jussi Ahonen" },
        { 'year': 2003, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2002, 'name': "Joni Kämäräinen" },
        { 'year': 2001, 'name': "Mika Alitalo" },
        { 'year': 2000, 'name': "Saku Ruottinen" },
        { 'year': 1999, 'name': "Jaakko Akkanen" },
        { 'year': 1998, 'name': "-" },
    ]);

    const rookie = ref([
        { 'year': 2026, 'name': "Leevi Nevalainen" },
        { 'year': 2025, 'name': "Veikka Rantala" },
        { 'year': 2024, 'name': "Eino Auvinen" },
        { 'year': 2023, 'name': "Eetu Knutars" },
        { 'year': 2022, 'name': "Lauri Lempiö" },
        { 'year': 2021, 'name': "-" },
        { 'year': 2020, 'name': "Erik Kuitunen" },
        { 'year': 2019, 'name': "?" },
        { 'year': 2018, 'name': "Vilppu Penttilä" },
        { 'year': 2017, 'name': "Elmo Pärssinen" },
        { 'year': 2016, 'name': "Ville Raukola (?)" },
        { 'year': 2015, 'name': "?" },
        { 'year': 2014, 'name': "Niko Strömberg" },
        { 'year': 2013, 'name': "?" },
        { 'year': 2012, 'name': "Henri Syyslahti" },
        { 'year': 2011, 'name': "Ville Vesterinen" },
        { 'year': 2010, 'name': "Ioannis Megas" },
        { 'year': 2009, 'name': "Petteri Westerholm" },
        { 'year': 2008, 'name': "Matti Tianen / Rauli Sillanpää" },
        { 'year': 2007, 'name': "Tuomas Aalto" },
        { 'year': 2006, 'name': "Henrik Tarkkio" },
        { 'year': 2005, 'name': "Fredrik Löfberg" },
        { 'year': 2004, 'name': "Janne Keränen" },
        { 'year': 2003, 'name': "Jukka Tanninen" },
        { 'year': 2002, 'name': "Janne Matikainen" },
        { 'year': 2001, 'name': "Sami Hämäläinen" },
        { 'year': 2000, 'name': "?" },
        { 'year': 1999, 'name': "Riku Kemppainen" },
        { 'year': 1998, 'name': "-" },
    ]);

    const tree = ref([
        { 'year': 2026, 'name': "Samuli Kantola" },
        { 'year': 2025, 'name': "Joona Lappalainen" },
        { 'year': 2024, 'name': "Mikko 'Temmi' Kuusio" },
        { 'year': 2023, 'name': "Joona Lappalainen" },
        { 'year': 2022, 'name': "Jarno Mikkola" },
    ]);

    const misc = ref([
        { 'year': 2026, 'name': 'Vuoden Fifty-Sixty', 'person': "Herkko Teittinen" },
        { 'year': 2026, 'name': 'Vuoden Heitto', 'person': "Ekin 10 kyykän + papin heitto puolivälierässä" },
        { 'year': 2025, 'name': 'Vuoden Heitto', 'person': "Masin kuuden kyykän lakaisu finaalissa" },
        { 'year': 2025, 'name': 'Vuoden Sulaminen', 'person': "AMK:n parkkipaikat ennen PoWiCupia" },
        { 'year': 2025, 'name': 'Vuoden Byrokraatti', 'person': "Atso Härkönen" },
        { 'year': 2025, 'name': 'Vuoden Epäilmiö', 'person': "MÄYRÄKOIRA" },
        { 'year': 2024, 'name': 'Vuoden Ilmiö', 'person': "KOFF" },
        { 'year': 2024, 'name': "Vuoden Kyykkacom", 'person': "Totti Sillanpää" },
        { 'year': 2022, 'name': "Vuoden Suurin Yllätys", 'person': "SÄTKY ky:n pronssi" },
        { 'year': 2022, 'name': "Suurin Sulaminen", 'person': "LSP kolme viimeistä mailaa yhteen kyykkään haukia, johtaen häviöön TAI K-Mafian häviö sätkyä vastaan jatkosarjassa." },
        { 'year': 2022, 'name': "Vuoden Heitto", 'person': "Elmon kahdeksan kyykän poisto finaalin viimeisen ottelun viimeisessä erässä." },
        { 'year': 2022, 'name': "Vuoden Pettymys", 'person': "K-Mafia ei tyhjentänyt" },
        { 'year': 2022, 'name': "Vuoden Onnekas", 'person': "Atso Härkönen, kolme kappaletta kolmen kyykän kilkkejä yhden pelipäivän aikana. Myös Lassi." }
    ]);

    const old_mentions = ref([
        { 'year': 2007, 'name': 'Faniklubin suosikkipelaaja', 'person': 'Juha Varis' },
        { 'year': 2006, 'name': 'Illan Tähti', 'person': "Niko Kuikka" },
        { 'year': 2006, 'name': 'Faniklubin suosikkipelaaja', 'person': 'Marjo Nieminen' },
        { 'year': 2005, 'name': 'Illan Tähti', 'person': "Mikko 'Temmi' Kuusio" },
        { 'year': 2005, 'name': 'Faniklubin suosikkipelaaja', 'person': 'Mikko Raatikainen' },
        { 'year': 2004, 'name': 'Illan Tähti', 'person': 'Katja Talvirinne' },
        { 'year': 2004, 'name': 'Faniklubin suosikkipelaaja', 'person': 'Jussi Ahonen' },
        { 'year': 2003, 'name': 'Illan Tähti', 'person': 'Juha Varis' },


        { 'year': 1999, 'name': 'Vuoden tuomari', 'person': 'Ossi Hämäläinen' },
        { 'year': 1999, 'name': 'Herrasmiespelaaja', 'person': 'Jarkko Sonninen' },
        { 'year': 1999, 'name': 'Kuvauksellisin pelaaja', 'person': 'Janne Pulli' },
        { 'year': 1999, 'name': 'Faniklubin suosikkipelaaja', 'person': 'Marko Parviainen' },
        { 'year': 1999, 'name': 'Finaalien MVP', 'person': 'Riku Kemppainen' }
    ])

    const sm = ref([
        { 'year': 2026, 'first': 'TBD', 'second': 'TBD' },
        { 'year': 2025, 'first': 'Cluster Prospects', 'second': 'MÄYRÄKOIRA' },
        { 'year': 2024, 'first': 'MaHaLasKu', 'second': 'DiSKO' },
        { 'year': 2023, 'first': 'MaHaLasKu', 'second': 'VSOP' },
        { 'year': 2022, 'first': 'Booga', 'second': "MaHaLasKu" },
        { 'year': 2021, 'first': 'MaHaLasKu', 'second': "Ei" },
        { 'year': 2020, 'first': 'MaHaLasKu', 'second': "Ei" },
        { 'year': 2019, 'first': '?', 'second': "?" },
        { 'year': 2018, 'first': 'NöHö', 'second': "?" },
        { 'year': 2017, 'first': '?', 'second': "?" },
        { 'year': 2016, 'first': '?', 'second': "?" },
        { 'year': 2015, 'first': '?', 'second': "?" },
        { 'year': 2014, 'first': '?', 'second': "?" },
        { 'year': 2013, 'first': '?', 'second': "?" },

    ]);

    const stars = ref([
        { 'year': 2025, 'first': '⭐ Sami Valjakka, Leevi Nevalainen', 'second': '⭐ Eero Koskikallio, Kaarlo Virtanen' },
        { 'year': 2024, 'first': '⭐ Sami Valjakka, Lauri Sorsa', 'second': '⭐ Eino Auvinen, Matias Ylätalo' },
        { 'year': 2023, 'first': '⭐ Totti Sillanpää, Juho Sallasmaa', 'second': '⭐ lassi onne, Veeti Sistonen' },
        { 'year': 2022, 'first': '⭐ Sami Valjakka, Antti Koivulahti', 'second': '⭐ Jarno Mikkola, Katja Rossi' },
        { 'year': 2021, 'first': '⭐ Elmo Pärssinen, Outi Jaakkola', 'second': '⭐ Jarno Mikkola, Vilma Rantanen' },
        { 'year': 2020, 'first': '⭐ lassi onne, Markus Laitinen', 'second': '⭐ Heikki Lohilahti, Juho Hautaniemi' },
        { 'year': 2019, 'first': '⭐ ?, ?', 'second': '⭐ ?, ?' },
        { 'year': 2018, 'first': '⭐ Elmo Pärssinen, Hanno Brander', 'second': '⭐ ?, ?' },
        { 'year': 2017, 'first': '⭐ ?, ?', 'second': '⭐ ?, ?' },
        { 'year': 2016, 'first': '⭐ Petri Manninen, Elmo Pärssinen', 'second': '⭐ ?, ?' },
        { 'year': 2015, 'first': '⭐ ?, ?', 'second': '⭐ ?, ?' },
        { 'year': 2014, 'first': '⭐ ?, ?', 'second': '⭐ ?, ?' },
        { 'year': 2013, 'first': '⭐ ?, ?', 'second': '⭐ ?, ?' },
        { 'year': 2012, 'first': '⭐ ?, ?', 'second': '⭐ ?, ?' },
    ])

    return {
        getAllAccolades,
        getAccoladeBySeason,
        getPlayerAccolades,
        getTeamAccolades,
        getRecords,
        championship,
        superData,
        bracketWinners,
        singleWinner,
        pairWinners,
        jaskanKarttu,
        KCKAhti,
        hauki,
        last,
        mvp,
        man_woman,
        p_o_y,
        old_mentions,
        bracketBest,
        playoffBest,
        rookie,
        tree,
        misc,
        sm,
        stars,
        medalTableTeams,
        medalTablePlayers,
        playerAccolades,
        playerAccoladesBySeason,
        teamAccoladesBySeason,
        teamAccolades,
        records,
        recordsLoading,
    }

})