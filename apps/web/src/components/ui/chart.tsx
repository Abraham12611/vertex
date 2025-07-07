"use client";

import * as React from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  RadialBarChart,
  RadialBar,
  Legend,
  Tooltip,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts";

// Mock data for all charts
const areaData = [
  { month: "Jan", users: 400, sessions: 240 },
  { month: "Feb", users: 300, sessions: 139 },
  { month: "Mar", users: 200, sessions: 980 },
  { month: "Apr", users: 278, sessions: 390 },
  { month: "May", users: 189, sessions: 480 },
  { month: "Jun", users: 239, sessions: 380 },
  { month: "Jul", users: 349, sessions: 430 },
];

const barData = [
  { name: "Strategy", value: 120 },
  { name: "Content", value: 98 },
  { name: "Community", value: 86 },
  { name: "Analytics", value: 99 },
];

const lineData = [
  { day: "Mon", visitors: 220 },
  { day: "Tue", visitors: 128 },
  { day: "Wed", visitors: 340 },
  { day: "Thu", visitors: 278 },
  { day: "Fri", visitors: 189 },
  { day: "Sat", visitors: 239 },
  { day: "Sun", visitors: 349 },
];

const pieData = [
  { name: "Organic", value: 400 },
  { name: "Referral", value: 300 },
  { name: "Social", value: 300 },
  { name: "Email", value: 200 },
];
const pieColors = ["#6366f1", "#f59e42", "#10b981", "#f43f5e"];

const radarData = [
  { metric: "SEO", A: 120, B: 110, fullMark: 150 },
  { metric: "Content", A: 98, B: 130, fullMark: 150 },
  { metric: "Community", A: 86, B: 130, fullMark: 150 },
  { metric: "Engagement", A: 99, B: 100, fullMark: 150 },
  { metric: "ROI", A: 85, B: 90, fullMark: 150 },
];

const radialData = [
  { name: "Completed", value: 80, fill: "#10b981" },
  { name: "In Progress", value: 15, fill: "#6366f1" },
  { name: "Failed", value: 5, fill: "#f43f5e" },
];

export function AnalyticsChartsGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
      {/* Area Chart */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow p-6">
        <h3 className="font-semibold mb-2">User Growth (Area)</h3>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={areaData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="month" />
            <Tooltip />
            <Area type="monotone" dataKey="users" stroke="#6366f1" fillOpacity={1} fill="url(#colorUsers)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Bar Chart */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow p-6">
        <h3 className="font-semibold mb-2">Agent Task Count (Bar)</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={barData}>
            <XAxis dataKey="name" />
            <Tooltip />
            <Bar dataKey="value" fill="#f59e42" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Line Chart */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow p-6">
        <h3 className="font-semibold mb-2">Daily Visitors (Line)</h3>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={lineData}>
            <XAxis dataKey="day" />
            <Tooltip />
            <Line type="monotone" dataKey="visitors" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Pie Chart */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow p-6">
        <h3 className="font-semibold mb-2">Traffic Sources (Pie)</h3>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
              {pieData.map((entry, idx) => (
                <Cell key={`cell-${idx}`} fill={pieColors[idx % pieColors.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Radar Chart */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow p-6">
        <h3 className="font-semibold mb-2">Performance Metrics (Radar)</h3>
        <ResponsiveContainer width="100%" height={220}>
          <RadarChart data={radarData} outerRadius={80}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" />
            <PolarRadiusAxis />
            <Radar name="Vertex" dataKey="A" stroke="#6366f1" fill="#6366f1" fillOpacity={0.6} />
            <Radar name="Competitor" dataKey="B" stroke="#f59e42" fill="#f59e42" fillOpacity={0.3} />
            <Legend />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Radial Bar Chart */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow p-6">
        <h3 className="font-semibold mb-2">Task Status (Radial)</h3>
        <ResponsiveContainer width="100%" height={220}>
          <RadialBarChart innerRadius="60%" outerRadius="100%" data={radialData} startAngle={90} endAngle={-270}>
            <RadialBar background clockWise dataKey="value" />
            <Legend iconSize={10} layout="vertical" verticalAlign="middle" align="right" />
            <Tooltip />
          </RadialBarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export { AnalyticsChartsGrid };