from flask import Blueprint, jsonify, render_template

from app.services.overview_service import OverviewService
from app.services.spatial_service import SpatialService
from app.services.market_segment_service import MarketSegmentRatingService
from app.services.prediction_service import PredictionAnalysisService

overview_bp = Blueprint("overview", __name__)


@overview_bp.route("/", methods=["GET"])
def overview_page():
    return render_template("overview.html")


@overview_bp.route("/api/overview", methods=["GET"])
def overview_data():
    payload = OverviewService.get_overview_payload()
    return jsonify(payload)


@overview_bp.route("/api/overview/segment-histograms", methods=["GET"])
def overview_segment_histograms():
    payload = OverviewService.get_segment_histograms()
    return jsonify(payload)


@overview_bp.route("/api/overview/area-histograms", methods=["GET"])
def overview_area_histograms():
    payload = OverviewService.get_area_histograms()
    return jsonify(payload)


@overview_bp.route("/spatial-diagnostics", methods=["GET"])
def spatial_diagnostics_page():
    return render_template("spatial_diagnostics.html")


@overview_bp.route("/api/spatial-diagnostics", methods=["GET"])
def spatial_diagnostics_data():
    payload = SpatialService.get_spatial_analysis_payload()
    return jsonify(payload)


@overview_bp.route("/market-segment-rating", methods=["GET"])
def market_segment_rating_page():
    return render_template("market_segment_rating.html")


@overview_bp.route("/api/market-segment-rating", methods=["GET"])
def market_segment_rating_data():
    payload = MarketSegmentRatingService.get_payload()
    return jsonify(payload)


@overview_bp.route("/dashboard", methods=["GET"])
def dashboard_page():
    return render_template("Zomato_Chennai_Dashboard.html")


@overview_bp.route("/prediction-analysis", methods=["GET"])
def prediction_analysis_page():
    return render_template("prediction_analysis.html")


@overview_bp.route("/api/prediction-analysis", methods=["GET"])
def prediction_analysis_data():
    payload = PredictionAnalysisService.get_payload()
    return jsonify(payload)
