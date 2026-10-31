param([Parameter(Mandatory=$true)][string]$RepositoryUrl)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if ($RepositoryUrl -notmatch '^https://github\.com/[^/]+/[^/]+?(\.git)?$') {
    throw 'Use the HTTPS URL of your NEW empty GitHub repository.'
}
if ($RepositoryUrl -match '^https://github\.com/vuvandat109/Gesture-AI-Web(\.git)?$') {
    throw 'This is the original repository. Supply your NEW repository URL.'
}
if (Test-Path '.git') {
    throw 'This folder already has Git history. Extract a fresh copy of the release ZIP to publish independently.'
}
python scripts/verify_tfc_release.py
if ($LASTEXITCODE -ne 0) { throw 'TF-C model verification failed.' }
python scripts/verify_preserved_assets.py
if ($LASTEXITCODE -ne 0) { throw 'Original assets verification failed.' }
git init -b main
if ($LASTEXITCODE -ne 0) { throw 'git init failed.' }
git add .
if ($LASTEXITCODE -ne 0) { throw 'git add failed.' }
git commit -m 'Create Gesture AI TF-C with trained model and original interface'
if ($LASTEXITCODE -ne 0) { throw 'Commit failed. Configure git user.name and user.email, then use the manual README commands.' }
git remote add origin $RepositoryUrl
if ($LASTEXITCODE -ne 0) { throw 'Adding remote failed.' }
git push -u origin main
if ($LASTEXITCODE -ne 0) { throw 'Push failed. Check GitHub sign-in and repository access; see README for manual retry.' }
