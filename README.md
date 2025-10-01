# 🗺️ Flash Memory Mapper for NRF52840

Ferramenta Python para analisar e mapear o uso de memória flash em linker scripts do NRF52840, com detecção automática de conflitos com o bootloader.

## 🎯 Funcionalidades

- ✅ **Análise automática** do linker script NRF52840.ld
- ✅ **Mapeamento visual** de todas as seções de memória flash
- ✅ **Detecção de conflitos** com regiões críticas do bootloader (0xFE000-0x100000)
- ✅ **Relatório detalhado** com tabelas e estatísticas
- ✅ **Warnings automáticos** para regiões conflitantes
- ✅ **Recomendações** para resolver conflitos

## 🚨 Problema que Resolve

O bootloader do NRF52840 usa as regiões `0xFE000-0xFF000` e `0xFF000-0x100000` para seus próprios dados. Quando a aplicação coloca a `SHARED_DATA` nessas regiões, ocorre **corrupção de dados** que causa **reset loops** infinitos.

Este script detecta automaticamente esses conflitos e ajuda a resolvê-los.

## 📦 Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `flash_memory_mapper.py` | Script principal do mapeador de memória |
| `test_flash_mapper.py` | Script de teste para o linker atual |
| `README.md` | Esta documentação |

## 🚀 Como Usar

### Método 1: Teste Rápido (Recomendado)
```bash
python test_flash_mapper.py
```

### Método 2: Análise Manual
```bash
python flash_memory_mapper.py <caminho_para_linker_script> [arquivo_saida]
```

**Exemplo:**
```bash
python flash_memory_mapper.py "Z:\path\to\NRF52840.ld" flash_analysis.txt
```

## 📊 Exemplo de Saída

```
🗺️  NRF52840 FLASH MEMORY MAP
================================================================================
📁 Linker Script: NRF52840.ld
📅 Generated: 2025-01-27 15:30:45

📊 MEMORY LAYOUT:
--------------------------------------------------------------------------------
Section              Start        End          Size     Size (KB)
--------------------------------------------------------------------------------
MBR                  0x00000000   0x00001000   4096     4        
SoftDevice           0x00001000   0x00027000   155648   152      
LKBoot               0x00027000   0x0002F000   32768    32       
LKApp                0x0002F000   0x000CA000   634880   620      
MBS Console          0x000CA000   0x000CC000   8192     8        
Storage              0x000CC000   0x000EA000   122880   120      
Manufacture          0x000EA000   0x000EC000   8192     8        
FDS                  0x000EC000   0x000F5000   36864    36       
SHARED_DATA          0x000F5000   0x000F7000   8192     8        
PSB Reserved         0x000F7000   0x000FD000   24576    24       
CB Reserved          0x000FD000   0x000FF000   8192     8        
🆓 Free Space       0x000FF000   0x00100000   4096     4        
--------------------------------------------------------------------------------

✅ NO BOOTLOADER CONFLICTS DETECTED!

🎯 CRITICAL BOOTLOADER REGIONS:
--------------------------------------------------------------------------------
   0xFE000-0xFF000: Bootloader uses this region for its data
   0xFF000-0x100000: Bootloader uses this region for its data
```

## ⚠️ Interpretando Warnings

### 🚨 Conflito Detectado
```
🚨 BOOTLOADER CONFLICT: SHARED_DATA (0x000FE000-0x00100000) 
   overlaps with bootloader region 0xFE000-0x100000!
```

**Significado:** A SHARED_DATA está na região que o bootloader usa, causando corrupção.

### ✅ Sem Conflitos
```
✅ NO BOOTLOADER CONFLICTS DETECTED!
```

**Significado:** Sua configuração está segura e não deve causar reset loops.

## 🔧 Como Resolver Conflitos

### 1. **Mover SHARED_DATA para Região Segura**
```c
// No linker script, altere:
FLASH_SHARED_START = ( FLASH_FDS_START + FLASH_FDS_SIZE );
// Em vez de:
FLASH_SHARED_START = ( FLASH_RESERVED_CB_START + FLASH_RESERVED_CB_SIZE );
```

### 2. **Reduzir Tamanho da FDS**
```c
// Reduza FDS para liberar espaço:
FLASH_FDS_SIZE = 36K;  // Era 64K
```

### 3. **Garantir CB Reserved Termina Antes de 0xFE000**
```c
// Reduza CB Reserved se necessário:
FLASH_RESERVED_CB_SIZE = 4K;  // Era 12K
```

## 🎯 Códigos de Saída

| Código | Significado |
|--------|-------------|
| `0` | ✅ Sucesso - Sem conflitos |
| `1` | ❌ Erro - Problema na execução |
| `2` | 🚨 Conflitos detectados |

## 📝 Arquivos Gerados

- **`flash_memory_map.txt`**: Relatório detalhado da análise
- **`nrf52840_flash_memory_analysis.txt`**: Análise específica (quando usando test script)

## 🛠️ Requisitos

- Python 3.6+
- Acesso ao arquivo linker script NRF52840.ld

## 💡 Dicas de Uso

1. **Execute sempre** após alterar o linker script
2. **Verifique warnings** antes de compilar
3. **Use em CI/CD** para detectar conflitos automaticamente
4. **Salve relatórios** para documentação

## 🎉 Casos de Uso

- ✅ **Debugar reset loops** causados por conflitos de memória
- ✅ **Validar configurações** de linker script
- ✅ **Otimizar uso** de memória flash
- ✅ **Documentar layout** de memória do projeto
- ✅ **Detectar problemas** antes da compilação

---

**🚀 Execute `python test_flash_mapper.py` para testar sua configuração atual!**



