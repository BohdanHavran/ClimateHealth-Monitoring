variable "permissions_boundary_arn" {
  type = string
}
variable "name" {
  type = string
}
variable "mode" {
  type = string
}
variable "subnet_ids" {
  type = list(string)
}
variable "security_group" {
  type = string
}
variable "availability_zone" {
  type = string
}
variable "mysql_ami_id" {
  type = string
}
variable "artifact_bucket_arn" {
  type = string
}
resource "aws_db_subnet_group" "this" {
  count = var.mode == "rds" ? 1 : 0
  subnet_ids = var.subnet_ids
}
resource "aws_db_parameter_group" "this" {
  count = var.mode == "rds" ? 1 : 0
  family = "mysql8.4"
  parameter {
    name = "require_secure_transport"
    value = "ON"
  }
}
resource "aws_db_instance" "this" {
  count = var.mode == "rds" ? 1 : 0
  identifier = var.name
  engine = "mysql"
  engine_version = "8.4.13"
  engine_lifecycle_support = "open-source-rds-extended-support-disabled"
  instance_class = "db.t4g.micro"
  allocated_storage = 20
  max_allocated_storage = 20
  storage_type = "gp3"
  storage_encrypted = true
  username = "climate_admin"
  manage_master_user_password = true
  db_name = "climate_db"
  port = 3306
  availability_zone = var.availability_zone
  multi_az = false
  publicly_accessible = false
  db_subnet_group_name = aws_db_subnet_group.this[0].name
  parameter_group_name = aws_db_parameter_group.this[0].name
  vpc_security_group_ids = [var.security_group]
  backup_retention_period = 7
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.name}-final"
  copy_tags_to_snapshot = true
}
resource "aws_instance" "mysql" {
  iam_instance_profile = aws_iam_instance_profile.backup[0].name
  count = var.mode == "ec2" ? 1 : 0
  ami = var.mysql_ami_id
  instance_type = "t3.small"
  subnet_id = var.subnet_ids[0]
  vpc_security_group_ids = [var.security_group]
  associate_public_ip_address = false
  metadata_options { http_tokens = "required" }
  credit_specification { cpu_credits = "standard" }
  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted = true
    delete_on_termination = false
  }
  lifecycle {
    prevent_destroy = true
    precondition {
      condition = var.mysql_ami_id != null
      error_message = "Approved MySQL AMI, secure initialization and backup/restore required for EC2 database."
    }
  }
}
output "host" { value = var.mode == "rds" ? aws_db_instance.this[0].address : aws_instance.mysql[0].private_ip }

resource "aws_iam_role" "backup" {
  count = var.mode == "ec2" ? 1 : 0
  name = "${var.name}-mysql-backup"
  permissions_boundary = var.permissions_boundary_arn
  assume_role_policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="ec2.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy" "backup" {
  count = var.mode == "ec2" ? 1 : 0
  role = aws_iam_role.backup[0].id
  policy = jsonencode({Version="2012-10-17",Statement=[
        {Effect="Allow",Action="s3:GetObject",Resource=["${var.artifact_bucket_arn}/mysql/*","${var.artifact_bucket_arn}/backups/mysql/*"]},
        {Effect="Allow",Action="s3:PutObject",Resource="${var.artifact_bucket_arn}/backups/mysql/*"}
  ]})
}
resource "aws_iam_instance_profile" "backup" {
  count = var.mode == "ec2" ? 1 : 0
  role = aws_iam_role.backup[0].name
}
