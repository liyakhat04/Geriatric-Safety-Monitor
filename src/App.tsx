/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { Camera, Bell, FileText, Settings, Activity, AlertCircle, CheckCircle2, History } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { GoogleGenAI } from "@google/genai";
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// --- Utilities ---
function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

interface Alert { id: string; time: string; type: 'Fall' | 'Movement' | 'Safe'; status: 'Active' | 'Resolved'; image?: string; }

export default function App() {
  const [tab, setTab] = useState<'monitor' | 'alerts' | 'reports'>('monitor');
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [report, setReport] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // --- Camera Setup ---
  useEffect(() => {
    if (isMonitoring) {
      navigator.mediaDevices.getUserMedia({ video: true }).then(s => { if (videoRef.current) videoRef.current.srcObject = s; });
    } else {
      const s = videoRef.current?.srcObject as MediaStream;
      s?.getTracks().forEach(t => t.stop());
    }
  }, [isMonitoring]);

  // --- Fall Detection Logic (Simulated for Demo) ---
  const triggerAlert = async (type: 'Fall' | 'Movement') => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d')?.drawImage(video, 0, 0);
    const imgData = canvas.toDataURL('image/jpeg');

    const newAlert: Alert = { id: Math.random().toString(36).substr(2, 9), time: new Date().toLocaleTimeString(), type, status: 'Active', image: imgData };
    setAlerts(prev => [newAlert, ...prev]);

    // --- LLM Analysis ---
    setIsAnalyzing(true);
    try {
      const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: [
          { text: `Analyze this potential ${type} event for a geriatric safety monitor. Provide a brief safety assessment and next steps for the caregiver.` },
          { inlineData: { mimeType: "image/jpeg", data: imgData.split(',')[1] } }
        ],
      });
      setReport(prev => `[${newAlert.time}] ${type} Detected:\n${response.text}\n\n${prev}`);
    } catch (e) { console.error(e); }
    setIsAnalyzing(false);
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] text-[#1A1A1A] font-sans">
      {/* Header */}
      <header className="bg-white border-b border-[#E5E7EB] px-6 py-4 flex justify-between items-center sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="bg-[#4F46E5] p-2 rounded-lg text-white"><Activity size={24} /></div>
          <h1 className="text-xl font-bold tracking-tight">Geriatic Safety Monitor</h1>
        </div>
        <div className="flex bg-[#F3F4F6] p-1 rounded-xl">
          {(['monitor', 'alerts', 'reports'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} className={cn("px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize", tab === t ? "bg-white shadow-sm text-[#4F46E5]" : "text-[#6B7280] hover:text-[#1A1A1A]")}>
              {t}
            </button>
          ))}
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6">
        <AnimatePresence mode="wait">
          {tab === 'monitor' && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <div className="relative aspect-video bg-black rounded-3xl overflow-hidden shadow-2xl border-4 border-white">
                  <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                  {!isMonitoring && <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm text-white flex-col gap-4">
                    <Camera size={48} className="opacity-50" />
                    <p className="text-lg font-medium">Camera Offline</p>
                  </div>}
                  {isMonitoring && <div className="absolute top-4 left-4 flex items-center gap-2 bg-red-500/80 text-white px-3 py-1 rounded-full text-xs font-bold animate-pulse">
                    <div className="w-2 h-2 bg-white rounded-full" /> LIVE MONITORING
                  </div>}
                </div>
                <div className="flex gap-4">
                  <button onClick={() => setIsMonitoring(!isMonitoring)} className={cn("flex-1 py-4 rounded-2xl font-bold text-lg transition-all shadow-lg flex items-center justify-center gap-2", isMonitoring ? "bg-red-50 text-red-600 border-2 border-red-200" : "bg-[#4F46E5] text-white hover:bg-[#4338CA]")}>
                    {isMonitoring ? "Stop Monitoring" : "Start Monitoring"}
                  </button>
                  <button onClick={() => triggerAlert('Fall')} disabled={!isMonitoring} className="px-8 bg-orange-500 text-white rounded-2xl font-bold hover:bg-orange-600 disabled:opacity-50 shadow-lg">Simulate Fall</button>
                </div>
              </div>
              <div className="space-y-6">
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-[#E5E7EB]">
                  <h3 className="font-bold text-lg mb-4 flex items-center gap-2"><Bell size={20} className="text-[#4F46E5]" /> Recent Activity</h3>
                  <div className="space-y-4">
                    {alerts.slice(0, 5).map(a => (
                      <div key={a.id} className="flex items-center gap-3 p-3 bg-[#F9FAFB] rounded-xl border border-[#F3F4F6]">
                        <div className={cn("p-2 rounded-lg", a.type === 'Fall' ? "bg-red-100 text-red-600" : "bg-blue-100 text-blue-600")}><AlertCircle size={18} /></div>
                        <div className="flex-1">
                          <p className="text-sm font-bold">{a.type} Detected</p>
                          <p className="text-xs text-[#6B7280]">{a.time}</p>
                        </div>
                        <div className="text-[10px] font-bold px-2 py-1 bg-white rounded-md border">{a.status}</div>
                      </div>
                    ))}
                    {alerts.length === 0 && <p className="text-center py-8 text-[#9CA3AF] text-sm italic">No activity detected</p>}
                  </div>
                </div>
                <div className="bg-[#4F46E5] p-6 rounded-3xl text-white shadow-xl relative overflow-hidden">
                  <div className="relative z-10">
                    <h3 className="font-bold text-lg mb-2">Safety Score</h3>
                    <div className="text-4xl font-black">98%</div>
                    <p className="text-xs opacity-80 mt-2">All systems operational. Environment is currently safe.</p>
                  </div>
                  <Activity className="absolute -bottom-4 -right-4 w-32 h-32 opacity-10" />
                </div>
              </div>
            </motion.div>
          )}

          {tab === 'alerts' && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-4">
              <h2 className="text-2xl font-bold mb-6">Alert History</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {alerts.map(a => (
                  <div key={a.id} className="bg-white rounded-3xl overflow-hidden shadow-sm border border-[#E5E7EB] hover:shadow-md transition-shadow">
                    {a.image && <img src={a.image} className="w-full h-48 object-cover" alt="Alert Capture" />}
                    <div className="p-5 space-y-3">
                      <div className="flex justify-between items-start">
                        <span className={cn("px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider", a.type === 'Fall' ? "bg-red-100 text-red-600" : "bg-blue-100 text-blue-600")}>{a.type}</span>
                        <span className="text-xs text-[#9CA3AF]">{a.time}</span>
                      </div>
                      <h4 className="font-bold text-lg">Incident #{a.id.toUpperCase()}</h4>
                      <div className="flex gap-2 pt-2">
                        <button className="flex-1 py-2 bg-[#F3F4F6] text-[#1A1A1A] rounded-xl text-xs font-bold hover:bg-[#E5E7EB]">View Details</button>
                        <button className="px-4 py-2 bg-[#4F46E5] text-white rounded-xl text-xs font-bold hover:bg-[#4338CA]">Resolve</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              {alerts.length === 0 && <div className="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-[#E5E7EB]"><Bell size={48} className="mx-auto text-[#D1D5DB] mb-4" /><p className="text-[#6B7280]">No alerts recorded yet.</p></div>}
            </motion.div>
          )}

          {tab === 'reports' && (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="bg-white rounded-3xl shadow-sm border border-[#E5E7EB] p-8">
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold flex items-center gap-3"><FileText className="text-[#4F46E5]" /> AI Safety Report</h2>
                <button onClick={() => window.print()} className="px-4 py-2 bg-[#F3F4F6] rounded-xl text-sm font-bold flex items-center gap-2 hover:bg-[#E5E7EB]"><History size={16} /> Export PDF</button>
              </div>
              <div className="prose max-w-none">
                {isAnalyzing && <div className="flex items-center gap-3 text-[#4F46E5] animate-pulse mb-4"><Activity size={20} className="animate-spin" /> Generating AI Analysis...</div>}
                <div className="bg-[#F9FAFB] p-6 rounded-2xl border border-[#F3F4F6] min-h-[400px] whitespace-pre-wrap font-mono text-sm leading-relaxed">
                  {report || "No safety events recorded. The environment is currently stable and no incidents have been flagged for analysis."}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
