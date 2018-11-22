Vue.prototype.$http = axios;
const GITHUB_API = 'https://api.github.com/search/code?q=solidity+in:file+extension:sol+repo:';
const GITHUB_RAW_API = 'https://raw.githubusercontent.com/${this.props.githubUser}/${this.props.repo}/master/${file.path}';

new Vue({
  el: '#app',
  delimiters: ['${','}'],
  data: {
    loading: false,
    user: '',
    repo: '',
    solidityFiles: [],
    newAudit: {}
  },
  beforeMount() {
    // Temporary! Up to speed!
    var url_string = window.location.href;
    var url = new URL(url_string);
    var user = url.searchParams.get('user');
    var repo = url.searchParams.get('repo');
    if (user && repo) {
      this.user = user;
      this.repo = repo;
    } else {
      window.location.replace('/');
    }
    this.getSolidityFiles()
  },
  methods: {
    getSolidityFiles() {
      this.loading = true;
      this.$http.get(`${GITHUB_API}${this.user}/${this.repo}`)
          .then((response) => {
            this.loading = false;
            if (response && response.data) {
              this.solidityFiles = response.data.items;
            }
            console.log(this.solidityFiles, 'asdf');

          })
          .catch((err) => {
            this.loading = false;
            console.log(err);
          })
    },
    auditGithubFile(file) {
      // pay, then API request
      this.loading = true;
      this.newAudit = {
        github_user: this.user,
        github_repo: this.repo,
        code_url: `https://raw.githubusercontent.com/${this.user}/${this.repo}/master/${file.path}`
      };
      alert('Requested audit for: ' + file.name);
      console.log(this.newAudit.code_url, 'adsf');
      this.$http.post('/api/github-audit/', this.newAudit)
          .then((response) => {
            this.loading = false;
            if (response.data && response.data.success) {
              this.issues = response.data.issues;
            }
          })
          .catch((err) => {
            this.loading = false;
            if (err.response.data && err.response.data.error) {
              this.error = err.response.data;
            }
          })
    }
  }
})
