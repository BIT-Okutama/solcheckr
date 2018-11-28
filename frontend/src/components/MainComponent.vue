<template>
  <div class="container">
    <div class="row mt-5 mb-5">
    <div v-bind:class="[ isResultsOpen ? 'col-sm-7' : 'col-sm-12']">
      <form v-on:submit.prevent="auditContract()">
        <div class="d-flex justify-content-between">
          <button type="submit" class="btn btn-md btn-dark font-weight-bold montserrat mb-3 px-5">Submit</button>
          <button v-on:click="toggleResults()" v-if="!isResultsOpen" type="button" class="btn-md btn-outline-dark montserrat mb-3">Open Results tab</button>
        </div>
        <editor v-model="newAudit.contract" required="" @init="editorInit" lang="solidity" theme="mono_industrial" height="500"></editor>
      </form>
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
      <div class="loader" v-if="loading === true"></div>

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
  name: 'MainComponent',
  data () {
    return {
      isResultsOpen: false,
      loading: false,
      classMap: ['alert-danger', 'alert-warning', 'alert-info', 'alert-dark'],
      severityMap: ['High', 'Medium', 'Low', 'Informational'],
      issues: [],
      error: null,
      newAudit: {
        'email': 'benemeritosam@gmail.com',
        'contract': `pragma solidity ^0.4.18;

contract Overflow {
  uint256 num = 999999999;

  function addToNum(uint256 _inputNumber) public {
    num += _inputNumber;
  }
}`
      }
    }
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
    editorInit () {
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
