<template>
  <div class="container">
    <div class="row mt-5 mb-5">
    <div class="col-sm-12 d-flex justify-content-center">
      <div class="loader" v-if="loading === true"></div>
      <editor v-if="!loading" v-model="auditInfo.contract" @init="editorInit" lang="solidity" theme="mono_industrial" height="500"></editor>
    </div>
    <div class="col-sm-5" v-if="isResultsOpen">
      <div class="results-labels">
        <h4>Results</h4>
        <small v-on:click="clearResults()"><a href="#">Clear</a></small>
        <small v-on:click="toggleResults()"><a href="#">Close</a></small>
      </div>
      <div class="alert alert-dark" role="alert" v-if="loading === false && issues.length === 0 && error === null">
        Nothing to show.
      </div>

      <div>
        <div v-bind:class="[classMap[issue.severity]]" class="alert" role="alert" v-for="(issue, index) in issues" :key="index">
          <p><b>{{ issue.description }}</b></p>
          <p v-if="issue.severity !== null">Severity: <b>{{ severityMap[issue.severity] }}</b></p>
          <p v-if="issue.contract">Contract: <b>{{ issue.contract }}</b></p>
          <p v-if="issue.sourceMapping.lines">Line(s): {{ issue.sourceMapping.lines[0] }}<span v-if="issue.sourceMapping.lines.length > 1 && issue.sourceMapping.lines[0] != issue.sourceMapping.lines[issue.sourceMapping.lines.length - 1]">:{{ issue.sourceMapping.lines[issue.sourceMapping.lines.length - 1] }}</span></p>
          <p v-if="issue.lines">Line(s): {{ issue.lines[0] }}<span v-if="issue.lines.length > 1 && issue.lines[0] != issue.lines[issue.lines.length - 1]">:{{ issue.lines[issue.lines.length - 1] }}</span></p>
          <br/>
          <p><b class="code" v-if="issue.info">{{ issue.info.replace(/\t/g, "") }}</b></p>
        </div>

        <div class="alert alert-danger" role="alert" v-if="error !== null">
          <p class="text-center"><b>==== Compilation Error ====</b></p>
          <p>Error: {{ error.details }}</p>
          <p>--------------------</p>
          <p>In file: {{ error.filename }}:{{ error.lineno }}:{{ error.character }}</p>
          <p><b class="code">{{ error.code }}</b></p>
          --------------------
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ResultComponent',
  data () {
    return {
      isResultsOpen: false,
      loading: true,
      classMap: ['alert-danger', 'alert-warning', 'alert-info', 'alert-dark'],
      severityMap: ['High', 'Medium', 'Low', 'Informational'],
      issues: [],
      error: null,
      auditInfo: {contract: ''}
    }
  },
  mounted () {
    axios.get(`http://localhost:8000/api/audit/${this.$route.params.auditTracker}`)
      .then((response) => {
        // this.loading = false
        if (response.data && response.data.id) {
          this.auditInfo = response.data
          console.log(this.auditInfo, 'inf')
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
    auditContract () {
      this.isResultsOpen = true
      this.loading = true
      this.issues = []
      this.error = null

      axios.post('http://localhost:8000/api/audit/', this.newAudit)
        .then((response) => {
          this.loading = false
          if (response.data && response.data.success) {
            this.$router.push({ path: `/audit/${response.data.tracking}` })
            this.issues = response.data.issues
          }
        })
        .catch((err) => {
          this.loading = false
          if (err.response.data && err.response.data.error) {
            this.error = err.response.data
          }

          this.highlightError()
        })
    },
    clearResults () {
      this.issues = []
    },
    highlightError () {
      let codeElemNode = document.querySelectorAll('.ace_text-layer')
      if (codeElemNode && codeElemNode.length > 0 && this.error) {
        let codeElem = codeElemNode[0].childNodes
        codeElem.forEach((line, lineNumber) => {
          line.style.background = lineNumber === this.error.lineno - 1 ? '#753131' : ''
        })
      }

      let gutterElemNode = document.querySelectorAll('.ace_gutter-layer')
      if (gutterElemNode && gutterElemNode.length > 0 && this.error) {
        let gutterElem = gutterElemNode[0].childNodes
        gutterElem.forEach((line, lineNumber) => {
          line.style.background = lineNumber === this.error.lineno - 1 ? '#753131' : ''
        })
      }
    },
    editorInit (editorElem) {
      editorElem.setReadOnly(true)
      require('brace/ext/language_tools')
      require('brace/theme/mono_industrial')
      require('../assets/js/solidity.js')
    },
    toggleResults () {
      this.isResultsOpen = !this.isResultsOpen
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
