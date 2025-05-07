import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from database.encryption import EncryptionManager
from database.models.frameworks import Frameworks
from database.models.fisiere import Fisiere
from database.models.chei import Chei
from database.models.performante import Performante
from database.models.algoritmi import Algoritmi
from database.enums import TipFramework, StatusFisier, TipAlgoritm, TipCheie
from database import SessionLocal
import uuid
from datetime import datetime, timedelta
import os
import subprocess
import time
from tkcalendar import DateEntry
import hashlib
from sqlalchemy.orm import Session
from database.operations import FisierAlgorithmCheie

class KeyGenerationDialog:
    def __init__(self, parent, algo_name, algo_type):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Generate {algo_name} Key")
        self.dialog.geometry("400x200")  # Reduced height since we removed key type selection
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.result = None
        self.algo_name = algo_name
        self.algo_type = algo_type
        
        # Key name
        name_frame = ttk.Frame(self.dialog)
        name_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(name_frame, text="Key Name:").pack(side='left')
        self.key_name = ttk.Entry(name_frame)
        self.key_name.pack(side='left', fill='x', expand=True)
        
        # Expiration date
        exp_frame = ttk.Frame(self.dialog)
        exp_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(exp_frame, text="Expiration Date:").pack(side='left')
        self.exp_date = DateEntry(exp_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2)
        self.exp_date.pack(side='left')
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Generate", command=self.generate).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side='left', padx=5)
        
        self.dialog.wait_window()
    
    def generate(self):
        self.result = {
            'name': self.key_name.get(),
            'expiration': self.exp_date.get_date()
        }
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

class NewOperationDialog:
    def __init__(self, parent, algorithms):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("New Operation")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.result = None
        self.algorithms = algorithms
        
        # File selection
        file_frame = ttk.LabelFrame(self.dialog, text="File Selection")
        file_frame.pack(fill='x', padx=5, pady=5)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).pack(side='left', padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side='left', padx=5)
        
        # Algorithm selection
        algo_frame = ttk.LabelFrame(self.dialog, text="Algorithm")
        algo_frame.pack(fill='x', padx=5, pady=5)
        
        self.selected_algo = tk.StringVar()
        self.algo_combo = ttk.Combobox(algo_frame, textvariable=self.selected_algo)
        self.algo_combo['values'] = list(algorithms.keys())
        self.algo_combo.pack(fill='x', padx=5, pady=5)
        self.algo_combo.bind('<<ComboboxSelected>>', self.on_algorithm_select)
        
        # Key selection
        key_frame = ttk.LabelFrame(self.dialog, text="Key")
        key_frame.pack(fill='x', padx=5, pady=5)
        
        self.selected_key = tk.StringVar()
        self.key_combo = ttk.Combobox(key_frame, textvariable=self.selected_key)
        self.key_combo.pack(fill='x', padx=5, pady=5)
        
        # Operation type
        op_frame = ttk.LabelFrame(self.dialog, text="Operation")
        op_frame.pack(fill='x', padx=5, pady=5)
        
        self.operation_type = tk.StringVar(value="encrypt")
        ttk.Radiobutton(op_frame, text="Encrypt", variable=self.operation_type, 
                       value="encrypt", command=self.on_operation_change).pack(side='left', padx=5)
        ttk.Radiobutton(op_frame, text="Decrypt", variable=self.operation_type, 
                       value="decrypt", command=self.on_operation_change).pack(side='left', padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Execute", command=self.execute).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side='left', padx=5)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            print(f"Selected input file: {filename}")
            self.file_path.set(filename)
    
    def on_algorithm_select(self, event):
        algo_name = self.selected_algo.get()
        print(f"Selected algorithm: {algo_name}")
        self.update_keys_list(algo_name)
    
    def on_operation_change(self):
        print(f"Operation type changed to: {self.operation_type.get()}")
        if self.selected_algo.get():
            self.update_keys_list(self.selected_algo.get())
    
    def update_keys_list(self, algo_name):
        print(f"Updating keys list for algorithm: {algo_name}")
        self.key_combo['values'] = []  # Clear existing values
        
        # Get algorithm from database
        db = SessionLocal()
        try:
            algo = db.query(Algoritmi).filter(Algoritmi.nume_algoritm == algo_name).first()
            if not algo:
                print(f"Algorithm {algo_name} not found in database")
                return
            
            # Get keys from database
            keys = db.query(Chei).filter(Chei.id_algoritm == algo.id_algoritm).all()
            
            # Show all keys for RSA, not just public/private based on operation
            available_keys = []
            for key in keys:
                available_keys.append(key.nume)
                print(f"Added key: {key.nume} (Type: {key.tip_cheie})")
            
            self.key_combo['values'] = available_keys
            print(f"Available keys: {self.key_combo['values']}")
        finally:
            db.close()

    def execute(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a file")
            return
        
        if not self.selected_algo.get():
            messagebox.showerror("Error", "Please select an algorithm")
            return
        
        if not self.selected_key.get():
            messagebox.showerror("Error", "Please select a key")
            return
        
        # Get output path
        operation = "Encrypt" if self.operation_type.get() == "encrypt" else "Decrypt"
        print(f"\nRequesting output path for {operation} operation")
        output_path = filedialog.asksaveasfilename(
            defaultextension=".enc" if operation == "Encrypt" else ".dec",
            initialfile=f"{os.path.basename(self.file_path.get())}.{'enc' if operation == 'Encrypt' else 'dec'}"
        )
        
        if not output_path:
            print("No output path selected, operation cancelled")
            return
        
        print(f"Selected output path: {output_path}")
        
        self.result = {
            'file_path': self.file_path.get(),
            'algorithm': self.selected_algo.get(),
            'key': self.selected_key.get(),
            'operation': operation,
            'output_path': output_path
        }
        print(f"Dialog result set: {self.result}")
        self.dialog.destroy()
    
    def cancel(self):
        print("Operation cancelled")
        self.dialog.destroy()

class PerformanceDetailsDialog:
    def __init__(self, parent, performance_data):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Performance Details")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create details view
        details_frame = ttk.Frame(self.dialog)
        details_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add performance details
        ttk.Label(details_frame, text=f"Algorithm: {performance_data['algorithm']}").pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Framework: {performance_data['framework']}").pack(anchor='w', pady=2)
        encrypt_time = performance_data['encrypt_time']
        decrypt_time = performance_data['decrypt_time']
        ttk.Label(details_frame, text=f"Encryption Time: {encrypt_time:.2f}s" if encrypt_time is not None else "Encryption Time: -").pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Decryption Time: {decrypt_time:.2f}s" if decrypt_time is not None else "Decryption Time: -").pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Memory Usage: {performance_data['memory']:.2f}MB").pack(anchor='w', pady=2)
        ttk.Label(details_frame, text=f"Test Date: {performance_data['date']}").pack(anchor='w', pady=2)
        
        # Close button
        ttk.Button(details_frame, text="Close", command=self.dialog.destroy).pack(pady=10)

class EncryptionManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Encryption Manager")
        self.root.geometry("1000x700")
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.algorithms_tab = ttk.Frame(self.notebook)
        self.files_tab = ttk.Frame(self.notebook)
        self.frameworks_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.algorithms_tab, text='Algorithms & Keys')
        self.notebook.add(self.files_tab, text='Files')
        self.notebook.add(self.frameworks_tab, text='Frameworks')
        
        self.setup_algorithms_tab()
        self.setup_files_tab()
        self.setup_frameworks_tab()
        
        # Initialize algorithms
        self.init_algorithms()
        # Refresh files list at startup
        self.refresh_files_list()

    def init_algorithms(self):
        # Predefined algorithms
        self.algorithms = {
            "AES": {
                "type": TipAlgoritm.SIMETRIC,
                "key_generation": "openssl rand -hex 32",
                "encrypt_cmd": "openssl enc -aes-256-cbc -pbkdf2 -salt -in \"{input}\" -out \"{output}\" -pass pass:{key}",
                "decrypt_cmd": "openssl enc -aes-256-cbc -d -pbkdf2 -salt -in \"{input}\" -out \"{output}\" -pass pass:{key}"
            },
            "RSA": {
                "type": TipAlgoritm.ASIMETRIC,
                "key_generation": "openssl genrsa -out {private} 2048 && openssl rsa -in {private} -pubout -out {public}",
                "encrypt_cmd": "openssl pkeyutl -encrypt -pubin -inkey {key} -in {input} -out {output}",
                "decrypt_cmd": "openssl pkeyutl -decrypt -inkey {key} -in {input} -out {output}"
            }
        }
        
        # Initialize algorithms in database
        print("\nInitializing algorithms in database...")
        db = SessionLocal()
        try:
            for algo_name, algo_info in self.algorithms.items():
                algo = db.query(Algoritmi).filter(Algoritmi.nume_algoritm == algo_name).first()
                if not algo:
                    print(f"Creating algorithm {algo_name} in database...")
                    algo = Algoritmi(
                        id_algoritm=str(uuid.uuid4()),
                        nume_algoritm=algo_name,
                        tip_algoritm=algo_info['type']
                    )
                    db.add(algo)
                    db.commit()
                    print(f"Algorithm {algo_name} created with ID: {algo.id_algoritm}")
        finally:
            db.close()
        
        self.update_algorithms_list()

    def setup_algorithms_tab(self):
        # Left side - Algorithms list
        algo_frame = ttk.LabelFrame(self.algorithms_tab, text="Algorithms")
        algo_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        self.algo_tree = ttk.Treeview(algo_frame, columns=('Name', 'Type'), show='headings')
        self.algo_tree.heading('Name', text='Algorithm')
        self.algo_tree.heading('Type', text='Type')
        self.algo_tree.pack(fill='both', expand=True)
        
        # Right side - Keys for selected algorithm
        keys_frame = ttk.LabelFrame(self.algorithms_tab, text="Keys")
        keys_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Key generation controls
        gen_frame = ttk.Frame(keys_frame)
        gen_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(gen_frame, text="Generate New Key", command=self.generate_key).pack(side='left', padx=5)
        
        # Keys list
        self.keys_tree = ttk.Treeview(keys_frame, 
                                    columns=('ID', 'Type', 'Created', 'Path'),
                                    show='headings')
        self.keys_tree.heading('ID', text='ID')
        self.keys_tree.heading('Type', text='Type')
        self.keys_tree.heading('Created', text='Created')
        self.keys_tree.heading('Path', text='Path')
        self.keys_tree.pack(fill='both', expand=True)
        
        # Bind selection event
        self.algo_tree.bind('<<TreeviewSelect>>', self.on_algorithm_select)

    def setup_files_tab(self):
        # Operation button
        btn_frame = ttk.Frame(self.files_tab)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="New Operation", command=self.new_operation).pack(side='left', padx=5)
        
        # Files list
        list_frame = ttk.LabelFrame(self.files_tab, text="Files")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.files_tree = ttk.Treeview(list_frame, 
                                     columns=('Name', 'Algorithm', 'Status', 'Size', 'Hash', 'Performance', 'Output Path', 'PerformanceID', 'FileID'),
                                     show='headings')
        self.files_tree.heading('Name', text='File Name')
        self.files_tree.heading('Algorithm', text='Algorithm')
        self.files_tree.heading('Status', text='Status')
        self.files_tree.heading('Size', text='Size')
        self.files_tree.heading('Hash', text='Hash')
        self.files_tree.heading('Performance', text='Performance')
        self.files_tree.heading('Output Path', text='Output Path')
        self.files_tree.heading('PerformanceID', text='PerformanceID')
        self.files_tree.heading('FileID', text='FileID')
        self.files_tree.column('PerformanceID', width=0, stretch=False)  # Hide this column
        self.files_tree.column('FileID', width=0, stretch=False)  # Hide this column
        self.files_tree.pack(fill='both', expand=True)
        
        # Bind double-click event for performance details
        self.files_tree.bind('<Double-1>', self.show_performance_details)

    def setup_frameworks_tab(self):
        # Left: Frameworks list
        left_frame = ttk.Frame(self.frameworks_tab)
        left_frame.pack(side='left', fill='y', padx=5, pady=5)
        ttk.Label(left_frame, text="Frameworks").pack(anchor='w')
        self.frameworks_tree = ttk.Treeview(left_frame, columns=('Name', 'Type', 'Version'), show='headings', height=15)
        self.frameworks_tree.heading('Name', text='Name')
        self.frameworks_tree.heading('Type', text='Type')
        self.frameworks_tree.heading('Version', text='Version')
        self.frameworks_tree.pack(fill='y', expand=True)
        self.frameworks_tree.bind('<<TreeviewSelect>>', self.on_framework_select)

        # Right: Algorithms for selected framework
        right_frame = ttk.Frame(self.frameworks_tab)
        right_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        ttk.Label(right_frame, text="Algorithms implemented").pack(anchor='w')
        self.framework_algos_tree = ttk.Treeview(right_frame, columns=('Name', 'Type', 'Encrypt Cmd', 'Decrypt Cmd'), show='headings', height=15)
        self.framework_algos_tree.heading('Name', text='Algorithm')
        self.framework_algos_tree.heading('Type', text='Type')
        self.framework_algos_tree.heading('Encrypt Cmd', text='Encrypt Cmd')
        self.framework_algos_tree.heading('Decrypt Cmd', text='Decrypt Cmd')
        self.framework_algos_tree.pack(fill='both', expand=True)

        self.refresh_frameworks_list()

    def update_algorithms_list(self):
        for algo_name, algo_info in self.algorithms.items():
            self.algo_tree.insert('', 'end', values=(algo_name, algo_info['type'].value))

    def on_algorithm_select(self, event):
        selection = self.algo_tree.selection()
        if selection:
            algo_name = self.algo_tree.item(selection[0])['values'][0]
            self.update_keys_list(algo_name)
            
            # Update key combo in NewOperationDialog if it exists
            if hasattr(self, 'operation_dialog') and self.operation_dialog:
                self.operation_dialog.update_keys_list(algo_name)

    def update_keys_list(self, algo_name):
        # Clear existing keys
        for item in self.keys_tree.get_children():
            self.keys_tree.delete(item)
        
        # Get algorithm from database
        db = SessionLocal()
        try:
            algo = db.query(Algoritmi).filter(Algoritmi.nume_algoritm == algo_name).first()
            if not algo:
                print(f"Algorithm {algo_name} not found in database")
                return
            
            # Get keys from database
            keys = db.query(Chei).filter(Chei.id_algoritm == algo.id_algoritm).all()
            
            for key in keys:
                # Determine key type based on algorithm and key type
                if algo_name == "RSA":
                    key_type = "Private" if key.tip_cheie == TipCheie.PRIVATA else "Public"
                else:  # AES
                    key_type = "Secret"
                
                # Add key to tree view
                self.keys_tree.insert('', 'end', values=(
                    key.nume,
                    key_type,
                    key.data_creare.strftime("%Y-%m-%d %H:%M:%S"),
                    f"DB ID: {key.id_cheie}"
                ))
        finally:
            db.close()

    def generate_key(self):
        selection = self.algo_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an algorithm")
            return
            
        algo_name = self.algo_tree.item(selection[0])['values'][0]
        algo_info = self.algorithms[algo_name]
        
        # Show key generation dialog
        dialog = KeyGenerationDialog(self.root, algo_name, algo_info['type'])
        if not dialog.result:
            return
            
        try:
            print(f"\nGenerating key for algorithm: {algo_name}")
            
            # Get algorithm from database
            db = SessionLocal()
            try:
                algo = db.query(Algoritmi).filter(Algoritmi.nume_algoritm == algo_name).first()
                if not algo:
                    raise Exception(f"Algorithm {algo_name} not found in database")
                
                if algo_info['type'] == TipAlgoritm.SIMETRIC:
                    # Generate symmetric key
                    print(f"Running command: {algo_info['key_generation']}")
                    process = subprocess.run(
                        algo_info['key_generation'],
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if process.returncode == 0:
                        # Get the generated key
                        key_value = process.stdout.strip()
                        print(f"Generated symmetric key")
                        
                        # Save key to database
                        print("Saving key to database...")
                        key = Chei(
                            id_cheie=str(uuid.uuid4()),
                            id_algoritm=algo.id_algoritm,
                            nume=dialog.result['name'],
                            cheie=key_value.encode(),
                            data_creare=datetime.now(),
                            expirare=dialog.result['expiration'],
                            tip_cheie=TipCheie.SECRETA
                        )
                        db.add(key)
                        db.commit()
                        print(f"Key saved to database with ID: {key.id_cheie}")
                        
                        self.update_keys_list(algo_name)
                    else:
                        raise Exception(f"Key generation failed: {process.stderr}")
                        
                else:  # Asymmetric
                    # Generate temporary files for key pair
                    temp_dir = "temp_keys"
                    os.makedirs(temp_dir, exist_ok=True)
                    private_path = os.path.join(temp_dir, f"private_{uuid.uuid4()}.pem")
                    public_path = os.path.join(temp_dir, f"public_{uuid.uuid4()}.pem")
                    
                    cmd = algo_info['key_generation'].format(
                        private=private_path,
                        public=public_path
                    )
                    
                    print(f"Running command: {cmd}")
                    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if process.returncode == 0:
                        print("Generated key pair")
                        
                        try:
                            # Read key contents
                            with open(private_path, 'rb') as f:
                                private_key_content = f.read()
                            with open(public_path, 'rb') as f:
                                public_key_content = f.read()
                            
                            # Save keys to database
                            print("Saving keys to database...")
                            
                            # Save private key
                            private_key = Chei(
                                id_cheie=str(uuid.uuid4()),
                                id_algoritm=algo.id_algoritm,
                                nume=f"{dialog.result['name']}_private",
                                cheie=private_key_content,
                                data_creare=datetime.now(),
                                expirare=dialog.result['expiration'],
                                tip_cheie=TipCheie.PRIVATA
                            )
                            db.add(private_key)
                            
                            # Save public key
                            public_key = Chei(
                                id_cheie=str(uuid.uuid4()),
                                id_algoritm=algo.id_algoritm,
                                nume=f"{dialog.result['name']}_public",
                                cheie=public_key_content,
                                data_creare=datetime.now(),
                                expirare=dialog.result['expiration'],
                                tip_cheie=TipCheie.PUBLICA
                            )
                            db.add(public_key)
                            db.commit()
                            
                            print(f"Private key saved to database with ID: {private_key.id_cheie}")
                            print(f"Public key saved to database with ID: {public_key.id_cheie}")
                            
                            self.update_keys_list(algo_name)
                        finally:
                            # Clean up temporary files
                            try:
                                os.remove(private_path)
                                os.remove(public_path)
                                os.rmdir(temp_dir)
                            except:
                                pass
                    else:
                        raise Exception(f"Key generation failed: {process.stderr}")
            finally:
                db.close()
                    
        except Exception as e:
            print(f"Error generating key: {str(e)}")
            messagebox.showerror("Error", str(e))

    def calculate_file_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def new_operation(self):
        print("\n=== Starting new operation ===")
        dialog = NewOperationDialog(self.root, self.algorithms)
        if not dialog.result:
            print("Dialog cancelled")
            return
        
        try:
            result = dialog.result
            print(f"\nStarting new operation:")
            print(f"File: {result['file_path']}")
            print(f"Algorithm: {result['algorithm']}")
            print(f"Operation: {result['operation']}")
            print(f"Key: {result['key']}")
            
            algo_info = self.algorithms[result['algorithm']]
            print(f"Algorithm info: {algo_info}")
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(result['output_path'])
            if output_dir and not os.path.exists(output_dir):
                print(f"Creating output directory: {output_dir}")
                os.makedirs(output_dir)
            
            # Get the key from database
            print("\nRetrieving key from database...")
            db = SessionLocal()
            try:
                key = db.query(Chei).filter(Chei.nume == result['key']).first()
                if not key:
                    raise Exception(f"Key {result['key']} not found in database")
                
                print(f"Found key in database with ID: {key.id_cheie}")
                print(f"Key type: {key.tip_cheie}")
                print(f"Key content length: {len(key.cheie)} bytes")
                
                # Create temporary directory for keys
                temp_dir = "temp_keys"
                os.makedirs(temp_dir, exist_ok=True)
                print(f"Created temporary directory: {temp_dir}")
                
                try:
                    # For RSA, we need to create a temporary key file
                    if result['algorithm'] == "RSA":
                        key_path = os.path.join(temp_dir, f"key_{uuid.uuid4()}.pem")
                        print(f"Creating temporary key file: {key_path}")
                        
                        # Write key content to temporary file
                        with open(key_path, 'wb') as f:
                            f.write(key.cheie)
                        print(f"Wrote {len(key.cheie)} bytes to key file")
                        
                        # Build and print the command
                        cmd_template = algo_info['encrypt_cmd'] if result['operation'] == 'Encrypt' else algo_info['decrypt_cmd']
                        cmd = cmd_template.format(
                            input=result['file_path'],
                            output=result['output_path'],
                            key=key_path
                        )
                    else:  # AES
                        # For AES, use the key value directly (do not create a temp file)
                        key_value = key.cheie.decode('utf-8')
                        print(f"Using AES key value: {key_value}")
                        
                        # Build and print the command
                        cmd_template = algo_info['encrypt_cmd'] if result['operation'] == 'Encrypt' else algo_info['decrypt_cmd']
                        cmd = cmd_template.format(
                            input=result['file_path'],
                            output=result['output_path'],
                            key=key_value
                        )
                    
                    print("\n" + "="*80)
                    print("COMANDA PENTRU CMD (COPY-PASTE):")
                    print("="*80)
                    print(cmd)
                    print("="*80 + "\n")
                    
                    # Execute the command
                    print("Executing command...")
                    start_time = time.time()
                    
                    # Split command into list for better execution
                    if result['algorithm'] == "RSA":
                        cmd_parts = cmd.split()
                        print(f"Command parts: {cmd_parts}")
                        process = subprocess.run(
                            cmd_parts,
                            capture_output=True,
                            text=True
                        )
                    else:  # AES
                        print(f"Executing AES command with shell=True")
                        process = subprocess.run(
                            cmd,
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                    
                    end_time = time.time()
                    
                    print(f"Command return code: {process.returncode}")
                    print(f"Command output: {process.stdout}")
                    print(f"Command error: {process.stderr}")
                    
                    if process.returncode == 0:
                        print("Operation completed successfully")
                        
                        # Verify the output file exists and has content
                        if not os.path.exists(result['output_path']):
                            raise Exception("Output file was not created")
                        
                        file_size = os.path.getsize(result['output_path'])
                        if file_size == 0:
                            raise Exception("Output file is empty")
                        
                        print(f"Output file created successfully: {result['output_path']} ({file_size} bytes)")
                        
                        # Calculate file hash
                        print("Calculating file hash...")
                        file_hash = self.calculate_file_hash(result['output_path'])
                        print(f"File hash: {file_hash}")
                        
                        # Get algorithm from database
                        algo = db.query(Algoritmi).filter(Algoritmi.nume_algoritm == result['algorithm']).first()
                        if not algo:
                            raise Exception(f"Algorithm {result['algorithm']} not found in database")
                        
                        # Create and save file in database
                        file = Fisiere(
                            id_fisier=str(uuid.uuid4()),
                            name_fisier=os.path.basename(result['output_path']),
                            locate_fisier=result['output_path'],
                            hash=file_hash,
                            dimensiune=file_size,
                            status=StatusFisier.CRIPTAT if result['operation'] == 'Encrypt' else StatusFisier.DECRIPTAT,
                            data_creare=datetime.now()
                        )
                        db.add(file)
                        db.flush()
                        print(f"File info saved to database: {result['output_path']}")
                        
                        # Create file operation and performance
                        from database.operations import create_file_operation
                        operation, error = create_file_operation(
                            db=db,
                            file_id=file.id_fisier,
                            algorithm_id=algo.id_algoritm,
                            key_id=key.id_cheie,
                            operation_type=result['operation'],
                            performance_data={
                                'encrypt_time': end_time - start_time if result['operation'] == 'Encrypt' else None,
                                'decrypt_time': end_time - start_time if result['operation'] == 'Decrypt' else None,
                                'memory_used': 0  # TODO: Implement memory measurement
                            },
                            output_path=result['output_path']
                        )
                        
                        if error:
                            raise Exception(f"Failed to save operation: {error}")
                        
                        print(f"Operation saved to database with ID: {operation.id}")
                        
                        # Update files list
                        print("Updating files list...")
                        self.refresh_files_list()
                        
                        messagebox.showinfo("Success", f"File {result['operation'].lower()}ed successfully!\nOutput path: {result['output_path']}")
                    else:
                        print(f"Operation failed with error: {process.stderr}")
                        raise Exception(f"Operation failed: {process.stderr}")
                finally:
                    # Clean up temporary files
                    if 'key_path' in locals():
                        try:
                            os.remove(key_path)
                            print(f"Removed temporary key file: {key_path}")
                        except Exception as e:
                            print(f"Warning: Failed to remove temporary key file: {str(e)}")
                    try:
                        os.rmdir(temp_dir)
                        print(f"Removed temporary directory: {temp_dir}")
                    except Exception as e:
                        print(f"Warning: Failed to remove temporary directory: {str(e)}")
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error during operation: {str(e)}")
            messagebox.showerror("Error", str(e))

    def get_performance_summary_and_id_by_file(self, db, file):
        status_str = str(file.status).upper() if hasattr(file, 'status') else ''
        fac = None
        if status_str == 'DECRIPTAT':
            fac = db.query(FisierAlgorithmCheie).filter(
                FisierAlgorithmCheie.id_fisier == file.id_fisier,
                FisierAlgorithmCheie.data_decriptare != None
            ).first()
        elif status_str == 'CRiPTAT' or status_str == 'CRIPTAT':
            fac = db.query(FisierAlgorithmCheie).filter(
                FisierAlgorithmCheie.id_fisier == file.id_fisier,
                FisierAlgorithmCheie.data_criptare != None
            ).first()
        else:
            fac = db.query(FisierAlgorithmCheie).filter(FisierAlgorithmCheie.id_fisier == file.id_fisier).first()
        if fac and fac.id_performanta:
            perf = db.query(Performante).filter(Performante.id_performanta == fac.id_performanta).first()
            if perf:
                if status_str == 'CRiPTAT' or status_str == 'CRIPTAT':
                    return (f"Encrypt: {perf.timp_criptare:.2f}s" if perf.timp_criptare is not None else "-", perf.id_performanta)
                elif status_str == 'DECRIPTAT':
                    return (f"Decrypt: {perf.timp_decriptare:.2f}s" if perf.timp_decriptare is not None else "-", perf.id_performanta)
        return ("-", "")

    def show_performance_details(self, event):
        selection = self.files_tree.selection()
        if not selection:
            return
        item = self.files_tree.item(selection[0])
        print(f"[DEBUG] item['values']: {item['values']}")
        # Find the index of 'PerformanceID' and 'FileID' columns
        perf_id_index = self.files_tree['columns'].index('PerformanceID')
        file_id_index = self.files_tree['columns'].index('FileID')
        perf_id = item['values'][perf_id_index] if len(item['values']) > perf_id_index else ''
        file_id = item['values'][file_id_index] if len(item['values']) > file_id_index else ''
        print(f"[DEBUG] show_performance_details: perf_id={perf_id}, file_id={file_id}")
        db = SessionLocal()
        try:
            # Use file_id to find the correct operation and performance if needed
            if not perf_id and file_id:
                fac = db.query(FisierAlgorithmCheie).filter(FisierAlgorithmCheie.id_fisier == file_id).first()
                if fac and fac.id_performanta:
                    perf_id = fac.id_performanta
            perf = db.query(Performante).filter(Performante.id_performanta == perf_id).first()
            print(f"[DEBUG] perf found: {perf is not None}")
            if not perf:
                messagebox.showerror("Error", "No performance data found for this file")
                return
            # Get algorithm name
            algo = db.query(Algoritmi).filter(Algoritmi.id_algoritm == perf.id_algoritm).first()
            performance_data = {
                'algorithm': algo.nume_algoritm if algo else '-',
                'framework': 'OpenSSL',
                'encrypt_time': perf.timp_criptare,
                'decrypt_time': perf.timp_decriptare,
                'memory': perf.memorie_utilizata,
                'date': perf.data_test.strftime("%Y-%m-%d %H:%M:%S")
            }
            PerformanceDetailsDialog(self.root, performance_data)
        finally:
            db.close()

    def refresh_files_list(self):
        # Clear existing entries
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        # Get all files from database
        db = SessionLocal()
        try:
            files = db.query(Fisiere).all()
            for file in files:
                # Get performance summary and id
                perf_summary, perf_id = self.get_performance_summary_and_id_by_file(db, file)
                self.files_tree.insert('', 'end', values=(
                    file.name_fisier,
                    self.get_algorithm_name_by_file(db, file),
                    file.status.name if hasattr(file.status, 'name') else str(file.status),
                    file.dimensiune,
                    file.hash,
                    perf_summary,
                    file.locate_fisier,
                    perf_id,
                    file.id_fisier
                ))
        finally:
            db.close()

    def get_algorithm_name_by_file(self, db, file):
        # Try to get the algorithm name via the FisierAlgorithmCheie relationship
        fac = db.query(FisierAlgorithmCheie).filter(FisierAlgorithmCheie.id_fisier == file.id_fisier).first()
        if fac:
            algo = db.query(Algoritmi).filter(Algoritmi.id_algoritm == fac.id_algorithm).first()
            if algo:
                return algo.nume_algoritm
        return "-"

    def refresh_frameworks_list(self):
        # Clear existing
        for item in self.frameworks_tree.get_children():
            self.frameworks_tree.delete(item)
        db = SessionLocal()
        try:
            frameworks = db.query(Frameworks).all()
            for fw in frameworks:
                self.frameworks_tree.insert('', 'end', values=(fw.nume_framework, fw.tip_framework, fw.versiune))
        finally:
            db.close()
        # Clear right panel
        for item in self.framework_algos_tree.get_children():
            self.framework_algos_tree.delete(item)

    def on_framework_select(self, event):
        selection = self.frameworks_tree.selection()
        if not selection:
            return
        item = self.frameworks_tree.item(selection[0])
        fw_name = item['values'][0]
        db = SessionLocal()
        try:
            fw = db.query(Frameworks).filter(Frameworks.nume_framework == fw_name).first()
            if not fw:
                return
            # Find all algorithms that have at least one operation with this framework
            # (via Performante table)
            algos = db.query(Algoritmi).join(Performante, Performante.id_algoritm == Algoritmi.id_algoritm)
            algos = algos.filter(Performante.id_framework == fw.id_framework).distinct().all()
            # Clear and populate right panel
            for item in self.framework_algos_tree.get_children():
                self.framework_algos_tree.delete(item)
            for algo in algos:
                self.framework_algos_tree.insert('', 'end', values=(
                    algo.nume_algoritm,
                    algo.tip_algoritm.value if hasattr(algo.tip_algoritm, 'value') else str(algo.tip_algoritm),
                    fw.comanda_criptare,
                    fw.comanda_decriptare
                ))
        finally:
            db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptionManagerGUI(root)
    root.mainloop() 