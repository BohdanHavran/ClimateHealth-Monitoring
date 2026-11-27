# Adapted from owner modules/vpc/main.tf; see VARIANT_B_REUSE.md.
variable "name" {
  type = string
}
variable "vpc_cidr" {
  type = string
}
data "aws_availability_zones" "available" {
  state = "available"
  filter {
    name   = "zone-type"
    values = ["availability-zone"]
  }
}
locals { zones = slice(data.aws_availability_zones.available.names, 0, 3) }
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  instance_tenancy     = "default"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = {
    Name = var.name
  }
}
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags                    = {
    Name = "${var.name}-igw"
  }
}
resource "aws_subnet" "public" {
  count = length(local.zones)
  vpc_id                  = aws_vpc.this.id
  cidr_block = cidrsubnet(var.vpc_cidr, 8, count.index)
  map_public_ip_on_launch = false
  availability_zone = local.zones[count.index]
  tags                    = {
    Name = "${var.name}-public-${count.index}"
  }
}

resource "aws_subnet" "private" {
  count = 2
  vpc_id                  = aws_vpc.this.id
  cidr_block = cidrsubnet(var.vpc_cidr, 8, 10 + count.index)
  availability_zone = local.zones[count.index]
  map_public_ip_on_launch = false
  tags                    = {
    Name = "${var.name}-private-${count.index}"
  }
}

resource "aws_route_table" "public" { vpc_id = aws_vpc.this.id }
resource "aws_route" "internet" {
  route_table_id = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.this.id
}
resource "aws_route_table" "private" { vpc_id = aws_vpc.this.id }
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)
  subnet_id = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
resource "aws_route_table_association" "private" {
  count = 2
  subnet_id = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
data "aws_region" "current" {}
resource "aws_vpc_endpoint" "s3" {
  vpc_id = aws_vpc.this.id
  service_name = "com.amazonaws.${data.aws_region.current.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids = [aws_route_table.public.id, aws_route_table.private.id]
}
output "vpc_id" { value = aws_vpc.this.id }
output "public_subnet_ids" {
  value = aws_subnet.public[*].id
  depends_on = [aws_route.internet, aws_route_table_association.public]
}
output "private_subnet_ids" {
  value = aws_subnet.private[*].id
  depends_on = [aws_route_table_association.private, aws_vpc_endpoint.s3]
}
output "availability_zone" { value = local.zones[0] }

# Existing ClimateHealth SG-to-SG rules, moved into their owning network module.
data "aws_ec2_managed_prefix_list" "cloudfront" { name = "com.amazonaws.global.cloudfront.origin-facing" }

resource "aws_security_group" "alb" {
  name_prefix = "${var.name}-alb-"
  vpc_id = aws_vpc.this.id
}

resource "aws_security_group" "backend" {
  name_prefix = "${var.name}-backend-"
  vpc_id = aws_vpc.this.id
}

resource "aws_security_group" "mysql" {
  name_prefix = "${var.name}-mysql-"
  vpc_id = aws_vpc.this.id
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

resource "aws_vpc_security_group_egress_rule" "https" {
  security_group_id = aws_security_group.backend.id
  cidr_ipv4 = "0.0.0.0/0"
  ip_protocol = "tcp"
  from_port = 443
  to_port = 443
}

output "alb_sg" { value = aws_security_group.alb.id }

output "backend_sg" { value = aws_security_group.backend.id }

output "mysql_sg" { value = aws_security_group.mysql.id }
