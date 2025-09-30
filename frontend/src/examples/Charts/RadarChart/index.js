import { useMemo } from "react";
import PropTypes from "prop-types";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Radar } from "react-chartjs-2";

// @mui components
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// configs
import configs from "./configs";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

function RadarChart({ color, title, description, chart }) {
  const { data, options } = configs(chart.labels || [], chart.datasets);

  return (
    <Card
      sx={{
        height: "100%",
        width: "100%",
        padding: "1rem",
      }}
    >
    <MDBox padding="1rem">
      {useMemo(
        () => (
          <MDBox
            variant="gradient"
              bgColor={color}
              borderRadius="lg"
              coloredShadow={color}
              py={2} 
              pr={0.5} 
              mt={-5} 
              height="16.5rem"
          >
            <Radar data={data} options={options} />
          </MDBox>
        ),
        [chart]
      )}
      <MDBox pt={3} textAlign="center">
        <MDTypography variant="h6" textTransform="capitalize">
          {title}
        </MDTypography>
        <MDTypography
          component="div"
          variant="button"
          color="text"
          fontWeight="light"
        >
          {description}
        </MDTypography>
      </MDBox>
    </MDBox>
    </Card>
  );
}

RadarChart.defaultProps = {
  title: "",
  description: "",
};

RadarChart.propTypes = {
  title: PropTypes.string,
  description: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  chart: PropTypes.shape({
    labels: PropTypes.array.isRequired,
    datasets: PropTypes.array.isRequired,
  }).isRequired,
};

export default RadarChart;
