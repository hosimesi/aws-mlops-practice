# VPC
resource "aws_vpc" "mlops_practice" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.name}-mlops-practice"
  }
}

# SecurityGroup for ML Pipeline
resource "aws_security_group" "ml_pipeline" {
  name        = "${var.name}-mlops-practice-ml-pipeline-sg"
  description = "security group for mlops practice ml pipeline"
  vpc_id      = aws_vpc.mlops_practice.id
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name}-mlops-practice-ml-pipeline-sg"
  }
}

# SecurityGroup for predicictor application load balancer
resource "aws_security_group" "predictor_alb" {
  name        = "${var.name}-mlops-practice-predictor-alb-sg"
  description = "security group for predictor mlops practice alb"
  vpc_id      = aws_vpc.mlops_practice.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name}-mlops-practice-predictor-alb-sg"
  }
}


# SecurityGroup for predictor
resource "aws_security_group" "predictor" {
  name        = "${var.name}-mlops-practice-predictor-sg"
  description = "security group for mlops practice predictor"
  vpc_id      = aws_vpc.mlops_practice.id
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = ["${aws_security_group.predictor_alb.id}"]
  }
  # Allow Prometheus scrape
  ingress {
    from_port       = 9779
    to_port         = 9779
    protocol        = "tcp"
    security_groups = ["${aws_security_group.prometheus.id}"]
  }

  egress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = ["${aws_security_group.predictor_alb.id}"]
  }
  # Allow VPC Endpoint traffic
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Allow pushgateway(http)
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Allow DNS Resolver
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "ALL"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "${var.name}-mlops-practice-predictor-sg"
  }
}


# SecurityGroup for Redshift
resource "aws_security_group" "redshift" {
  name        = "${var.name}-mlops-practice-redshift-sg"
  description = "security group for mlops practice redshift"
  vpc_id      = aws_vpc.mlops_practice.id
  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow ALL traffic from anywhere"
  }

  ingress {
    from_port       = 5439
    to_port         = 5439
    protocol        = "tcp"
    security_groups = [aws_security_group.ml_pipeline.id]
    description     = "Allow from ECS Task"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "ALL"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name}-mlops-practice-redshift-sg"
  }
}

# SecurityGroup for EFS
resource "aws_security_group" "efs" {
  vpc_id = aws_vpc.mlops_practice.id
  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = ["${aws_security_group.predictor.id}"]
  }
}


##################################################
# SecurityGroup for dashboard application load balancer
resource "aws_security_group" "dashboard_alb" {
  name        = "${var.name}-mlops-practice-dashboard-alb-sg"
  description = "security group for dashboard mlops practice alb"
  vpc_id      = aws_vpc.mlops_practice.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name}-mlops-practice-dashboard-alb-sg"
  }
}


# SecurityGroup for dashboard
resource "aws_security_group" "dashboard" {
  name        = "${var.name}-mlops-practice-dashboard-sg"
  description = "security group for mlops practice dashboard"
  vpc_id      = aws_vpc.mlops_practice.id
  ingress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = ["${aws_security_group.dashboard_alb.id}"]
  }
  egress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = ["${aws_security_group.dashboard_alb.id}"]
  }
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Allow pushgateway(http)
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Allow DNS Resolver
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "ALL"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "${var.name}-mlops-practice-dashboard-sg"
  }
}


# SecurityGroup for prometheus
resource "aws_security_group" "prometheus" {
  name        = "${var.name}-mlops-practice-prometheus-sg"
  description = "security group for mlops practice prometheus"
  vpc_id      = aws_vpc.mlops_practice.id

  # Allow inbound traffic from Predictor application
  ingress {
    from_port = 9090
    to_port   = 9090
    protocol  = "tcp"
    # security_groups = ["${aws_security_group.dashboard.id}"]
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "ALL"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name}-mlops-practice-prometheus-sg"
  }
}


# SecurityGroup for pushgateway
resource "aws_security_group" "pushgateway" {
  name        = "${var.name}-mlops-practice-pushgateway-sg"
  description = "security group for mlops practice pushgateway"
  vpc_id      = aws_vpc.mlops_practice.id

  # Allow inbound traffic from Predictor application
  ingress {
    from_port       = 9091
    to_port         = 9091
    protocol        = "tcp"
    security_groups = ["${aws_security_group.predictor.id}", "${aws_security_group.ml_pipeline.id}", "${aws_security_group.prometheus.id}"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }


  tags = {
    Name = "${var.name}-mlops-practice-pushgateway-sg"
  }
}

##################################################


# Public Subnet (${var.aws_region}a)
resource "aws_subnet" "public1a" {
  vpc_id            = aws_vpc.mlops_practice.id
  availability_zone = "${var.aws_region}a"
  cidr_block        = "10.0.1.0/24"

  tags = {
    Name = "${var.name}-mlops-practice-public-subnet-1a"
  }
}

# Public Subnet (${var.aws_region}c)
resource "aws_subnet" "public1c" {
  vpc_id            = aws_vpc.mlops_practice.id
  availability_zone = "${var.aws_region}c"
  cidr_block        = "10.0.2.0/24"

  tags = {
    Name = "${var.name}-mlops-practice-public-subnet-1c"
  }
}

# Public Subnet (${var.aws_region}d)
resource "aws_subnet" "public1d" {
  vpc_id            = aws_vpc.mlops_practice.id
  availability_zone = "${var.aws_region}d"
  cidr_block        = "10.0.3.0/24"

  tags = {
    Name = "${var.name}-mlops-practice-public-subnet-1d"
  }
}

# Private Subnets (${var.aws_region}a)
resource "aws_subnet" "private1a" {
  vpc_id            = aws_vpc.mlops_practice.id
  availability_zone = "${var.aws_region}a"
  cidr_block        = "10.0.10.0/24"

  tags = {
    Name = "${var.name}-mlops-practice-private-subnet-1a"
  }
}

# Private Subnets (${var.aws_region}c)
resource "aws_subnet" "private1c" {
  vpc_id            = aws_vpc.mlops_practice.id
  availability_zone = "${var.aws_region}c"
  cidr_block        = "10.0.20.0/24"

  tags = {
    Name = "${var.name}-mlops-practice-private-subnet-1c"
  }
}

# Private Subnets (${var.aws_region}d)
resource "aws_subnet" "private1d" {
  vpc_id            = aws_vpc.mlops_practice.id
  availability_zone = "${var.aws_region}d"
  cidr_block        = "10.0.30.0/24"

  tags = {
    Name = "${var.name}-mlops-practice-private-subnet-1d"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "mlops_practice" {
  vpc_id = aws_vpc.mlops_practice.id

  tags = {
    Name = "${var.name}-mlops-practice-igw"
  }
}


# Route Table (Public)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.mlops_practice.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.mlops_practice.id
  }

  tags = {
    Name = "${var.name}-mlops-practice-public-route"
  }
}

# Association (Public ${var.aws_region}a)
resource "aws_route_table_association" "public1a" {
  subnet_id      = aws_subnet.public1a.id
  route_table_id = aws_route_table.public.id
}

# Association (Public ${var.aws_region}c)
resource "aws_route_table_association" "public1c" {
  subnet_id      = aws_subnet.public1c.id
  route_table_id = aws_route_table.public.id
}

# Association (Public ${var.aws_region}d)
resource "aws_route_table_association" "public1d" {
  subnet_id      = aws_subnet.public1d.id
  route_table_id = aws_route_table.public.id
}


# Route Table (Private)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.mlops_practice.id

  route {
    cidr_block = "10.0.0.0/16"
    gateway_id = "local"
  }

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_private_1a.id
  }

  tags = {
    Name = "${var.name}-mlops-practice-private-route"
  }
}

# Association (Private ${var.aws_region}a)
resource "aws_route_table_association" "private1a" {
  subnet_id      = aws_subnet.private1a.id
  route_table_id = aws_route_table.private.id
}

# Association (Private ${var.aws_region}c)
resource "aws_route_table_association" "private1c" {
  subnet_id      = aws_subnet.private1c.id
  route_table_id = aws_route_table.private.id
}

# Association (Private ${var.aws_region}d)
resource "aws_route_table_association" "private1d" {
  subnet_id      = aws_subnet.private1d.id
  route_table_id = aws_route_table.private.id
}

## VPC Endpoints
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.mlops_practice.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = ["${aws_route_table.private.id}", "${aws_route_table.public.id}"]
  tags = {
    Name = "${var.name}-mlops-practice-s3-vpe"
  }
}

resource "aws_vpc_endpoint" "ecr-dkr" {
  vpc_id              = aws_vpc.mlops_practice.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.ml_pipeline.id}", "${aws_security_group.predictor.id}"]
  tags = {
    Name = "${var.name}-mlops-practice-ecr-dkr-vpe"
  }
}

resource "aws_vpc_endpoint" "ecr-api" {
  vpc_id              = aws_vpc.mlops_practice.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.ml_pipeline.id}", "${aws_security_group.predictor.id}"]
  tags = {
    Name = "${var.name}-mlops-practice-ecr-api-vpe"
  }
}

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.mlops_practice.id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.ml_pipeline.id}", "${aws_security_group.predictor.id}"]
  tags = {
    Name = "${var.name}-mlops-practice-secretsmanager-vpe"
  }
}

resource "aws_vpc_endpoint" "ssm" {
  vpc_id              = aws_vpc.mlops_practice.id
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.ml_pipeline.id}", "${aws_security_group.predictor.id}"]
  tags = {
    Name = "${var.name}-mlops-practice-ssm-vpe"
  }
}

resource "aws_vpc_endpoint" "logs" {
  vpc_id              = aws_vpc.mlops_practice.id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = ["${aws_subnet.private1a.id}", "${aws_subnet.private1c.id}", "${aws_subnet.private1d.id}"]
  security_group_ids  = ["${aws_security_group.ml_pipeline.id}", "${aws_security_group.predictor.id}"]
  tags = {
    Name = "${var.name}-mlops-practice-logs-vpe"
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.mlops_practice.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = ["${aws_route_table.private.id}"]
  tags = {
    Name = "${var.name}-mlops-practice-dynamodb-vpe"
  }
}


# NAT Gateway
resource "aws_eip" "nat_private_1a" {
  domain = "vpc"

  tags = {
    Name = "${var.name}-mlops-practice-natgw-1a"
  }
}

resource "aws_nat_gateway" "nat_private_1a" {
  subnet_id     = aws_subnet.public1a.id
  allocation_id = aws_eip.nat_private_1a.id

  tags = {
    Name = "${var.name}-mlops-practice-natgw-1a"
  }
}

# resource "aws_route" "private_nat" {
#   route_table_id         = aws_route_table.private.id
#   destination_cidr_block = "0.0.0.0/0"
#   nat_gateway_id         = aws_nat_gateway.nat_private_1a.id
# }
