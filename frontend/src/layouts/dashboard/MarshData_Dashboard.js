/**
=========================================================
* End User Dashboard Page -- data taken from MARSH
=========================================================
*/

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/MarshDashboardNavbar";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import DefaultDoughnutChart from "examples/Charts/DoughnutCharts/DefaultDoughnutChart";
import HorizontalBarChart from "examples/Charts/BarCharts/HorizontalBarChart";

// Data
import reportsBarChartData from "layouts/dashboard/data/reportsBarChartData";
import reportsLineChartData from "layouts/dashboard/data/reportsLineChartData";

// Material Data Table 2 React example components
import DataTable from "examples/Tables/DataTable";
import authorsTableData from "layouts/tables/data/authorsTableData";
import StackedBarChart from "examples/Charts/BarCharts/StackedBarChart/StackedBar";
import RadarChart from "examples/Charts/RadarChart";
import SankeyChart from "examples/Charts/SankeyChart/Sankey";

import { useState, useEffect } from "react";

// process JSON after it has been fetched
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
        const pulled_data = resp?.result || resp?.industries || [];
        setData(pulled_data);
      })
      .catch((err) => setError(err))
      .finally(() => {console.log("Failed"); setLoading(false);});
  }, [endpoint_link]);

  return { data, loading, error };
}

function MarshData_Dashboard() {
  const { sales, tasks } = reportsLineChartData;
  const { columns, rows } = authorsTableData();

  /* HANDLE REQUIRED TO POPULATE THE TOPBAR FILTER DROPDOWN */
  const [selectedIndustry, setSelectedIndustry] = useState("All Industries");
  // Function to handle the industry selection change
  const handleIndustryChange = (event) => {
    setSelectedIndustry(event);
  };
  const {
    data: Industries,
    loading: loadingIndustry,
  } = useFetchData("http://127.0.0.1:8000/api/getIndustries");
  // Build Industry dropdown options safely
  const ALL_IndustriesValues = [
    "All Industries",
    ...new Set(Object.values(Industries|| {})),
  ];


  const [selected_ClaimCause, setSelected_ClaimCause] = useState("All Causes");
  // Function to handle the Causes selection change
  const handleClaimsCauseChange = (event) => {
    setSelected_ClaimCause(event);
  };
  const {
    data: ClaimCauses,
    loading: loadingClaimCauses,
  } = useFetchData("http://127.0.0.1:8000/api/unique_valueFOR?group_by_field=Cause");
  // Build Industry dropdown options safely
  const ALL_ClaimCausesValues = [
    "All Causes",
    ...new Set(Object.values(ClaimCauses|| {})),
  ];


  const [selected_ClaimType, setSelected_ClaimType] = useState("All Types");
  // Function to handle the Types selection change
  const handleClaimsTypeChange = (event) => {
    setSelected_ClaimType(event);
  };
  const {
    data: ClaimTypes,
    loading: loadingClaimType,
  } = useFetchData("http://127.0.0.1:8000/api/unique_valueFOR?group_by_field=Type%20of%20Claim");
  // Build Industry dropdown options safely
  const ALL_ClaimTypeValues = [
    "All Types",
    ...new Set(Object.values(ClaimTypes|| {})),
  ];


  const [selected_TimePeriod, setSelected_TimePeriod] = useState("5Y");
  // Function to handle the Types selection change
  const handleTimePeriodChange = (event) => {
    setSelected_TimePeriod(event);
  };

  // ✅ Fetch datasets
  const {
    data: incidentsByIndustry_TP_YearMonth,
    loading: loadingYearMonth,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregate_by_filters?industry=${selectedIndustry}&period=${selected_TimePeriod}&isChange=${0}`);
  const {
    data: incidentsByIndustry_TP_Coverage,
    loading: loadingCoverage,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregateby_Claim_Coverage?industry=${selectedIndustry}&period=${selected_TimePeriod}`);
  const {
    data: incidentsByIndustry_TPYearMonth_CHANGE,
    loading: loadingYearMonth_Change,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregate_by_filters?industry=${selectedIndustry}&period=${selected_TimePeriod}&isChange=${1}`);
  const {
    data: incidentsByIndustry_TPY_LossEstimate,
    loading: loadingYearMonth_LossEstimate,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregateby_Loss_Estimate?industry=${selectedIndustry}&period=${selected_TimePeriod}&bins=${5}`);
  const {
    data: incidentsByIndustry_TPY_Cause,
    loading: loadingYearMonth_Cause,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregateby_CauseOrType?industry=${selectedIndustry}&period=${selected_TimePeriod}&group_by_field=Cause`);
  const {
    data: incidentsByIndustry_TPY_Types,
    loading: loadingYearMonth_Types,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregateby_CauseOrType?industry=${selectedIndustry}&period=${selected_TimePeriod}&group_by_field=Type%20of%20Claim`);
  const {
    data: incidentsByIndustry_TPY_Countries,
    loading: loadingYearMonsth_TPY_Countries
  } = useFetchData(`http://127.0.0.1:8000/api/aggregateby_AffectedCountries?industry=${selectedIndustry}&period=${selected_TimePeriod}&group_by_field=Type%20of%20Claim`);
const {
    data: incidentsByIndustry_TPY_Sankey,
    loading: loadingYearMonsth_TPY_Sankey
  } = useFetchData(`http://127.0.0.1:8000/api/aggregateby_Claim_Sankey?industry=${selectedIndustry}&period=${selected_TimePeriod}`);


  return (
    <DashboardLayout>
      <DashboardNavbar 
        dashboardView={true}
        Selected_Industry={selectedIndustry}
        ALL_IndustryValues={ALL_IndustriesValues}
        onIndustry_FilterChange={handleIndustryChange}

        selected_ClaimCause={selected_ClaimCause}
        ALL_ClaimsCauseValues={ALL_ClaimCausesValues}
        onCause_FilterChange={handleClaimsCauseChange}

        selected_ClaimType={selected_ClaimType}
        ALL_ClaimsTypeValues={ALL_ClaimTypeValues}
        onType_FilterChange={handleClaimsTypeChange}

        selected_TimePeriod={selected_TimePeriod}
        ALL_TimePeriodValues={["3M", "6M", "1Y", "3Y", "5Y"]}
        onTimePeriod_FilterChange={handleTimePeriodChange}
      />

      {/* First row of the Dashboard */}
      <MDBox py={3}>
      
        <MDBox mt={2}>
          <Grid container spacing={2.5}>
            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="secondary"
                  title="Claims over time"
                  chart={incidentsByIndustry_TP_YearMonth?.[selected_ClaimType]?.[selected_ClaimCause] || { labels: [], datasets: [] }}
                />
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <DefaultDoughnutChart
                  color="secondary"
                  title="Coverage of Claims"
                  chart={incidentsByIndustry_TP_Coverage?.[selected_ClaimType]?.[selected_ClaimCause] || { labels: [], datasets: [] }}
                />
              </MDBox>
            </Grid>

          </Grid>
        </MDBox>
        
        {/* Second row of the Dashboard */}
        <MDBox mt={3}>
          <Grid container spacing={3}>

            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <ReportsLineChart
                  color="secondary"
                  title="Change in Claims over Time"
                  description="Money is the most common motive at 60% (50) followed by Espionage"
                  date="campaign sent 2 days ago"
                  chart={incidentsByIndustry_TPYearMonth_CHANGE?.[selected_ClaimType]?.[selected_ClaimCause] || { labels: [], datasets: [] }}
                />                
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="secondary"
                  title="Estimated Loss from Claims (USD)"
                  description="In Thousands"
                  date="campaign sent 2 days ago"
                  chart={incidentsByIndustry_TPY_LossEstimate?.[selected_ClaimType]?.[selected_ClaimCause] || { labels: [], datasets: [] }}
                />
              </MDBox>
            </Grid>
            
          </Grid>
        </MDBox>

        {/* Third row of the Dashboard */}
        <MDBox mt={3}>
          <Grid container spacing={3}>

            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <HorizontalBarChart
                  color="secondary"
                  title="Cause of Claims"
                  date="campaign sent 2 days ago"
                  chart={incidentsByIndustry_TPY_Cause?.["Output"]?.[selected_ClaimType] || { labels: [], datasets: [] }}
                />                
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <StackedBarChart
                  color="secondary"
                  title="Affected Countries"
                  date="campaign sent 2 days ago"
                  chart={
                    incidentsByIndustry_TPY_Countries?.[selected_ClaimType]?.[selected_ClaimCause] || { 
                    labels: ["Countries"],
                    datasets: [
                      { label: "No Data", data: [25], backgroundColor: "navy" }
                    ],
                   }
                  }
                />  
              </MDBox>
            </Grid>
            
          </Grid>
        </MDBox>

        {/* Fourth row of the Dashboard */}
        <MDBox mt={3}>
          <Grid container spacing={3}>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                   <RadarChart 
                   color="secondary"
                   title="Types of Claims"
                   chart= {{
                      labels: incidentsByIndustry_TPY_Types?.["Output"]?.[selected_ClaimCause]?.["labels"],
                      datasets: [
                        {
                          label: "No",
                          data: incidentsByIndustry_TPY_Types?.["Output"]?.[selected_ClaimCause]?.["datasets"]?.["data"],
                          borderColor: 'rgba(255, 99, 132, 1)'
                        },
                      ],
                    }}/>       
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <SankeyChart
                color = "secondary"
                title = "Result of Claims"
                chart = {{ data: [ 
                           ["From","To","Weight"],
                           ...(incidentsByIndustry_TPY_Sankey?.[selected_ClaimType]?.[selected_ClaimCause]?.["data"] || []) 
                           ] 
                        }}
                />
              </MDBox>
            </Grid>
            
          </Grid>
        </MDBox>

        {/* Fifth row of the Dashboard */}
        <MDBox mt={3}>
          <Grid container spacing={3}>

            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <HorizontalBarChart
                  color="secondary"
                  title="Claims Handling Countries"
                  date="campaign sent 2 days ago"
                  chart={reportsBarChartData}
                /> 
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="secondary"
                  title="Time Taken to Report Claims"
                  date="campaign sent 2 days ago"
                  chart={reportsBarChartData}
                />
              </MDBox>
            </Grid>

          </Grid>
        </MDBox>
        
        <MDBox>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={12}>
              <Card>
              <MDBox
                mx={2}
                mt={-.5}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDTypography variant="h6" color="white">
                  Cyber Incident Table
                </MDTypography>
              </MDBox>

              <MDBox pt={3}>
                <DataTable
                  table={{ columns, rows }}
                  isSorted={false}
                  entriesPerPage={false}
                  showTotalEntries={false}
                  noEndBorder
                />
              </MDBox>
            </Card>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>

    </DashboardLayout>
  );
}

export default MarshData_Dashboard;
