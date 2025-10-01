# nRF52840 Boot Analysis Tools

Este conjunto de scripts automatiza a análise completa de problemas de boot no nRF52840, comparando o estado da memória entre programação direta e programação via bootloader+DFU.

## 🎯 Objetivo

Identificar exatamente **POR QUE** uma aplicação funciona quando gravada diretamente mas falha quando programada via bootloader+DFU, comparando:
- Toda a memória flash
- Registradores críticos do ARM Cortex-M4
- Tabelas de vetores
- Configurações do MBR
- Estados do sistema

## 📁 Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `nrf52_memory_dump.py` | Script principal para dump completo da memória |
| `nrf52_memory_dump_halted.py` | **🎯 NOVA VERSÃO:** Dump com MCU halted em pontos consistentes |
| `compare_dumps.py` | Script para comparar dois dumps e identificar diferenças |
| `compare_halted_dumps.py` | **🎯 NOVA VERSÃO:** Comparação de dumps halted (mais preciso) |
| `automated_analysis.py` | Script de automação completa do processo |
| `run_analysis.bat` | Script batch para Windows (fácil de usar) |
| `run_halted_analysis.bat` | **🎯 NOVA VERSÃO:** Análise halted (elimina timing artifacts) |
| `README.md` | Este arquivo de documentação |

## 🚀 Uso Rápido (Windows)

### Método 1: Análise HALTED (🎯 RECOMENDADO - Mais Preciso)

```batch
# Navegue até a pasta scripts
cd Z:\home\filipe\Projetos\athos\sdk17\isolated\scripts

# Execute a análise halted (elimina timing artifacts)
run_halted_analysis.bat
```

**✅ VANTAGENS DA ANÁLISE HALTED:**
- MCU halted em **pontos consistentes** em ambos os cenários
- **Elimina timing artifacts** e race conditions  
- Identifica **diferenças REAIS** de registradores
- Comparação de **CPU registers, execution context** e system state
- **Mais confiável** para identificar causa raiz

### Método 2: Script Batch Tradicional

```batch
# Execute a análise completa tradicional
run_analysis.bat ..\examples\ble_app_hrs_freertos\build\ble_app_hrs_freertos.hex ..\examples\dfu\secure_bootloader\build\secure_bootloader.hex
```

### Método 2: Python Direto

```bash
python automated_analysis.py --app-hex path/to/app.hex --bootloader-hex path/to/bootloader.hex
```

## 📋 Pré-requisitos

### Software Necessário:
- **Python 3.6+**
- **nRF Command Line Tools** (`nrfjprog`)
- **nrfutil** (para DFU)
- **nRF52840 conectado via USB**

### Verificação:
```bash
python --version          # Deve mostrar Python 3.x
nrfjprog --version        # Deve mostrar versão do nrfjprog
nrfutil version           # Deve mostrar versão do nrfutil
```

## 🔧 Uso Detalhado

### 1. Dump Individual de Memória

```bash
# Dump após programação direta
python nrf52_memory_dump.py --mode direct --output direct_dump.txt

# Dump após bootloader+DFU  
python nrf52_memory_dump.py --mode bootloader --output bootloader_dump.txt
```

### 2. Comparação Manual

```bash
python compare_dumps.py direct_dump.txt bootloader_dump.txt comparison_report.txt
```

### 3. Análise Automatizada Completa

```bash
python automated_analysis.py \
  --app-hex ../examples/ble_app_hrs_freertos/build/ble_app_hrs_freertos.hex \
  --bootloader-hex ../examples/dfu/secure_bootloader/build/secure_bootloader.hex \
  --softdevice-hex ../components/softdevice/s140/hex/s140_nrf52_7.0.1_softdevice.hex
```

## 📊 Saídas Geradas

### Arquivos de Dump (`*_dump_*.txt`):
- **Device Information**: ID, info, reset reason
- **Critical Registers**: VTOR, NVIC, UICR, etc.
- **Vector Tables**: MBR, SoftDevice, Bootloader, Application
- **MBR Settings**: Forward addresses, bootloader config
- **Flash Memory**: Conteúdo de cada região da flash

### Relatório de Comparação (`*_report_*.txt`):
- **Summary**: Total de diferenças encontradas
- **Critical Differences**: Diferenças que causam falha de boot
- **Detailed Analysis**: Comparação registro por registro
- **Recommendations**: Sugestões de correção

## 🔍 Interpretando os Resultados

### ✅ Sem Diferenças Críticas:
```
✅ NO CRITICAL DIFFERENCES FOUND
The memory states are very similar. Boot issues may be timing-related.
```
**→ Problema pode ser timing, inicialização de periféricos, ou FDS/peer manager**

### ⚠️ Diferenças Críticas Encontradas:
```
⚠️ CRITICAL DIFFERENCES DETECTED
• VTOR difference: Vector table offset mismatch
• Stack Pointer difference: Initial SP mismatch  
• Reset Vector difference: Entry point mismatch
```
**→ Problema identificado! Seguir recomendações do relatório**

## 🎯 Exemplos de Problemas Detectados

### 1. Vector Table Offset (VTOR) Incorreto
```
[REGISTER] VTOR (Vector Table Offset) (0xE000ED08)
  Direct Flash: 0x00027000
  Bootloader:   0x00000000
```
**→ Aplicação não está configurando VTOR corretamente**

### 2. Stack Pointer Inválido
```
[VECTOR] Application Vector Table - Stack Pointer
  Direct:    0x2003FEB0
  Bootloader: 0x00000000
```
**→ Stack pointer não foi inicializado**

### 3. Reset Vector Incorreto
```
[VECTOR] Application Vector Table - Reset Vector  
  Direct:    0x0002F001
  Bootloader: 0x00000000
```
**→ Reset handler não foi configurado**

## 🚨 Solução de Problemas

### Erro: "nrfjprog not found"
```bash
# Instalar nRF Command Line Tools
# Download: https://www.nordicsemi.com/Products/Development-tools/nrf-command-line-tools
```

### Erro: "nrfutil not found"  
```bash
pip install nrfutil
```

### Erro: "Device not found"
```bash
# Verificar conexão USB
nrfjprog --ids

# Reset manual se necessário
nrfjprog -f nrf52 --recover
```

### DFU Programming Failed
```
⚠️ Automatic DFU failed. Please program manually and press Enter when done.
```
**→ Usar nRF Connect Desktop ou programar manualmente via DFU**

## 🔄 Processo Automatizado

O script `automated_analysis.py` executa automaticamente:

1. **🗑️ Erase completo** do dispositivo
2. **📡 Programa SoftDevice + App** (direto)
3. **📊 Captura dump** da memória (direto)
4. **🗑️ Erase completo** novamente
5. **🔧 Programa SoftDevice + Bootloader**
6. **📦 Cria pacote DFU** da aplicação
7. **🔄 Programa via DFU** (automático ou manual)
8. **📊 Captura dump** da memória (bootloader)
9. **🔍 Compara e analisa** diferenças
10. **📋 Gera relatório** completo

## 💡 Dicas

- **Execute como administrador** se houver problemas de acesso
- **Feche outros softwares** que possam usar o nRF52840
- **Use cabos USB curtos** e de qualidade
- **Aguarde os tempos** especificados entre operações
- **Leia o relatório completo** para entender todas as diferenças

## 🎯 Próximos Passos

Após executar a análise:

1. **Abra o relatório** de comparação
2. **Identifique diferenças críticas**
3. **Implemente correções** baseadas nas recomendações
4. **Execute novamente** para verificar se foi corrigido
5. **Compare com aplicação funcionando** se necessário

---

**🚀 Com estes scripts, você terá visibilidade completa do que acontece durante o boot e poderá identificar exatamente onde está o problema!**
