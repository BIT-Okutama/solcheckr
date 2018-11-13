Vue.prototype.$http = axios;

new Vue({
  el: '#app',
  delimiters: ['${','}'],
  data: {
    loading: false,
    issues: [],
    newAudit: { 'email': null, 'contract': null },
  },
  methods: {
    auditContract() {
      this.loading = true;
      this.$http.post('/api/audit/', this.newAudit)
          .then((response) => {
            this.loading = false;
            if (response.data) {
              this.issues = response.data.issues;
              console.log(this.issues);
            }
          })
          .catch((err) => {
            this.loading = false;
            console.log(err);
          })
    },
    clearResults() {
      this.issues = [];
    }
  }
})
