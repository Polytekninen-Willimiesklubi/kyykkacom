import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';

Vue.use(Router);

export default new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        {
            path: '/',
            name: 'home',
            component: Home
        },
        {
            path: '/info',
            name: 'info',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "info" */ './views/Info.vue');
            }
        },
        {
            path: '/ottelut',
            name: 'ottelut',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "ottelut" */ './views/OttelutView.vue');
            }
        },
        {
            path: '/ottelu/(.*)',
            name: 'ottelu',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "ottelut" */ './views/SingleOtteluView.vue');
            }
        },
        {
            path: '/joukkueet',
            name: 'joukkueet',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "joukkueet" */ './views/Joukkueet.vue');
            }
        },
        {
            path: '/pelaajat',
            name: 'pelaajat',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "pelaajat" */ './views/PelaajatView.vue');
            }
        },
        {
            path: '/joukkue/(.*)',
            name: 'joukkue',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "joukkue" */ './views/JoukkueView.vue');
            }
        },
        {
            path: '/pelaaja/(.*)',
            name: 'pelaaja',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "pelaaja" */ './views/PelaajaView.vue');
            }
        },
        {
            path: '/kyykka_admin',
            name: 'kyykka_admin',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "kyykka_admin" */ './views/AdminView.vue');
            }
        },
        {
            path: '/superweekend',
            name: 'superweekend',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "superweekend" */ './views/SuperWeekendView.vue');
            }
        },
        {
            path: '/jatkosarja',
            name: 'jatkosarja',
            // route level code-splitting
            // this generates a separate chunk (about.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: function () {
                return import(/* webpackChunkName: "jatkosarja" */ './views/JatkosarjaView.vue');
            }
        },
    ]
});
