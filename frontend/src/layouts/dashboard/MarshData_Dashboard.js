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
import DashboardNavbar from "examples/Navbars/ActualDashboardNavbar";
import Footer from "examples/Footer";
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

function MarshData_Dashboard() {
  const { sales, tasks } = reportsLineChartData;
  const { columns, rows } = authorsTableData();

  return (
    <DashboardLayout>
      <DashboardNavbar 
        dashboardView={true}
        Selected_Industry={"All Industries"}
        ALL_IndustryValues={["All Industrues", "Transport"]}
        onIndustry_FilterChange={(ele) => {ele.console.log(ele)}}
      />

      {/* First row of the Dashboard */}
      <MDBox py={3}>
      
        <MDBox mt={2}>
          <Grid container spacing={2.5}>
            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <ReportsLineChart
                  color="secondary"
                  title="How many incidents occured over time?"
                  description={
                    <>
                      Marsh data ee
                    </>
                  }
                  chart={sales}
                />
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <DefaultDoughnutChart
                  color="secondary"
                  title="What is the impact of the attacks?"
                  description="Disruption is the biggest event type at 70%"
                  chart={{
                    labels: ["Desktop", "Tablet", "Mobile"],
                    datasets: { label: "Devices", data: [63, 15, 22] },
                    backgroundColors: [
                      'rgba(255, 99, 132, 0.8)',
                      'rgba(54, 162, 235, 0.8)',
                      'rgba(255, 206, 86, 0.8)',
                    ]
                  }}
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
                  description="Avg number of attacks is 5 with APT29 is the most active threat actor at 5 attacks"
                  date="campaign sent 2 days ago"
                  chart={reportsBarChartData}
                />                
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="secondary"
                  title="What drives attackers?"
                  description="Money is the most common motive at 60% (50) followed by Espionage"
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
