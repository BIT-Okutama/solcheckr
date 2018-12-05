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
            <span class="mb-5"><input class="link-input" type="text" name="pageLink" id="pageLink" v-bind:value="pageLink"> <i class="fas fa-copy"></i></span><br/>
            <span class="font-weight-bold">GitHub badge (Markdown):</span><br/>
            <span><input class="link-input" type="text" name="badgeMarkdown" id="badgeMarkdown" v-bind:value="badgeMarkdown"> <i class="fas fa-copy"></i></span><br/>
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
    <div v-if="!loading" class="row mt-5 mx-0 results-div text-white">
      <div class="container">
        <h1 class="mt-4 mb-1"><b>Security Report</b></h1>
        <div v-bind:class="[classMap[issue.severity]]" class="alert" role="alert" v-for="(issue, index) in auditInfo.report" :key="index">
          <p><b>{{ issue.description }}</b></p>
          <p v-if="issue.severity !== null">Severity: <b>{{ severityMap[issue.severity] }}</b></p>
          <p v-if="issue.contract">Contract: <b>{{ issue.contract }}</b></p>
          <p v-if="issue.sourceMapping.lines">Line(s): {{ issue.sourceMapping.lines[0] }}<span v-if="issue.sourceMapping.lines.length > 1 && issue.sourceMapping.lines[0] != issue.sourceMapping.lines[issue.sourceMapping.lines.length - 1]">:{{ issue.sourceMapping.lines[issue.sourceMapping.lines.length - 1] }}</span></p>
          <p v-if="issue.lines">Line(s): {{ issue.lines[0] }}<span v-if="issue.lines.length > 1 && issue.lines[0] != issue.lines[issue.lines.length - 1]">:{{ issue.lines[issue.lines.length - 1] }}</span></p>
          <br/>
          <p><b class="code" v-if="issue.info">{{ issue.info.replace(/\t/g, "") }}</b></p>
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
      badgeMarkdown: '',
      openedContract: '',
      loading: true,
      classMap: ['alert-danger', 'alert-warning', 'alert-info', 'alert-dark'],
      severityMap: ['High', 'Medium', 'Low', 'Informational'],
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
          this.openedContract = this._.keys(this.auditInfo.contracts).pop()
          let sortedReport = this._.orderBy(this.auditInfo.report, ['severity', 'vuln'], ['asc', 'asc'])
          // use sorted report for proper display
          console.log(sortedReport, 'inf')
          console.log(response.data, 'inf')
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
