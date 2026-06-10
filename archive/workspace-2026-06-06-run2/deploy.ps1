<#
.SYNOPSIS
    One-run deploy of this generated site to Google Cloud (Artifact Registry + Cloud Run).

.DESCRIPTION
    Performs every step needed to take the build in this workspace live, in order:
      1. Checks prerequisites (gcloud + terraform installed, an active gcloud login).
      2. terraform init.
      3. terraform plan (shown for review) + a single confirmation.
      4. terraform apply (targeted) to enable APIs and create the Artifact Registry repo.
      5. Builds & pushes the frontend image with Cloud Build (no local Docker required).
      6. terraform apply (full) to create/update the Cloud Run service + public IAM.
      7. Prints the live service URL.

    SAFE BY DEFAULT: it stops on the first error and asks for one explicit confirmation
    before creating any billable resources. Nothing here runs automatically as part of the
    agent pipeline — you run it manually when you are ready to deploy.

.PARAMETER ProjectId
    GCP project ID. Defaults to $env:GOOGLE_CLOUD_PROJECT.

.PARAMETER Region
    GCP region for Artifact Registry + Cloud Run. Defaults to $env:GOOGLE_CLOUD_REGION,
    then us-central1.

.PARAMETER AutoApprove
    Skip the interactive confirmation (for unattended/CI use).

.EXAMPLE
    ./deploy.ps1
    ./deploy.ps1 -ProjectId my-proj -Region us-central1
    ./deploy.ps1 -AutoApprove

.NOTES
    Prerequisites: Google Cloud SDK (gcloud) and Terraform on PATH, and
    `gcloud auth login` + `gcloud auth application-default login` already done.
    To tear everything down later: cd terraform; terraform destroy
#>
[CmdletBinding()]
param(
    [string]$ProjectId = $env:GOOGLE_CLOUD_PROJECT,
    [string]$Region = $(if ($env:GOOGLE_CLOUD_REGION) { $env:GOOGLE_CLOUD_REGION } else { "us-central1" }),
    [switch]$AutoApprove
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$tfDir = Join-Path $root "terraform"
$frontendDir = Join-Path $root "frontend"

# Must match terraform/variables.tf defaults.
$ServiceName = "story-of-everything"
$RepositoryId = "story-of-everything-repo"

function Run-Native {
    param([string]$Exe, [string[]]$Args, [string]$WorkingDir = $root)
    Write-Host "  > $Exe $($Args -join ' ')" -ForegroundColor DarkGray
    Push-Location $WorkingDir
    try { & $Exe @Args } finally { Pop-Location }
    if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): $Exe $($Args -join ' ')" }
}

function Section($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }

# --- 0. Validate inputs & prerequisites ------------------------------------ #
if (-not $ProjectId) { throw "No project id. Pass -ProjectId or set GOOGLE_CLOUD_PROJECT." }
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) { throw "gcloud not found on PATH. Install the Google Cloud SDK." }
if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) { throw "terraform not found on PATH." }
if (-not (Test-Path $tfDir)) { throw "terraform/ not found next to this script." }
if (-not (Test-Path (Join-Path $frontendDir "Dockerfile"))) { throw "frontend/Dockerfile not found." }

$active = (& gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null)
if (-not $active) { throw "No active gcloud login. Run: gcloud auth login ; gcloud auth application-default login" }

$Image = "$Region-docker.pkg.dev/$ProjectId/$RepositoryId/$ServiceName`:latest"

Section "Deployment plan"
Write-Host "  Project : $ProjectId"
Write-Host "  Region  : $Region"
Write-Host "  Service : $ServiceName (Cloud Run)"
Write-Host "  Image   : $Image"
Write-Host "  Account : $active"
Write-Host "  WARNING : This creates BILLABLE resources (Cloud Run, Artifact Registry, Cloud Build)." -ForegroundColor Yellow

& gcloud config set project $ProjectId | Out-Null

# --- 1. terraform init ----------------------------------------------------- #
Section "1/6 terraform init"
Run-Native terraform @("init", "-input=false") $tfDir

# --- 2. terraform plan (review) -------------------------------------------- #
Section "2/6 terraform plan"
Run-Native terraform @("plan", "-input=false", "-var", "gcp_project_id=$ProjectId", "-var", "gcp_region=$Region") $tfDir

# --- 3. confirm ------------------------------------------------------------ #
if (-not $AutoApprove) {
    $ans = Read-Host "`nProceed with deployment to '$ProjectId'? Type 'yes' to continue"
    if ($ans -ne "yes") { Write-Host "Aborted. Nothing was created." -ForegroundColor Yellow; exit 0 }
}

# --- 4. create APIs + Artifact Registry first (image must exist before Cloud Run) --- #
Section "3/6 terraform apply (enable APIs + Artifact Registry)"
Run-Native terraform @(
    "apply", "-input=false", "-auto-approve",
    "-var", "gcp_project_id=$ProjectId", "-var", "gcp_region=$Region",
    "-target=google_project_service.run_api",
    "-target=google_project_service.artifactregistry_api",
    "-target=google_project_service.cloudbuild_api",
    "-target=google_artifact_registry_repository.repository"
) $tfDir

# --- 5. build & push the image with Cloud Build (no local Docker needed) ---- #
Section "4/6 Cloud Build: build & push image"
Run-Native gcloud @("builds", "submit", $frontendDir, "--tag", $Image, "--project", $ProjectId) $root

# --- 6. full apply: Cloud Run service + public access ----------------------- #
Section "5/6 terraform apply (Cloud Run service)"
Run-Native terraform @(
    "apply", "-input=false", "-auto-approve",
    "-var", "gcp_project_id=$ProjectId", "-var", "gcp_region=$Region"
) $tfDir

# --- 7. report the URL ----------------------------------------------------- #
Section "6/6 Done"
$url = (& terraform -chdir="$tfDir" output -raw service_url 2>$null)
if ($url) {
    Write-Host "`n  Deployed: $url" -ForegroundColor Green
    Write-Host "  (Re-running this script redeploys the latest build. To remove everything: cd terraform; terraform destroy)"
} else {
    Write-Host "Deployed, but could not read service_url output. Check: cd terraform; terraform output" -ForegroundColor Yellow
}
