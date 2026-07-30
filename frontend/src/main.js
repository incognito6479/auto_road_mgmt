import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
// Global adaptive layer — must load after component styles so its
// media-query overrides win. See the file header for why it uses !important.
import './assets/responsive.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
