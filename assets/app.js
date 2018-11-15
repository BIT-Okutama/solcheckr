Vue.prototype.$http = axios;

new Vue({
  el: '#app',
  delimiters: ['${','}'],
  data: {
    loading: false,
    issues: [],
    error: null,
    newAudit: { 'email': null, 'contract': null },
  },
  methods: {
    auditContract() {
      this.loading = true;
      this.issues = [];
      this.error = null;
      this.$http.post('/api/audit/', this.newAudit)
          .then((response) => {
            this.loading = false;
            if (response.data && response.data.success) {
              this.issues = response.data.issues;
            }
          })
          .catch((err, k) => {
            this.loading = false;
            if (err.response.data && err.response.data.error) {
              this.error = err.response.data;
            }
          })
    },
    clearResults() {
      this.issues = [];
    }
  }
})
