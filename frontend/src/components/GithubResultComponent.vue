<template>
  <div>
    <div class="container">
      <div class="row mt-5 mb-5">
        <div class="col-sm-2 d-flex justify-content-center" style="height: 500px">
          <div class="text-center w-100">
          <b><i class="fas fa-file-code" style="font-size: 1.5em"></i></b><br/>
          <b>Contracts</b>
          <div class="divider"></div>
          <ul class="pl-0 text-center list-unstyled">
            <li class="mb-2" v-for="(contract, name) in auditInfo.contracts" :key="name" v-on:click="switchContract(name)" v-bind:class="{ 'font-weight-bold bg-dark text-white rounded': name === openedContract }">{{ name }}</li>
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
        <div class="d-flex justify-content-between">
          <h1 class="mt-4 mb-1"><b>Security Report</b></h1>
          <span class="montserrat mt-4 mb-5"><b>Share this report:</b><br/>{{ pageLink }}</span>
        </div>
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
