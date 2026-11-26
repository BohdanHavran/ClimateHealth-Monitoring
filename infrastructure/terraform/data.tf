# Read the account of the already configured AWS identity during the HCP run.
# This neither configures authentication nor makes a plan offline.
data "aws_caller_identity" "current" {}
