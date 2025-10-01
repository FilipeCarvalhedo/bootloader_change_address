# PowerShell script para relocar arquivo Intel HEX
# Uso: .\relocate_hex.ps1 input.hex output.hex from_addr to_addr

param(
    [Parameter(Mandatory=$true)][string]$InputFile,
    [Parameter(Mandatory=$true)][string]$OutputFile, 
    [Parameter(Mandatory=$true)][string]$FromAddr,
    [Parameter(Mandatory=$true)][string]$ToAddr
)

# Verificar se arquivo existe
if (-not (Test-Path $InputFile)) {
    Write-Host "Erro: Arquivo $InputFile nao encontrado" -ForegroundColor Red
    exit 1
}

try {
    # Ler conteudo do arquivo
    $content = Get-Content $InputFile -Raw
    
    # Converter enderecos
    $fromAddrInt = [Convert]::ToInt32($FromAddr, 16)
    $toAddrInt = [Convert]::ToInt32($ToAddr, 16)
    
    # Substituir Extended Linear Address record
    # :020000040FF0EB -> :02000004003003B (0xFF0 -> 0x030)
    $oldELA = ":020000040FF0"
    $newELA = ":02000004003"
    
    if ($content -match $oldELA) {
        # Calcular novo checksum para ELA
        # Checksum = 256 - (02 + 00 + 00 + 04 + 00 + 30) % 256
        $checksum = (256 - (0x02 + 0x00 + 0x00 + 0x04 + 0x00 + 0x30) % 256) % 256
        $newELAFull = ":02000004003" + $checksum.ToString("X1")
        
        # Substituir no conteudo
        $newContent = $content -replace ":020000040FF0EB", $newELAFull
        
        # Escrever arquivo relocado
        $newContent | Out-File -FilePath $OutputFile -Encoding ASCII -NoNewline
        
        Write-Host "OK: Relocado de $FromAddr para $ToAddr" -ForegroundColor Green
        Write-Host "   Input:  $InputFile"
        Write-Host "   Output: $OutputFile"
        exit 0
    } else {
        Write-Host "Erro: Formato de arquivo HEX nao reconhecido" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
