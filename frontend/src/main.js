import '@babel/polyfill';
import Vue from 'vue';
import './plugins/vuetify';
import App from './App.vue';
import router from './router';

Vue.config.productionTip = false;

export const eventBus = new Vue();

import VueResource from 'vue-resource';
import VueSession from 'vue-session';

Vue.use(VueResource);
Vue.use(VueSession);
Vue.use(require('vue-moment'));

new Vue({
    router,
    render: function(h) {
        return h(App);
    }
}).$mount('#app');
