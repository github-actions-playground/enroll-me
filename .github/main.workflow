workflow "Create a repo for commenter" {
  on = "issue_comment"
  resolves = [
    "Enroll the commenter",
    "Debug",
  ]
}

action "Enroll the commenter" {
  uses = "./"
}

action "Debug" {
  uses = "actions/bin/debug@master"
}
