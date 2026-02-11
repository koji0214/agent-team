from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
import os
import time
import google.generativeai as genai
from rich.console import Console

# リッチな出力を提供するためのコンソールインスタンス
console = Console()

class Agent(ABC):
    """
    全てのAIエージェントの基底クラス。
    Gemini APIとの通信、履歴管理、基本的な思考プロセスを担当する。
    """

    def __init__(self, name: str, role: str, instructions: str, model_name: Optional[str] = None, tools: Optional[List[Any]] = None):
        """
        エージェントを初期化する。

        Args:
            name (str): エージェントの名前（例: "Manager", "Coder"）。
            role (str): エージェントの役割（例: "Project Manager"）。
            instructions (str): システムプロンプトとしての詳細な指示。
            model_name (str, optional): 使用するGeminiモデルの名前。
            tools (list, optional): エージェントが使用可能なツールのリスト。
        """
        self.name = name
        self.role = role
        self.instructions = instructions
        self.tools = tools
        
        # モデル名の決定: 引数 > 環境変数 > デフォルト
        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME") or "gemini-1.5-flash"
        self.history: List[Dict[str, Any]] = []
        
        # APIキーの確認
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            error_msg = "GEMINI_API_KEY environment variable is not set."
            console.print(f"[bold red]Error:[/bold red] {error_msg}")
            raise ValueError(error_msg)
        else:
            genai.configure(api_key=api_key)

        # モデルの初期化
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self._build_system_prompt(),
            tools=self.tools
        )
        
        # チャットセッションの開始（手動で関数呼び出しを制御するため False に設定）
        self.chat_session = self.model.start_chat(history=[], enable_automatic_function_calling=False)

    def _build_system_prompt(self) -> str:
        """
        エージェントの役割に基づいたシステムプロンプトを構築する。
        """
        return f"""
        あなたは {self.name} という名前のAIエージェントです。
        役割: {self.role}
        
        以下の指示に従ってください:
        {self.instructions}
        
        回答は常に日本語で行ってください。
        """

    def send_message(self, message: str) -> str:
        """
        ユーザーまたは他のエージェントからのメッセージを受け取り、応答を生成する。
        """
        # 連続リクエストによる429を防ぐための最小インターバル（秒）
        request_interval = 1.0

        # 最初のメッセージを送信
        try:
            response = self._call_api(message)
        except Exception as e:
            return f"APIエラーが発生しました: {str(e)}"

        # 関数呼び出しのループ処理
        while True:
            # APIクォータを保護するためのインターバル
            time.sleep(request_interval)
            
            try:
                # ツール実行依頼が含まれているか確認
                function_calls = [part.function_call for part in response.parts if part.function_call]
                
                if not function_calls:
                    # 思考が完了し、最終的なテキスト応答が得られた
                    return response.text

                # ツール実行結果のリストを作成
                tool_results = []
                for fc in function_calls:
                    result = self.execute_tool(fc.name, dict(fc.args))
                    tool_results.append({
                        "function_response": {
                            "name": fc.name,
                            "response": {"result": result}
                        }
                    })
                
                # 実行結果をモデルに返送
                console.print(f"[dim]{self.name} is processing tool results...[/dim]")
                response = self._call_api(tool_results)
                
            except Exception as e:
                return f"処理中にエラーが発生しました: {str(e)}"

    def _call_api(self, content: Any, max_retries: int = 3) -> Any:
        """
        Gemini APIを呼び出し、429エラー時はリトライを行います。
        """
        initial_delay = 5
        
        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    console.print(f"[bold blue]{self.name}[/bold blue] is thinking...")
                else:
                    console.print(f"[yellow]Retrying {self.name} (attempt {attempt + 1}/{max_retries})...[/yellow]")
                
                return self.chat_session.send_message(content)
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str and ("quota" in error_str.lower() or "limit" in error_str.lower()):
                    if "limit: 0" in error_str:
                        raise e # モデル利用不可は即時失敗
                    
                    if attempt < max_retries - 1:
                        wait_time = initial_delay * (2 ** attempt)
                        console.print(f"[yellow]Quota exceeded. Waiting {wait_time}s before retry...[/yellow]")
                        time.sleep(wait_time)
                        continue
                raise e
        
        raise Exception(f"{self.name} failed after {max_retries} attempts.")

    @abstractmethod
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        サブクラスで実装されるべきツール実行メソッド。
        Function Callingの仕組みと連携することを想定。
        """
        pass
