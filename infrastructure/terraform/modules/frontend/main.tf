variable "name" {
  type = string
}
variable "origin_hostname" {
  type = string
}
variable "origin_header" {
  type = string
  sensitive = true
}
resource "aws_s3_bucket" "frontend" { bucket = "${var.name}-frontend" }
resource "aws_s3_bucket" "artifacts" { bucket = "${var.name}-artifacts" }
locals { buckets = { frontend = aws_s3_bucket.frontend.id, artifacts = aws_s3_bucket.artifacts.id } }
resource "aws_s3_bucket_public_access_block" "this" {
  for_each = local.buckets
  bucket = each.value
  block_public_acls = true
  ignore_public_acls = true
  block_public_policy = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_versioning" "this" {
  for_each = local.buckets
  bucket = each.value
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  for_each = local.buckets
  bucket = each.value
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}
resource "aws_s3_bucket_ownership_controls" "this" {
  for_each = local.buckets
  bucket = each.value
  rule { object_ownership = "BucketOwnerEnforced" }
}
resource "aws_cloudfront_origin_access_control" "this" {
  name = var.name
  origin_access_control_origin_type = "s3"
  signing_behavior = "always"
  signing_protocol = "sigv4"
}
data "aws_cloudfront_cache_policy" "disabled" { name = "Managed-CachingDisabled" }
data "aws_cloudfront_origin_request_policy" "api" { name = "Managed-AllViewerExceptHostHeader" }
resource "aws_cloudfront_cache_policy" "assets" {
  name = "${var.name}-assets"
  min_ttl = 0
  default_ttl = 86400
  max_ttl = 31536000
  parameters_in_cache_key_and_forwarded_to_origin {
    enable_accept_encoding_gzip = true
    enable_accept_encoding_brotli = true
    cookies_config { cookie_behavior = "none" }
    headers_config { header_behavior = "none" }
    query_strings_config { query_string_behavior = "none" }
  }
}
resource "aws_cloudfront_function" "routes" {
  name = "${var.name}-spa"
  runtime = "cloudfront-js-2.0"
  publish = true
  code = <<-JS
    function handler(event) {
      var request = event.request;
      if (['/', '/dashboard', '/hri', '/map', '/history'].indexOf(request.uri) !== -1) request.uri = '/index.html';
      return request;
    }
  JS
}
resource "aws_cloudfront_distribution" "this" {
  enabled = true
  default_root_object = "index.html"
  price_class = "PriceClass_100"
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id = "frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.this.id
  }
  origin {
    domain_name = var.origin_hostname
    origin_id = "api"
    custom_header {
      name = "X-ClimateHealth-Origin"
      value = var.origin_header
    }
    custom_origin_config {
      http_port = 80
      https_port = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols = ["TLSv1.2"]
    }
  }
  default_cache_behavior {
    target_origin_id = "frontend"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods = ["GET", "HEAD"]
    cached_methods = ["GET", "HEAD"]
    cache_policy_id = data.aws_cloudfront_cache_policy.disabled.id
    compress = true
    function_association {
      event_type = "viewer-request"
      function_arn = aws_cloudfront_function.routes.arn
    }
  }
  ordered_cache_behavior {
    path_pattern = "/api/*"
    target_origin_id = "api"
    viewer_protocol_policy = "https-only"
    allowed_methods = ["GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]
    cached_methods = ["GET", "HEAD"]
    cache_policy_id = data.aws_cloudfront_cache_policy.disabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.api.id
    compress = true
  }
  ordered_cache_behavior {
    path_pattern = "/assets/*"
    target_origin_id = "frontend"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods = ["GET", "HEAD"]
    cached_methods = ["GET", "HEAD"]
    cache_policy_id = aws_cloudfront_cache_policy.assets.id
    compress = true
  }
  restrictions {
    geo_restriction { restriction_type = "none" }
  }
  viewer_certificate { cloudfront_default_certificate = true }
}
resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
        { Sid = "CloudFrontOnly", Effect = "Allow", Principal = { Service = "cloudfront.amazonaws.com" }, Action = "s3:GetObject", Resource = "${aws_s3_bucket.frontend.arn}/*", Condition = { StringEquals = { "AWS:SourceArn" = aws_cloudfront_distribution.this.arn } } },
        { Sid = "DenyHTTP", Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.frontend.arn,"${aws_s3_bucket.frontend.arn}/*"], Condition = { Bool = { "aws:SecureTransport" = "false" } } }
      ] })
}
resource "aws_s3_bucket_policy" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.artifacts.arn,"${aws_s3_bucket.artifacts.arn}/*"], Condition = { Bool = { "aws:SecureTransport" = "false" } } }] })
}
output "domain" { value = aws_cloudfront_distribution.this.domain_name }
output "distribution_id" { value = aws_cloudfront_distribution.this.id }
output "bucket" { value = aws_s3_bucket.frontend.id }
output "artifact_bucket" { value = aws_s3_bucket.artifacts.id }
output "artifact_bucket_arn" { value = aws_s3_bucket.artifacts.arn }
