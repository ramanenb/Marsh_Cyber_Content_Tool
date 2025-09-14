import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { XAxis, YAxis, CartesianGrid, Tooltip, Legend,
        Line, LineChart, Pie, Cell, PieChart} from "recharts";

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
          <Line type="monotone" dataKey="count" stroke="#8884d8" />
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