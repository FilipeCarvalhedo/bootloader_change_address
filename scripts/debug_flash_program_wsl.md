# Debug: flash_program funcionou mas aplicação não inicia

## ✅ O que funcionou:

1. **nrfutil_6** gerou bootloader settings para 0xFF000
2. **sed** relocou settings para 0x30000  
3. **nrfjprog** gravou aplicação (40636 bytes) em 0x31000
4. **nrfjprog** gravou bootloader settings relocadas em 0x30000
5. **Reset** foi aplicado

## ❓ Possíveis problemas:

### **1. Checksum do sed pode estar errado**
O sed fez: `:020000040FF0EB` → `:02000004003B`

Vamos verificar se o checksum está correto:
- Para 0x30000: dados = `02 00 00 04 00 30`
- Checksum = `256 - (02 + 00 + 00 + 04 + 00 + 30) % 256 = 256 - 36 = 220 = 0xDC`
- Deveria ser: `:02000004003DC` (não `3B`)

### **2. Bootloader não encontra settings válidas**
Se o checksum estiver errado, bootloader ignora as settings.

### **3. Aplicação não está no endereço correto**
Verificar se aplicação foi realmente gravada em 0x31000.

## 🔧 Correção necessária:

Corrigir o comando sed:

```cmake
# ERRADO:
sed 's/:020000040FF0EB/:02000004003B/g'

# CORRETO:  
sed 's/:020000040FF0EB/:02000004003DC/g'
```

## 🧪 Como testar:

1. Corrigir checksum no CMakeLists.txt
2. Rebuild e flash novamente
3. Verificar se aplicação inicia

## 📊 Verificações adicionais:

No WSL, verificar:
```bash
# Settings em 0x30000
nrfjprog -f nrf52 --memrd 0x30000 --n 16

# Aplicação em 0x31000  
nrfjprog -f nrf52 --memrd 0x31000 --n 8

# Status do bootloader
nrfjprog -f nrf52 --memrd 0x27000 --n 8
```
