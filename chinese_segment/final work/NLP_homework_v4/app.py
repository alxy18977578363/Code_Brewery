"""Flask 入口。

API 设计：
- GET  /                   返回前端页面
- POST /api/pipeline       一键跑全流程
- POST /api/retrieve       仅检索（前端可分步展示用）
- POST /api/extract        仅抽取
- POST /api/cluster        仅聚类
- POST /api/review         仅综述
"""
import logging

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT, llm_available
from src.clustering import cluster_papers, year_trend, trend_analysis
from src.models import Paper, StructuredRecord
from src.pipeline import extract_all, keyword_cloud, retrieve, run_full_pipeline
from src.review.generator import generate_review
from src.review.optimizer import optimize_review
from src.review.assistant import chat_with_assistant
from src.review.qa import answer_question

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

def _coerce_dataclass(cls, d: dict):
    """将 dict 安全转成 dataclass：忽略前端注入的额外字段（如 _deep_read_attempted）。"""
    if not isinstance(d, dict):
        return cls(**{})
    allowed = getattr(cls, "__dataclass_fields__", {}) or {}
    filtered = {k: v for k, v in d.items() if k in allowed}
    return cls(**filtered)


@app.get("/")
def index():
    return render_template("index.html", llm_available=llm_available())


@app.get("/api/status")
def status():
    return jsonify({"llm_available": llm_available()})


@app.post("/api/pipeline")
def api_pipeline():
    body = request.get_json(force=True) or {}
    topic = (body.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "topic 不能为空"}), 400
    try:
        result = run_full_pipeline(
            topic,
            max_results=int(body.get("max_results", 12)),
            year_from=_int_or_none(body.get("year_from")),
            year_to=_int_or_none(body.get("year_to")),
            method=body.get("method", "rule"),
            deep_read=body.get("deep_read", False),
        )
    except Exception as e:
        app.logger.exception("pipeline failed")
        return jsonify({"error": str(e)}), 500
    return jsonify(result)


@app.post("/api/retrieve")
def api_retrieve():
    body = request.get_json(force=True) or {}
    papers = retrieve(
        body.get("topic", ""),
        max_results=int(body.get("max_results", 12)),
        year_from=_int_or_none(body.get("year_from")),
        year_to=_int_or_none(body.get("year_to")),
    )
    return jsonify({"papers": [p.to_dict() for p in papers]})


@app.post("/api/extract")
def api_extract():
    body = request.get_json(force=True) or {}
    papers = [_coerce_dataclass(Paper, p) for p in body.get("papers", [])]
    method = body.get("method", "rule")
    records = extract_all(papers, method=method)
    return jsonify({"records": [r.to_dict() for r in records]})


@app.post("/api/deep_read_paper")
def api_deep_read_paper():
    body = request.get_json(force=True) or {}
    paper_dict = body.get("paper", {})
    if not paper_dict:
        return jsonify({"error": "缺少论文信息"}), 400
    paper = _coerce_dataclass(Paper, paper_dict)
    from src.retrieval.enricher import enrich_paper
    enrich_paper(paper, fetch_full=True)
    method = body.get("method", "llm")
    records = extract_all([paper], method=method)
    return jsonify({"paper": paper.to_dict(), "record": records[0].to_dict()})



@app.post("/api/cluster")
def api_cluster():
    body = request.get_json(force=True) or {}
    papers = [_coerce_dataclass(Paper, p) for p in body.get("papers", [])]
    records = [_coerce_dataclass(StructuredRecord, r) for r in body.get("records", [])]
    clusters = cluster_papers(papers, records)
    return jsonify({
        "clusters": clusters,
        "year_trend": year_trend(papers),
        "keyword_cloud": keyword_cloud(records),
        "analytics": trend_analysis(records),
    })


@app.post("/api/review")
def api_review():
    body = request.get_json(force=True) or {}
    papers = [_coerce_dataclass(Paper, p) for p in body.get("papers", [])]
    records = [_coerce_dataclass(StructuredRecord, r) for r in body.get("records", [])]
    clusters = body.get("clusters")
    review = generate_review(papers, records, clusters)
    return jsonify(review)


@app.post("/api/optimize_review")
def api_optimize_review():
    body = request.get_json(force=True) or {}
    draft = body.get("draft", "")
    level = int(body.get("level", 1))
    records = [_coerce_dataclass(StructuredRecord, r) for r in body.get("records", [])]
    unsupported_claims = body.get("unsupported_claims", [])
    
    try:
        result = optimize_review(draft, records, level, unsupported_claims)
        return jsonify(result)
    except Exception as e:
        app.logger.exception("Optimize failed")
        return jsonify({"error": str(e)}), 500


@app.post("/api/chat_assistant")
def api_chat_assistant():
    body = request.get_json(force=True) or {}
    history = body.get("history", [])
    if not history:
        return jsonify({"error": "缺少聊天记录"}), 400
    try:
        reply = chat_with_assistant(history)
        return jsonify({"reply": reply})
    except Exception as e:
        app.logger.exception("Assistant failed")
        return jsonify({"error": str(e)}), 500


@app.post("/api/paper_qa")
def api_paper_qa():
    """基于当前检索结果的 RAG 问答，答案带 [n] 引用并校验越界。"""
    body = request.get_json(force=True) or {}
    question = (body.get("question") or "").strip()
    if not question:
        return jsonify({"error": "问题不能为空"}), 400
    papers = [_coerce_dataclass(Paper, p) for p in body.get("papers", [])]
    records = [_coerce_dataclass(StructuredRecord, r) for r in body.get("records", [])]
    try:
        return jsonify(answer_question(question, papers, records))
    except Exception as e:
        app.logger.exception("paper_qa failed")
        return jsonify({"error": str(e)}), 500


@app.post("/api/eval_compare")
def api_eval_compare():
    """在 eval/labeled.json 上跑规则法（可选 LLM 法）抽取评测，返回 P/R/F1。"""
    body = request.get_json(force=True) or {}
    with_llm = bool(body.get("llm", False)) and llm_available()
    from src.extraction.evaluator import run_comparison
    try:
        result = run_comparison(with_llm=with_llm)
        result["llm_available"] = llm_available()
        return jsonify(result)
    except Exception as e:
        app.logger.exception("eval_compare failed")
        return jsonify({"error": str(e)}), 500


def _int_or_none(v):
    try:
        return int(v) if v not in (None, "", "null") else None
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    # 关闭 use_reloader 防止 Windows 下因为并发或文件监视导致的 WinError 10038 报错
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG, use_reloader=False)
