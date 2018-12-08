<template>
  <div>
    <div class="w-100 px-5">
      <div class="row mt-5 mb-5">
        <div class="col-sm-12 mb-5 d-flex justify-content-between align-items-center">
          <div>
          <h5>Security Report for</h5>
          <h4 class="font-weight-bold"><i class="fab fa-github"></i> {{ auditInfo.repo }}</h4>
          <small>Submitted: {{ (new Date(auditInfo.submitted)).toString() }}</small>
          </div>
          <div>
            <span class="font-weight-bold">Share this report:</span><br/>
            <span class="mb-5"><input class="link-input" type="text" name="pageLink" id="pageLink" v-bind:value="pageLink"> <i v-on:click="copyLink('pageLink')" class="fas fa-copy"></i></span><br/>
            <span class="font-weight-bold">GitHub badge (Markdown):</span><br/>
            <span><input class="link-input" type="text" name="badgeMarkdown" id="badgeMarkdown" v-bind:value="badgeMarkdown"> <a href="javascript:void(0);"><i v-on:click="copyLink('badgeMarkdown')" class="fas fa-copy"></i></a></span><br/>
          </div>
        </div>
        <div class="col-sm-2 d-flex justify-content-center" style="height: 500px">
          <div class="text-center w-100">
          <b><i class="fas fa-file-code" style="font-size: 1.5em"></i></b><br/>
          <b>Solidity Files</b>
          <div class="divider"></div>
          <ul class="pl-0 text-center list-unstyled">
            <a v-for="(contract, name) in auditInfo.contracts" :key="name" v-on:click="switchContract(name)" href="javascript:void(0);"><li v-bind:class="{ 'font-weight-bold bg-dark text-white rounded': name === openedContract }" class="mb-2">{{ name }}</li></a>
          </ul>
          </div>
        </div>
        <div class="col-sm-10 d-flex justify-content-center">
          <div class="loader" v-if="loading === true"></div>
          <editor v-if="!loading" v-model="auditInfo.contracts[openedContract]" @init="editorInit" lang="solidity" theme="mono_industrial" height="500"></editor>
        </div>
      </div>
    </div>

    <div v-if="!loading" class="row mt-5 pb-5 mx-0 results-div text-white">
      <div class="container">
        <h2 class="mt-4 mb-1"><b><i class="fas fa-shield-alt"></i> Vulnerability Details</b></h2>
        <span class="montserrat">Please click a vulnerability to view detailed information about it. </span>
        <div class="accordion text-dark mt-5" id="reportAccordion">
          <div v-for="(issue, index) in sortedReport" :key="index" class="card">
            <div class="card-header pl-1 font-weight-bold" v-bind:id="`heading${index}`">
              <h5 class="mb-0 d-flex justify-content-between align-items-center">
                <button v-bind:class="index === 0 ? '' : 'collapsed'" class="btn w-75 bg-transparent text-left" type="button" data-toggle="collapse" v-bind:data-target="`#collapse${index}`" v-bind:aria-expanded="index === 0" v-bind:aria-controls="`collapse${index}`"><span v-bind:class="[classMap[issue.severity]]" class="badge badge-pill mr-2" style="width: 120px;">{{ severityMap[issue.severity] }}</span> {{ issue.name }}
                </button>
                <span class="badge badge-pill text-dark">{{ issue.instances.length }}</span>
              </h5>
            </div>

            <div v-bind:id="`collapse${index}`" v-bind:class="index === 0 ? 'show' : ''" class="collapse" v-bind:aria-labelledby="`heading${index}`" data-parent="#reportAccordion">
              <div class="card-body">
                <li v-for="(instance, instance_index) in issue.instances" :key="instance_index">{{ instance.info }}</li>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'GithubResultComponent',
  props: ['audit_data'],
  data () {
    return {
      sortedReport: [],
      badgeMarkdown: '',
      openedContract: '',
      loading: true,
      classMap: ['badge-danger', 'badge-warning', 'badge-info', 'badge-dark'],
      severityMap: ['High Impact', 'Medium Impact', 'Low Impact', 'Informational'],
      pageLink: window.location.href,
      auditInfo: {contract: ''}
    }
  },
  mounted () {
    axios.get(`http://localhost:8000/api/github-audit/${this.$route.params.auditTracker}`)
      .then((response) => {
        this.loading = false
        if (response.data && response.data.id) {
          this.auditInfo = response.data
          this.badgeMarkdown = `[![SolCheckr](https://solcheckr.localtunnel.me/api/badge?tracking=${this.auditInfo.tracking})](https://solcheckr.localtunnel.me/#/github-audit/${this.auditInfo.tracking})`
          this.openedContract = this._.keys(this.auditInfo.contracts)[0]

          let previousName = ''
          let rawReport = {}
          this._.forEach(this.auditInfo.report, (item) => {
            if (item.description !== previousName && !rawReport[item.description]) {
              rawReport[item.description] = {
                name: item.description,
                severity: item.severity,
                instances: [item]
              }
            } else {
              rawReport[item.description].instances.push(item)
            }
          })
          this.sortedReport = this._.orderBy(rawReport, ['severity', 'name'], ['asc', 'asc'])
        }
      })
      .catch((err) => {
        console.log(err, 'error!')
        this.loading = false
        if (err.response.data && err.response.data.error) {
          this.error = err.response.data
        }
      })
  },
  methods: {
    editorInit (editorElem) {
      editorElem.setReadOnly(true)
      require('brace/ext/language_tools')
      require('brace/theme/mono_industrial')
      require('../assets/js/solidity.js')
    },
    switchContract (name) {
      this.openedContract = name
    },
    copyLink (copyId) {
      var copyText = document.getElementById(copyId)
      copyText.select()
      document.execCommand('copy')
    }
  },
  components: {
    editor: require('vue2-ace-editor')
  }
}
</script>

<style scoped>
.ace_editor {
  font-size: 16px !important;
}
</style>
