terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Optional: Store state in Azure Storage
  # Uncomment after creating storage account
  # backend "azurerm" {
  #   resource_group_name  = "betania-terraform-state"
  #   storage_account_name = "betaniatfstate"
  #   container_name       = "tfstate"
  #   key                  = "content-automation.tfstate"
  # }
}

provider "azurerm" {
  features {}
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "betania-content"
}

# Secrets (passed via pipeline or terraform.tfvars - never commit!)
variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "wordpress_username" {
  description = "WordPress username"
  type        = string
  sensitive   = true
}

variable "wordpress_password" {
  description = "WordPress application password"
  type        = string
  sensitive   = true
}

variable "wordpress_db_host" {
  description = "WordPress database host"
  type        = string
  sensitive   = true
}

variable "wordpress_db_name" {
  description = "WordPress database name"
  type        = string
  sensitive   = true
}

variable "wordpress_db_user" {
  description = "WordPress database user"
  type        = string
  sensitive   = true
}

variable "wordpress_db_password" {
  description = "WordPress database password"
  type        = string
  sensitive   = true
}

variable "sendgrid_api_key" {
  description = "SendGrid API Key"
  type        = string
  sensitive   = true
}

# Locals
locals {
  resource_prefix = "${var.project_name}-${var.environment}"
  tags = {
    Environment = var.environment
    Project     = "Betania Content Automation"
    ManagedBy   = "Terraform"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${local.resource_prefix}-rg"
  location = var.location
  tags     = local.tags
}

# Storage Account for Azure Functions
resource "azurerm_storage_account" "functions" {
  name                     = replace("${var.project_name}${var.environment}st", "-", "")
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = local.tags
}

# Application Insights for monitoring
resource "azurerm_application_insights" "main" {
  name                = "${local.resource_prefix}-insights"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  application_type    = "web"
  tags                = local.tags
}

# App Service Plan (Consumption)
resource "azurerm_service_plan" "functions" {
  name                = "${local.resource_prefix}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "Y1" # Consumption tier (serverless)
  tags                = local.tags
}

# Linux Function App
resource "azurerm_linux_function_app" "main" {
  name                       = "${local.resource_prefix}-func"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  service_plan_id            = azurerm_service_plan.functions.id
  storage_account_name       = azurerm_storage_account.functions.name
  storage_account_access_key = azurerm_storage_account.functions.primary_access_key
  tags                       = local.tags

  site_config {
    application_stack {
      python_version = "3.11"
    }

    application_insights_connection_string = azurerm_application_insights.main.connection_string
    application_insights_key               = azurerm_application_insights.main.instrumentation_key

    # CORS settings (if needed)
    cors {
      allowed_origins = ["https://betania.io"]
    }
  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "AzureWebJobsFeatureFlags"       = "EnableWorkerIndexing"
    "ENABLE_ORYX_BUILD"              = "true"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"

    # Application settings
    "WORDPRESS_URL"          = "https://betania.io"
    "WORDPRESS_USERNAME"     = var.wordpress_username
    "WORDPRESS_PASSWORD"     = var.wordpress_password
    "WORDPRESS_DB_HOST"      = var.wordpress_db_host
    "WORDPRESS_DB_NAME"      = var.wordpress_db_name
    "WORDPRESS_DB_USER"      = var.wordpress_db_user
    "WORDPRESS_DB_PASSWORD"  = var.wordpress_db_password
    "OPENAI_API_KEY"         = var.openai_api_key
    "SENDGRID_API_KEY"       = var.sendgrid_api_key
    "SENDGRID_FROM_EMAIL"    = "newsletter@betania.io"
    "SENDGRID_FROM_NAME"     = "Betania Tech Newsletter"
    "EMAIL_PROVIDER"         = "sendgrid"
    "MAX_DAILY_ARTICLES"     = "3"
    "MAX_NEWSLETTER_ARTICLES" = "3"
    "ENVIRONMENT"            = var.environment
  }

  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    ignore_changes = [
      # Ignore changes to these as they're managed by deployment
      app_settings["WEBSITE_RUN_FROM_PACKAGE"],
    ]
  }
}

# Outputs
output "function_app_name" {
  value       = azurerm_linux_function_app.main.name
  description = "Function App name"
}

output "function_app_default_hostname" {
  value       = azurerm_linux_function_app.main.default_hostname
  description = "Function App default hostname"
}

output "resource_group_name" {
  value       = azurerm_resource_group.main.name
  description = "Resource Group name"
}

output "application_insights_instrumentation_key" {
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
  description = "Application Insights instrumentation key"
}
