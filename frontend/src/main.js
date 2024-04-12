// import { createApp } from 'vue'
// import { createPinia } from 'pinia'
// import { router } from './router'
// import vuetify from './plugins/vuetify'
// import App from './App.vue'


// const app = createApp(App)

// app.use(router)
// app.use(vuetify)
// app.use(createPinia())
// app.use(createVuetify)

// app.mount('#app')

/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'
import './index.css'

const app = createApp(App)

registerPlugins(app)

app.mount('#app')