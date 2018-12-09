<template>
  <div class="container">
    <div class="row mt-5 mb-5">
    <div v-bind:class="[ (isErrorsOpen && !loading) || (loading && auditType === 'contract') ? 'col-sm-7' : 'col-sm-12']">
      <form v-on:submit.prevent="auditContract()">
        <div class="d-flex justify-content-between">
          <div class="mb-3">
            <button :disabled="loading || (auditType === 'contract' && newAudit.contract.trim().length < 25) || (auditType === 'repository' && !repoUrl)" type="submit" class="btn btn-md btn-dark font-weight-bold montserrat px-5">Submit</button>
            <button :disabled="loading || auditType === 'contract'" v-on:click="toggleAuditType('contract')" type="button" class="btn btn-md btn-outline-dark font-weight-bold montserrat px-5"><i class="fas fa-code"></i> Code scan</button>
            <button :disabled="loading || auditType === 'repository'" v-on:click="toggleAuditType('repository')" type="button" class="btn btn-md btn-outline-dark font-weight-bold montserrat px-5"><i class="fab fa-github"></i> GitHub scan</button>
            <button :disabled="loading || auditType === 'zip'" v-on:click="toggleAuditType('zip')" type="button" class="btn btn-md btn-outline-dark font-weight-bold montserrat px-5"><i class="fas fa-file-archive"></i> Upload ZIP</button>
          </div>
        </div>
        <editor v-if="auditType === 'contract'" v-model="newAudit.contract" @init="editorInit" lang="solidity" theme="mono_industrial" height="500"></editor>
        <div v-if="auditType === 'repository' && !loading" class="row justify-content-center align-items-center text-center" style="height: 500px;">
          <div class="col-sm-8">
            <h1><i class="fab fa-github"></i></h1>
            <div class="form-group">
              <label for="repository_url">GitHub repository</label>
              <input type="text" v-model="repoUrl" class="form-control" id="repository_url" aria-describedby="repository_url_help" placeholder="ex. https://github.com/githubusername/helloworld.git">
              <small id="repository_url_help" class="form-text text-muted">Make sure the repository is public. HTTPS and SSH is supported.<br/>Experimental feature, a lot of things to improve :)</small>
            </div>
          </div>
        </div>
      </form>
      <div v-if="loading === true && auditType === 'repository'" style="height: 500px" class="d-flex justify-content-center align-items-center"><div class="loader"></div></div>
    </div>
    <div class="col-sm-5" v-if="isErrorsOpen || (loading === true && auditType === 'contract')">
      <div class="errors-labels">
        <h4 v-if="error !== null">Errors</h4>
        <h4 v-on:click="toggleErrors()"><a href="#"><i class="far fa-window-close"></i></a></h4>
      </div>

      <div v-if="loading === true && auditType === 'contract'" class="loader"></div>

      <div>
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

    <div class="container">
      <div class="large-12 medium-12 small-12 cell">
        <label>File
          <input type="file" id="file" ref="file" v-on:change="handleFileUpload()"/>
        </label>
          <button v-on:click="auditContract()">Submit</button>
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
      file: '',
      isErrorsOpen: false,
      auditType: 'contract',
      loading: false,
      issues: [],
      error: null,
      repoUrl: null,
      newAudit: {
        'contract': `pragma solidity ^0.4.18;

contract SampleReentrancy {

  mapping(address => uint) public balances;

  function donate(address _to) public payable {
    balances[_to] += msg.value;
  }

  function balanceOf(address _who) public view returns (uint balance) {
    return balances[_who];
  }

  function withdraw(uint _amount) public {
    if(balances[msg.sender] >= _amount) {
      if(msg.sender.call.value(_amount)()) {
        _amount;
      }
      balances[msg.sender] -= _amount;
    }
  }

  function() public payable {}
}
`
      }
    }
  },
  methods: {
    auditContract () {
      this.loading = true
      this.issues = []
      this.error = null

      if (this.auditType === 'contract') {
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
              this.isErrorsOpen = true
              this.error = err.response.data
            }

            this.highlightError()
          })
      } else if (this.auditType === 'repository') {
        axios.post('http://localhost:8000/api/github-audit/', {repository_url: this.repoUrl})
          .then((response) => {
            this.loading = false
            if (response.data && response.data.success) {
              this.$router.push({ path: `/github-audit/${response.data.tracking}` })
            }
          })
          .catch((err) => {
            this.loading = false
            if (err.response.data && err.response.data.error) {
              this.isErrorsOpen = true
              this.error = err.response.data
            }
          })
      } else {
        let formData = new FormData()
        formData.append('file', this.file)

        axios.post('http://localhost:8000/api/zip-audit/', formData, {headers: {'Content-Type': 'multipart/form-data'}})
          .then((response) => {
            this.loading = false
            if (response.data && response.data.success) {
              this.$router.push({ path: `/zip-audit/${response.data.tracking}` })
            }
          })
          .catch((err) => {
            this.loading = false
            if (err.response.data && err.response.data.error) {
              this.isErrorsOpen = true
              this.error = err.response.data
            }
          })
      }
    },
    highlightError () {
      let codeElemNode = document.querySelectorAll('.ace_text-layer')
      if (codeElemNode && codeElemNode.length > 0 && this.error) {
        let codeElem = codeElemNode[0].childNodes
        codeElem.forEach((line, lineNumber) => {
          line.style.background = lineNumber === this.error.lineno - 1 ? '#753131' : ''
        })
      }
    },
    editorInit () {
      require('brace/ext/language_tools')
      require('brace/theme/mono_industrial')
      require('../assets/js/solidity.js')
    },
    toggleErrors () {
      this.isErrorsOpen = !this.isErrorsOpen
    },
    toggleAuditType (newType) {
      this.isErrorsOpen = false
      this.auditType = newType
    },
    handleFileUpload () {
      this.file = this.$refs.file.files[0]
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
