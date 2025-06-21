// pages/dashboard.tsx

import { useRouter } from "next/router";
import { useEffect, useRef, useState } from "react";
import useSWR, { useSWRConfig } from "swr";
import QRCode from "react-qr-code";
import { toPng } from "html-to-image";
import { bookSpot } from "../lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL!;

async function fetcher(url: string, token: string) {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Fetch error");
  return res.json();
}

type Message =
  | { type: "success"; text: string; qr: string }
  | { type: "error"; text: string };

export default function Dashboard() {
  const router = useRouter();
  const { mutate } = useSWRConfig();
  const qrRef = useRef<HTMLDivElement>(null);

  // Auth
  const [token, setToken] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const t = localStorage.getItem("token");
    setToken(t);
    setAuthLoading(false);
    if (!t) router.replace("/login");
  }, [router]);

  function logout() {
    localStorage.removeItem("token");
    router.replace("/login");
  }

  // Booking form state
  const [start, setStart] = useState(
    () => new Date().toISOString().slice(0, 16)
  );
  const [hours, setHours] = useState(1);
  const [days, setDays] = useState(0);
  const [months, setMonths] = useState(0);
  const [plate, setPlate] = useState("");
  const [message, setMessage] = useState<Message | null>(null);

  // fetch current occupancy
  const now = new Date().toISOString();
  const { data: occupancyData } = useSWR(
    token
      ? [`${API_URL}/occupancy?at=${encodeURIComponent(now)}`, token]
      : null,
    fetcher,
    { refreshInterval: 10000 }
  );

  const freeSlots =
    occupancyData?.total != null
      ? occupancyData.total - occupancyData.occupied
      : 0;

  // handle booking
  async function handleBooking(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);

    try {
      const res = await bookSpot(token!, {
        start: new Date(start).toISOString(),
        hours,
        days,
        months,
        plate: plate.trim().toUpperCase(),
      });

      setMessage({
        type: "success",
        text:
          `✔️ Booked slot (${res.slot.row}, ${res.slot.col})\n` +
          `🕒 From: ${new Date(res.start).toLocaleString()}\n` +
          `🕔 To:   ${new Date(res.end).toLocaleString()}`,
        qr: res.qr,
      });

      // refresh occupancy
      mutate([`${API_URL}/occupancy?at=${encodeURIComponent(now)}`, token]);
    } catch (err: any) {
      setMessage({ type: "error", text: err.message || "Booking failed" });
    }
  }

  const handleDownloadQR = async () => {
    if (!qrRef.current) return;
    const dataUrl = await toPng(qrRef.current);
    const link = document.createElement("a");
    link.download = "parking_qr.png";
    link.href = dataUrl;
    link.click();
  };

  if (authLoading || !token) return null;

  return (
    <div className="container">
      <header className="header">
        <h1> Park & Ride Dashboard</h1>
        <button className="btn logout" onClick={logout}>
          Logout
        </button>
      </header>

      {/* Booking Form */}
      <section className="card">
        <h2> New Booking</h2>
        <form onSubmit={handleBooking}>
          <label>
            Start Time:
            <input
              type="datetime-local"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              required
            />
          </label>

          <label>
            Duration:
            <input
              type="number"
              min={0}
              value={hours}
              onChange={(e) => setHours(+e.target.value)}
            />{" "}
            hrs
            <input
              type="number"
              min={0}
              value={days}
              onChange={(e) => setDays(+e.target.value)}
            />{" "}
            days
            <input
              type="number"
              min={0}
              value={months}
              onChange={(e) => setMonths(+e.target.value)}
            />{" "}
            months
          </label>

          <label>
            Plate Number:
            <input
              type="text"
              value={plate}
              onChange={(e) => setPlate(e.target.value)}
              placeholder="ABC-1234"
              required
            />
          </label>

          <button type="submit" className="btn primary">
            Book Slot
          </button>
        </form>
      </section>

      {/* Cancel & Availability Links */}
      <section className="card link-card">
        <h2> Need to Cancel?</h2>
        <button className="btn danger" onClick={() => router.push("/cancel")}>
          Go to Cancellation Page
        </button>
      </section>

      <section className="card link-card">
        <h2> Check Availability</h2>
        <button
          className="btn info"
          onClick={() => router.push("/availability")}
        >
          View Available Slots
        </button>
      </section>

      {/* New: Cost Calculator Link */}
      <section className="card link-card">
        <h2> Parking Cost Calculator</h2>
        <button className="btn" onClick={() => router.push("/cost")}>
          Calculate Cost
        </button>
      </section>

      {/* Current Occupancy */}
      {occupancyData && (
        <section className="card">
          <h2> Current Occupancy</h2>
          <p>🟩 Free Slots: {freeSlots}</p>
          <p>🟥 Occupied Slots: {occupancyData.occupied}</p>
        </section>
      )}

      {/* Booking Result / QR */}
      {message && (
        <section className={`message ${message.type}`}>
          {message.text.split("\n").map((line, i) => (
            <p key={i}>{line}</p>
          ))}
          {message.type === "success" && message.qr && (
            <div className="qr-container">
              <h4>📎 Your QR Code:</h4>
              <div ref={qrRef} className="qr-box">
                <QRCode value={message.qr} size={160} />
              </div>
              <button className="btn" onClick={handleDownloadQR}>
                ⬇️ Download QR Code
              </button>
            </div>
          )}
        </section>
      )}

      <style jsx>{`
        .container {
          max-width: 800px;
          margin: 2rem auto;
          padding: 0 1rem;
          font-family: sans-serif;
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        .card {
          background: #fff;
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .link-card {
          text-align: center;
        }
        form label {
          display: block;
          margin-bottom: 0.75rem;
          font-weight: 500;
        }
        input[type="datetime-local"],
        input[type="number"],
        input[type="text"] {
          margin-left: 0.5rem;
          padding: 0.4rem;
          border: 1px solid #ccc;
          border-radius: 4px;
        }
        .btn {
          padding: 0.6rem 1.2rem;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          margin-top: 1rem;
        }
        .primary {
          background: #0070f3;
          color: #fff;
        }
        .danger {
          background: #f44336;
          color: #fff;
        }
        .info {
          background: #2196f3;
          color: #fff;
        }
        .logout {
          background: #e00;
          color: #fff;
        }
        .message {
          padding: 1rem;
          border-radius: 6px;
          margin-top: 1rem;
          white-space: pre-wrap;
        }
        .message.success {
          background: #e8f5e9;
          border: 1px solid #4caf50;
          color: #256029;
        }
        .message.error {
          background: #ffebee;
          border: 1px solid #f44336;
          color: #b71c1c;
        }
        .qr-container {
          margin-top: 1rem;
          text-align: center;
        }
        .qr-box {
          display: inline-block;
          background: #fff;
          padding: 1rem;
          border-radius: 8px;
        }
      `}</style>
    </div>
  );
}