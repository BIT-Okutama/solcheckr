<template>
  <div class="container">
    <div class="row mt-5 mb-5">
    <div class="col-sm-12 mb-3 text-center font-weight-bold">
      <div class="alert alert-dark">{{ headerMessage }}<p>To improve SolCheckr's analysis, contribute to <a target="_blank" href="https://github.com/trailofbits/slither">Slither</a>, make sure to read their docs <a target="_blank" href="https://github.com/trailofbits/slither/wiki/API-examples">here</a>.</p></div>
    </div>
    <div class="col-xs-12 col-sm-3 mb-3"><button :disabled="!account || loading || (auditType === 'contract' && auditCode.trim().length < 25) || (auditType === 'repository' && !repoUrl) || (auditType === 'zip' && !validFile)" type="submit" class="btn btn-md btn-dark font-weight-bold montserrat w-100 px-5" v-on:click="auditContract()">Submit</button></div>
    <div class="col-xs-12 col-sm-3 mb-3"><button :disabled="loading || auditType === 'contract'" v-on:click="toggleAuditType('contract')" type="button" class="btn btn-md btn-outline-dark font-weight-bold montserrat w-100 px-5"><i class="fas fa-code"></i> Code scan</button></div>
    <div class="col-xs-12 col-sm-3 mb-3"><button :disabled="loading || auditType === 'repository'" v-on:click="toggleAuditType('repository')" type="button" class="btn btn-md btn-outline-dark font-weight-bold montserrat w-100 px-5"><i class="fab fa-github"></i> GitHub scan</button></div>
    <div class="col-xs-12 col-sm-3 mb-3"><button :disabled="loading || auditType === 'zip'" v-on:click="toggleAuditType('zip')" type="button" class="btn btn-md btn-outline-dark font-weight-bold montserrat w-100 px-5"><i class="fas fa-file-archive"></i> Upload ZIP</button></div>
    <div v-bind:class="[ (isErrorsOpen && !loading) || (loading && auditType === 'contract') ? 'col-sm-7' : 'col-sm-12']">
      <form v-on:submit.prevent="auditContract()">
        <editor v-if="auditType === 'contract'" v-model="auditCode" @init="editorInit" lang="solidity" theme="mono_industrial" height="500"></editor>
        <div v-if="auditType === 'repository' && !loading" class="row justify-content-center align-items-center text-center" style="height: 500px;">
          <div class="col-sm-8">
            <h1><i class="fab fa-github"></i></h1>
            <div class="form-group">
              <label for="repository_url">GitHub repository</label>
              <div v-if="repoErr" class="alert alert-danger" role="alert">
                {{ repoErr }}
              </div>
              <input type="text" v-model="repoUrl" autocomplete="off" required="" class="form-control field-input px-3" id="repository_url" aria-describedby="repository_url_help" placeholder="ex. https://github.com/githubusername/helloworld.git">
              <small id="repository_url_help" class="form-text text-muted">Make sure the repository is public. HTTPS and SSH is supported.<br/>Experimental feature, a lot of things to improve :)</small>
            </div>
          </div>
        </div>
        <div v-if="auditType === 'zip' && !loading" class="row justify-content-center align-items-center text-center" style="height: 500px;">
          <div class="col-sm-8">
            <h1><i class="fas fa-file-archive"></i></h1>
            <div class="form-group">
              <label for="repository_url">Upload ZIP</label><br/>
              <div v-if="zipError" class="alert alert-danger" role="alert">
                {{ zipError }}
              </div>
              <input class="field-input" type="file" id="file" ref="file" accept="application/zip" v-on:change="handleFileUpload()"/>
              <small id="repository_url_help" class="form-text text-muted">Please upload your project .zip file. The Solidity files will be extracted and checked (Max size: 30 MB)<br/>Experimental feature, a lot of things to improve :)</small>
            </div>
          </div>
        </div>
      </form>
      <div v-if="loading === true && auditType !== 'contract'" style="height: 500px; margin-top: 150px;" class="text-center pt-5">
        <div class="loader mx-auto my-0"></div>
        <p class="montserrat mt-4 animate-flicker font-weight-bold">{{ loadingMessage }}</p>
      </div>
    </div>
    <div class="col-sm-5" v-if="isErrorsOpen || (loading === true && auditType === 'contract')">
      <div class="errors-labels">
        <h4 v-if="error !== null"> </h4>
        <h4 v-if="!loading" v-on:click="toggleErrors()"><a href="#"><i class="far fa-window-close"></i></a></h4>
      </div>

      <div class="text-center mt-5">
        <div v-if="loading === true && auditType === 'contract'" class="loader mx-auto my-0"></div>
        <p v-if="loading === true && auditType === 'contract'" class="montserrat mt-4 animate-flicker font-weight-bold">{{ loadingMessage }}</p>
      </div>

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
  </div>
</template>

<script>
import axios from 'axios'
import getWeb3 from '../assets/js/getWeb3'
import SolCheckrContractAbi from '../assets/js/SolCheckr.abi'

const SolCheckrContractAddress = '0xCFFF2D96d3851176B53a030db0aF36AEF9b6797D'

export default {
  name: 'MainComponent',
  data () {
    return {
      web3: null,
      account: null,
      headerMessage: 'Make sure you are connected to Ropsten Test Network to use the app.',
      loadingMessage: 'Waiting for transaction to complete...',
      contractInstance: null,
      file: '',
      validFile: false,
      repoErr: null,
      zipError: null,
      isErrorsOpen: false,
      auditType: 'contract',
      typeMap: {contract: 0, repository: 1, zip: 2},
      loading: false,
      issues: [],
      error: null,
      repoUrl: null,
      auditCode: `pragma solidity ^0.4.18;

contract MiniDAO {

    mapping(address => uint) public balances;

    function donate(address _to) public payable {
      balances[_to] += msg.value;
    }

    function withdraw(uint _amount) public {
      require(balances[msg.sender] >= _amount);
      msg.sender.call.value(_amount)();
      balances[msg.sender] -= _amount;
    }

    function() public payable {}

}
`
    }
  },
  mounted () {
    getWeb3().then((res) => {
      this.web3 = res
      this.contractInstance = new this.web3.eth.Contract(SolCheckrContractAbi, SolCheckrContractAddress)
      this.web3.eth.getAccounts().then((accounts) => {
        if (accounts.length === 0) {
          this.headerMessage = 'No MetaMask accounts found! Please check MetaMask and refresh the page'
        }
        this.account = accounts[0]
      }).catch((err) => {
        this.headerMessage = 'MetaMask is required to use this app, please install MetaMask first'
        console.log(err, 'err!!')
      })
    })
  },
  methods: {
    auditContract () {
      this.loading = true
      this.issues = []
      this.error = null

      this.contractInstance.methods.addAudit(this.typeMap[this.auditType]).send({ from: this.account })
        .then((receipt) => {
          this.loadingMessage = 'Analyzing code and publishing result to blockchain...'
          if (receipt.events && receipt.events.AuditAdded) {
            let payload = {
              auditType: receipt.events.AuditAdded.returnValues.auditType,
              author: receipt.events.AuditAdded.returnValues.author,
              tracking: receipt.events.AuditAdded.returnValues.tracker
            }

            if (this.auditType === 'contract') {
              payload.contract = this.auditCode
              axios.post(`${process.env.ROOT_API}/audit/`, payload)
                .then((response) => {
                  this.loading = false
                  if (response.data && response.data.success) {
                    this.$router.push({ path: `/audit/${response.data.tracking}` })
                    this.issues = response.data.issues
                  }
                })
                .catch((err) => {
                  this.loading = false
                  this.loadingMessage = 'Waiting for transaction to complete...'
                  if (err.response.data && err.response.data.error) {
                    this.isErrorsOpen = true
                    this.error = err.response.data
                  }

                  this.highlightError()
                })
            } else if (this.auditType === 'repository') {
              let re = /(?:git|ssh|https?|git@[-\w.]+):(\/\/)?(.*?)(\.git)$/
              if (!re.test(this.repoUrl)) {
                this.repoErr = 'The provided GitHub URL is invalid'
                this.loading = false
                return
              }

              let reMatch = re.exec(this.repoUrl)
              let repoName = reMatch[2].substring(reMatch[2].indexOf('/') + 1, reMatch[2].length)
              this.getRepoSolidityCount(repoName)
                .then((solFileCount) => {
                  if (solFileCount <= 0) {
                    this.repoErr = 'Repository may be invalid or does not contain any Solidity file'
                    this.loading = false
                  } else {
                    this.repoErr = null
                    payload.repository_url = this.repoUrl
                    axios.post(`${process.env.ROOT_API}/github-audit/`, payload)
                      .then((response) => {
                        this.loading = false
                        if (response.data && response.data.success) {
                          this.$router.push({ path: `/github-audit/${response.data.tracking}` })
                        }
                      })
                      .catch((err) => {
                        this.loading = false
                        this.loadingMessage = 'Waiting for transaction to complete...'
                        if (err.response.data && err.response.data.error) {
                          this.isErrorsOpen = true
                          this.error = err.response.data
                        }
                      })
                  }
                })
            } else {
              let formData = new FormData()
              formData.append('file', this.file)
              formData.append('auditType', payload.auditType)
              formData.append('author', payload.author)
              formData.append('tracking', payload.tracking)

              axios.post(`${process.env.ROOT_API}/zip-audit/`, formData, {headers: {'Content-Type': 'multipart/form-data'}})
                .then((response) => {
                  this.loading = false
                  if (response.data && response.data.success) {
                    this.$router.push({ path: `/zip-audit/${response.data.tracking}` })
                  }
                })
                .catch((err) => {
                  this.loading = false
                  this.loadingMessage = 'Waiting for transaction to complete...'
                  if (err.response.data && err.response.data.error) {
                    this.isErrorsOpen = true
                    this.error = err.response.data
                  }
                })
            }
          }
        })
        .catch((err) => {
          console.log(err, 'err')
        })
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
      if (this.$refs.file.files[0] && this.$refs.file.files[0].type === 'application/zip' && this.$refs.file.files[0].size <= 30000000) {
        this.file = this.$refs.file.files[0]
        this.zipError = null
        this.validFile = true
      } else {
        this.file = null
        this.zipError = 'The uploaded file is not a ZIP file or exceeds the limit of 30 MB'
        this.validFile = false
      }
    },
    getRepoSolidityCount (repo) {
      return axios.get(`https://api.github.com/search/code?q=extension:sol+repo:${repo}`)
        .then((response) => {
          if (response.data && response.data.total_count !== null) {
            return response.data.total_count
          }
        })
        .catch((err) => {
          console.log(err, 'Error')
          return -1
        })
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
