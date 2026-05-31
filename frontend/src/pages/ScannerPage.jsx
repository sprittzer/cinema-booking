import { useEffect, useRef, useState } from "react";
import { Camera, CheckCircle, Upload, X } from "lucide-react";
import jsQR from "jsqr";
import Header from "../components/Header";
import { scanTicket } from "../api/api";

export default function ScannerPage() {
  const [mode, setMode] = useState("camera");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [scanning, setScanning] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const rafRef = useRef(null);
  const processingRef = useRef(false);

  function stopCamera() {
    if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
    if (streamRef.current) { streamRef.current.getTracks().forEach((t) => t.stop()); streamRef.current = null; }
    setCameraActive(false);
  }

  async function handleCode(ticketCode) {
    if (processingRef.current) return;
    processingRef.current = true;
    setScanning(true);
    setError("");
    try {
      const data = await scanTicket(ticketCode);
      setResult(data);
    } catch (err) {
      setError(err.message || "Билет не найден");
    } finally {
      setScanning(false);
      processingRef.current = false;
    }
  }

  function loopScan() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !streamRef.current || processingRef.current) return;

    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);
      if (code) {
        stopCamera();
        handleCode(code.data);
        return;
      }
    }
    rafRef.current = requestAnimationFrame(loopScan);
  }

  async function startCamera() {
    setError("");
    setResult(null);
    processingRef.current = false;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
      });
      streamRef.current = stream;
      setCameraActive(true);
    } catch {
      setError("Не удалось получить доступ к камере");
    }
  }

  useEffect(() => () => stopCamera(), []);

  useEffect(() => {
    if (!cameraActive || !videoRef.current || !streamRef.current) return;
    videoRef.current.srcObject = streamRef.current;
    videoRef.current.play().then(() => loopScan()).catch(() => {});
  }, [cameraActive]);

  function switchMode(newMode) {
    stopCamera();
    setResult(null);
    setError("");
    processingRef.current = false;
    setMode(newMode);
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setResult(null);
    setError("");

    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      const canvas = canvasRef.current;
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0);
      const imageData = ctx.getImageData(0, 0, img.width, img.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);
      if (code) {
        handleCode(code.data);
      } else {
        setError("QR-код не найден на изображении");
      }
    };
    img.src = url;
    e.target.value = "";
  }

  function reset() {
    setResult(null);
    setError("");
    processingRef.current = false;
    if (mode === "camera") startCamera();
  }

  const seatLabel = (s) => `${String.fromCharCode(64 + s.row)}-${s.number}`;

  return (
    <>
      <Header />
      <main className="scanner-page">
        <div className="page-title">
          <span className="overline">Вход в зал</span>
          <h1>Сканер билетов</h1>
        </div>

        <div className="scanner-card">
          <div className="scanner-tabs">
            <button className={`scanner-tab${mode === "camera" ? " active" : ""}`} onClick={() => switchMode("camera")}>
              <Camera size={16} /> Камера
            </button>
            <button className={`scanner-tab${mode === "photo" ? " active" : ""}`} onClick={() => switchMode("photo")}>
              <Upload size={16} /> Фото
            </button>
          </div>

          {scanning && <div className="scanner-loading">Проверяем билет...</div>}

          {result && (
            <div className="scanner-result">
              <CheckCircle size={52} className="scanner-ok-icon" />
              <h2>Билет принят</h2>
              <div className="scanner-result-grid">
                <span>Посетитель</span><b>{result.user_name}</b>
                <span>Фильм</span><b>{result.movie_title}</b>
                <span>Зал</span><b>{result.hall_name}</b>
                <span>Начало</span>
                <b>{new Date(result.start_time).toLocaleString("ru-RU", { dateStyle: "short", timeStyle: "short" })}</b>
                <span>Места</span><b>{result.seats.map(seatLabel).join(", ")}</b>
              </div>
              <button className="primary-btn" style={{ marginTop: 24 }} onClick={reset}>
                Сканировать ещё
              </button>
            </div>
          )}

          {!result && !scanning && error && (
            <div className="scanner-error">
              <X size={18} /> {error}
              <button className="secondary-btn small" onClick={reset} style={{ marginLeft: 12 }}>
                Повторить
              </button>
            </div>
          )}

          {!result && !error && mode === "camera" && (
            <div className="scanner-camera-wrap">
              {!cameraActive ? (
                <button className="primary-btn scanner-start-btn" onClick={startCamera}>
                  <Camera size={18} /> Включить камеру
                </button>
              ) : (
                <>
                  <div className="scanner-video-wrap">
                    <video ref={videoRef} className="scanner-video" playsInline muted autoPlay />
                    <div className="scanner-viewfinder" />
                  </div>
                  <button className="secondary-btn small" style={{ marginTop: 14 }} onClick={stopCamera}>
                    Выключить
                  </button>
                </>
              )}
            </div>
          )}

          {!result && !error && mode === "photo" && (
            <label className="scanner-upload-label">
              <Upload size={32} />
              <span>Выбрать фото с QR-кодом</span>
              <input type="file" accept="image/*" onChange={handleFileChange} hidden />
            </label>
          )}

          <canvas ref={canvasRef} hidden />
        </div>
      </main>
    </>
  );
}
