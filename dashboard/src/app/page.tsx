"use client";
import { useEffect, useMemo, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import "chartjs-adapter-date-fns";
import { parseNumber } from "@/lib/parser";
import {
  FireIcon,
  ChartBarIcon,
  ClockIcon,
  CalendarDaysIcon,
  ListBulletIcon,
  CogIcon,
  SunIcon,
  BeakerIcon,
  CubeIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import { IconBuildingWarehouse } from "@tabler/icons-react";

type Snapshot = {
  timestamp: string;
  pages: Record<string, Record<string, string>>;
};
type Bucket = "hour" | "day" | "none";
type SeriesPoint = { t: Date; v: number };

Chart.register(LineElement, PointElement, LinearScale, TimeScale, Filler, Tooltip, Legend);

type DataResponse = { snapshots: Snapshot[]; components: string[] };

export default function Home() {
  const [data, setData] = useState<DataResponse | null>(null);
  const [component, setComponent] = useState<string>("");
  const [metric, setMetric] = useState<string>("");
  const [bucket, setBucket] = useState<Bucket>("hour");

  useEffect(() => {
    fetch("/api/data", { cache: "no-store" })
      .then((r) => r.json())
      .then((j: DataResponse) => {
        setData(j);
        setComponent(j.components[0] || "");
      });
  }, []);

  const numericKeys = useMemo(() => {
    if (!data || !component) return [];
    const set = new Set<string>();
    for (const s of data.snapshots) {
      const comp = s.pages?.[component];
      if (!comp) continue;
      for (const [k, v] of Object.entries(comp)) {
        const num = parseNumber(v);
        if (num != null) set.add(k);
      }
    }
    const arr = Array.from(set).sort();
    if (!metric && arr.length) setMetric(arr[0]);
    return arr;
  }, [data, component]);

  const series: SeriesPoint[] = useMemo(() => {
    if (!data || !component || !metric) return [];
    const points: SeriesPoint[] = [];
    for (const s of data.snapshots) {
      const comp = s.pages?.[component];
      if (!comp) continue;
      const raw = comp[metric];
      const num = parseNumber(raw);
      if (num == null) continue;
      points.push({ t: new Date(s.timestamp), v: num });
    }
    points.sort((a, b) => a.t.getTime() - b.t.getTime());
    if (bucket === "none") {
      return points;
    }
    const map = new Map<number, number>();
    for (const p of points) {
      const d = new Date(p.t);
      if (bucket === "day") {
        d.setHours(0, 0, 0, 0);
      } else {
        d.setMinutes(0, 0, 0);
      }
      const ts = d.getTime();
      map.set(ts, p.v); // keep the latest value per bucket
    }
    const out: SeriesPoint[] = [];
    for (const [ts, value] of map.entries()) {
      out.push({ t: new Date(ts), v: value });
    }
    return out.sort((a, b) => a.t.getTime() - b.t.getTime());
  }, [data, component, metric, bucket]);

  const chartData = useMemo(() => {
    return {
      datasets: [
        {
          label: metric ? `${component} • ${metric} (${bucket})` : "",
          data: series.map((p) => ({ x: p.t, y: p.v })),
          borderColor: "#0ea5e9",
          backgroundColor: "rgba(14,165,233,0.2)",
          tension: 0.2,
          fill: true,
        },
      ],
    };
  }, [series, metric, component, bucket]);

  const chartOptions = {
    responsive: true,
    scales: {
      x: { type: "time" as const },
      y: { type: "linear" as const, beginAtZero: false },
    },
    plugins: { legend: { display: true }, tooltip: { enabled: true } },
  };

  const solarFacts = useMemo(() => {
    if (!data || !data.snapshots.length) return null;
    const latest = data.snapshots[data.snapshots.length - 1];
    const hoursRaw = latest.pages?.["Solar"]?.["Collector pump runtime"];
    const hours = parseNumber(hoursRaw);
    if (hours == null) return null;
    const days = hours / 24;
    const weeks = Math.floor(days / 7);
    const remDays = Math.floor(days) % 7;
    return { hours, days, weeks, remDays };
  }, [data]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="flex items-center gap-2 text-2xl font-semibold">
            <FireIcon className="h-6 w-6 text-sky-500" />
            Boiler Room Dashboard
          </h1>
          <div className="flex gap-2">
            <button
              className={`px-3 py-1 rounded ${bucket === "hour" ? "bg-sky-600" : "bg-slate-800"}`}
              onClick={() => setBucket("hour")}
            >
              <span className="flex items-center gap-1"><ClockIcon className="h-4 w-4" /> Hourly</span>
            </button>
            <button
              className={`px-3 py-1 rounded ${bucket === "day" ? "bg-sky-600" : "bg-slate-800"}`}
              onClick={() => setBucket("day")}
            >
              <span className="flex items-center gap-1"><CalendarDaysIcon className="h-4 w-4" /> Daily</span>
            </button>
            <button
              className={`px-3 py-1 rounded ${bucket === "none" ? "bg-sky-600" : "bg-slate-800"}`}
              onClick={() => setBucket("none")}
            >
              <span className="flex items-center gap-1"><ListBulletIcon className="h-4 w-4" /> All</span>
            </button>
          </div>
        </header>

        <section className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm mb-1">Component</label>
            <select
              className="w-full bg-slate-800 border border-slate-700 rounded p-2"
              value={component}
              onChange={(e) => setComponent(e.target.value)}
            >
              {data?.components.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm mb-1">Metric</label>
            <select
              className="w-full bg-slate-800 border border-slate-700 rounded p-2"
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
            >
              {numericKeys.map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
            </select>
          </div>
        </section>

        <section className="bg-slate-900 border border-slate-800 rounded p-4">
          <div className="flex items-center gap-2 mb-2 text-slate-300">
            <ChartBarIcon className="h-5 w-5" />
            <span>Trend</span>
          </div>
          <Line data={chartData} options={chartOptions} />
        </section>

        <section>
          <h2 className="text-lg font-medium mb-2">Latest Snapshot</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {data?.snapshots.length ? (
              Object.entries(data.snapshots[data.snapshots.length - 1].pages).map(([name, kv]) => (
                <div key={name} className="bg-slate-900 border border-slate-800 rounded p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {name === "Boiler" && <FireIcon className="h-5 w-5 text-sky-500" />}
                    {name === "Hot Water Tank" && <BeakerIcon className="h-5 w-5 text-sky-500" />}
                    {name === "Heating Tank" && (
                      <svg viewBox="0 0 56.693 56.693" className="h-5 w-5 text-sky-500" aria-label="Heating Tank">
                        <path fill="currentColor" d="M43.722,0a12.912,12.912,0,0,0,0,25.823A13,13,0,0,0,56.693,12.852,12.977,12.977,0,0,0,43.722,0Zm2.649,21.159H43.216V9.266a10.886,10.886,0,0,1-4.077,2.392V8.794a9.154,9.154,0,0,0,2.685-1.533A5.833,5.833,0,0,0,43.81,4.627h2.561Z" />
                        <path fill="currentColor" d="M46.206,29.155a16.483,16.483,0,0,1-2.425.2,16.352,16.352,0,0,1-7.522-1.833,3.866,3.866,0,0,1-.419,0L12.8,25.01a3.1,3.1,0,1,1,.594-6.157l15.85,1.728A16.32,16.32,0,0,1,27.6,15.758L12.8,14.144a3.1,3.1,0,1,1,.594-6.157L27.687,9.546A16.415,16.415,0,0,1,33.033.488,63.814,63.814,0,0,0,25.052,0h-.871C12.5,0,3.026,2.944,3.026,6.576V50.117c0,1.075.83,2.09,2.3,2.986l-2.3,3.589,6.184-.005,1.015-1.629a54.769,54.769,0,0,0,13.956,1.634h.871a54.769,54.769,0,0,0,13.956-1.634l1.015,1.629,6.184.005L43.9,53.1c1.472-.9,2.3-1.911,2.3-2.986V47.5h7.461v-4.8H46.206ZM35.84,49.06,12.8,46.548a3.1,3.1,0,1,1,.594-6.157L36.433,42.9A3.1,3.1,0,1,1,35.84,49.06Zm0-10.8L12.8,35.747a3.1,3.1,0,1,1,.594-6.157L36.433,32.1A3.1,3.1,0,1,1,35.84,38.259Z" />
                      </svg>
                    )}
                    {name === "Solar" && <SunIcon className="h-5 w-5 text-yellow-400" />}
                    {name === "Feed System" && <IconBuildingWarehouse className="h-5 w-5 text-sky-500" />}
                    <h3 className="font-semibold">{name}</h3>
                  </div>
                  <ul className="space-y-2 text-sm">
                    {Object.entries(kv).map(([k, v]) => (
                      <li key={k} className="bg-slate-950/40 rounded p-2">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400">{k}</span>
                          <span className="text-slate-200 font-medium">{v}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              ))
            ) : (
              <div className="text-slate-400">No data available</div>
            )}
          </div>
        </section>

        <section className="bg-slate-900 border border-slate-800 rounded p-4">
          <div className="flex items-center gap-2 mb-2">
            <SparklesIcon className="h-5 w-5 text-sky-500" />
            <h2 className="text-lg font-medium">Fun Facts</h2>
          </div>
          {solarFacts ? (
            <div className="text-sm text-slate-200">
              <div>
                That’s approximately <span className="font-semibold">{(solarFacts.days).toFixed(1)} days</span> 
                ({solarFacts.weeks} weeks and {solarFacts.remDays} days).
              </div>
            </div>
          ) : (
            <div className="text-slate-400 text-sm">No solar runtime data found.</div>
          )}
        </section>
      </div>
    </div>
  );
}
