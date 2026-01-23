$headers = @{
    "X-Api-Key" = "lsv2_sk_YOUR_API_KEY_HERE"  # Replace with your actual LANGSMITH_API_KEY
    "X-Tenant-Id" = "950d802b-125a-45bc-88e4-3d7d0edee182"
}
$deployments = Invoke-RestMethod -Uri "https://api.host.langchain.com/v2/deployments" -Headers $headers
$indufix = $deployments.resources | Where-Object { $_.name -like "*indufix*" -or $_.name -like "*ndufix*" }
$indufix | ConvertTo-Json -Depth 10
