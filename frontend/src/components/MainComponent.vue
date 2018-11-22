<template>
  <div class="container">
    <div class="row mt-5 mb-5">
    <div class="col-sm-7">
      <form v-on:submit.prevent="auditContract()">
        <div class="form-group">
          <label class="montserrat" for="exampleFormControlInput1">Email address</label>
          <input type="email" class="form-control" id="exampleFormControlInput1" aria-describedby="emailHelpText" placeholder="name@example.com" v-model="newAudit.email" required="">
          <small id="emailHelpText" class="form-text text-muted">
            Needed in-case the app takes too long, we'll email you the results instead :)
          </small>
        </div>
        <div class="form-group">
          <label class="montserrat" for="contract-code">Solidity code</label>
          <textarea class="form-control" id="contract-code" rows="3" v-model="newAudit.contract" required=""></textarea>
        </div>
        <button type="submit" class="btn-block btn-lg btn-dark montserrat" >Submit</button>
      </form>
    </div>
    <div class="col-sm-5">
      <div class="results-labels">
        <h4>Results</h4>
        <small v-on:click="clearResults()"><a href="#">Clear</a></small>
      </div>
      <div class="alert alert-dark" role="alert" v-if="loading === false && issues.length === 0 && error === null">
        No errors to show.
      </div>
      <div class="loader" v-if="loading === true"></div>

      <div>
        <div v-bind:class="[issue.type === 'Warning' ? 'alert-warning' : 'alert-info']" class="alert" role="alert" v-for="(issue, index) in issues" :key="index">
          <p class="text-center">==== {{ issue.title }} ====</p>
          <p>Contract: <b>{{ issue.contract }}</b></p>
          <p>Function: <b>{{ issue.function }}</b></p>
          <p>{{ issue.description }}</p>
          <p>--------------------</p>
          <p>In file: {{ issue.filename }}:{{ issue.lineno }}</p>
          <p><b class="code">{{ issue.code }}</b></p>
          --------------------
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
      loading: false,
      issues: [],
      error: null,
      newAudit: {
        'email': null,
        'contract': null
      }
    }
  },
  methods: {
    auditContract () {
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
        })
    },
    clearResults () {
      this.issues = []
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
