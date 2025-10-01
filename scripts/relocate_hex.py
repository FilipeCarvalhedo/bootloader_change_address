#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para relocar arquivo Intel HEX de um endereco para outro
Usado para mover bootloader settings de 0xFF000 para 0x30000
"""

import sys
import os

def parse_intel_hex_line(line):
    """Parse uma linha Intel HEX"""
    if not line.startswith(':'):
        return None
    
    try:
        byte_count = int(line[1:3], 16)
        address = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
        data = line[9:9+byte_count*2]
        checksum = int(line[9+byte_count*2:11+byte_count*2], 16)
        
        return {
            'byte_count': byte_count,
            'address': address,
            'record_type': record_type,
            'data': data,
            'checksum': checksum
        }
    except:
        return None

def calculate_checksum(byte_count, address, record_type, data_bytes):
    """Calcula checksum Intel HEX"""
    checksum = byte_count + (address >> 8) + (address & 0xFF) + record_type
    for i in range(0, len(data_bytes), 2):
        checksum += int(data_bytes[i:i+2], 16)
    return (256 - (checksum % 256)) % 256

def relocate_hex(input_file, output_file, from_addr, to_addr):
    """Reloca arquivo HEX de um endereco para outro"""
    
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo {input_file} nao encontrado")
        return False
    
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        relocated_lines = []
        extended_addr = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            parsed = parse_intel_hex_line(line)
            if not parsed:
                relocated_lines.append(line)
                continue
            
            if parsed['record_type'] == 4:  # Extended Linear Address
                extended_addr = int(parsed['data'], 16) << 16
                relocated_lines.append(line)
                continue
            elif parsed['record_type'] == 0:  # Data record
                full_addr = extended_addr + parsed['address']
                
                # Verificar se esta no range que queremos relocar
                if full_addr >= from_addr and full_addr < from_addr + 0x1000:  # 4KB page
                    # Calcular novo endereco
                    offset = full_addr - from_addr
                    new_full_addr = to_addr + offset
                    
                    # Verificar se precisa de novo Extended Linear Address
                    new_extended_addr = new_full_addr >> 16
                    new_address = new_full_addr & 0xFFFF
                    
                    if new_extended_addr != (extended_addr >> 16):
                        # Adicionar novo Extended Linear Address
                        ela_data = f"{new_extended_addr:04X}"
                        ela_checksum = calculate_checksum(2, 0, 4, ela_data)
                        relocated_lines.append(f":02000004{ela_data}{ela_checksum:02X}")
                        extended_addr = new_extended_addr << 16
                    
                    # Criar nova linha de dados
                    new_checksum = calculate_checksum(
                        parsed['byte_count'], 
                        new_address, 
                        parsed['record_type'], 
                        parsed['data']
                    )
                    
                    new_line = f":{parsed['byte_count']:02X}{new_address:04X}{parsed['record_type']:02X}{parsed['data']}{new_checksum:02X}"
                    relocated_lines.append(new_line)
                else:
                    # Linha nao precisa ser relocada
                    relocated_lines.append(line)
            else:
                # Outros tipos de record
                relocated_lines.append(line)
        
        # Escrever arquivo relocado
        with open(output_file, 'w') as f:
            for line in relocated_lines:
                f.write(line + '\n')
        
        print(f"OK Arquivo relocado de 0x{from_addr:X} para 0x{to_addr:X}")
        print(f"   Input:  {input_file}")
        print(f"   Output: {output_file}")
        return True
        
    except Exception as e:
        print(f"Erro ao relocar arquivo: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python relocate_hex.py <input.hex> <output.hex> <from_addr> <to_addr>")
        print("Exemplo: python relocate_hex.py settings_ff000.hex settings_30000.hex 0xFF000 0x30000")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    from_addr = int(sys.argv[3], 16)
    to_addr = int(sys.argv[4], 16)
    
    if relocate_hex(input_file, output_file, from_addr, to_addr):
        print("Relocacao concluida com sucesso!")
    else:
        print("Falha na relocacao!")
        sys.exit(1)
