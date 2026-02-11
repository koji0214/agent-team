import os
import google.generativeai as genai
from rich.console import Console

console = Console()

def test_connection():
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL_NAME") or "gemini-1.5-flash"
    
    console.print(f"[bold blue]Testing API Connection[/bold blue]")
    console.print(f"Model: [cyan]{model_name}[/cyan]")
    
    if not api_key:
        console.print("[bold red]Error: GEMINI_API_KEY is not set.[/bold red]")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name)
        
        console.print("Sending a simple ping message...")
        response = model.generate_content("Hello! Please reply with 'ACK' if you receive this.")
        
        console.print("[bold green]Success![/bold green]")
        console.print(f"Response: {response.text}")
        
    except Exception as e:
        console.print(f"[bold red]Connection failed:[/bold red]")
        console.print(str(e))
        
        if "429" in str(e):
            console.print("[yellow]Hint: You are likely hitting a quota limit.[/yellow]")
        elif "404" in str(e):
            console.print(f"[yellow]Hint: Model '{model_name}' might not exist or be accessible.[/yellow]")
        elif "400" in str(e):
            console.print("[yellow]Hint: Bad request. Check if the model name is correct or if function calling is the issue.[/yellow]")

if __name__ == "__main__":
    test_connection()
