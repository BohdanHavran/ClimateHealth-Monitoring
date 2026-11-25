variable "name" {
  type = string
}
variable "vpc_id" {
  type = string
}
data "aws_ec2_managed_prefix_list" "cloudfront" { name = "com.amazonaws.global.cloudfront.origin-facing" }
resource "aws_security_group" "alb" {
  name_prefix = "${var.name}-alb-"
  vpc_id = var.vpc_id
}
resource "aws_security_group" "backend" {
  name_prefix = "${var.name}-backend-"
  vpc_id = var.vpc_id
}
resource "aws_security_group" "mysql" {
  name_prefix = "${var.name}-mysql-"
  vpc_id = var.vpc_id
}
resource "aws_security_group" "ai" {
  name_prefix = "${var.name}-ai-"
  vpc_id = var.vpc_id
}
resource "aws_vpc_security_group_ingress_rule" "cloudfront" {
  security_group_id = aws_security_group.alb.id
  prefix_list_id = data.aws_ec2_managed_prefix_list.cloudfront.id
  ip_protocol = "tcp"
  from_port = 443
  to_port = 443
}
resource "aws_vpc_security_group_ingress_rule" "targets" {
  security_group_id = aws_security_group.backend.id
  referenced_security_group_id = aws_security_group.alb.id
  ip_protocol = "tcp"
  from_port = 8080
  to_port = 8080
}
resource "aws_vpc_security_group_egress_rule" "targets" {
  security_group_id = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.backend.id
  ip_protocol = "tcp"
  from_port = 8080
  to_port = 8080
}
resource "aws_vpc_security_group_ingress_rule" "database" {
  security_group_id = aws_security_group.mysql.id
  referenced_security_group_id = aws_security_group.backend.id
  ip_protocol = "tcp"
  from_port = 3306
  to_port = 3306
}
resource "aws_vpc_security_group_egress_rule" "database" {
  security_group_id = aws_security_group.backend.id
  referenced_security_group_id = aws_security_group.mysql.id
  ip_protocol = "tcp"
  from_port = 3306
  to_port = 3306
}
resource "aws_vpc_security_group_ingress_rule" "inference" {
  security_group_id = aws_security_group.ai.id
  referenced_security_group_id = aws_security_group.backend.id
  ip_protocol = "tcp"
  from_port = 8001
  to_port = 8001
}
resource "aws_vpc_security_group_egress_rule" "inference" {
  security_group_id = aws_security_group.backend.id
  referenced_security_group_id = aws_security_group.ai.id
  ip_protocol = "tcp"
  from_port = 8001
  to_port = 8001
}
resource "aws_vpc_security_group_egress_rule" "https" {
  security_group_id = aws_security_group.backend.id
  cidr_ipv4 = "0.0.0.0/0"
  ip_protocol = "tcp"
  from_port = 443
  to_port = 443
}
data "aws_region" "current" {}
data "aws_prefix_list" "s3" { name = "com.amazonaws.${data.aws_region.current.region}.s3" }
resource "aws_vpc_security_group_egress_rule" "s3" {
  for_each = { ai = aws_security_group.ai.id, mysql = aws_security_group.mysql.id }
  security_group_id = each.value
  prefix_list_id = data.aws_prefix_list.s3.id
  ip_protocol = "tcp"
  from_port = 443
  to_port = 443
}
output "alb_sg" { value = aws_security_group.alb.id }
output "backend_sg" { value = aws_security_group.backend.id }
output "mysql_sg" { value = aws_security_group.mysql.id }
output "ai_sg" { value = aws_security_group.ai.id }
