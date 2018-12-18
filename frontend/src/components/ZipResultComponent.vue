<template>
  <div>
    <div class="w-100 px-5">
      <div class="row mt-5 mb-5">
        <div class="col-sm-12 mb-3 text-center font-weight-bold">
          <div class="alert alert-dark">
            <p>To improve SolCheckr's analysis, contribute to <a target="_blank" href="https://github.com/trailofbits/slither">Slither</a>, make sure to read their docs <a target="_blank" href="https://github.com/trailofbits/slither/wiki/API-examples">here</a>.</p>
            <p>SolCheckr isn't so mobile-friendly yet, so we recommend you use a desktop :)</p></div>
        </div>
        <div class="col-sm-12 mb-5">
          <div class="row">
          <div class="col-xs-6 col-sm-6" style="overflow-wrap: break-word;">
            <h5>Security Report for</h5>
            <h4 class="font-weight-bold"><i class="fas fa-code"></i> Submitted code</h4>
            <small><b>Submitted by:</b> {{ auditInfo.author }}<br/><b>{{ auditInfo.submitted }}</b></small>
          </div>
          <div class="col-xs-6 col-sm-6 pt-4">
            <span class="font-weight-bold">Share this report:</span><br/>
            <input class="link-input" type="text" name="pageLink" id="pageLink" v-bind:value="pageLink"> <a href="javascript:void(0);"><i v-on:click="copyLink()" class="fas fa-copy"></i></a>
          </div>
          </div>
        </div>
        <div class="col-sm-12 mb-2 text-center font-weight-bold">
          <div v-if="auditInfo.result" class="alert alert-success">
            <span v-if="!auditInfo.report.length">Awesome! We give your code a 10 out of 10!</span>
            <span v-if="auditInfo.report && auditInfo.report.length > 0">Nice! No vulnerabilities were found, but we've provided you with what parts you can improve!</span>
          </div>
        </div>
        <div class="col-sm-2 d-flex justify-content-center border-right-0 rounded-left px-3 py-4" style="height: 500px;border: 2px solid #1d2621;">
          <div class="text-center w-100">
          <b><i class="fas fa-file-code" style="font-size: 1.5em"></i></b><br/>
          <b>Solidity Files</b>
          <div class="divider"></div>
          <ul class="pl-0 text-center list-unstyled">
            <a v-for="(contract, name) in auditInfo.contracts" :key="name" v-on:click="switchContract(name)" href="javascript:void(0);"><li v-bind:class="{ 'font-weight-bold bg-dark text-white rounded': name === openedContract }" class="mb-2">{{ name }}</li></a>
          </ul>
          </div>
        </div>
        <div class="col-sm-10 d-flex justify-content-center px-0">
          <div class="loader" v-if="loading === true"></div>
          <editor v-if="!loading" v-model="auditInfo.contracts[openedContract]" @init="editorInit" lang="solidity" theme="mono_industrial" height="500"></editor>
        </div>
      </div>
    </div>

    <div v-if="!loading" class="row mt-5 pb-5 mx-0 results-div text-white">
      <div class="container">
        <h2 class="mt-4 mb-1"><b><i class="fas fa-shield-alt"></i> Vulnerability Details</b></h2>
        <div class="accordion text-dark mt-5" id="reportAccordion">
          <div v-for="(issue, index) in sortedReport" :key="index" class="card">
            <div class="card-header pl-1 font-weight-bold" v-bind:id="`heading${index}`">
              <h5 class="mb-0 d-flex justify-content-between align-items-center" style="overflow-x: auto;">
                <button v-bind:class="index === 0 ? '' : 'collapsed'" class="btn w-100 bg-transparent text-left" type="button" data-toggle="collapse" v-bind:data-target="`#collapse${index}`" v-bind:aria-expanded="index === 0" v-bind:aria-controls="`collapse${index}`"><span v-bind:class="[classMap[issue.severity]]" class="badge badge-pill mr-2" style="width: 120px;">{{ severityMap[issue.severity] }}</span> {{ issue.name }} <b class="ml-3">[ {{ issue.instances.length }} ]</b>
                </button>
              </h5>
            </div>

            <div v-bind:id="`collapse${index}`" v-bind:class="index === 0 ? 'show' : ''" class="collapse" v-bind:aria-labelledby="`heading${index}`" data-parent="#reportAccordion">
              <div class="card-body code">Confidence: {{ issue.confidence }}<br/>Wiki: <a target="_blank" v-bind:href="issue.wiki">{{ issue.wiki }}</a><br/>
                <ul class="list-unstyled">
                  <li v-for="(instance, instance_index) in issue.instances" :key="instance_index" v-bind:class="[`list-pre${instance.impact_level}`]"> {{ instance.description }}</li>
                </ul>
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
  name: 'ZipResultComponent',
  props: ['audit_data'],
  data () {
    return {
      sortedReport: [],
      openedContract: '',
      loading: true,
      classMap: ['badge-danger', 'badge-warning', 'badge-info', 'badge-dark'],
      severityMap: ['High Impact', 'Medium Impact', 'Low Impact', 'Informational'],
      pageLink: window.location.href,
      auditInfo: {contract: ''}
    }
  },
  mounted () {
    axios.get(`${process.env.ROOT_API}/zip-audit/${this.$route.params.auditTracker}`)
      .then((response) => {
        this.loading = false
        if (response.data && response.data.id) {
          this.auditInfo = response.data
          this.openedContract = this._.keys(this.auditInfo.contracts)[0]

          let previousName = ''
          let rawReport = {}
          this._.forEach(this.auditInfo.report, (item) => {
            if (item.check !== previousName && !rawReport[item.check]) {
              rawReport[item.check] = {
                name: item.name,
                severity: item.impact_level,
                confidence: item.confidence,
                wiki: item.wiki,
                instances: [item]
              }
            } else {
              rawReport[item.check].instances.push(item)
            }
          })
          this.sortedReport = this._.orderBy(rawReport, ['severity', 'description'], ['asc', 'asc'])
        }
      })
      .catch((err) => {
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
      var copyText = document.getElementById('pageLink')
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
