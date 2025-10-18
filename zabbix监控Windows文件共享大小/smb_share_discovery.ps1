# smb_share_discovery.ps1
# 强制设置控制台输出编码为UTF-8（解决中文/特殊字符乱码）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
# 强制设置PowerShell的标准输出流编码为UTF-8（确保Zabbix能正确解析）
#$OutputEncoding = [System.Text.Encoding]::UTF8

# 获取所有 SMB 共享（排除系统默认共享）
$shares = Get-SmbShare | Where-Object { 
    -not $_.Name.Endswith('$') -and  # 排除卷挂载点
    $_.Name -notin 'ADMIN$', 'IPC$', 'PRINT$' # 排除系统共享
}

# 构造 LLD 数据数组
$discoveryData = @()
foreach ($share in $shares) {
# 对路径中的反斜杠进行替换（核心修改）
    $normalizedPath = $share.Path.Trim() -replace '\\', '/'
    $discoveryData += @{
        "{#SHARENAME}" = $share.Name.Trim()          # 共享名称（宏变量）
        "{#SHAREPATH}" = $normalizedPath             # 共享路径（宏变量）
        "{#SHAREDESCRIPTION}" = $share.Description   # 共享描述（可选）
    }
}

# 直接将 $discoveryData 转换为 JSON，并包裹在 {"data": [...]} 中
$discoveryJson = @{ data = $discoveryData } | ConvertTo-Json -Compress -Depth 3

# 输出结果（必须为单行 JSON）
Write-Output $discoveryJson

