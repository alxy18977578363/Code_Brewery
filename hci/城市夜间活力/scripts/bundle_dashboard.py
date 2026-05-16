"""
将 dashboard 所依赖的本地文件全部内联进 bundle.js。
index.html 只需 <script src="./bundle.js"></script> 即可复现完整效果。
"""
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent   # .../code
OUT  = BASE / "dashboard" / "bundle.js"

def js_str(s: str) -> str:
    """将任意文本安全嵌入 JS 模板字符串（反引号包裹）"""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

# ── 读取资源 ──────────────────────────────────────────────────────────────────
district_csv   = (BASE / "data/synthetic/district_hourly_revenue.csv").read_text(encoding="utf-8-sig")
wordfreq_csv   = (BASE / "data/synthetic/poi_name_word_freq.csv").read_text(encoding="utf-8-sig")
map_json_raw   = (BASE / "data/assets/data-1521463392670-HkYvx4TtG.json").read_text(encoding="utf-8")
style_json_raw = (BASE / "data/assets/data-1522488401196-HJYUN03qz.json").read_text(encoding="utf-8")
data_js_src    = (BASE / "dashboard/data.js").read_text(encoding="utf-8")

# ── 组装 bundle ───────────────────────────────────────────────────────────────
parts = []

parts.append("// ── DASHBOARD_DATA ──────────────────────────────────────────")
parts.append(data_js_src.strip())
parts.append("")

parts.append("// ── Bundled local files ─────────────────────────────────────")
parts.append(f"const __DISTRICT_CSV__ = `{js_str(district_csv)}`;\n")
parts.append(f"const __WORDFREQ_CSV__ = `{js_str(wordfreq_csv)}`;\n")
parts.append(f"const __MAP_JSON__ = `{js_str(map_json_raw)}`;\n")
parts.append(f"const __STYLE_JSON__ = `{js_str(style_json_raw)}`;\n")

parts.append("""\
// ── fetch shim：拦截本地路径，直接返回内联数据 ──────────────────────────────
(function () {
  const _ASSETS = {
    "../data/synthetic/district_hourly_revenue.csv":     __DISTRICT_CSV__,
    "../data/synthetic/poi_name_word_freq.csv":          __WORDFREQ_CSV__,
    "../data/assets/data-1521463392670-HkYvx4TtG.json": __MAP_JSON__,
    "../data/assets/data-1522488401196-HJYUN03qz.json":  __STYLE_JSON__,
  };
  const _orig = window.fetch.bind(window);
  window.fetch = function (url, opts) {
    const key = String(url);
    if (Object.prototype.hasOwnProperty.call(_ASSETS, key)) {
      const body = _ASSETS[key];
      return Promise.resolve({
        ok:   true,
        status: 200,
        text: () => Promise.resolve(body),
        json: () => Promise.resolve(JSON.parse(body)),
      });
    }
    return _orig(url, opts);
  };
})();
""")

OUT.write_text("\n".join(parts), encoding="utf-8")
size_mb = OUT.stat().st_size / 1024 / 1024
print(f"bundle.js written ({size_mb:.2f} MB) → {OUT}")
