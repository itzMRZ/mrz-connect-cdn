# DNS Propagation Checker for connect-cdn.itzmrz.xyz

Write-Host "Checking DNS propagation..." -ForegroundColor Cyan
Write-Host ""

$domain = "connect-cdn.itzmrz.xyz"

try {
    $result = Resolve-DnsName $domain -Type CNAME -ErrorAction Stop
    Write-Host "DNS is propagated!" -ForegroundColor Green
    Write-Host ""
    $result | Format-Table -AutoSize
    Write-Host ""
    Write-Host "Next step: Configure GitHub Pages with custom domain" -ForegroundColor Yellow
    Write-Host "https://github.com/itzMRZ/mrz-connect-cdn/settings/pages" -ForegroundColor Cyan
}
catch {
    Write-Host "DNS not propagated yet" -ForegroundColor Red
    Write-Host "Wait a few minutes and try again..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run this script again to check status" -ForegroundColor Cyan
}
