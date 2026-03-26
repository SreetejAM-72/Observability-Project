provider "aws" {
  region = var.region
}

resource "aws_iam_role" "lambda" {
  name = "nr-policy-sync"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "ec2_read" {
  name = "nr-ec2-read"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ec2:DescribeInstances"]
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ec2" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.ec2_read.arn
}

resource "aws_lambda_function" "this" {
  function_name = "nr-policy-sync"
  role          = aws_iam_role.lambda.arn
  runtime       = "python3.11"
  handler       = "app.handler"
  filename      = "../build/lambda.zip"
  timeout       = 30

  environment {
    variables = {
      NEW_RELIC_API_KEY    = var.new_relic_api_key
      NEW_RELIC_ACCOUNT_ID = var.new_relic_account_id
    }
  }
}

# Event-driven
resource "aws_cloudwatch_event_rule" "ec2" {
  name = "ec2-running"

  event_pattern = jsonencode({
    source      = ["aws.ec2"]
    detail-type = ["EC2 Instance State-change Notification"]
    detail = {
      state = ["running"]
    }
  })
}

resource "aws_cloudwatch_event_target" "event_lambda" {
  rule = aws_cloudwatch_event_rule.ec2.name
  arn  = aws_lambda_function.this.arn
}

# Scheduled sync
resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "nr-sync-schedule"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "schedule_lambda" {
  rule = aws_cloudwatch_event_rule.schedule.name
  arn  = aws_lambda_function.this.arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "events.amazonaws.com"
}