import os
import sys
import torch
import tkinter as tk
from tkinter import scrolledtext, ttk, font
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import threading

# Add this function to get the correct path for bundled files
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AnupamaAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anupama AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f2f5")
        
        # Load model from LOCAL FILES
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Get the correct path to model directory
        model_dir = resource_path("anupama_model")
        
        # Load tokenizer and model from local directory
        self.tokenizer = GPT2Tokenizer.from_pretrained(
            model_dir,
            local_files_only=True  # CRITICAL: Only use local files
        )
        self.model = GPT2LMHeadModel.from_pretrained(
            model_dir,
            local_files_only=True  # CRITICAL: Only use local files
        ).to(self.device)
        
        # Create UI
        self.create_widgets()
    
    # ... [REST OF YOUR CODE REMAINS UNCHANGED] ...
        
    def create_widgets(self):
        # Header
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill=tk.X, padx=10, pady=10)
        
        title = ttk.Label(header, text="🧠 Anupama AI Assistant", 
                         font=("Arial", 16, "bold"), 
                         style="Header.TLabel")
        title.pack(pady=5)
        
        subtitle = ttk.Label(header, text="Personal Assistant Trained on Anupama Pandey's Knowledge",
                           style="Subtitle.TLabel")
        subtitle.pack(pady=2)
        
        # Chat history
        self.chat_history = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            font=("Arial", 11),
            bg="white",
            padx=10,
            pady=10
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.chat_history.configure(state=tk.DISABLED)
        
        # Input area
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.user_input = ttk.Entry(
            input_frame, 
            font=("Arial", 11),
            width=50
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self.on_enter)
        
        send_button = ttk.Button(
            input_frame, 
            text="Send", 
            command=self.generate_response
        )
        send_button.pack(side=tk.RIGHT)
        
        # Configure styles
        self.configure_styles()
        
        # Add welcome message
        self.add_message("Anupama AI", "Hello! I'm your personal AI assistant trained on Anupama Pandey's knowledge. You can ask me about her work, hobbies, or birthday!")
    
    def configure_styles(self):
        style = ttk.Style()
        style.configure("Header.TFrame", background="#4f46e5")
        style.configure("Header.TLabel", background="#4f46e5", foreground="white")
        style.configure("Subtitle.TLabel", background="#4f46e5", foreground="#e0e7ff")
        style.configure("TButton", padding=6, font=("Arial", 10))
        style.configure("TEntry", padding=8)
        
        # Configure text tags
        self.chat_history.tag_configure("sender", foreground="#1e40af", font=("Arial", 11, "bold"))
        self.chat_history.tag_configure("ai", foreground="#7e22ce", font=("Arial", 11, "bold"))
    
    def add_message(self, sender, message):
        self.chat_history.configure(state=tk.NORMAL)
        tag = "sender" if sender == "You" else "ai"
        self.chat_history.insert(tk.END, f"{sender}: ", tag)
        self.chat_history.insert(tk.END, f"{message}")
        self.chat_history.configure(state=tk.DISABLED)
        self.chat_history.see(tk.END)
    
    def on_enter(self, event):
        self.generate_response()
    
    def generate_response(self):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
            
        self.add_message("You", user_text)
        self.user_input.delete(0, tk.END)
        
        # Start generation in separate thread
        threading.Thread(target=self._generate_response, args=(user_text,), daemon=True).start()
    
    def _generate_response(self, user_text):
        # Add "thinking" message
        self.add_message("Anupama AI", "Thinking...")
        
        try:
            # Prepare input
            prompt = f"Human: {user_text}\nAnupama AI:"
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate response
            outputs = self.model.generate(
                inputs,
                max_length=200,
                temperature=0.7,
                top_k=40,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1
            )
            
            # Decode and clean response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = full_response[len(prompt):].strip()
            
            # Remove trailing incomplete sentences
            last_punct = max(response.rfind('.'), response.rfind('!'), response.rfind('?'))
            if last_punct != -1:
                response = response[:last_punct+1]
            
            # Remove "thinking" message and add actual response
            self.chat_history.configure(state=tk.NORMAL)
            self.chat_history.delete("end-3l linestart", "end")
            self.chat_history.configure(state=tk.DISABLED)
            
            self.add_message("Anupama AI", response)
            
        except Exception as e:
            self.add_message("Anupama AI", f"Sorry, I encountered an error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnupamaAIApp(root)
    root.mainloop()
