variable "name" {
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
resource "aws_db_subnet_group" "this" {
  subnet_ids = var.subnet_ids
}
resource "aws_db_parameter_group" "this" {
  family = "mysql8.4"
  parameter {
    name = "require_secure_transport"
    value = "ON"
  }
}
resource "aws_db_instance" "this" {
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
  db_subnet_group_name = aws_db_subnet_group.this.name
  parameter_group_name = aws_db_parameter_group.this.name
  vpc_security_group_ids = [var.security_group]
  backup_retention_period = 7
  deletion_protection = true
  lifecycle { prevent_destroy = true }
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.name}-final"
  copy_tags_to_snapshot = true
}
output "host" { value = aws_db_instance.this.address }
