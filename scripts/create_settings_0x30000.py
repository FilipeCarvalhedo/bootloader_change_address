#!/usr/bin/env python3
"""
Script para criar bootloader settings no endereço correto (0x30000)
Como o nrfutil_6 sempre gera para 0xFF000, precisamos fazer manualmente.
"""

import struct
import sys
import subprocess
import tempfile
import os

def calculate_crc32(data):
    """Calcula CRC32 dos dados"""
    import zlib
    return zlib.crc32(data) & 0xFFFFFFFF

def create_bootloader_settings(app_hex_file, output_hex_file, settings_addr=0x30000):
    """
    Cria bootloader settings para o endereço especificado
    """
    
    # Primeiro, vamos gerar as settings normalmente para extrair os dados
    temp_settings = tempfile.mktemp(suffix='.hex')
    
    try:
        # Gerar settings com nrfutil_6 (vai para 0xFF000)
        cmd = [
            'nrfutil_6', 'settings', 'generate',
            '--family', 'NRF52840',
            '--application', app_hex_file,
            '--application-version', '1',
            '--bootloader-version', '1', 
            '--bl-settings-version', '2',
            temp_settings
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Erro ao gerar settings: {result.stderr}")
            return False
            
        # Ler o arquivo HEX gerado e extrair os dados
        settings_data = read_hex_data(temp_settings, 0xFF000)
        if not settings_data:
            print("Erro ao ler dados das settings")
            return False
            
        # Criar novo arquivo HEX com endereço correto
        write_hex_data(output_hex_file, settings_addr, settings_data)
        
        print(f"✅ Bootloader settings criadas para endereço 0x{settings_addr:X}")
        return True
        
    finally:
        if os.path.exists(temp_settings):
            os.remove(temp_settings)

def read_hex_data(hex_file, start_addr):
    """Lê dados de um arquivo HEX a partir do endereço especificado"""
    try:
        with open(hex_file, 'r') as f:
            lines = f.readlines()
            
        data = bytearray(4096)  # 4KB para settings
        
        for line in lines:
            line = line.strip()
            if not line.startswith(':'):
                continue
                
            # Parse Intel HEX format
            byte_count = int(line[1:3], 16)
            address = int(line[3:7], 16)
            record_type = int(line[7:9], 16)
            
            if record_type == 0:  # Data record
                # Verificar se está no range das settings
                if address >= (start_addr & 0xFFFF):
                    hex_data = line[9:9+byte_count*2]
                    offset = address - (start_addr & 0xFFFF)
                    
                    for i in range(0, len(hex_data), 2):
                        if offset < len(data):
                            data[offset] = int(hex_data[i:i+2], 16)
                            offset += 1
                            
        return bytes(data)
        
    except Exception as e:
        print(f"Erro ao ler HEX: {e}")
        return None

def write_hex_data(hex_file, start_addr, data):
    """Escreve dados em formato Intel HEX"""
    try:
        with open(hex_file, 'w') as f:
            # Escrever dados em chunks de 16 bytes
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                addr = start_addr + i
                
                # Formato Intel HEX
                line = f":{len(chunk):02X}{addr:04X}00"
                line += ''.join(f'{b:02X}' for b in chunk)
                
                # Calcular checksum
                checksum = (256 - (len(chunk) + (addr >> 8) + (addr & 0xFF) + 
                                  sum(chunk)) % 256) % 256
                line += f"{checksum:02X}"
                
                f.write(line + '\n')
                
            # End of file record
            f.write(":00000001FF\n")
            
    except Exception as e:
        print(f"Erro ao escrever HEX: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python create_settings_0x30000.py <app.hex> <settings.hex>")
        sys.exit(1)
        
    app_hex = sys.argv[1]
    settings_hex = sys.argv[2]
    
    if create_bootloader_settings(app_hex, settings_hex):
        print(f"Settings criadas em: {settings_hex}")
    else:
        print("Falha ao criar settings")
        sys.exit(1)
