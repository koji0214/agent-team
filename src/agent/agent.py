from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
import os
import google.generativeai as genai
from rich.console import Console

# リッチな出力を提供するためのコンソールインスタンス
console = Console()

class Agent(ABC):
    """
    全てのAIエージェントの基底クラス。
    Gemini APIとの通信、履歴管理、基本的な思考プロセスを担当する。
    """

    def __init__(self, name: str, role: str, instructions: str, model_name: Optional[str] = None):
        """
        エージェントを初期化する。

        Args:
            name (str): エージェントの名前（例: "Manager", "Coder"）。
            role (str): エージェントの役割（例: "Project Manager"）。
            instructions (str): システムプロンプトとしての詳細な指示。
            model_name (str, optional): 使用するGeminiモデルの名前。未指定の場合は環境変数 GEMINI_MODEL_NAME または 'gemini-1.5-flash' を使用。
        """
        self.name = name
        self.role = role
        self.instructions = instructions
        
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
        # system_instruction パラメータは gemini-1.5 以降で使用可能と想定
        # 0.3.2 SDKでの対応状況を確認しつつ、まずは標準的な構成で実装
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self._build_system_prompt()
        )
        
        # チャットセッションの開始
        self.chat_session = self.model.start_chat(history=[])

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

        Args:
            message (str): 入力メッセージ。

        Returns:
            str: エージェントの応答。
        """
        try:
            # コンソールに進捗を表示
            console.print(f"[bold blue]{self.name}[/bold blue] is thinking...")
            
            # Gemini APIへのリクエスト
            response = self.chat_session.send_message(message)
            
            # 応答テキストの取得
            response_text = response.text
            
            # 履歴への追加などはSDKが管理してくれるが、独自ログが必要ならここで処理
            
            return response_text
            
        except Exception as e:
            error_str = str(e)
            advice = ""
            
            if "404" in error_str:
                advice = f"\n[yellow]ヒント: モデル '{self.model_name}' が見つかりません。[/yellow]"
                advice += f"\n[yellow]scripts/check_models.py を実行して、利用可能なモデル名を確認し、.env の GEMINI_MODEL_NAME に設定してください。[/yellow]"
            elif "429" in error_str and ("quota" in error_str.lower() or "limit" in error_str.lower()):
                if "limit: 0" in error_str:
                    advice = f"\n[yellow]重要: モデル '{self.model_name}' は現在のアカウントで有効化されていません（利用枠 0）。[/yellow]"
                    advice += f"\n[yellow].env の GEMINI_MODEL_NAME を、より標準的な 'gemini-flash-latest' に変更してください。[/yellow]"
                else:
                    advice = f"\n[yellow]ヒント: クォータ制限に達しました。しばらく待つか、別のモデル（'gemini-flash-latest' など）を試してください。[/yellow]"
            
            if advice:
                console.print(f"[bold red]API Error in {self.name}:[/bold red] {error_str}{advice}")
            else:
                console.print(f"[bold red]Error in {self.name}:[/bold red] {error_str}")
            
            return f"申し訳ありません。エラーが発生しました（{type(e).__name__}）。"

    @abstractmethod
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        サブクラスで実装されるべきツール実行メソッド。
        Function Callingの仕組みと連携することを想定。
        """
        pass
