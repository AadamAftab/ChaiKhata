// frontend/src/app/page.tsx
"use client";

import React, { useState } from 'react';
import { Wallet, Users, Compass, ShieldAlert, Sparkles } from 'lucide-react';

export default function ChaiKhataDashboard() {
  const [username] = useState('aadam');
  const [burnStatus] = useState('Critical Burn');
  const [daysToBroke] = useState(4);

  return (
    <main className="min-h-screen px-6 py-12 md:px-16 max-w-6xl mx-auto selection:bg-stone-200">
      
      {/* MINIMALIST NAVIGATION */}
      <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-stone-200 pb-8 mb-12 gap-4">
        <div>
          <h1 className="text-xl font-medium tracking-tight text-stone-800">
            chaikhata <span className="text-stone-400 font-light">/ iiitb node</span>
          </h1>
          <p className="text-xs text-stone-400 font-serif italic mt-0.5">electronic city phase one</p>
        </div>
        <div className="text-xs font-mono bg-stone-100 text-stone-600 px-3 py-1.5 rounded-md border border-stone-200/60">
          profile: <span className="font-semibold text-stone-800">{username}</span>
        </div>
      </header>

      {/* SOOTHING INSIGHT BAR */}
      <div className="mb-10 p-4 bg-amber-50/60 border border-amber-100/80 rounded-xl flex items-start gap-3 text-stone-700 text-xs shadow-xs">
        <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-medium text-amber-900">Spending alert:</span> Your personal burn rate is accelerated. Consider moderating quick-commerce orders this week to extend your balance.
        </div>
      </div>

      {/* THREE-COLUMN MINIMALIST GRID */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* CARD 1: RUNWAY FORECAST */}
        <div className="bg-white border border-stone-200/80 rounded-2xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-sm font-medium text-stone-700 flex items-center gap-2">
                <Wallet className="text-stone-400 w-4 h-4" /> Personal Runway
              </h2>
              <span className="text-[10px] font-mono tracking-wider uppercase px-2 py-0.5 bg-rose-50 text-rose-600 rounded border border-rose-100">
                {burnStatus}
              </span>
            </div>
            
            <div className="my-4">
              <span className="text-[11px] font-mono text-stone-400 uppercase tracking-wider block">Estimated Velocity</span>
              <div className="flex items-baseline gap-1.5 mt-1">
                <span className="text-6xl font-light text-stone-800 tracking-tighter">{daysToBroke}</span>
                <span className="text-sm text-stone-400 italic font-serif">days remaining</span>
              </div>
            </div>
          </div>
          
          <p className="text-xs text-stone-400 mt-6 pt-4 border-t border-stone-100 font-serif italic">
            Calculated deterministically from chronological transaction inputs.
          </p>
        </div>

        {/* CARD 2: BALANCED DEBT MATRIX */}
        <div className="bg-white border border-stone-200/80 rounded-2xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-sm font-medium text-stone-700 flex items-center gap-2">
                <Users className="text-stone-400 w-4 h-4" /> Shared Trips
              </h2>
              <span className="text-[10px] font-mono tracking-wider uppercase px-2 py-0.5 bg-stone-100 text-stone-500 rounded">
                gokarna_vault
              </span>
            </div>
            
            <div className="space-y-3.5">
              <div className="flex justify-between text-[11px] font-mono text-stone-400 border-b border-stone-100 pb-1">
                <span>PEER NETWORKS</span>
                <span>STATUS</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-stone-600">aarav</span>
                <span className="font-mono text-emerald-600 font-medium">+₹1,100.00</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-stone-600">vinay</span>
                <span className="font-mono text-stone-400">-₹200.00</span>
              </div>
            </div>
          </div>

          <button className="w-full mt-8 bg-stone-900 hover:bg-stone-800 text-white text-xs font-medium py-2 px-4 rounded-xl transition-all cursor-pointer shadow-xs">
            Add transaction
          </button>
        </div>

        {/* CARD 3: LOCAL RADAR FEED */}
        <div className="bg-white border border-stone-200/80 rounded-2xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-sm font-medium text-stone-700 flex items-center gap-2">
                <Compass className="text-stone-400 w-4 h-4" /> Campus Radar
              </h2>
              <span className="text-[10px] font-mono tracking-wider uppercase px-2 py-0.5 bg-stone-100 text-stone-500 rounded">
                ecity_p1
              </span>
            </div>
            
            <div className="space-y-4">
              <div className="p-3.5 bg-stone-50/80 rounded-xl border border-stone-200/40">
                <div className="flex justify-between items-baseline">
                  <span className="text-xs font-medium text-stone-800">Cali Burrito</span>
                  <span className="text-[10px] font-mono text-stone-400">85% value score</span>
                </div>
                <p className="text-[11px] text-stone-500 mt-1">Tuesday Promotion: Buy one get one free</p>
              </div>

              <div className="p-3 bg-stone-50/30 rounded-xl border border-dashed border-stone-200 flex gap-2 items-start text-[11px] text-stone-500">
                <Sparkles className="w-3.5 h-3.5 text-stone-400 shrink-0 mt-0.5" />
                <div>Skip delivery applications tonight; dining directly saves an estimated ₹170.</div>
              </div>
            </div>
          </div>
          
          <div className="text-[10px] font-mono text-stone-400 mt-4 text-right">
            updates dynamically
          </div>
        </div>

      </section>
    </main>
  );
}