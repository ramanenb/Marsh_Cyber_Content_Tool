/**
=========================================================
* Dashboard Horizontal Bar Chart 
- Count of attacks by threat actor, shaded by attacker_type w country in tooltip
- Count of attacks by Country
=========================================================
*/

import { useMemo, useState } from "react";

// porp-types is a library for typechecking of props
import PropTypes from "prop-types";

// react-chartjs-2 components
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// @mui material components
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// HorizontalBarChart configurations
import configs from "examples/Charts/BarCharts/HorizontalBarChart/configs";

// Material Dashboard 2 React base styles
import colors from "assets/theme/base/colors";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function HorizontalBarChart({ color, title, description, chart }) {
  const visibleCount = 6; // Number of bars to show at once
  const [startIndex, setStartIndex] = useState(0);
    console.log(chart);

  const rawDatasets = chart.datasets
    ? Array.isArray(chart.datasets) ? chart.datasets : [chart.datasets]
    : [];

  // get start and total number index for slicing data
  const totalDataPoints = chart.labels?.length || 0;
  const maxStartIndex = Math.max(0, totalDataPoints - visibleCount);

  // Get the visible slice of data
  const visibleLabels = chart.labels?.slice(startIndex, startIndex + visibleCount) || [];
  
  const chartDatasets = rawDatasets.map((dataset) => ({
    ...dataset,
    data: dataset.data?.slice(startIndex, startIndex + visibleCount) || [],
    weight: 5,
    borderWidth: 0,
    borderRadius: 4,
    backgroundColor: colors[dataset.color]
      ? colors[dataset.color || "dark"].main
      : colors.warning.main,
    fill: false,
    maxBarThickness: 35,
  }));

  const { data, options } = configs(visibleLabels, chartDatasets, visibleCount);

  // upon scrolling, change start index -> update the visible data range
  const handleScrollUp = () => {
    setStartIndex(Math.max(0, startIndex - 5));
  };

  const handleScrollDown = () => {
    setStartIndex(Math.min(maxStartIndex, startIndex + 5));
  };

  // Determine if scrolling is possible
  const canScrollUp = startIndex > 0;
  const canScrollDown = startIndex < maxStartIndex;

  return (
    <Card sx={{ height: "100%", width: "100%" }}>
      <MDBox padding="1rem">
        
        {/* This part is prely just for the scrolling functionality */}
        {useMemo(
          () => (
            <Box sx={{ position: "relative" }}>
              <MDBox
                variant="gradient"
                bgColor={color}
                borderRadius="lg"
                coloredShadow={color}
                py={2}
                pr={0.5}
                mt={-5}
                height="16.5rem"
                sx={{ position: "relative" }}
              >
                <Bar data={data} options={options} redraw />
                
                {/* Scroll Controls */}
                {totalDataPoints > visibleCount && (
                  <Box
                    sx={{
                      position: "absolute",
                      right: 8,
                      top: "50%",
                      transform: "translateY(-50%)",
                      display: "flex",
                      flexDirection: "column",
                      gap: 0.5,
                      backgroundColor: "rgba(0, 0, 0, 0.28)",
                      borderRadius: 1,
                      backdropFilter: "blur(4px)",
                    }}
                  >
                    <IconButton
                      size="small"
                      onClick={handleScrollUp}
                      disabled={!canScrollUp}
                      sx={{
                        color: "black",
                        "&:disabled": {
                          color: "rgba(255, 255, 255, 1)",
                        },
                      }}
                    >
                      <KeyboardArrowUpIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={handleScrollDown}
                      disabled={!canScrollDown}
                      sx={{
                        color: "black",
                        "&:disabled": {
                          color: "rgba(255, 255, 255, 1)",
                        },
                      }}
                    >
                      <KeyboardArrowDownIcon />
                    </IconButton>
                  </Box>
                )}
              </MDBox>
            </Box>
          ),
          [color, chart, startIndex, visibleCount, totalDataPoints, data, options]
        )}
        
        <MDBox pt={3} pb={1} px={1}>
          <MDBox sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <MDBox>
              <MDTypography variant="h6" textTransform="capitalize">
                {title}
              </MDTypography>
              <MDTypography component="div" variant="button" color="text" fontWeight="light">
                {description}
              </MDTypography>
            </MDBox>
            
            {/* Data Counter */}
            {totalDataPoints > visibleCount && (
              <MDTypography variant="caption" color="text">
                Showing {startIndex + 1}-{Math.min(startIndex + visibleCount, totalDataPoints)} of {totalDataPoints}
              </MDTypography>
            )}
          </MDBox>
        </MDBox>
      </MDBox>
    </Card>
  );
}

// Setting default values for the props of HorizontalBarChart
HorizontalBarChart.defaultProps = {
  icon: { color: "info", component: "" },
  title: "",
  description: "",
  height: "19.125rem",
};

// Typechecking props for the HorizontalBarChart
HorizontalBarChart.propTypes = {
  icon: PropTypes.shape({
    color: PropTypes.oneOf([
      "primary",
      "secondary",
      "info",
      "success",
      "warning",
      "error",
      "light",
      "dark",
    ]),
    component: PropTypes.node,
  }),
  title: PropTypes.string,
  description: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  chart: PropTypes.objectOf(PropTypes.array).isRequired,
};

export default HorizontalBarChart;