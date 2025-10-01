# Solução para o Problema do flash_program

## 🔍 Problema Identificado

O `nrfutil_6 settings generate` **não tem parâmetro para especificar o endereço** das bootloader settings. Ele usa o endereço **hardcoded padrão (0xFF000)** independente das nossas alterações no código.

## ⚠️ Limitação do nrfutil_6

O nrfutil_6 sempre gera bootloader settings para 0xFF000, mesmo que tenhamos alterado `BOOTLOADER_SETTINGS_ADDRESS` no código. Isso é uma limitação da ferramenta.

## 💡 Soluções Possíveis

### **Solução 1: Usar nrfutil mais recente**
```bash
# nrfutil mais recente tem --start-address
nrfutil settings generate \
    --family NRF52840 \
    --application app.hex \
    --application-version 1 \
    --bootloader-version 1 \
    --bl-settings-version 2 \
    --start-address 0x30000 \
    settings.hex
```

### **Solução 2: Modificar HEX após geração**
```bash
# 1. Gerar settings normalmente (para 0xFF000)
nrfutil_6 settings generate --family NRF52840 --application app.hex settings_temp.hex

# 2. Usar srec_cat para mover de 0xFF000 para 0x30000
srec_cat settings_temp.hex -intel -offset -0xCF000 -o settings.hex -intel
```

### **Solução 3: Flash manual (RECOMENDADA)**
```bash
# 1. Gerar settings
nrfutil_6 settings generate --family NRF52840 --application app.hex settings.hex

# 2. Flash aplicação
nrfjprog -f nrf52 --program app.hex --sectorerase --verify

# 3. Flash settings com offset correto
nrfjprog -f nrf52 --program settings.hex --sectorerase --verify --sectoranduicrerase
```

## 🎯 Implementação da Solução 3

Vou modificar o CMakeLists.txt para usar a abordagem mais robusta:
