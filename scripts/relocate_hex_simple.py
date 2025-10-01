#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

def relocate_hex_simple(input_file, output_file, from_addr, to_addr):
    """Relocacao simples de arquivo Intel HEX"""
    
    if not os.path.exists(input_file):
        print("Erro: " + input_file + " nao encontrado")
        return False
    
    try:
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Offset de relocacao
        offset = to_addr - from_addr
        
        # Substituir endereco base no Extended Linear Address record
        # :020000040FF0EB -> :02000004003003B (0xFF0 -> 0x030)
        old_ela = ":020000040FF0"
        new_ela = ":02000004003"
        
        if old_ela in content:
            # Calcular novo checksum para ELA
            # Checksum = 256 - (02 + 00 + 00 + 04 + 00 + 30) % 256
            checksum = (256 - (0x02 + 0x00 + 0x00 + 0x04 + 0x00 + 0x30) % 256) % 256
            new_ela_full = ":02000004003" + format(checksum, '01X')
            
            content = content.replace(":020000040FF0EB", new_ela_full)
            
            with open(output_file, 'w') as f:
                f.write(content)
            
            print("OK: Relocado de 0x" + format(from_addr, 'X') + " para 0x" + format(to_addr, 'X'))
            return True
        else:
            print("Erro: Formato de arquivo HEX nao reconhecido")
            return False
            
    except Exception as e:
        print("Erro: " + str(e))
        return False

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python relocate_hex_simple.py input.hex output.hex from_addr to_addr")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    from_addr = int(sys.argv[3], 16)
    to_addr = int(sys.argv[4], 16)
    
    if relocate_hex_simple(input_file, output_file, from_addr, to_addr):
        print("Relocacao concluida!")
    else:
        sys.exit(1)
