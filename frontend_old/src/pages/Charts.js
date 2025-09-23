import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { XAxis, YAxis, CartesianGrid, Tooltip, Legend,
        Line, LineChart, Pie, Cell, PieChart, Bar, BarChart, ResponsiveContainer} from "recharts";

export function IndustryOverTime_LineChart({ incident_data, selectedIndustry }) {

  // Filter dynamically
  const filteredData = incident_data
    .filter((item) => item.industry === selectedIndustry)
    .map((item) => ({
      ...item,
      yearMonth: `${item.year}-${String(item.month).padStart(2, "0")}`, // YYYY-MM
    }));

  return (
    <div>
      <div>
        <LineChart
          width={730}
          height={250}
          data={filteredData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="yearMonth" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="count" stroke="#3f37d1ff" />
        </LineChart>
      </div>
    </div>
  );
}

export function Event_DonutChart({incident_data, selectedIndustry, col_used}) {

  const COLORS = ["#003366", "#1e3e5eff", "#336699", "#6699CC", "#99CCFF"];
  const GREY = "#D3D3D3";
  // Filter dynamically
  const filteredData = incident_data
    .filter((item) => 
        item.industry && 
        item[col_used] &&
        item.industry === selectedIndustry);

    return (
    <div>
      <PieChart width={500} height={300}>
        <Pie
          data={filteredData}
          dataKey="count"
          nameKey= {col_used}
          cx="50%"
          cy="50%"
          innerRadius={30}
          outerRadius={100}
          labelLine={ ({index}) => index < 4 ? true : false}
          label={({ index, value }) =>
            filteredData[index]?.[col_used]
                ? (index < 5 ? `${filteredData[index][col_used]}: ${value}` : null)
                : null
            }
        >
          {filteredData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={index < 5 ? COLORS[index] : GREY}
            />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </div>
    );
}

export function AffectCountry_BarChart({ incident_data, selectedIndustry }) {
  const filteredData = incident_data.filter(
    (item) =>
      item.industry &&
      item.affected_country &&
      item.industry === selectedIndustry
  );

  const COLORS = ["#3f37d1ff", "#3f37d1ff", "#3f37d1ff", "#3f37d1ff", "#3f37d1ff"];

  return (
    <div style={{ height: 400, overflowY: "scroll" }}>
      <BarChart
        width={600}
        height={filteredData.length * 40} // Dynamic height based on rows
        data={filteredData}
        layout="vertical"
        margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis type="category" dataKey="affected_country" />
        <Tooltip />
        <Bar dataKey="count">
          {filteredData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={index < 5 ? COLORS[index] : "#716cccff"}
            />
          ))}
        </Bar>
      </BarChart>
    </div>
  );
}


export function ActorType_BarChart({ incident_data, selectedIndustry }) {
  // Filter and sort data for selected industry
  const filteredData = incident_data
    .filter(
      (item) =>
        item.industry === selectedIndustry &&
        item.actor &&
        item.actor_type &&
        item.count
    )
    .sort((a, b) => b.count - a.count); // descending by count

  // Color map for actor_type
  const uniqueActorTypes = [...new Set(filteredData.map((d) => d.actor_type))];
  const colorPalette = [
    "#3f37d1ff",
    "#716cccff",
    "#ff6f61",
    "#f7b267",
    "#6a0572",
    "#00917c"
  ];
  const colorMap = uniqueActorTypes.reduce((acc, actorType, idx) => {
    acc[actorType] = colorPalette[idx % colorPalette.length];
    return acc;
  }, {});

  // Show top 10 only, but allow scroll for rest
  const visibleCount = 10;
  const containerHeight = visibleCount * 40; // 40px per bar approx

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
        <div style={{ backgroundColor: "white", border: "1px solid #ccc", padding: 10 }}>
            <p><strong>Actor:</strong> {label}</p>
            <p><strong>Actor Type:</strong> {data.actor_type}</p>
            <p><strong>Count:</strong> {data.count}</p>
        </div>
        );
    }
    return null;
    };

  return (
    <div
      style={{
        height: containerHeight,
        overflowY: "scroll",
        paddingRight: 10 // prevent scrollbar overlap
      }}
    >
      <BarChart
        layout="vertical"
        width={600}
        height={filteredData.length * 40} // full height for all bars
        data={filteredData}
        margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="actor" type="category" />
        <Tooltip content={<CustomTooltip />} />
        <Bar
          dataKey="count"
          label={{ position: "right", fill: "#000", fontSize: 12 }}
        >
          {filteredData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colorMap[entry.actor_type]} />
          ))}
        </Bar>
      </BarChart>
    </div>
  );
}
