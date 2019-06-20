workflow "Create a repo for commenter" {
  on = "issue_comment"
  resolves = [
    "Enroll the commenter",
    "Debug",
  ]
}

action "Enroll the commenter" {
  uses = "./"
  secrets = ["GITHUB_TOKEN"]
}

action "Debug" {
  uses = "actions/bin/debug@master"
}
