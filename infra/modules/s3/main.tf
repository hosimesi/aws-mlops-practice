resource "aws_s3_bucket" "mlops_practice" {
  bucket = "${var.name}-mlops-practice"
}
