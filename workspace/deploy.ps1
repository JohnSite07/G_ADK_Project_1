[CmdletBinding()]
param (
    [string]$ProjectId,
    [string]$Region,
    [switch]$AutoApprove
)

# Stop script on first error
$ErrorActionPreference = 'Stop'

# --- 1. Prerequisites Check ---
Write-Host "Step 1: Checking prerequisites..." -ForegroundColor Cyan

# Check for Terraform
if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: 'terraform' CLI not found in your PATH." -ForegroundColor Red
    Write-Host "Please install it and try again: https://learn.hashicorp.com/tutorials/terraform/install-cli"
    exit 1
}

# Check for gcloud
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: 'gcloud' CLI not found in your PATH." -ForegroundColor Red
    Write-Host "Please install it and try again: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Check gcloud login
if (-not (gcloud auth print-access-token -q 2>$null)) {
    Write-Host "❌ Error: You are not logged into Google Cloud." -ForegroundColor Red
    Write-Host "Please run 'gcloud auth login' and 'gcloud config set project <YOUR_PROJECT_ID>'."
    exit 1
}

# Determine Project ID and Region
$gcloudProject = if ([string]::IsNullOrEmpty($ProjectId)) { (gcloud config get-value project 2>$null) } else { $ProjectId }
$gcloudRegion = if ([string]::IsNullOrEmpty($Region)) { (gcloud config get-value compute/region 2>$null) } else { $Region }

if ([string]::IsNullOrEmpty($gcloudProject)) {
    Write-Host "❌ Error: Google Cloud Project ID not found." -ForegroundColor Red
    Write-Host "Set it via 'gcloud config set project <PROJECT_ID>' or use the -ProjectId parameter."
    exit 1
}
if ([string]::IsNullOrEmpty($gcloudRegion)) {
    Write-Host "❌ Error: Google Cloud Region not found." -ForegroundColor Red
    Write-Host "Set it via 'gcloud config set compute/region <REGION>' or use the -Region parameter."
    exit 1
}

Write-Host "✅ Prerequisites met."
Write-Host "   - Project: $gcloudProject"
Write-Host "   - Region:  $gcloudRegion"


# --- 2. Terraform Plan ---
Write-Host "`nStep 2: Initializing and planning Terraform..." -ForegroundColor Cyan
Push-Location -Path "./terraform"

$tfVars = "-var=`"project_id=$gcloudProject`" -var=`"region=$gcloudRegion`""

try {
    terraform init -no-color
    # The -out parameter for plan requires a file path
    terraform plan -no-color -out="tfplan" -detailed-exitcode $tfVars

    $planExitCode = $LASTEXITCODE
    if ($planExitCode -eq 1) {
        Write-Host "❌ Terraform plan failed. See errors above." -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Write-Host "`nTerraform has generated the following execution plan:"
    Write-Host "----------------------------------------------------"
    terraform show -no-color tfplan
    Write-Host "----------------------------------------------------"
}
catch {
    # This block catches script-terminating errors, not Terraform execution errors
    Write-Host "❌ An unexpected error occurred during Terraform plan. See errors above." -ForegroundColor Red
    Pop-Location
    exit 1
}


# --- 3. Confirmation ---
if (-not $AutoApprove) {
    Write-Host "`nStep 3: Confirmation" -ForegroundColor Cyan
    Write-Host "WARNING: This will create billable Google Cloud resources." -ForegroundColor Yellow
    $confirmation = Read-Host "Do you want to apply this plan? (y/n)"
    if ($confirmation.ToLower() -ne 'y') {
        Write-Host "🛑 Deployment aborted by user." -ForegroundColor Yellow
        Pop-Location
        exit 0
    }
} else {
    Write-Host "`nStep 3: Confirmation skipped due to -AutoApprove switch." -ForegroundColor Cyan
}


# --- 4. Targeted Apply for APIs and Artifact Registry ---
Write-Host "`nStep 4: Applying Phase 1 - Enabling APIs and creating Artifact Registry..." -ForegroundColor Cyan
try {
    # Apply only the resources needed to build and push the image
    $targets = @(
        'google_project_service.run_api',
        'google_project_service.artifact_registry_api',
        'google_project_service.cloud_build_api',
        'google_artifact_registry_repository.repo'
    ) 
    $targetArgs = $targets | ForEach-Object { "-target=$_`n" } 
    terraform apply -no-color -auto-approve $tfVars $targetArgs
    Write-Host "✅ Phase 1 complete."
}
catch {
    Write-Host "❌ Terraform apply (Phase 1) failed. See errors above." -ForegroundColor Red
    Pop-Location
    exit 1
}


# --- 5. Build and Push Image ---
Write-Host "`nStep 5: Building and pushing application image with Cloud Build..." -ForegroundColor Cyan
$repoName = terraform output -raw repo_name
$appName = terraform output -raw app_name
$imageUrl = "${gcloudRegion}-docker.pkg.dev/${gcloudProject}/${repoName}/${appName}:latest"
Pop-Location # Go back to root to run gcloud build

try {
    # Ensure next.config.mjs exists for standalone build mode in Dockerfile
    $nextConfigFile = "frontend/next.config.mjs"
    if (-not (Test-Path -Path $nextConfigFile)) {
        Write-Host "INFO: Creating '$nextConfigFile' for standalone build..." -ForegroundColor Gray
        $nextConfigContent = "/** @type {import('next').NextConfig} */`nconst nextConfig = { output: 'standalone' };`n`nexport default nextConfig;`n"
        Set-Content -Path $nextConfigFile -Value $nextConfigContent
    }

    gcloud builds submit "./frontend" --tag=$imageUrl --project=$gcloudProject
    Write-Host "✅ Image built and pushed to $imageUrl"
}
catch {
    Write-Host "❌ Google Cloud Build failed. See errors above." -ForegroundColor Red
    exit 1
}


# --- 6. Full Terraform Apply ---
Write-Host "`nStep 6: Applying Phase 2 - Deploying Cloud Run service..." -ForegroundColor Cyan
Push-Location -Path "./terraform"
try {
    # Now apply the full plan, which includes the Cloud Run service referencing the new image
    terraform apply -no-color -auto-approve $tfVars tfplan
    Write-Host "✅ Phase 2 complete."
}
catch {
    Write-Host "❌ Terraform apply (Phase 2) failed. See errors above." -ForegroundColor Red
    Pop-Location
    exit 1
}


# --- 7. Print Final URL ---
Write-Host "`n🚀 Deployment Complete!" -ForegroundColor Green
$finalUrl = terraform output -raw service_url
Write-Host "Your service is available at: $finalUrl"
Pop-Location
