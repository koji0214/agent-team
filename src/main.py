import typer
from rich.console import Console
from agent.manager import Manager

app = typer.Typer()
console = Console()

@app.command()
def chat():
    """
    Start a chat session with the Manager Agent.
    Try asking: "ログイン機能を実装したい"
    Type 'exit' or 'quit' to end the session.
    """
    console.print("[bold green]GeminiCLI Agent Team Started![/bold green]")
    console.print("Type 'exit' or 'quit' to end the session.")

    try:
        from agent import Manager, Architect, Coder
        manager = Manager()
        architect = Architect()
        coder = Coder()
        
        manager.assign_agent("Architect", architect)
        manager.assign_agent("Coder", coder)
        
        while True:
            try:
                # 入力待ち。EOF (Ctrl+D) や Abort (Ctrl+C) を明示的にキャッチする
                user_input = typer.prompt("You", default=None, show_default=False)
            except (EOFError, typer.Abort):
                console.print("\n[bold green]Goodbye![/bold green]")
                break
            
            # 入力が None または空文字だけの場合はスキップ
            if not user_input or not user_input.strip():
                continue

            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold green]Goodbye![/bold green]")
                break
            
            response = manager.send_message(user_input)
            console.print(f"[bold blue]Manager:[/bold blue] {response}")

            # エラー応答だった場合、リクエストの連打を防ぐために少し待機する
            if "エラーが発生しました" in response:
                import time
                time.sleep(2)
            
    except Exception as e:
        console.print(f"[bold red]Critical Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
