// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import Header from './Header'
import router from './router'
import './assets/css/app.scss'

Vue.config.productionTip = false
Vue.set(Vue.prototype, '_', require('lodash'))

/* eslint-disable no-new */
new Vue({
  el: '#header',
  components: { Header },
  template: '<Header/>'
})

new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
