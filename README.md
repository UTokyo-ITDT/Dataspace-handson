# EDC Simple UI

シンプルで軽量なEDC (Eclipse Dataspace Components) 操作インターフェースです。

## 🎯 特徴

- **最小構成**: 3つのサービスのみ（EDC、データサーバー、UI）
- **単一コネクター**: 1つのEDCで全機能をテスト可能
- **Web UI**: Streamlitベースの直感的インターフェース
- **完全機能**: Asset/Policy/Contract/Catalog/Transfer 全操作対応

## 🚀 クイックスタート

```bash
# ディレクトリに移動
cd edc-simple

# サービス起動（自動初期化付き）
./setup.sh

# ブラウザでアクセス
open http://localhost:8501
```

## 📋 サービス構成

| サービス | ポート | 説明 |
|---------|--------|------|
| EDC Connector | 19193 | EDC管理API |
| Data Server | 8000 | サンプルデータサーバー |
| EDC Simple UI | 8501 | Streamlit操作UI |

## 🔄 操作フロー

1. **Asset作成** → データアセット定義
2. **Policy作成** → アクセス制御ポリシー設定  
3. **Contract作成** → コントラクト定義作成
4. **Catalog取得** → 利用可能データセット確認
5. **Data Transfer** → コントラクト交渉〜データ取得

## 🛠️ 個別操作

### 起動・停止

```bash
# サービス起動
docker compose up -d --build

# ログ確認
docker compose logs -f

# サービス停止
docker compose down
```

## 🔧 トラブルシューティング

### サービス確認
```bash
# ヘルスチェック
curl http://localhost:19193/health
curl http://localhost:7080/health
curl http://localhost:8501

# コンテナ状態
docker compose ps
```

## 📚 API 参考

- EDC Management API: `http://localhost:19193/management/v3/`
- Data Server: `http://localhost:7080/`
- UI: `http://localhost:8501`

## 🎓 学習用途

このプロジェクトは以下の学習に最適です：
- EDCの基本概念理解
- データスペースプロトコルの動作確認
- コントラクト交渉フローの体験
- データ転送プロセスの理解