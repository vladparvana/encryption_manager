import subprocess
import os
import time
import psutil
from typing import Tuple, Optional
from database.models.frameworks import Frameworks
from database.models.fisiere import Fisiere
from database.models.chei import Chei

class EncryptionManager:
    def __init__(self, framework: Frameworks):
        self.framework = framework

    def _get_process_memory_usage(self, process: subprocess.Popen) -> float:
        """Get memory usage of a process in MB"""
        process_info = psutil.Process(process.pid)
        return process_info.memory_info().rss / 1024 / 1024  # Convert to MB

    def _run_command(self, command: str) -> Tuple[subprocess.Popen, float, float]:
        """Run a command and measure its execution time and memory usage"""
        start_time = time.time()
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        memory_usage = self._get_process_memory_usage(process)
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        if process.returncode != 0:
            raise Exception(f"Command failed: {stderr.decode()}")
            
        return process, end_time - start_time, memory_usage

    def encrypt_file(self, file: Fisiere, key: Chei) -> Tuple[float, float]:
        """Encrypt a file using the configured framework"""
        command = self.framework.comanda_criptare.format(
            input_file=file.locate_fisier,
            key_file=key.cheie,
            output_file=f"{file.locate_fisier}.enc"
        )
        
        _, execution_time, memory_usage = self._run_command(command)
        return execution_time, memory_usage

    def decrypt_file(self, file: Fisiere, key: Chei) -> Tuple[float, float]:
        """Decrypt a file using the configured framework"""
        command = self.framework.comanda_decriptare.format(
            input_file=file.locate_fisier,
            key_file=key.cheie,
            output_file=f"{file.locate_fisier}.dec"
        )
        
        _, execution_time, memory_usage = self._run_command(command)
        return execution_time, memory_usage 