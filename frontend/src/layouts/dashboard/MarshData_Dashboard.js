/**
=========================================================================
* End User Dashboard Page -- data taken from MARSH propietary data source
=========================================================================
*/

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/MarshDashboardNavbar";

// Material Dashboard 2 React example components
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import DefaultDoughnutChart from "examples/Charts/DoughnutCharts/DefaultDoughnutChart";
import HorizontalBarChart from "examples/Charts/BarCharts/HorizontalBarChart";
import DataTable from "examples/Tables/DataTable";
import StackedBarChart from "examples/Charts/BarCharts/StackedBarChart/StackedBar";
import RadarChart from "examples/Charts/RadarChart";
import SankeyChart from "examples/Charts/SankeyChart/Sankey";

import { useState, useEffect, useMemo } from "react";
import { fetchWithFallback } from "utils/apiConfig";

// process JSON after it has been fetched
function useFetchData(endpoint_link) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWithFallback(endpoint_link)
      .then((resp) => resp.json())
      .then((resp) => {
        const pulled_data = resp?.result || resp?.industries || [];
        setData(pulled_data);
        setLoading(false);
      })
      .catch((err) => {setError(err); setLoading(false);})
      .finally(() => 0);
  }, [endpoint_link]);

  return { data, loading, error };
}

// function to create the necessary variables for the FILTERS
function useCreateFilterVariables({defaultValue, endpoint_link}) {
  const [selectedOption, setSelectedOption] = useState(defaultValue);
  const handleValueChange = (event) => setSelectedOption(event);

  const { data, loading } = useFetchData(endpoint_link);
  // re-render only when data or defaultValue changes. Add in default value w pulled data
  let ALL_Values = useMemo(
    () => [defaultValue, 
          ...new Set(Object.values(data || {}))
        ],
    [data, defaultValue]
  );

  return { selectedOption, handleValueChange, ALL_Values, loading };
}

function MarshData_Dashboard() {
  // Create FILTER variables
  const [selected_TimePeriod, setSelected_TimePeriod] = useState("1Y");
  const handleTimePeriodChange = (event) => setSelected_TimePeriod(event);

  // 2️. INDUSTRY FILTER
  const { selectedOption: selectedIndustry, handleValueChange: handleIndustryChange,
    ALL_Values: ALL_IndustriesValues, loadingValues: loadingIndustry,
  } = useCreateFilterVariables({
    defaultValue: "All Industries",
    endpoint_link: "/api/getIndustries",
  });

  // 3️. CLAIM CAUSE FILTER
  const { selectedOption: selected_ClaimCause, handleValueChange: handleClaimsCauseChange,
    ALL_Values: ALL_ClaimCausesValues, loadingValues: loadingClaimCauses,
  } = useCreateFilterVariables({
    defaultValue: "All Causes",
    endpoint_link: `/api/unique_valueFOR?group_by_field=Cause&period=${selected_TimePeriod}&industry=${selectedIndustry}`,
  });

  // 4️. CLAIM TYPE FILTER
  const { selectedOption: selected_ClaimType, handleValueChange: handleClaimsTypeChange,
    ALL_Values: ALL_ClaimTypeValues, loadingValues: loadingClaimType,
  } = useCreateFilterVariables({
    defaultValue: "All Types",
    endpoint_link: `/api/unique_valueFOR?group_by_field=Type%20of%20Claim&period=${selected_TimePeriod}&industry=${selectedIndustry}`,
  });

  // Fetch datasets
  const {
    data: incidentsByIndustry_TP_YearMonth, loading: loadingYearMonth,
  } = useFetchData(`/api/aggregate_by_filters?industry=${selectedIndustry}&period=${selected_TimePeriod}&isChange=${0}`);
  const {
    data: incidentsByIndustry_TP_Coverage, loading: loadingCoverage,
  } = useFetchData(`/api/aggregateby_Claim_Coverage?industry=${selectedIndustry}&period=${selected_TimePeriod}`);
  const {
    data: incidentsByIndustry_TPYearMonth_CHANGE, loading: loadingYearMonth_Change,
  } = useFetchData(`/api/aggregate_by_filters?industry=${selectedIndustry}&period=${selected_TimePeriod}&isChange=${1}`);
  const {
    data: incidentsByIndustry_TPY_LossEstimate, loading: loadingYearMonth_LossEstimate,
  } = useFetchData(`/api/aggregateby_Loss_Estimate?industry=${selectedIndustry}&period=${selected_TimePeriod}&bins=${5}`);
  const {
    data: incidentsByIndustry_TPY_Cause, loading: loadingYearMonth_Cause,
  } = useFetchData(`/api/aggregateby_CauseOrType?industry=${selectedIndustry}&period=${selected_TimePeriod}&group_by_field=Cause`);
  const {
    data: incidentsByIndustry_TPY_Types, loading: loadingYearMonth_Types,
  } = useFetchData(`/api/aggregateby_CauseOrType?industry=${selectedIndustry}&period=${selected_TimePeriod}&group_by_field=Type%20of%20Claim`);
  const {
    data: incidentsByIndustry_TPY_Countries, loading: loadingYearMonsth_TPY_Countries
  } = useFetchData(`/api/aggregateby_AffectedCountries?industry=${selectedIndustry}&period=${selected_TimePeriod}&group_by_field=Type%20of%20Claim`);
  const {
    data: incidentsByIndustry_TPY_Sankey, loading: loadingYearMonsth_TPY_Sankey
  } = useFetchData(`/api/aggregateby_Claim_Sankey?industry=${selectedIndustry}&period=${selected_TimePeriod}`);
  const {
    data: incidentsByIndustry_TPY, loading: loadingYearMonsth_TPY
  } = useFetchData(`/api/aggregateby_IndivIncidents?industry=${selectedIndustry}&period=${selected_TimePeriod}&Cause=${selected_ClaimCause}&ClaimType=${selected_ClaimType}`);
  const {
    data: incidentsByIndustry_TPY_Cause_SumLoss, loading: loadingYearMonth_Cause_SumLoss,
  } = useFetchData(`/api/aggregateby_CauseOrType?industry=${selectedIndustry}&period=${selected_TimePeriod}&group_by_field=Cause&aggregation_method=Sum_Loss`);
  const {
    data: incidentsByIndustry_TPY_Cause_AvgLoss, loading: loadingYearMonth_Cause_AvgLoss,
  } = useFetchData(`/api/aggregateby_CauseOrType?industry=${selectedIndustry}&period=${selected_TimePeriod}&group_by_field=Cause&aggregation_method=Avg_Loss`);
  
  const {data: latestIncidentDate, loading: loadingLatestIncidentDate} = useFetchData(`/api/Marsh_Data`);

  // PREP structure of components for the claims table at the very BOTTOM
  const Author = ({ name, email }) => (
        <MDBox display="flex" alignItems="left" lineHeight={1}>
          <MDBox ml={0} lineHeight={1}>
            <MDTypography display="block" variant="button" fontWeight="medium">
              {name}
            </MDTypography>
            <MDTypography variant="caption">{email}</MDTypography>
          </MDBox>
        </MDBox>
      );

  const columns = [
      { Header: "Client", accessor: "Client", width: "45%", align: "left"},
      { Header: "Industry", accessor: "Industry", align: "left" },
      { Header: "Incident date", accessor: "Incident_date", align: "center" },
      { Header: "Cause", accessor: "Cause", align: "center" },
      { Header: "Claim Type", accessor: "Claim_Type", align: "center" },
      { Header: "Marsh Loss Estimate (USD)", accessor: "Marsh_Loss_Estimate_USD", align: "center" },  
      { Header: "Total Paid (USD)", accessor: "Total_Paid_USD", align: "center" },  
      { Header: "Description", accessor: "Description", align: "center" },
      { Header: "Loss Details", accessor: "Loss_Details", align: "center" },  
      { Header: "Claim Result", accessor: "Claim_Result", align: "center" },  
      { Header: "Claim Pos", accessor: "Claim_Pos", align: "center" },  
      { Header: "Policy Currency", accessor: "Policy_Currency", align: "center" },  
      { Header: "Total Paid", accessor: "Total_Paid", align: "center" },  
  ];

  var rows = incidentsByIndustry_TPY
    .map(Incident_Info => (
      {
        Client: <Author name={Incident_Info?.Client} email={""}/>
        ,
        Industry: <Author name={Incident_Info?.Industry} />,
        Incident_date: (
          <MDTypography variant="h6" color="text" fontWeight="medium">
            {Incident_Info?.Incident_Date}
          </MDTypography>
        ),
        Cause: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {Incident_Info?.Cause}
          </MDTypography>
        ),
        Claim_Type: <Author name={Incident_Info?.Claim_Type} email={Incident_Info?.Claim_SubType} />,
        Marsh_Loss_Estimate_USD: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {Math.round(Incident_Info?.Marsh_Loss_Estimate_USD)}
          </MDTypography>
        ),
        Total_Paid_USD: (
          <MDTypography variant="h6" color="text" fontWeight="medium">
            {Math.round(Incident_Info?.Total_Paid_USD)}
          </MDTypography>
        ),
        Description: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {Incident_Info?.Description}
          </MDTypography>
        )
        ,
        Loss_Details: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {Incident_Info?.Loss_Details}
          </MDTypography>
        )
        ,
        Claim_Result: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {Incident_Info?.Claim_Result}
          </MDTypography>
        )
        ,
        Claim_Pos: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {Incident_Info?.Claim_Pos}
          </MDTypography>
        )
        ,
        Policy_Currency: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {Incident_Info?.Policy_Currency}
          </MDTypography>
        ),
        Total_Paid: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {Math.round(Incident_Info?.Total_Paid)}
          </MDTypography>
        )
      }
    ));

  // Filtered data for each charts for easier readability-passed into chart data & description param
  var ClaimsOverTime_chData = incidentsByIndustry_TP_YearMonth?.[selected_ClaimType]?.[selected_ClaimCause]
  var CoverageClaims_chData = incidentsByIndustry_TP_Coverage?.[selected_ClaimType]?.[selected_ClaimCause]
  var ChangeInClaims_chData = incidentsByIndustry_TPYearMonth_CHANGE?.[selected_ClaimType]?.[selected_ClaimCause]
  var CauseOfClaims_chData = incidentsByIndustry_TPY_Cause?.["Output"]?.[selected_ClaimType]
  var TypesOfClaims_chData = incidentsByIndustry_TPY_Types?.["Output"]?.[selected_ClaimCause]
  var AffectedCountries_chData = incidentsByIndustry_TPY_Countries?.[selected_ClaimType]?.[selected_ClaimCause]
  var SumLossEsimate = incidentsByIndustry_TPY_Cause_SumLoss?.["Output"]?.[selected_ClaimType]

  // Dashboard code starts here
  return (
    <DashboardLayout>
      {loadingYearMonth ? 
        (<p> Loading Marsh Data....</p>) :

        (<DashboardNavbar 
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
          latestIncidentDate={latestIncidentDate}
        />)
      }

      {/* First row of the Dashboard */}
      <MDBox py={3}>
      
        <MDBox mt={2}>
          <Grid container spacing={2.5}>
            <Grid item xs={12} md={6} lg={8}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="secondary"
                  title="Claims over time"
                  chart={ClaimsOverTime_chData || { labels: [], datasets: [] }}
                  description={`The highest number of claims recorded was in
                      ${ClaimsOverTime_chData?.["labels"]?.at(
                        ClaimsOverTime_chData?.["datasets"]?.["data"]?.indexOf(Math.max(...(ClaimsOverTime_chData?.["datasets"]?.["data"] || [0])))
                      ) || "No Data"} with
                      ${Math.max(...(ClaimsOverTime_chData?.["datasets"]?.["data"] || [0])) || "No Data"} claims.

                      Average Monthly Claims is
                      ${Math.round(
                        ClaimsOverTime_chData?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0) /
                        ClaimsOverTime_chData?.["datasets"]?.["data"]?.length
                      ) || "No Data"}.
                    `}
                />
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <DefaultDoughnutChart
                  color="secondary"
                  title="Coverage of Claims"
                  chart={CoverageClaims_chData || { labels: [], datasets: [] }}
                  description={` 
                      ${CoverageClaims_chData?.["labels"]?.at(0) || "No Data"} accounts for
                      ${Math.round(
                        100.0 * CoverageClaims_chData?.["datasets"]?.["data"]?.at(0) /
                        CoverageClaims_chData?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0)
                        ) || "No Data"
                      }% of the total at ${CoverageClaims_chData?.["datasets"]?.["data"]?.at(0) || "No Data"} Claims.
                  `}
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
                  chart={ChangeInClaims_chData || { labels: [], datasets: [] }}
                  description={` 
                      ${Math.round(
                        100.0 * (ClaimsOverTime_chData?.["datasets"]?.["data"]?.at(-1) - ClaimsOverTime_chData?.["datasets"]?.["data"]?.at(-2)) /
                        ClaimsOverTime_chData?.["datasets"]?.["data"]?.at(-2)
                        ) || "No Data"
                      }%
                      change from ${ClaimsOverTime_chData?.["datasets"]?.["data"]?.at(-2) || "No Data"} claims in ${ClaimsOverTime_chData?.["labels"].at(-2)} 
                      to ${ClaimsOverTime_chData?.["datasets"]?.["data"]?.at(-1) || "No Data"} in ${ClaimsOverTime_chData?.["labels"].at(-1)} 
                    `}
                />                
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="secondary"
                  title="Estimated Loss from Claims (USD)"
                  description="Estimated loss distribution from claims by selected filters."
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
                  chart={CauseOfClaims_chData || { labels: [], datasets: [] }}
                  description={` 
                      First 2 Causes accounts for
                      ${Math.round(
                        100.0 * CauseOfClaims_chData?.["datasets"]?.["data"]?.at(0) /
                        CauseOfClaims_chData?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0)
                      ) || "No Data"
                      }% 
                       (${CauseOfClaims_chData?.["datasets"]?.["data"]?.at(0)})
                      and 
                      ${Math.round(
                        100.0 * CauseOfClaims_chData?.["datasets"]?.["data"]?.at(1) /
                        CauseOfClaims_chData?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0)
                      ) || "No Data"
                      }% 
                       (${CauseOfClaims_chData?.["datasets"]?.["data"]?.at(1)})
                      respectively of total incidents
                  `}
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
                  description={` 
                      Most affected country is 
                      ${(AffectedCountries_chData?.["datasets"][0]?.["label"] || "No Data")} with
                      ${Math.round(100.0 * (AffectedCountries_chData?.["datasets"][0]?.["data"] || [0] || "No Data") /
                        AffectedCountries_chData?.["datasets"].reduce((sum, b) => 
                                                              sum + (b.data?.[0] || 0),0)
                        )}% 
                       (${(AffectedCountries_chData?.["datasets"][0]?.["data"] || [0]) || "No Data"}) claims.
                  `}
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
                    labels: TypesOfClaims_chData?.["labels"],
                    datasets: [
                      {
                        label: "No",
                        data: TypesOfClaims_chData?.["datasets"]?.["data"],
                        borderColor: 'rgba(255, 99, 132, 1)'
                      },
                    ],
                  }}
                  description={` 
                    Most Popular Claim Type is 
                    ${TypesOfClaims_chData?.["labels"]?.at(
                      TypesOfClaims_chData?.["datasets"]?.["data"]?.indexOf(Math.max(...(TypesOfClaims_chData?.["datasets"]?.["data"] || [0])))
                    ) || "No Data"} with 
                    ${(Math.max(...(TypesOfClaims_chData?.["datasets"]?.["data"] || [0])) || "No Data") /
                      TypesOfClaims_chData?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0) * 100.0 || "No Data"}%
                     (${(Math.max(...(TypesOfClaims_chData?.["datasets"]?.["data"] || [0])) || "No Data")})
                    claims.
                  `}
                />       
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
                description = "This Sankey diagram illustrates the flow of Claim Type (left) to their Results (right)."
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>

        {/* fifth row of the Dashboard */}
        <MDBox mt={3}>
          <Grid container spacing={3}>

            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                <HorizontalBarChart
                  color="secondary"
                  title="Sum of Estimated Loss (in Thousands) by Claim Cause"
                  date="campaign sent 2 days ago"
                  chart={SumLossEsimate || { labels: [], datasets: [] }}
                  description={` 
                      Total Estimated Loss is 
                      $${Math.round(SumLossEsimate?.["datasets"]?.["data"]?.reduce((a, b) => a + b, 0)) || "No Data"}K
                      with highest loss from
                      ${SumLossEsimate?.["labels"]?.at(
                        SumLossEsimate?.["datasets"]?.["data"]?.indexOf(Math.max(...(SumLossEsimate?.["datasets"]?.["data"] || [0])))
                      ) || "No Data"} at
                      $${Math.round(Math.max(...(SumLossEsimate?.["datasets"]?.["data"] || [0]))) || "No Data"}K.
                  `}
                />                
              </MDBox>
            </Grid>

            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                <HorizontalBarChart
                  color="secondary"
                  title="Avg of Estimated Loss (in Thousands) by Claim Cause (USD)"
                  date="campaign sent 2 days ago"
                  chart={incidentsByIndustry_TPY_Cause_AvgLoss?.["Output"]?.[selected_ClaimType] || { labels: [], datasets: [] }}
                  description={"Data shows the average estimated loss (USD in thousands) for each claim in claim cause."}
                />  
              </MDBox>
            </Grid>
            
          </Grid>
        </MDBox>

        {/* sixth row of the Dashboard */}
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
