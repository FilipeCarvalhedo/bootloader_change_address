# 🔧 TESTE DA CORREÇÃO DE STACK CORRUPTION

## 📋 RESUMO DA IMPLEMENTAÇÃO

### ✅ **O QUE FOI IMPLEMENTADO:**

1. **Detecção de Corrupção** no início de `sysCtlInitialize()`:
   - ✅ **R8 = 0x00027000**: Detecta se R8 contém endereço do bootloader
   - ✅ **initType inválido**: Verifica se parâmetro está corrompido (> 2)
   - ✅ **Stack scan**: Procura por endereços do bootloader (0x00027000) no stack

2. **Correção Automática**:
   - ✅ **initType**: Força `SYSTEM_CONTROL_PRE_RTOS` se corrompido
   - ✅ **Stack cleanup**: Remove endereços 0x00027000 e 0x000fe000 do stack
   - ✅ **Register cleanup**: Força R8=initType, R5=0, R9=0 via assembly

3. **Logging Detalhado**:
   - ✅ **Debug output**: Mostra detecção e correção em tempo real
   - ✅ **Estado antes/depois**: Permite verificar se correção funcionou

---

## 🧪 PROCEDIMENTO DE TESTE

### **1. 📦 COMPILAR A APLICAÇÃO**
```bash
# No projeto lkrelay:
cd Z:\home\filipe\Projetos\loop\loopkey-nrf51\projects\lkrelay
make clean
make paramount_static_lib  # Recompila app-athos com correção
make DEV_PARAMOUNT_BARNETT-BOARD_PARAMOUNT_BARNETT-0820-DEBUG
```

### **2. 🔥 FLASH COM BOOTLOADER**
```bash
# Flash bootloader + aplicação:
make flash_bootloader
make package_dfu
make flash_dfu_package
```

### **3. 📊 VERIFICAR LOGS**
```bash
# Conectar ao log USB/RTT e procurar por:
# "STACK CORRUPTION: R8 contains bootloader address 0x00027000"
# "=== APPLYING STACK CORRUPTION CORRECTION ==="
# "CORRECTED: initType forced to SYSTEM_CONTROL_PRE_RTOS"
# "CORRECTED: Cleared bootloader addr from SP[X]"
# "CORRECTED: Registers R5, R8, R9 cleaned"
# "=== STACK CORRUPTION CORRECTION COMPLETE ==="
```

### **4. 🎯 TESTE COM GDB**
```bash
# Parar no mesmo ponto e comparar:
(gdb) break sysCtlInitialize
(gdb) continue
(gdb) source capture_vectors.gdb

# Verificar se agora:
# - R5, R8, R9 estão corretos
# - Stack não contém 0x00027000
# - initType é válido
```

---

## 📈 RESULTADOS ESPERADOS

### **🟢 SUCESSO - Se a correção funcionar:**
```
STACK CORRUPTION: R8 contains bootloader address 0x00027000
=== APPLYING STACK CORRUPTION CORRECTION ===
CORRECTED: initType forced to SYSTEM_CONTROL_PRE_RTOS
CORRECTED: Cleared bootloader addr from SP[12]
CORRECTED: Registers R5, R8, R9 cleaned
=== STACK CORRUPTION CORRECTION COMPLETE ===
```

**E depois:**
- ✅ Aplicação **NÃO entra em reset loop**
- ✅ **dispatchEvent()** executa sem HardFault
- ✅ **rccMainVostio** é chamado e executa **linha 83**
- ✅ **nrf_sdh_freertos_init()** executa com sucesso

### **🔴 FALHA - Se ainda houver problemas:**
```
STACK CHECK: No corruption detected (R8=0x00027000, initType=134520896)
```

**Indica que:**
- ❌ Detecção não funcionou (parâmetros ainda corrompidos)
- ❌ Correção precisa ser ajustada
- ❌ Problema é mais profundo (antes de sysCtlInitialize)

---

## 🔧 TROUBLESHOOTING

### **Se a detecção não funcionar:**
1. **Verificar se mbsLogDebug está habilitado**
2. **Adicionar prints antes da detecção**
3. **Verificar se R8 realmente contém 0x00027000**

### **Se a correção não funcionar:**
1. **Problema pode estar antes de sysCtlInitialize**
2. **Stack pode estar mais corrompido**
3. **Registradores podem ser restaurados após correção**

### **Se ainda houver HardFault:**
1. **Capturar endereço exato do HardFault**
2. **Verificar se é em dispatchEvent ou outra função**
3. **Pode precisar corrigir em ponto anterior**

---

## 🎯 PRÓXIMOS PASSOS

### **Se FUNCIONAR:**
1. ✅ **Confirmar que resolve o problema**
2. ✅ **Testar em diferentes cenários**
3. ✅ **Implementar correção similar no bootloader**
4. ✅ **Documentar solução final**

### **Se NÃO FUNCIONAR:**
1. ❌ **Mover correção para ponto anterior** (systemControlStart)
2. ❌ **Investigar corrupção mais profunda**
3. ❌ **Implementar correção no bootloader diretamente**

---

## 📝 NOTAS IMPORTANTES

- **Esta é uma correção defensiva** - detecta e corrige problema existente
- **Ideal seria bootloader não causar corrupção** - mas isso é mais complexo
- **Solução temporária** até que bootloader seja corrigido adequadamente
- **Logs são cruciais** para confirmar que correção está funcionando

**🚀 EXECUTE O TESTE E REPORTE OS RESULTADOS!**



