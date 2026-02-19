"""
core/ip_utils.py - Utilitário para capturar IP real do usuário
"""

import streamlit as st
import re
from typing import Optional


class IPUtils:
    """Utilitário para capturar e processar IP do usuário"""
    
    @staticmethod
    def get_client_ip() -> str:
        """
        Captura o IP real do cliente considerando proxies e headers
        Retorna o IP ou '127.0.0.1' como fallback
        """
        try:
            # Tentar obter dos headers do Streamlit
            headers = st.context.headers if hasattr(st, 'context') else {}
            
            # Lista de headers que podem conter o IP real (em ordem de prioridade)
            ip_headers = [
                'x-forwarded-for',
                'x-real-ip',
                'x-client-ip',
                'cf-connecting-ip',  # Cloudflare
                'true-client-ip',
                'x-cluster-client-ip',
                'forwarded-for',
                'forwarded',
                'x-original-forwarded-for'
            ]
            
            # Verificar cada header
            for header in ip_headers:
                if header in headers:
                    ip_value = headers[header]
                    if ip_value:
                        # X-Forwarded-For pode conter múltiplos IPs (cliente, proxy1, proxy2)
                        if header == 'x-forwarded-for':
                            # Pega o primeiro IP da lista (cliente original)
                            ip = ip_value.split(',')[0].strip()
                        else:
                            ip = ip_value.strip()
                        
                        # Validar se é um IP válido
                        if IPUtils._is_valid_ip(ip):
                            return ip
            
            # Fallback para ambiente local/desenvolvimento
            return "127.0.0.1"
            
        except Exception as e:
            # Em caso de erro, retornar IP local
            return "127.0.0.1"
    
    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """Valida se a string é um IP válido (IPv4 ou IPv6)"""
        if not ip or ip == '':
            return False
        
        # Remover portas se houver (ex: 192.168.1.1:8080)
        if ':' in ip and ip.count(':') == 1:  # IPv4 com porta
            ip = ip.split(':')[0]
        
        # Padrão para IPv4
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, ip):
            # Validar se cada octeto está entre 0-255
            octetos = ip.split('.')
            for octeto in octetos:
                if int(octeto) < 0 or int(octeto) > 255:
                    return False
            return True
        
        # Padrão simples para IPv6 (validação básica)
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::|^[0-9a-fA-F]{1,4}::'
        if re.match(ipv6_pattern, ip, re.IGNORECASE):
            return True
        
        return False
    
    @staticmethod
    def get_ip_location(ip: str) -> str:
        """
        Retorna localização aproximada do IP (opcional)
        Usa API gratuita ipapi.co
        """
        if ip == "127.0.0.1" or ip.startswith("192.168.") or ip.startswith("10."):
            return "Rede Local"
        
        # Opcional: integrar com API de geolocalização
        # import requests
        # try:
        #     response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        #     if response.status_code == 200:
        #         data = response.json()
        #         if data['status'] == 'success':
        #             return f"{data['city']}, {data['regionName']} - {data['country']}"
        # except:
        #     pass
        
        return "Localização não disponível"
    
    @staticmethod
    def mask_ip(ip: str) -> str:
        """
        Mascara o IP para exibição segura (ex: 192.168.xxx.xxx)
        """
        if not ip or ip == "127.0.0.1":
            return ip
        
        if '.' in ip:  # IPv4
            parts = ip.split('.')
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.xxx.xxx"
        
        # IPv6 - mostrar apenas os primeiros segmentos
        if ':' in ip:
            parts = ip.split(':')
            if len(parts) >= 4:
                return f"{parts[0]}:{parts[1]}:xxxx:xxxx"
        
        return "IP mascarado"
