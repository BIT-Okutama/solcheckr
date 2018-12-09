import Vue from 'vue'
import Router from 'vue-router'
import MainComponent from '@/components/MainComponent'
import ResultComponent from '@/components/ResultComponent'
import GithubResultComponent from '@/components/GithubResultComponent'
import ZipResultComponent from '@/components/ZipResultComponent'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'MainComponent',
      component: MainComponent
    },
    {
      path: '/audit/:auditTracker',
      name: 'ResultComponent',
      component: ResultComponent
    },
    {
      path: '/github-audit/:auditTracker',
      name: 'GithubResultComponent',
      component: GithubResultComponent
    },
    {
      path: '/zip-audit/:auditTracker',
      name: 'ZipResultComponent',
      component: ZipResultComponent
    }
  ]
})
