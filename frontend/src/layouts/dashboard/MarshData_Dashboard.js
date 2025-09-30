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
                  title="Claims over time"
                  chart={sales}
                />
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <DefaultDoughnutChart
                  color="secondary"
                  title="Coverage of Claims"
                  chart={{
                    labels: ["Desktop", "Tablet", "Mobile"],
                    datasets: { label: "Devices", data: [63, 15, 22] }
                  }}
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
                <ReportsBarChart
                  color="secondary"
                  title="Change in Claims over Time"
                  description="Money is the most common motive at 60% (50) followed by Espionage"
                  date="campaign sent 2 days ago"
                  chart={reportsBarChartData}
                />                
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="secondary"
                  title="Estimated Loss from Claims"
                  description="Money is the most common motive at"
                  date="campaign sent 2 days ago"
                  chart={reportsBarChartData}
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
                  chart={reportsBarChartData}
                />                
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <StackedBarChart
                  color="secondary"
                  title="Affected Countries"
                  date="campaign sent 2 days ago"
                  chart={{
                    labels: ["Countries"],
                    datasets: [
                      { label: "Singapore", data: [25], backgroundColor: "navy" },
                      { label: "USA", data: [35], backgroundColor: "blue" },
                      { label: "China", data: [40], backgroundColor: "teal" },
                    ],
                  }}
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
                      labels: ['FINPRO-Comprehensive Crime',
                        'FINPRO-Cyber & Privacy Liability',
                        'FINPRO-Investment Management Liability (IMI)',
                        'FINPRO-Professional Indemnity (PI)',
                        'Others',
                        'Professional/Management Liability',
                        'Property',
                        'Public/General Liability'],
                      datasets: [
                        {
                          label: 'No',
                          data: [10, 2, 4, 8, 6, 8, 7, 9],
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
                  ["From", "To", "Weight"],
                  ['FINPRO-Comprehensive Crime', "X", 5],
                  ['FINPRO-Comprehensive Crime', "Y", 7],
                  ['FINPRO-Investment Management Liability (IMI)', "X", 6],
                  ['FINPRO-Investment Management Liability (IMI)', "Z", 2],
                ]}}
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
