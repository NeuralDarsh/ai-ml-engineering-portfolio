# Starting the new repository track with localization architecture

def load_system_config(language_code):
    """
    Simulates loading production environment variables based on localization.
    Supports 'EN' (English) and 'JA' (Japanese).
    """
    # 1. Configuration Database
    translations = {
        "EN": {
            "welcome": "System initialized successfully.",
            "status": "Current Mode: AI / ML Pipeline Deployment",
            "alert": "Warning: High memory consumption detected."
        },
        "JA": {
            "welcome": "システムが正常に初期化されました。",
            "status": "現在のモード：AI・機械学習パイプライン構築",
            "alert": "警告：メモリ使用量が高くなっています。"
        }
    }
    
    # 2. Extraction Logic with Fallback Guardrail
    config = translations.get(language_code.upper(), translations["EN"])
    
    print(f"---  System Boot Localizer [{language_code.upper()}] ---")
    print(f"Message: {config['welcome']}")
    print(f"Status:  {config['status']}")
    print(f"Alert:   {config['alert']}\n")

if __name__ == "__main__":
    # Test loading the Japanese localization configurations
    load_system_config(language_code="JA")
    # Test loading the English localization configurations
    load_system_config(language_code="EN")