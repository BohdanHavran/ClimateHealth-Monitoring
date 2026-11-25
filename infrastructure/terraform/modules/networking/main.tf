variable "name" {
  type = string
}
variable "vpc_cidr" {
  type = string
  default = "10.42.0.0/16"
}
variable "public_subnet_cidrs" {
  type = list(string)
  default = ["10.42.0.0/24", "10.42.1.0/24"]
}
variable "private_subnet_cidrs" {
  type = list(string)
  default = ["10.42.10.0/24", "10.42.11.0/24"]
}
data "aws_availability_zones" "available" { state = "available" }
locals { zones = slice(data.aws_availability_zones.available.names, 0, 2) }
resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = { Name = var.name }
}
resource "aws_internet_gateway" "this" { vpc_id = aws_vpc.this.id }
resource "aws_subnet" "public" {
  count = 2
  vpc_id = aws_vpc.this.id
  availability_zone = local.zones[count.index]
  cidr_block = var.public_subnet_cidrs[count.index]
  map_public_ip_on_launch = false
}
resource "aws_subnet" "private" {
  count = 2
  vpc_id = aws_vpc.this.id
  availability_zone = local.zones[count.index]
  cidr_block = var.private_subnet_cidrs[count.index]
  map_public_ip_on_launch = false
}
resource "aws_route_table" "public" { vpc_id = aws_vpc.this.id }
resource "aws_route" "internet" {
  route_table_id = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.this.id
}
resource "aws_route_table_association" "public" {
  count = 2
  subnet_id = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
resource "aws_route_table" "private" { vpc_id = aws_vpc.this.id }
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
output "public_subnet_ids" { value = aws_subnet.public[*].id }
output "private_subnet_ids" { value = aws_subnet.private[*].id }
output "availability_zone" { value = local.zones[0] }
