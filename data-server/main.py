#!/usr/bin/env python3
"""
Simple Data Sharing API for EDC
サンプルデータを提供するシンプルなAPIサーバー
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import json
import uuid
import os
import shutil
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title="Simple Data Server API",
    description="Simple data sharing API for Eclipse Data Connector with file storage",
    version="1.0.0"
)

# データ保存用ディレクトリ
DATA_DIR = Path("./saved_data")
DATA_DIR.mkdir(exist_ok=True)
SAVE_DIR = DATA_DIR / "files"
SAVE_DIR.mkdir(exist_ok=True)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルのサーブ
static_dir = Path("./static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 保存されたファイルの情報を保存
saved_files_registry = []

def load_saved_files_registry():
    """保存ファイル情報を読み込み"""
    global saved_files_registry
    registry_file = DATA_DIR / "files_registry.json"
    if registry_file.exists():
        with open(registry_file, 'r', encoding='utf-8') as f:
            saved_files_registry = json.load(f)

def save_saved_files_registry():
    """保存ファイル情報を保存"""
    registry_file = DATA_DIR / "files_registry.json"
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(saved_files_registry, f, ensure_ascii=False, indent=2)

# 起動時にレジストリを読み込み
load_saved_files_registry()

@app.get("/")
async def redirect_to_console():
    """ルートパスをdata-server-consoleにリダイレクト"""
    return FileResponse("static/index.html")

@app.get("/data-server-console")
async def web_ui():
    """Web UI を返す"""
    return FileResponse("static/index.html")

@app.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None)
):
    """ファイルを保存"""
    try:
        # ファイル情報
        file_id = str(uuid.uuid4())
        filename = file.filename or f"file_{file_id}"
        file_extension = Path(filename).suffix.lower()
        
        # サポートされているファイル形式をチェック
        supported_extensions = ['.csv', '.json', '.txt', '.xlsx']
        if file_extension not in supported_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Supported: {', '.join(supported_extensions)}"
            )
        
        # ファイル保存
        file_path = SAVE_DIR / f"{file_id}_{filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # ファイル情報をレジストリに追加
        file_info = {
            "id": file_id,
            "filename": filename,
            "title": title or filename,
            "description": description or "",
            "category": "data",
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "file_extension": file_extension,
            "save_time": datetime.now().isoformat(),
            "content_type": file.content_type
        }
        
        saved_files_registry.append(file_info)
        save_saved_files_registry()
        
        return {
            "message": "File saved successfully",
            "file_id": file_id,
            "filename": filename,
            "size": file_info["file_size"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")

@app.get("/files/list")
async def list_files(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """保存されたファイル一覧を取得"""
    files = saved_files_registry.copy()
    
    # ページネーション
    total = len(files)
    files = files[offset:offset + limit]
    
    # ファイルパスを除外してレスポンス用にクリーンアップ
    clean_files = []
    for f in files:
        clean_file = f.copy()
        clean_file.pop("file_path", None)
        clean_files.append(clean_file)
    
    return {
        "data": clean_files,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    }

@app.get("/files/{file_id}/data")
async def get_file_data(
    file_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """ファイルの内容を構造化データとして取得"""
    # ファイル情報を検索
    file_info = None
    for f in uploaded_files_registry:
        if f["id"] == file_id:
            file_info = f
            break
    
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = Path(file_info["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File data not found")
    
    try:
        file_extension = file_info["file_extension"]
        
        if file_extension == ".csv":
            # CSVファイルの処理
            df = pd.read_csv(file_path)
            total_rows = len(df)
            data = df.iloc[offset:offset + limit].to_dict('records')
            
        elif file_extension == ".json":
            # JSONファイルの処理
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if isinstance(json_data, list):
                total_rows = len(json_data)
                data = json_data[offset:offset + limit]
            else:
                total_rows = 1
                data = [json_data] if offset == 0 else []
                
        elif file_extension == ".xlsx":
            # Excelファイルの処理
            df = pd.read_excel(file_path)
            total_rows = len(df)
            data = df.iloc[offset:offset + limit].to_dict('records')
            
        elif file_extension == ".txt":
            # テキストファイルの処理
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            total_rows = len(lines)
            data = [{"line_number": i + offset + 1, "content": line.strip()} 
                   for i, line in enumerate(lines[offset:offset + limit])]
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format for data extraction")
        
        return {
            "file_info": {
                "id": file_info["id"],
                "title": file_info["title"],
                "filename": file_info["filename"],
                "category": file_info["category"]
            },
            "data": data,
            "pagination": {
                "total": total_rows,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_rows
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file data: {str(e)}")

@app.get("/files/{file_id}/view")
async def view_file_content(
    file_id: str,
    format: str = Query(default="json", pattern="^(json|csv|html|raw)$"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """ファイルの内容を指定された形式で表示"""
    # ファイル情報を検索
    file_info = None
    for f in uploaded_files_registry:
        if f["id"] == file_id:
            file_info = f
            break
    
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = Path(file_info["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File data not found")
    
    try:
        file_extension = file_info["file_extension"]
        
        # データを読み込み
        if file_extension == ".csv":
            df = pd.read_csv(file_path)
            total_rows = len(df)
            data = df.iloc[offset:offset + limit].to_dict('records')
            
        elif file_extension == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if isinstance(json_data, list):
                total_rows = len(json_data)
                data = json_data[offset:offset + limit]
            else:
                total_rows = 1
                data = [json_data] if offset == 0 else []
                
        elif file_extension == ".xlsx":
            df = pd.read_excel(file_path)
            total_rows = len(df)
            data = df.iloc[offset:offset + limit].to_dict('records')
            
        elif file_extension == ".txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            total_rows = len(lines)
            data = [{"line_number": i + offset + 1, "content": line.strip()} 
                   for i, line in enumerate(lines[offset:offset + limit])]
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format for viewing")
        
        # 形式に応じてレスポンスを生成
        if format == "json":
            return {
                "file_info": {
                    "id": file_info["id"],
                    "title": file_info["title"],
                    "filename": file_info["filename"],
                    "category": file_info["category"]
                },
                "data": data,
                "pagination": {
                    "total": total_rows,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_rows
                },
                "view_format": "json"
            }
            
        elif format == "csv":
            # CSVとして出力
            if not data:
                return JSONResponse(
                    content={"error": "No data available"},
                    status_code=404
                )
            
            import io
            output = io.StringIO()
            if data:
                keys = data[0].keys()
                output.write(','.join(keys) + '\n')
                for row in data:
                    values = [str(row.get(key, '')) for key in keys]
                    output.write(','.join(values) + '\n')
            
            return JSONResponse(
                content={
                    "file_info": {
                        "id": file_info["id"],
                        "title": file_info["title"],
                        "filename": file_info["filename"]
                    },
                    "csv_content": output.getvalue(),
                    "view_format": "csv",
                    "total_rows": total_rows
                },
                headers={"Content-Type": "application/json"}
            )
            
        elif format == "html":
            # HTMLテーブルとして出力
            html_content = f"""
            <h2>{file_info['title']}</h2>
            <p><strong>ファイル:</strong> {file_info['filename']}</p>
            <p><strong>カテゴリ:</strong> {file_info['category']}</p>
            <p><strong>表示範囲:</strong> {offset + 1} - {min(offset + limit, total_rows)} / {total_rows}</p>
            """
            
            if data:
                html_content += "<table border='1' style='border-collapse: collapse;'>"
                keys = data[0].keys()
                html_content += "<thead><tr>"
                for key in keys:
                    html_content += f"<th style='padding: 8px;'>{key}</th>"
                html_content += "</tr></thead><tbody>"
                
                for row in data:
                    html_content += "<tr>"
                    for key in keys:
                        html_content += f"<td style='padding: 8px;'>{row.get(key, '')}</td>"
                    html_content += "</tr>"
                html_content += "</tbody></table>"
            else:
                html_content += "<p>データがありません</p>"
            
            return JSONResponse(
                content={
                    "file_info": {
                        "id": file_info["id"],
                        "title": file_info["title"],
                        "filename": file_info["filename"]
                    },
                    "html_content": html_content,
                    "view_format": "html",
                    "total_rows": total_rows
                }
            )
            
        elif format == "raw":
            # 生データとして出力
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return JSONResponse(
                content={
                    "file_info": {
                        "id": file_info["id"],
                        "title": file_info["title"],
                        "filename": file_info["filename"]
                    },
                    "raw_content": content,
                    "view_format": "raw",
                    "file_size": len(content)
                }
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to view file: {str(e)}")

@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    """ファイルをダウンロード"""
    # ファイル情報を検索
    file_info = None
    for f in uploaded_files_registry:
        if f["id"] == file_id:
            file_info = f
            break
    
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = Path(file_info["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=file_info["filename"],
        media_type=file_info.get("content_type", "application/octet-stream")
    )

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """ファイルを削除"""
    global saved_files_registry
    
    # ファイル情報を検索
    file_info = None
    file_index = None
    for i, f in enumerate(saved_files_registry):
        if f["id"] == file_id:
            file_info = f
            file_index = i
            break
    
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # ファイルを削除
        file_path = Path(file_info["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        # レジストリから削除
        saved_files_registry.pop(file_index)
        save_saved_files_registry()
        
        return {"message": "File deleted successfully", "file_id": file_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")



@app.get("/config")
async def get_config():
    """API設定情報を返す"""
    import os
    
    # 環境変数またはデフォルト値から設定を取得
    fqdn = os.getenv('PARTICIPANT_FQDN', 'sample-participant-1.handson.dataspace.internal')
    
    return {
        "fqdn": fqdn,
        "base_url": f"http://{fqdn}",
        "vpn_required": True,
        "reverse_proxy": True,
        "endpoints": {
            "data": "/files/{file_id}/data",
            "view": "/files/{file_id}/view",
            "download": "/files/{file_id}/download",
            "save": "/files/upload",
            "list": "/files/list"
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)