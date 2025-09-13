import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend} from "recharts";

export default function VizDashboard() {
  const [incidentsByIndustryYearMonth, setIncidents] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState("All Industries");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/aggregate_by_industry_and_month", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((resp) => resp.json())
      .then((resp) => {
        const byIndustry = resp.result?.by_industry || [];
        const totalsByMonth = resp.result?.totals_by_month || [];
        setIncidents(byIndustry.concat(totalsByMonth));
        })
      .catch((error) => console.log(error));
  }, []);

  // Get all unique industries for DROPDOWN (avoid crash on empty data)
  const industries = [
    ...new Set(incidentsByIndustryYearMonth.map((item) => item.industry).filter(Boolean)),
  ];

  return (
    <div>
      <p>this is a dashboard page</p>
      <li>
        <a href="/slidesCreationTool">Cyber Content Tool Page</a>
      </li>

    {/* Dropdown to select industry */}
      <div>
        <select
          value={selectedIndustry}
          onChange={(e) => setSelectedIndustry(e.target.value)}
        >
          {industries.map((ind) => (
            <option key={ind} value={ind}>
              {ind}
            </option>
          ))}
        </select>
      </div>

    {/* Pass data down into chart */}
      <MyChart incidents={incidentsByIndustryYearMonth} selectedIndustry={selectedIndustry} />
    </div>
  );
}


function MyChart({ incidents, selectedIndustry }) {

  // Filter dynamically
  const filteredData = incidents
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
