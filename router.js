// import { createRouter, createWebHistory } from 'vue-router'

// // Instead of static import, use dynamic to make pages lazy-loaded
// export const router = createRouter({
//   history: createWebHistory(import.meta.env.BASE_URL),
//   linkActiveClass: 'active',
//   routes: [
//     { path: '/', component: () => import("./pages/Home.vue") },
//     { path: '/info', component: () => import("./pages/Info.vue") },
//     { path: '/kyykka_admin', component: () => import("./pages/Admin.vue") },
//     { path: '/ottelut', component: () => import("./pages/Matches.vue") },
//     { path: '/ottelu/(.*)',component: () => import("./pages/Match.vue")},
//     { path: '/joukkueet', component: () => import("./pages/Teams.vue") },
//     { path: '/joukkue/(.*)', component: () => import("./pages/Team.vue") },
//     { path: '/pelaajat', component: () => import("./pages/Players.vue") },
//     { path: '/pelaaja/(.*)', component: () => import("./pages/Player.vue") },
//     { path: '/superweekend', component: () => import("./pages/SuperWeekend.vue")},
//     { path: '/jatkosarja', component: () => import("./pages/Playoffs.vue")},

//   ]
// })
