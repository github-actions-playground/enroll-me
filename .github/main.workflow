workflow "Create a repo for commenter" {
  on = "issue_comment"
  resolves = ["Enroll the commenter"]
}

action "Enroll the commenter" {
  uses = "./"
}
