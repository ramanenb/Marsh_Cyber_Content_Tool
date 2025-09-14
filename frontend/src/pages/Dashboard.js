import React, { useState, useEffect } from "react";
import { XAxis, YAxis, CartesianGrid, Tooltip, Legend,
        Line, LineChart, Pie, Cell, PieChart } from "recharts";
import { IndustryOverTime_LineChart, Event_DonutChart } from "./Charts";

// ✅ Custom hook to fetch data safely
function useFetchData(endpoint_link) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(endpoint_link, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    })
      .then((resp) => resp.json())
      .then((resp) => {
        const byIndustry = resp?.result?.by_industry || [];
        const totals_by_group = resp?.result?.totals_by_group || [];
        setData([...byIndustry, ...totals_by_group]);
      })
      .catch((err) => setError(err))
      .finally(() => setLoading(false));
  }, [endpoint_link]);

  return { data, loading, error };
}

export default function VizDashboard() {
  const [selectedIndustry, setSelectedIndustry] = useState("All Industries");

  // ✅ Fetch datasets
  const {
    data: incidentsByIndustryYearMonth,
    loading: loadingYearMonth,
  } = useFetchData("http://127.0.0.1:8000/api/aggregate_by_industry_and_month");

  const {
    data: incidentsByIndustry_EventSubtype,
    loading: loadingSubtype,
  } = useFetchData("http://127.0.0.1:8000/api/aggregate_by_industry?group_by_field=event_subtype");

  const {
    data: incidentsByIndustry_Motive,
    loading: loadingMotive,
  } = useFetchData("http://127.0.0.1:8000/api/aggregate_by_industry?group_by_field=motive");

  // ✅ Build dropdown options safely
  const industries = [
    ...new Set((incidentsByIndustryYearMonth || []).map((item) => item.industry).filter(Boolean)),
  ];

  return (
    <div>
      <p>this is a dashboard page</p>
      <li>
        <a href="/slidesCreationTool">Cyber Content Tool Page</a>
      </li>

      {/* Industry Dropdown */}
      <div>
        {loadingYearMonth ? (
          <p>Loading industries...</p>
        ) : (
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
        )}
      </div>

      {/* Charts */}
      {!loadingYearMonth && (
        <IndustryOverTime_LineChart
          incident_data={incidentsByIndustryYearMonth}
          selectedIndustry={selectedIndustry}
        />
      )}
      {!loadingSubtype && (
        <Event_DonutChart
          incident_data={incidentsByIndustry_EventSubtype}
          selectedIndustry={selectedIndustry}
          col_used="event_subtype"
        />
      )}
      {!loadingMotive && (
        <Event_DonutChart
          incident_data={incidentsByIndustry_Motive}
          selectedIndustry={selectedIndustry}
          col_used="motive"
        />
      )}
    </div>
  );
}
