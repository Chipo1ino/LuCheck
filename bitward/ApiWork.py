import subprocess
import json
import os
import time
import shlex
from bitward.config_items import MAIN_URL

class BitWardCl:
    def __init__(self, server_url=MAIN_URL):
        self.server_url = server_url
        self.session = None
        
    def setup(self):
        try:
            result = subprocess.run(
                f'bw config server {self.server_url}', 
                shell=True, 
                capture_output=True, 
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return True
        except Exception as e:
            return False
    
    def unlock(self, master_password: str) -> bool:
        try:
            result = subprocess.run(
                f'bw unlock "{master_password}" --raw',
                shell=True, 
                capture_output=True, 
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0 and result.stdout:
                self.session = result.stdout.strip()
                return True
            return False
        except Exception as e:
            return False
    
    def sync(self):
        if not self.session:
            return False
            
        try:
            result = subprocess.run(
                f'bw sync --session {self.session}',
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0
        except Exception as e:
            return False
    
    def get_status(self):
        try:
            result = subprocess.run(
                'bw status',
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"raw": result.stdout}
            return None
        except Exception as e:
            return None
    
    def create_login(self, username: str, password: str, name="PasswdArc"):
        item = {
            "type": 1,
            "name": name,
            "login": {
                "username": username,
                "password": password
            }
        }
        
        json_str = json.dumps(item, ensure_ascii=False)
        try:
            encode_process = subprocess.Popen(
                ['bw', 'encode'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            encoded, encode_err = encode_process.communicate(input=json_str)
            
            if encode_process.returncode != 0:
                return {"error": f"Encode failed: {encode_err}"}
            cmd = ['bw', 'create', 'item', '--session', self.session]
            create_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            output, error = create_process.communicate(input=encoded.strip())
            
            if create_process.returncode == 0:
                self.sync()
                
                if output:
                    try:
                        return json.loads(output)
                    except json.JSONDecodeError:
                        return {"success": True, "name": name, "message": output[:100]}
                else:
                    return {"success": True, "name": name}
            else:
                return {"error": error}
                
        except Exception as e:
            return {"error": str(e)}
    
    def list_items(self, search: str = None):
        if not self.session:
            return []
        
        cmd = ['bw', 'list', 'items', '--session', self.session]
        if search:
            cmd.extend(['--search', search])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return []
            return []
        except Exception as e:
            return []