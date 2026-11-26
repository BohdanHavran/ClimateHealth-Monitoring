# Adapted from owner modules/alb/main.tf; see VARIANT_B_REUSE.md.
variable "vpc_id" {
  type = string
}
variable "subnet_ids" {
  type = list(string)
}
variable "security_group" {
  type = string
}
variable "certificate_arn" {
  type = string
}
variable "origin_header" {
  type = string
  sensitive = true
}
resource "aws_lb" "this" {
  name_prefix = "ch-"
  load_balancer_type         = "application"
  security_groups            = [var.security_group]
  subnets = var.subnet_ids
  internal                   = false
  desync_mitigation_mode     = "strictest"
  drop_invalid_header_fields = true
}
# Adapted from owner aws_alb_target_group.ecs: one bridge/instance target, strict readiness.
resource "aws_lb_target_group" "backend" {
  name_prefix = "ch-"
  port = 8080
  protocol = "HTTP"
  target_type = "instance"
  vpc_id = var.vpc_id
  deregistration_delay = 30
  health_check {
    enabled = true
    protocol = "HTTP"
    healthy_threshold = 2
    unhealthy_threshold = 2
    timeout = 5
    interval = 30
    matcher = "200"
    path = "/health/ready"
  }
}
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  protocol          = "HTTPS"
  port              = 443
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Origin access required"
      status_code  = "403"
    }
  }
}
resource "aws_lb_listener_rule" "origin" {
  listener_arn = aws_lb_listener.https.arn
  priority = 10
  action {
    type = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
  condition {
    http_header {
      http_header_name = "X-ClimateHealth-Origin"
      values = [var.origin_header]
    }
  }
}
output "target_group_arn" { value = aws_lb_target_group.backend.arn }
output "listener_rule_arn" { value = aws_lb_listener_rule.origin.arn }
output "dns" { value = aws_lb.this.dns_name }
output "zone_id" { value = aws_lb.this.zone_id }
