variable "permissions_boundary_arn" {
  type = string
}
variable "name" {
  type = string
}
variable "enabled" {
  type = bool
}
variable "ami_id" {
  type = string
}
variable "instance_type" {
  type = string
}
variable "subnet_id" {
  type = string
}
variable "security_group" {
  type = string
}
variable "artifact_bucket_arn" {
  type = string
}
resource "aws_iam_role" "this" {
  permissions_boundary = var.permissions_boundary_arn
  count = var.enabled ? 1 : 0
  name = "${var.name}-ai"
  assume_role_policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="ec2.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy" "read" {
  count = var.enabled ? 1 : 0
  role = aws_iam_role.this[0].id
  policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Action="s3:GetObject",Resource="${var.artifact_bucket_arn}/ai/*"}]})
}
resource "aws_iam_instance_profile" "this" {
  count = var.enabled ? 1 : 0
  role = aws_iam_role.this[0].name
}
resource "aws_instance" "this" {
  count = var.enabled ? 1 : 0
  ami = var.ami_id
  instance_type = var.instance_type
  subnet_id = var.subnet_id
  vpc_security_group_ids = [var.security_group]
  associate_public_ip_address = false
  iam_instance_profile = aws_iam_instance_profile.this[0].name
  metadata_options { http_tokens = "required" }
  credit_specification { cpu_credits = "standard" }
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted = true
    delete_on_termination = false
  }
  lifecycle {
    precondition {
      condition = var.ami_id != null
      error_message = "Approved AMI with private TLS/auth, model_unavailable and S3 reconcile agent required."
    }
  }
}
output "private_ip" { value = try(aws_instance.this[0].private_ip,null) }
