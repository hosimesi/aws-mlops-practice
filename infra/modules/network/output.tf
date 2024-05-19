output "public_subnets" {
  value = ["${aws_subnet.public1a.id}", "${aws_subnet.public1c.id}", "${aws_subnet.public1d.id}"]
}

output "private_subnets" {
  value = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
}

output "predictor_alb_security_group" {
  value = aws_security_group.predictor_alb.id
}

output "dashboard_alb_security_group" {
  value = aws_security_group.dashboard_alb.id
}

output "ml_pipeline_security_group" {
  value = aws_security_group.ml_pipeline.id
}

output "predictor_security_group" {
  value = aws_security_group.predictor.id
}

output "dashboard_security_group" {
  value = aws_security_group.dashboard.id
}

output "prometheus_security_group" {
  value = aws_security_group.prometheus.id
}

output "pushgateway_security_group" {
  value = aws_security_group.pushgateway.id
}

output "vpc_id" {
  value = aws_vpc.mlops_practice.id
}

output "ml_pipeline_subnet" {
  value = aws_subnet.private1a.id
}
