/**
=========================================================
* End User Dashboard Page -- data taken from INTERNET
=========================================================
*/

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDBadge from "components/MDBadge";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/ActualDashboardNavbar";

import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import DefaultDoughnutChart from "examples/Charts/DoughnutCharts/DefaultDoughnutChart";
import HorizontalBarChart from "examples/Charts/BarCharts/HorizontalBarChart";
import DataTable from "examples/Tables/DataTable";

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
        const pulled_data = resp?.result || [];
        setData(pulled_data);
      })
      .catch((err) => setError(err))
      .finally(() => {setLoading(false);});
  }, [endpoint_link]);

  return { data, loading, error };
}

function Dashboard() {
  const [selected_TimePeriod, setSelected_TimePeriod] = useState("1Y");
  // Function to handle the Types selection change
  const handleTimePeriodChange = (event) => setSelected_TimePeriod(event);

  const [selectedIndustry, setSelectedIndustry] = useState("All Industries");
  // Function to handle the industry selection change
  const handleIndustryChange = (event) => setSelectedIndustry(event);

  // ✅ Fetch datasets
  const {
    data: incidentsByIndustryYearMonth,
    loading: loadingYearMonth,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregate_by_industry_and_month?period=${selected_TimePeriod}`);
  // Build Industry dropdown options safely
  const ALL_IndustryValues = [
    ...new Set(Object.keys(incidentsByIndustryYearMonth || {})),
  ];

  const {
    data: incidentsByIndustry_EventSubtype,
    loading: loadingSubtype,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregate_by_industry?group_by_field=event_subtype&period=${selected_TimePeriod}`);

  const {
    data: incidentsByIndustry_Motive,
    loading: loadingMotive,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregate_by_industry?group_by_field=motive&period=${selected_TimePeriod}`);

  const {
    data: incidentsByIndustry_Actor,
    loading: loadingActor,
  } = useFetchData(`http://127.0.0.1:8000/api/aggregate_by_industry_and_actors?period=${selected_TimePeriod}`);

  /* ✅ Code Needed to generate the TABLE at the bottom */
  const {
    data: Incidents, loading: loadingIncidents, error: errorIncidents
  } = useFetchData(`http://127.0.0.1:8000/api/list_incidents?industry=${encodeURIComponent(selectedIndustry)}&period=${selected_TimePeriod}`);

  const {data: latestIncidentDate, loading: loadingLatestIncidentDate} = useFetchData(`http://127.0.0.1:8000/api/Internet_Data`);
  
  const columns = [
      { Header: "Victim", accessor: "Victim", width: "45%", align: "left"},
      { Header: "Industry", accessor: "Industry", align: "left" },
      { Header: "Event date", accessor: "Event_date", align: "center" },
      { Header: "Event type", accessor: "Event_type", align: "center" },
      { Header: "Attacker", accessor: "Attacker", align: "center" },
      { Header: "Attacker Origin", accessor: "Attacker_Origin", align: "center" },
      { Header: "Victim Origin", accessor: "Victim_Origin", align: "center" },
      { Header: "Motive", accessor: "Motive", align: "center" },  
      { Header: "Description", accessor: "Description", align: "center" },
      { Header: "Source", accessor: "Source_Link", align: "center" },                   
  ];

  const Author = ({ image, name, email }) => (
      <MDBox display="flex" alignItems="left" lineHeight={1}>
        {/* <MDAvatar src={image} name={name} size="sm" /> */}
        <MDBox ml={0} lineHeight={1}>
          <MDTypography display="block" variant="button" fontWeight="medium">
            {name}
          </MDTypography>
          <MDTypography variant="caption">{email}</MDTypography>
        </MDBox>
      </MDBox>
    );

    // code to create the JSX for each row
    var rows = Incidents
  .map(Incident_Info => (
    {
      Victim: <Author name={Incident_Info.Victim} />,
      Industry: <Author name={Incident_Info.Industry} />,
      Event_date: (
        <MDTypography variant="h6" color="text" fontWeight="medium">
          {Incident_Info.Event_date}
        </MDTypography>
      ),
      Event_type: (
        <MDBox ml={-1}>
          <MDBadge
            badgeContent={Incident_Info.event_subtype}
            color="warning"
            variant="gradient"
            size="lg"
          />
        </MDBox>
      ),
      Attacker: <Author name={Incident_Info.Attacker} email={Incident_Info.actor_type} />,
      Attacker_Origin: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          {Incident_Info.Attacker_Origin}
        </MDTypography>
      ),
      Victim_Origin: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          {Incident_Info.Victim_Origin}
        </MDTypography>
      ),
      Motive: (
        <MDTypography variant="h6" color="text" fontWeight="medium">
          {Incident_Info.Motive}
        </MDTypography>
      ),
      Description: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          {Incident_Info.Description}
        </MDTypography>
      ),
      Source_Link: (
        <MDTypography
          component="a"
          href={Incident_Info.Link}
          variant="button"
          color="text"
          fontWeight="medium"
        >
          Link
        </MDTypography>
      ),
    }
  ));


  return (
    <DashboardLayout>
      {loadingYearMonth ? 
        (<p> Loading Navbar....</p>) :

        (<DashboardNavbar 
          dashboardView = {true}
          Selected_Industry = {selectedIndustry}
          ALL_IndustryValues = {ALL_IndustryValues}
          onIndustry_FilterChange = {handleIndustryChange}

          selected_TimePeriod={selected_TimePeriod}
          ALL_TimePeriodValues={["1Y", "3Y", "5Y"]}
          onTimePeriod_FilterChange={handleTimePeriodChange}
          latestIncidentDate={latestIncidentDate}
        />)
      }

      {/* First row of the Dashboard */}
      <MDBox py={3}>
      
        <MDBox mt={2}>
          <Grid container spacing={2.5}>
            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <ReportsLineChart
                  color="secondary"
                  title="How many incidents occured over time?"
                  description={` 
                      ${Math.round(
                        100.0 * (incidentsByIndustryYearMonth?.[selectedIndustry]?.["datasets"]?.["data"]?.at(-1) - incidentsByIndustryYearMonth?.[selectedIndustry]?.["datasets"]?.["data"]?.at(-2)) /
                        incidentsByIndustryYearMonth?.[selectedIndustry]?.["datasets"]?.["data"]?.at(-2)
                        ) || "No Data"
                      }%
                      change from ${incidentsByIndustryYearMonth?.[selectedIndustry]?.["labels"]?.at(-2) || "No Data"} to ${incidentsByIndustryYearMonth?.[selectedIndustry]?.["labels"]?.at(-1) || "No Data"}
                    `}
                  chart={incidentsByIndustryYearMonth?.[selectedIndustry] || { labels: [], datasets: [] }}
                />
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <DefaultDoughnutChart
                  color="secondary"
                  title={"What is the impact of the attacks?"}
                  description={` 
                      ${incidentsByIndustry_EventSubtype?.[selectedIndustry]?.["labels"]?.at(0) || "No Data"} accounts for
                      ${Math.round(
                        100.0 * incidentsByIndustry_EventSubtype?.[selectedIndustry]?.["datasets"]?.["data"]?.at(0) /
                        incidentsByIndustry_EventSubtype?.[selectedIndustry]?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0)
                        ) || "No Data"
                      }% of total incidents
                  `}
                  chart={incidentsByIndustry_EventSubtype?.[selectedIndustry] || { labels: [], datasets: [] }}
                />
              </MDBox>
            </Grid>

          </Grid>
        </MDBox>

        <MDBox mt={3}>
          <Grid container spacing={3}>

            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <HorizontalBarChart
                  color="secondary"
                  title="Who are the attackers?"
                  date="campaign sent 2 days ago"
                  description={` 
                      First 2 Attackers accounts for
                      ${Math.round(
                        100.0 * incidentsByIndustry_Actor?.[selectedIndustry]?.["datasets"]?.["data"]?.at(0) /
                        incidentsByIndustry_Actor?.[selectedIndustry]?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0)
                      ) || "No Data"
                      }% and 
                      ${Math.round(
                        100.0 * incidentsByIndustry_Actor?.[selectedIndustry]?.["datasets"]?.["data"]?.at(1) /
                        incidentsByIndustry_Actor?.[selectedIndustry]?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0)
                      ) || "No Data"
                      }% respectively of total incidents
                  `}
                  chart={incidentsByIndustry_Actor?.[selectedIndustry] || { labels: [], datasets: [] }}
                />                
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="secondary"
                  title="What drives attackers?"
                  date="campaign sent 2 days ago"
                  chart={incidentsByIndustry_Motive?.[selectedIndustry] || { labels: [], datasets: [] }}
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

export default Dashboard;
