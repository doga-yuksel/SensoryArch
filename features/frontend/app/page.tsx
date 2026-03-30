"use client";

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";

type RiskType = "light" | "reflection" | "pattern" | "combined";

type BBox = { x: number; y: number; w: number; h: number };

type RiskRegion = {
  id: string;
  type: RiskType;
  severity: number;
  bbox: BBox;
};

type Recommendation = {
  region_id: string;
  title: string;
  actions: string[];
};

type AnalyzeResponse = {
  score: number;
  timing_ms: number;
  heatmap_image: string;
  risk_regions: RiskRegion[];
  recommendations: Recommendation[];
};

const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? "http://127.0.0.1:8000";

function score_hint(score: number): string {
  if (score >= 80) return "Genel olarak düşük uyaran; küçük iyileştirmeler yeterli olabilir.";
  if (score >= 60) return "Orta seviye uyaran; hedefli iyileştirmeler önerilir.";
  if (score >= 40) return "Yüksek uyaran; aydınlatma/parlama/patern sadeleştirme kritik.";
  return "Çok yüksek uyaran; kapsamlı iyileştirme planı önerilir.";
}

function severity_label(sev: number): string {
  if (sev >= 0.8) return "yüksek";
  if (sev >= 0.6) return "orta";
  if (sev >= 0.4) return "düşük";
  return "çok düşük";
}

export default function Page() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const originalImgRef = useRef<HTMLImageElement | null>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isShowingOverlay, setIsShowingOverlay] = useState(true);
  const [activeRegionId, setActiveRegionId] = useState<string | null>(null);

  const activeRegion = useMemo(
    () => (analysis?.risk_regions ?? []).find((r) => r.id === activeRegionId) ?? null,
    [analysis, activeRegionId]
  );

  const regionToRecommendation = useMemo(() => {
    const map = new Map<string, Recommendation>();
    for (const rec of analysis?.recommendations ?? []) map.set(rec.region_id, rec);
    return map;
  }, [analysis]);

  useEffect(() => {
    if (!selectedFile) {
      setOriginalUrl(null);
      return;
    }
    const url = URL.createObjectURL(selectedFile);
    setOriginalUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);

  const onPickFile = useCallback((file: File | null) => {
    setErrorMessage(null);
    setAnalysis(null);
    setActiveRegionId(null);
    setIsShowingOverlay(true);
    setSelectedFile(file);
  }, []);

  const onAnalyze = useCallback(async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setErrorMessage(null);
    setAnalysis(null);
    setActiveRegionId(null);

    try {
      const fd = new FormData();
      fd.append("image", selectedFile);

      const res = await fetch(`${BACKEND_BASE_URL}/analyze`, {
        method: "POST",
        body: fd,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      const json = (await res.json()) as AnalyzeResponse;
      setAnalysis(json);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Bilinmeyen hata";
      setErrorMessage(msg);
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile]);

  const onDrop: React.DragEventHandler<HTMLDivElement> = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      const file = e.dataTransfer.files?.[0] ?? null;
      if (!file) return;
      if (!/image\/(png|jpeg)/.test(file.type)) {
        setErrorMessage("Sadece JPG/PNG yükleyin.");
        return;
      }
      onPickFile(file);
    },
    [onPickFile]
  );

  const onDragOver: React.DragEventHandler<HTMLDivElement> = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const displayedImageSrc = useMemo(() => {
    if (!originalUrl) return null;
    if (!analysis) return originalUrl;
    return isShowingOverlay ? analysis.heatmap_image : originalUrl;
  }, [analysis, originalUrl, isShowingOverlay]);

  const [renderSize, setRenderSize] = useState<{ w: number; h: number } | null>(null);

  const refreshRenderSize = useCallback(() => {
    const el = originalImgRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return;
    setRenderSize({ w: rect.width, h: rect.height });
  }, []);

  useEffect(() => {
    refreshRenderSize();
    window.addEventListener("resize", refreshRenderSize);
    return () => window.removeEventListener("resize", refreshRenderSize);
  }, [refreshRenderSize]);

  const scale = useMemo(() => {
    if (!analysis || !renderSize) return null;
    const img = originalImgRef.current;
    if (!img || !img.naturalWidth || !img.naturalHeight) return null;
    return {
      sx: renderSize.w / img.naturalWidth,
      sy: renderSize.h / img.naturalHeight,
    };
  }, [analysis, renderSize]);

  return (
    <main className="container">
      <div className="header">
        <div>
          <h1 className="title">SensoryArch AI (MVP)</h1>
          <p className="subtitle">
            2D görsel yükleyin. Sistem ışık/parlama/patern kaynaklı “yüksek uyaran” bölgeleri çıkarır, heatmap üretir ve
            erişilebilirlik skoru + öneriler döndürür.
          </p>
        </div>
        <div className="row">
          <span className="pill">Backend: {BACKEND_BASE_URL}</span>
        </div>
      </div>

      <div className="grid">
        <section className="card">
          <div
            className="drop"
            onDrop={onDrop}
            onDragOver={onDragOver}
            role="button"
            tabIndex={0}
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " " ? fileInputRef.current?.click() : null)}
          >
            <strong>Görsel yükle (JPG/PNG)</strong>
            <div className="muted">Sürükle-bırak veya tıkla seç. Önerilen: 10MB altı.</div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg"
              style={{ display: "none" }}
              onChange={(e) => onPickFile(e.target.files?.[0] ?? null)}
            />
          </div>

          <div style={{ height: 12 }} />

          <div className="row">
            <button className="btn primary" disabled={!selectedFile || isAnalyzing} onClick={onAnalyze}>
              {isAnalyzing ? "Analiz ediliyor..." : "Analiz Et"}
            </button>
            <button className="btn" disabled={!analysis} onClick={() => setIsShowingOverlay((v) => !v)}>
              {isShowingOverlay ? "Orijinali Göster" : "Heatmap Göster"}
            </button>
            {selectedFile ? <span className="pill">{selectedFile.name}</span> : <span className="pill">Dosya seçilmedi</span>}
            {analysis ? <span className="pill">Süre: {analysis.timing_ms} ms</span> : null}
          </div>

          {errorMessage ? (
            <>
              <div style={{ height: 12 }} />
              <div className="error">{errorMessage}</div>
            </>
          ) : null}

          <div style={{ height: 12 }} />

          {displayedImageSrc ? (
            <div className="imageStage">
              <img
                ref={originalImgRef}
                src={displayedImageSrc}
                alt="Analiz görseli"
                onLoad={() => {
                  refreshRenderSize();
                }}
              />

              {analysis && scale
                ? analysis.risk_regions.map((r) => {
                    const left = r.bbox.x * scale.sx;
                    const top = r.bbox.y * scale.sy;
                    const width = r.bbox.w * scale.sx;
                    const height = r.bbox.h * scale.sy;
                    const isActive = r.id === activeRegionId;
                    return (
                      <div
                        key={r.id}
                        className={`bbox ${isActive ? "active" : ""}`}
                        style={{ left, top, width, height }}
                        aria-hidden
                      />
                    );
                  })
                : null}
            </div>
          ) : (
            <div className="muted">Henüz görsel yok.</div>
          )}
        </section>

        <aside className="card">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <div>
              <div className="k">Erişilebilirlik skoru</div>
              <div className="score">
                <div className="scoreValue">{analysis ? analysis.score : "—"}</div>
                <div className="scoreHint">{analysis ? score_hint(analysis.score) : "Analiz sonrası 0–100 arası skor."}</div>
              </div>
            </div>
          </div>

          <div style={{ height: 10 }} />

          <div className="k">Risk bölgeleri</div>
          {analysis ? (
            <div className="list">
              {analysis.risk_regions.length ? (
                analysis.risk_regions.map((r) => (
                  <div
                    key={r.id}
                    className={`item ${r.id === activeRegionId ? "active" : ""}`}
                    onClick={() => setActiveRegionId(r.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => (e.key === "Enter" ? setActiveRegionId(r.id) : null)}
                  >
                    <div className="itemTop">
                      <div className="v">
                        {r.id} • {r.type}
                      </div>
                      <div className="k">{severity_label(r.severity)} ({r.severity.toFixed(2)})</div>
                    </div>
                    <div className="k">
                      bbox: x={r.bbox.x}, y={r.bbox.y}, w={r.bbox.w}, h={r.bbox.h}
                    </div>
                  </div>
                ))
              ) : (
                <div className="muted">Risk bölgesi bulunamadı (eşik üstü alan yok).</div>
              )}
            </div>
          ) : (
            <div className="muted">Analiz yapınca listelenir.</div>
          )}

          <div style={{ height: 12 }} />

          <div className="k">Öneriler</div>
          {analysis ? (
            activeRegion ? (
              (() => {
                const rec = regionToRecommendation.get(activeRegion.id) ?? null;
                if (!rec) return <div className="muted">Seçili bölge için öneri bulunamadı.</div>;
                return (
                  <div className="item active" style={{ cursor: "default" }}>
                    <div className="itemTop">
                      <div className="v">{rec.title}</div>
                      <div className="k">bölge: {rec.region_id}</div>
                    </div>
                    <ul className="actions">
                      {rec.actions.map((a, i) => (
                        <li key={`${rec.region_id}-${i}`}>{a}</li>
                      ))}
                    </ul>
                  </div>
                );
              })()
            ) : (
              <div className="muted">Bir risk bölgesi seçin.</div>
            )
          ) : (
            <div className="muted">Analiz yapınca öneriler gelir.</div>
          )}
        </aside>
      </div>
    </main>
  );
}

